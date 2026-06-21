"""Research Tools.

This module provides search and content processing utilities for the research agent,
including web search capabilities and content summarization tools.
"""

from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated
from langgraph.prebuilt import InjectedState
from state import DeepAgentState
from IPython import core
from IPython import core
import uuid
import os
import base64
## Model for summarization to be used only for generaing summaries within the web_research agent tool
import httpx
from typing import List
from prompts import SUMMARIZE_WEB_SEARCH
from langchain_core.tools import InjectedToolArg, InjectedToolCallId, tool
from langchain_core.messages import HumanMessage
from typing import Literal
from datetime import datetime
from pydantic import Field
from pydantic import BaseModel
from tavily import TavilyClient
from langchain.chat_models import init_chat_model
from markdownify import markdownify
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from langchain_groq import ChatGroq


summarization_model = ChatNVIDIA(
  model="meta/llama-3.1-8b-instruct",
  api_key="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",
  temperature=1,
  top_p=0.95,
  max_completion_tokens=8192,
)

## Search Engine clil
tavily_client = TavilyClient()

## Summarization model should only respond with structured output
class Summary(BaseModel):
    """Schema for web page content summary"""
    filename:str = Field(description="Name of the file to store the summary")
    summary:str = Field(description="Key Learnings from the web page")


def get_today_str()->str:
    """Get Current date in human readable format"""
    return datetime.now().strftime("%a %b % -d, %Y")


def run_tavily_search(
    search_query:str,
    max_results:int=1,
    topic:Literal["general","news","finance"]="general",
    include_raw_content:bool=True
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
        topic=topic
    )
    print(f"search_result_links from run_tavily_search for query :{search_query} are : \n{search_result_links}")
    return search_result_links


def summarize_webpage_content(
    webpage_content:str
) -> Summary:
    """Summarize webpage content using the configured summarization model.

    Args:
        webpage_content: Raw webpage content to summarize

    Returns:
        Summary object with filename and summary
    """
    try:
        summarization_model_structured=summarization_model.with_structured_output(Summary)

        ## Genrate Summary
        summary_and_filename =summarization_model_structured.invoke(
            [
                HumanMessage(content=SUMMARIZE_WEB_SEARCH.format(
                    webpage_content=webpage_content,
                    date=get_today_str
                ))
            ]
        )
        print(f"summary_and_filename from summarizer module is : \n{summary_and_filename}")
        return summary_and_filename # type: ignore
    except Exception:
        # Return a basic summary on failure
        return Summary(
            filename="failure_path_search_result.md",
            summary=webpage_content[:1000] + "..." if len(webpage_content)>1000 else webpage_content
        )


def process_search_results(
    search_result_hits:dict
)->List[dict]:
    """Process search results by summarizing content where available.

    Args:
        results: Tavily search results dictionary

    Returns:
        List of processed results with summaries
    """
    processed_results = []

    HTTPX_CLIENT = httpx.Client(timeout=30.0)

    for search_result in search_result_hits.get("results",[]):
        url = search_result['url']
        try:
            response = HTTPX_CLIENT.get(url)
            if response.status_code==200:
                raw_content = markdownify(response.text)
                summary_obj = summarize_webpage_content(raw_content)

                ## Convert HTML to Markdown
            else:
                 # Use Tavily's generated summary
                raw_content = search_result.get('raw_content', '')
                summary_obj = Summary(
                    filename="URL_error.md",
                    summary=search_result.get('content', 'Error reading URL; try another search.')
                )
        except Exception:
           # Handle timeout or connection errors gracefully
            raw_content = search_result.get('raw_content', '')
            summary_obj = Summary(
                filename="connection_error.md",
                summary=search_result.get('content', f'Could not fetch URL (timeout/connection error). Try another search.')
            )

        # uniquify file names
        uid = base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b"=").decode("ascii")[:8]
        name, ext = os.path.splitext(summary_obj.filename)
        summary_obj.filename = f"{name}_{uid}{ext}"

        processed_results.append({
            'url': search_result['url'],
            'title': search_result['title'],
            'summary': summary_obj.summary,
            'filename': summary_obj.filename,
            'raw_content': raw_content,
        })
    print(f"processed_results from method process search results is : \n{processed_results}")
    return processed_results


## Glue all above code in the tool

@tool(parse_docstring=True)
def tavily_search_tool(
    query:str,
    state: Annotated[DeepAgentState,InjectedState],
    tool_call_id : Annotated[str,InjectedToolCallId],
    max_results: Annotated[int, InjectedToolArg] =1,
    topic : Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
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
        query,
        max_results=max_results,
        topic=topic,
        include_raw_content=True
    )
    processed_results = process_search_results(search_results_links)
    files =state.get("files",{})
    saved_files=[]
    summaries=[]
    print(f"processed_results just before dumping to filesystem is :\n{processed_results} ")
    for i, result in enumerate(processed_results):
        filename = result['filename']
        file_content = f"""# Search Result: {result['title']}

            **URL:** {result['url']}
            **Query:** {query}
            **Date:** {get_today_str()}

            ## Summary
            {result['summary']}

            ## Raw Content
            {result['raw_content'] if result['raw_content'] else 'No raw content available'}
            """
        files[filename] = file_content
        saved_files.append(filename)
        summaries.append(f"- {filename}: {result['summary']}...")
    # Create minimal summary for tool message - focus on what was collected
    summary_text = f"""🔍 Found {len(processed_results)} result(s) for '{query}':

        {chr(10).join(summaries)}

        Files: {', '.join(saved_files)}
    💡 Use read_file() to access full details when  needed. """
    return Command(
        update={
            "files" : files,
            "messages":[
                ToolMessage(summary_text,tool_call_id=tool_call_id)
            ]
        }
    )

@tool(parse_docstring=True)
def think_tool(reflection:str)->str:
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
