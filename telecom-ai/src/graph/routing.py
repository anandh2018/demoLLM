from langgraph.graph import END


def route_nova(state):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    content = last.content.lower() if hasattr(last, "content") else ""
    if "rajan" in content or "billing" in content:
        return "rajan"
    if "priya" in content or "tech" in content:
        return "priya"
    if "arjun" in content or "retention" in content:
        return "arjun"
    return END


def specialist_route(state):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def after_tools(state):
    return state.get("current_agent", "nova")
