
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.utils.uuid import uuid7
from langchain.chat_models import init_chat_model
from analysis_tools import slack_send_msg

checkpointer = InMemorySaver()


llm_google = init_chat_model(
    model="google_genai:gemini-3.5-flash"
)

analysis_agent = create_deep_agent(
    model = llm_google,
    tools=[slack_send_msg],
    backend=backend,
    checkpointer=checkpointer
)

thread_id = str(uuid7())
config = {
    "configurable":{
        "thread_id":thread_id
    }
}

from langchain_core.messages import HumanMessage
stream = analysis_agent.stream_events(
    {
        "messages":[
            HumanMessage(
                "Analyze /tmp/sales_data_new.csv in the current dir and generate a beautiful plot. "
        "When finished, send your analysis and the plot to Slack using the tool."
            )
        ]
    },
    version="v3",
    config=config
)

for snapshot in stream.values:
    snapshot["messages"][-1].pretty_print()
