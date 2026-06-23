# Agents Documentation

This file provides a list of agents and their configurations used in this project.

## Example Agent
```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a helpful assistant.",
    tools=[search, fetch_url],
    memory=["./AGENTS.md"],
    skills=["./skills/"],
)
```

Feel free to add more agent definitions and notes here.
