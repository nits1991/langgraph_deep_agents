"""Web Research Assistant.

This script provides a tool for conducting web research and summarizing content using various APIs. It includes tools for searching the web, summarizing webpage content, and managing task delegation.

Key Features:
- Web search with Tavily API
- Summarization of webpage content using OpenAI's GPT-5 model
- Storage and retrieval of research results
- Task delegation to sub-agents

Usage:
1. Run the script to enter interactive mode.
2. Enter a search query to start the web research process.
3. Analyze the summaries and decide on next steps using the provided tools.

Dependencies:
- Python 3.x
- dotenv
- httpx
- langchain
- markdownify
- pydantic
- tavily

Installation:
1. Clone the repository: https://github.com/your-repo/web-research-assistant.git
2. Install dependencies: pip install -r requirements.txt
3. Set up environment variables in a .env file:
    OPENAI_API_KEY_2=your-openai-api-key
"""

import base64
import os
import uuid
from datetime import datetime
from typing import Annotated, Literal

import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import InjectedToolArg, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from markdownify import markdownify
from pydantic import BaseModel, Field
from tavily import TavilyClient

from .file_tools import ls, read_file, write_file
from .prompts import *  # noqa: F403
from .state import DeepAgentState
from .task_tool import _create_task_tool
from .todo_tools import read_todos, write_todos
from .utils import *  # noqa: F403

load_dotenv()  # pyright: ignore[reportUnusedCallResult]

openai_key = os.getenv("OPENAI_API_KEY_2")

summarization_model = init_chat_model(model="gpt-5-nano", api_key=openai_key)

## Search Engine clil
tavily_client = TavilyClient()


class Summary(BaseModel):
    """Schema for web page content summary."""

    filename: str = Field(description="Name of the file to store the summary")
    summary: str = Field(description="Key Learnings from the web page")


def run_tavily_search(
    search_query: str,
    max_results: int = 1,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = True,
) -> dict:
    """Perform search using Tavily API for a single query.

    Args:
        search_query: Search query to execute
        max_results: Maximum number of results per query
        topic: Topic filter for search results
        include_raw_content: Whether to include raw webpage content

    Returns:
        Search results dictionary
    """
    search_result_links = tavily_client.search(
        search_query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return search_result_links


def get_today_str() -> str:
    """Get Current date in human readable format."""
    return datetime.now().strftime("%a %b % -d, %Y")


def summarize_webpage_content(webpage_content: str) -> Summary:
    """Summarize webpage content using the configured summarization model.

    Args:
        webpage_content: Raw webpage content to summarize

    Returns:
        Summary object with filename and summary
    """
    try:
        summarization_model_structured = summarization_model.with_structured_output(
            Summary
        )

        ## Genrate Summary
        summary_and_filename = summarization_model_structured.invoke(
            [
                HumanMessage(
                    content=SUMMARIZE_WEB_SEARCH.format(  # noqa: F405
                        webpage_content=webpage_content, date=get_today_str
                    )
                )
            ]
        )

        return summary_and_filename
    except Exception:
        # Return a basic summary on failure
        return Summary(
            filename="failure_path_search_result.md",
            summary=webpage_content[:1000] + "..."
            if len(webpage_content) > 1000
            else webpage_content,
        )


def process_search_results(search_result_hits: dict) -> list[dict]:
    """Process search results by summarizing content where available.

    Args:
        results: Tavily search results dictionary

    Returns:
        List of processed results with summaries
    """
    processed_results = []

    HTTPX_CLIENT = httpx.Client(timeout=30.0)

    for search_result in search_result_hits.get("results", []):
        url = search_result["url"]
        try:
            response = HTTPX_CLIENT.get(url)
            if response.status_code == 200:
                raw_content = markdownify(response.text)
                summary_obj = summarize_webpage_content(raw_content)

                ## Convert HTML to Markdown
            else:
                # Use Tavily's generated summary
                raw_content = search_result.get("raw_content", "")
                summary_obj = Summary(
                    filename="URL_error.md",
                    summary=search_result.get(
                        "content", "Error reading URL; try another search."
                    ),
                )
        except Exception:
            # Handle timeout or connection errors gracefully
            raw_content = search_result.get("raw_content", "")
            summary_obj = Summary(
                filename="connection_error.md",
                summary=search_result.get(
                    "content",
                    "Could not fetch URL (timeout/connection error). Try another search.",
                ),
            )

        # uniquify file names
        uid = (
            base64.urlsafe_b64encode(uuid.uuid4().bytes)
            .rstrip(b"=")
            .decode("ascii")[:8]
        )
        name, ext = os.path.splitext(summary_obj.filename)
        summary_obj.filename = f"{name}_{uid}{ext}"

        processed_results.append(
            {
                "url": search_result["url"],
                "title": search_result["title"],
                "summary": summary_obj.summary,
                "filename": summary_obj.filename,
                "raw_content": raw_content,
            }
        )

    return processed_results


## Glue all above code in the tool


@tool(parse_docstring=True)
def tavily_search_tool(
    query: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    max_results: Annotated[int, InjectedToolArg] = 1,
    topic: Annotated[
        Literal["general", "news", "finance"], InjectedToolArg
    ] = "general",
) -> Command:
    """Search web and save detailed results to files while returning minimal context.

    Performs web search and saves full content to files for context offloading.
    Returns only essential information to help the agent decide on next steps.

    Args:
        query: Search query to execute
        state: Injected agent state for file storage
        tool_call_id: Injected tool call identifier
        max_results: Maximum number of results to return (default: 1)
        topic: Topic filter - 'general', 'news', or 'finance' (default: 'general')

    Returns:
        Command that saves full results to files and provides minimal summary
    """
    search_results_links = run_tavily_search(
        query, max_results=max_results, topic=topic, include_raw_content=True
    )
    processed_results = process_search_results(search_results_links)
    files = state.get("files", {})
    saved_files = []
    summaries = []
    for i, result in enumerate(processed_results):
        filename = result["filename"]
        file_content = f"""# Search Result: {result["title"]}

            **URL:** {result["url"]}
            **Query:** {query}
            **Date:** {get_today_str()}

            ## Summary
            {result["summary"]}

            ## Raw Content
            {result["raw_content"] if result["raw_content"] else "No raw content available"}
            """
        files[filename] = file_content
        saved_files.append(filename)
        summaries.append(f"- {filename}: {result['summary']}...")
    # Create minimal summary for tool message - focus on what was collected
    summary_text = f"""🔍 Found {len(processed_results)} result(s) for '{query}':

        {chr(10).join(summaries)}

        Files: {", ".join(saved_files)}
    💡 Use read_file() to access full details when  needed. """
    return Command(
        update={
            "files": files,
            "messages": [ToolMessage(summary_text, tool_call_id=tool_call_id)],
        }
    )


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?
    - How complex is the question: Have I reached the number of search limits?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Reflection recorded: {reflection}"


model = init_chat_model(model="gpt-5-nano", api_key=openai_key)

max_concurrent_research_units = 3
max_researcher_iterations = 3


sub_agent_tools = [tavily_search_tool, think_tool, read_file]
built_in_tools = [ls, read_file, write_file, write_todos, read_todos, think_tool]

# Create research sub-agent
research_sub_agent = {
    "name": "research-agent",
    "description": "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
    "prompt": RESEARCHER_INSTRUCTIONS.format(date=get_today_str()),
    "tools": ["tavily_search_tool", "think_tool", "read_file"],
}

task_tool = _create_task_tool(
    sub_agent_tools, [research_sub_agent], model, DeepAgentState
)


delegation_tools = [task_tool]

all_tools = sub_agent_tools + built_in_tools + delegation_tools

SUBAGENT_INSTRUCTIONS = SUBAGENT_USAGE_INSTRUCTIONS.format(
    max_concurrent_research_units=max_concurrent_research_units,
    max_researcher_iterations=max_researcher_iterations,
    date=datetime.now().strftime("%a %b %-d, %Y"),
)


MAIN_AGENT_INSTRUCTION = (
    "# TODO MANAGEMENT\n"
    + TODO_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# FILE SYSTEM USAGE\n"
    + FILE_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# SUB-AGENT DELEGATION\n"
    + SUBAGENT_INSTRUCTIONS
)


main_agent = create_agent(
    model=model,
    tools=all_tools,
    system_prompt=MAIN_AGENT_INSTRUCTION,
    state_schema=DeepAgentState,
)


def run_agent():
    """Run Agent.

    Args:
    - None

    Returns:
    - None
    """
    while True:
        user_input = input("User: ")
        response = main_agent.invoke({"messages": [(HumanMessage(user_input))]})
        format_messages(response["messages"])


if __name__ == "__main__":
    run_agent()
