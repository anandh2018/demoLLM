from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.nodes import arjun_node, nova_node, priya_node, rajan_node
from src.graph.routing import after_tools, route_nova, specialist_route
from src.graph.state import TelecomState
from src.tools import ALL_TOOLS

tool_node = ToolNode(tools=ALL_TOOLS)

builder = StateGraph(TelecomState)
builder.add_node("nova", nova_node)
builder.add_node("rajan", rajan_node)
builder.add_node("priya", priya_node)
builder.add_node("arjun", arjun_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "nova")

builder.add_conditional_edges(
    "nova",
    route_nova,
    {"tools": "tools", "rajan": "rajan", "priya": "priya", "arjun": "arjun", END: END},
)
builder.add_conditional_edges("rajan", specialist_route, {"tools": "tools", END: END})
builder.add_conditional_edges("priya", specialist_route, {"tools": "tools", END: END})
builder.add_conditional_edges("arjun", specialist_route, {"tools": "tools", END: END})
builder.add_conditional_edges(
    "tools",
    after_tools,
    {"nova": "nova", "rajan": "rajan", "priya": "priya", "arjun": "arjun"},
)

graph = builder.compile()
