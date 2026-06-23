"""This guide walks you through creating your first deep agent with planning, file system tools, and subagent capabilities. You’ll build a research agent that can conduct research and write reports."""

import sys

sys.path.append("/Users/nitinaggarwal/Documents/learning/langgraph_deep_agents")

import os
from typing import Literal

from deepagents import create_deep_agent  # pyright: ignore[reportMissingTypeStubs]
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from tavily import TavilyClient

from .utils import format_messages

load_dotenv()  # pyright: ignore[reportUnusedCallResult]


# Load the model spec
from .llm_provider import get_model_spec

spec = get_model_spec("nvidia_llama_3_1_8b")
print(spec)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


## Create a search tool
def internet_research(
    user_query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a Internet research for a topic."""
    return tavily_client.search(
        query=user_query,
        max_results=max_results,
        topic=topic,
        include_raw_content=include_raw_content,
    )


## LLM Object
llm = init_chat_model(model=spec.model, model_provider=spec.provider)

## Create a deep agent

system_prompt = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

deep_agent = create_deep_agent(
    model=llm,
    tools=[internet_research],
    system_prompt=system_prompt,
    name="research_agent",
)

while True:
    result = deep_agent.invoke(
        {
            "messages": [
                (
                    HumanMessage(
                        content="Conduct research on the latest developments in renewable energy and write a report."
                    )
                ),
                (
                    HumanMessage(
                        content="Include information on solar, wind, and hydro power technologies."
                    )
                ),
            ]
        }
    )

    format_messages(result["messages"])  # pyright: ignore[reportAny]
