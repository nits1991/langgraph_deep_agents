Introduction

Welcome to LangChain Academy’s Deep Agents course!

There are now several successful examples of long-running, highly capable agents. We've given the name 'Deep Agents' to these, as they are distinctly different than previous generations of agents. In this course, you will learn what makes them different and will build your own Deep Agent.

At LangChain, we've built a Deep Agent that is simple and configurable, allowing users to build long-running agents quickly and simply.

In this course, you'll build a deep research agent using a Deep Agent.  This course is divided into seven modules.

Each module includes a video lesson to walk you through key concepts, along with corresponding notebooks.

A special thank you to Dmitry Labazkin for his contributions and feedback on this course.


Setup

Prerequisites

Python version

Ensure you're using Python 3.11 or later. This version is required for optimal compatibility with LangGraph.

python3 --version

uv package manager

curl -LsSf https://astral.sh/uv/install.sh | sh
# Update PATH to use the new uv version
export PATH="/Users/$USER/.local/bin:$PATH"

Installation

We'll be using the set of notebooks located here.  Each module will also include links to the corresponding notebooks.

Clone the repository

git clone https://github.com/langchain-ai/deep-agents-from-scratch.git
cd deep-agents-from-scratch

Install the package and dependencies

This automatically creates and manages the virtual environment:

uv sync

Sign up for LangSmith

Create a LangSmith account and API key. You can reference LangSmith docs here.

Navigate to the Settings page, and generate an API key in LangSmith.

Set up LLM API keys

If you don’t have an Anthropic API key, you can sign up here.

If you don’t have an OpenAI API key, you can sign up here.

 Tavily for web search

Tavily Search API is a search engine optimized for LLMs, aimed at efficient, quick, and persistent search results. You can sign up for an API key here. It’s easy to sign up and offers a generous free tier. We'll use Tavily for building research agents with external search.

Set environment variables

Create a .env file in the project root directory:

# Copy the example.env file to .env
cp example.env  .env

Edit the .env file with the following:

# Required for research agents with external search
TAVILY_API_KEY=your_tavily_api_key_here

# Required for model usage
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For evaluation and tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=deep-agents-from-scratch
# If you are on the EU instance:
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com

You can alternatively set the environment variables in your terminal.

export TAVILY_API_KEY=your_tavily_api_key_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
# Optional: For evaluation and tracing
export LANGSMITH_API_KEY=your_langsmith_api_key_here
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=deep-agents-from-scratch


Running notebooks

If you don't have Jupyter set up, follow the installation instructions here.

You can run Jupyter notebooks directly:

uv run jupyter notebook

Or activate the virtual environment if preferred:

source .venv/bin/activate

On windows:
.venv\Scripts\activate jupyter notebook


Background

Deep Research broke out as one of the first major agent use-cases, along with coding.

Now, we're seeing an emergence of general-purpose agents that can be used for a wide range of tasks. For example, Manus has gained significant attention and popularity for long-horizon tasks; the average Manus task uses ~50 tool calls!

As a second example, Claude Code is being used generally for tasks beyond coding.

Careful review of the context engineering patterns across these popular "deep" agents shows some common approaches:

    Task planning (e.g., todo), often with recitation
    Context offloading to file systems
    Context isolation through sub-agent delegation

This course will show how to implement these patterns from scratch using LangGraph.


Organization

Tutorial Overview

This repository contains five progressive notebooks that teach you to build advanced AI agents:

0_create_agent.ipynb - Create Agent Component

Learn to use the create_agent component. This component:

    Implements a ReAct (Reason-Act) loop that is the foundation for many agents
    Is easy to use and quick to set up
    Is the core building block for the Deep Agent

1_todo.ipynb - Task Planning Foundations

Learn to implement structured task planning using TODO lists. This notebook introduces:

    Task tracking with status management (pending/in_progress/completed)
    Progress monitoring and context management
    The `write_todos()` tool for organizing complex multi-step workflows
    Best practices for maintaining focus and preventing task drift

2_files.ipynb - Virtual File Systems

Implement a virtual file system stored in agent state for context offloading:

    File operations: `Is()`, `read_file()`, `write_file()`
    Context management through information persistence
    Enabling agent "memory" across conversation turns
    Reducing token usage by storing detailed information in files

3_subagents.ipynb - Context Isolation

Master sub-agent delegation for handling complex workflows:

    Creating specialized sub-agents with focused tool sets
    Context isolation to prevent confusion and task interference
    The `task()` delegation tool and agent registry patterns
    Parallel execution capabilities for independent research streams

4_full_agent.ipynb - Complete Research Agent

Combine all techniques into a production-ready research agent:

    Integration of TODOs, files, and sub-agents
    Real web search with intelligent context offloading
    Content summarization and strategic thinking tools
    Complete workflow for complex research tasks

Each notebook builds on the previous concepts, culminating in a sophisticated agent architecture capable of handling real-world research and analysis tasks.

Course Overview

    Notebook Reference: No notebooks in this lesson. See 'Getting Set Up' for the git repo.
    Overview Slides: Deep Agents.pdf
    Other resources:
        Quickstart for LangGraph
            Workflow Documentation
            Building Effective Agents (YouTube)
            How to Apply Context Engineering
        Foundations for LangGraph/LangSmith
            Introduction to LangGraph
            Introduction to LangSmith
