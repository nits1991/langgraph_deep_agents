"""QuickStart."""

from deepagents import create_deep_agent  # pyright: ignore[reportMissingTypeStubs]
from dotenv import load_dotenv

from .utils import format_messages

load_dotenv()  # Load environment variables from .env file if present.  # pyright: ignore[reportUnusedCallResult]


def get_weather(city: str) -> str:
    """Return a mock weather description for the given city.

    Args:
        city (str): The name of the city.

    Returns:
        str: A mock weather description.
    """
    return f"Weather in {city} is sunny."


if __name__ == "__main__":
    agent = create_deep_agent(
        model="google_genai:gemini-3.5-flash",
        tools=[get_weather],
        system_prompt="You are a helpful weather assistant",
    )
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "What's the weather like in New York?"}
            ]
        }
    )
    format_messages(result["messages"])  # pyright: ignore[reportAny]
