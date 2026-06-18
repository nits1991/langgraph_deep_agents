import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model
from langchain.agents import AgentState, create_agent
from typing import  Annotated, List, Union, Literal
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId,tool
from langgraph.prebuilt import InjectedState
from IPython.display import Image, display
## Add in wo
from utils import format_messages

load_dotenv()

# llm = ChatGoogleGenerativeAI(
#     model = 'gemini-3.5-flash'
# )

llm = init_chat_model(
    model='google_genai:gemini-2.5-flash',
    temperature=0.0
)

def reduce_list(left: List[str] | None, right: List[str] | None) -> List[str]:
    """Safely combine two lists of strings, handling cases where either or both inputs might be None.

    Args:
        left (List[str] | None): The first list to combine, or None.
        right (List[str] | None): The second list to combine, or None.

    Returns:
        List[str]: A new list containing all elements from both input lists.
               If an input is None, it's treated as an empty list.
    """
    if not left:
        left = []
    if not right:
        right = []
    return left + right

class CalcState(AgentState):
    """Graph State."""
    # add type hint
    ops: Annotated[List[str], reduce_list]

@tool
def calculator_wstate(
    operation:Literal['ADD','SUB','MUL','DIV'],
    num1:Union[int,float],
    num2:Union[int,float],
    tool_call_id:Annotated[str,InjectedToolCallId],
    state:Annotated[CalcState,InjectedState]
):
    """Define a two-input calculator tool that returns precise answers.

    Arg:
        operation (str): The operation to perform ('add', 'subtract', 'multiply', 'divide').
        a (float or int): The first number.
        b (float or int): The second number.
        tool_call_id (str): The tool call id.
        
    Returns:
        result (float or int): the result of the operation
    Example
        Divide: result   = a / b
        Subtract: result = a - b
    """
    if operation=='DIV' and num2==0:
        return {'error':'division by zero'}

    if operation=='ADD':
        result=num1+num2
    elif operation=='SUB':
        result=num1-num2
    elif operation=='MUL':
        result=num1*num2
    elif operation=='DIV':
        result=num1/num2
    else:
        result = 'invalid operation'
    ops = [f'({operation}, {num1}, {num2}) = {result}']
    # return {'result':result}
    Command(
        update={
            'ops':ops,
            'messages':[
                ToolMessage(f"{result}",tool_call_id=tool_call_id)
            ]
        }
    )


tools = [calculator_wstate]

SYSTEM_PROMPT = """
You are a helpful arithmetic assistant who is an expert at using a calculator. 
Return all text as plain text without Markdown math delimiters.
"""

agent = create_agent(
    llm,
    tools,
    system_prompt=SYSTEM_PROMPT,
    state_schema=CalcState
).with_config({
    "recursion_limit":20 #recursion_limit limits the number of steps the agent will run
})

print (f'The type of agent is : {type(agent)}')
# graph_image = agent.get_graph(xray=True).draw_mermaid_png()
# with open("graph.png","wb") as f:
#     f.write(graph_image)

result = agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":"what is 2/1 and 4+7 and 6/3"
            }
        ]
    }
)

format_messages(result['messages'])
print(result)



