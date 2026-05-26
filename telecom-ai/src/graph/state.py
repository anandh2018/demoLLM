from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class TelecomState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str
    memory_context: str
