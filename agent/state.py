from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict, total=False):
    user_input: str
    messages: Annotated[list[BaseMessage], add_messages]
    intent: Literal["policy", "employee", "leave_balance", "leave_request", "general"]
    resolved_input: str
    employee_id: str
    context: str
    tool_result: dict
    answer: str
    approved: bool
