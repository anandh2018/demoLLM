from langchain_core.messages import SystemMessage

from src.agents.prompts import arjun_system, nova_system, priya_system, rajan_system
from src.memory import recall_from_memory
from src.models import llm
from src.tools import ALL_TOOLS, BILLING_TOOLS, NOVA_TOOLS, RETAIN_TOOLS, TECH_TOOLS

nova_llm = llm.bind_tools(ALL_TOOLS)
rajan_llm = llm.bind_tools(BILLING_TOOLS)
priya_llm = llm.bind_tools(TECH_TOOLS)
arjun_llm = llm.bind_tools(RETAIN_TOOLS)


def nova_node(state):
    ctx = recall_from_memory(state["messages"][-1].content)
    resp = nova_llm.invoke([SystemMessage(content=nova_system(ctx))] + state["messages"])
    return {"messages": [resp], "current_agent": "nova", "memory_context": ctx}


def rajan_node(state):
    ctx = recall_from_memory(state["messages"][-1].content)
    resp = rajan_llm.invoke([SystemMessage(content=rajan_system(ctx))] + state["messages"])
    return {"messages": [resp], "current_agent": "rajan", "memory_context": ctx}


def priya_node(state):
    ctx = recall_from_memory(state["messages"][-1].content)
    resp = priya_llm.invoke([SystemMessage(content=priya_system(ctx))] + state["messages"])
    return {"messages": [resp], "current_agent": "priya", "memory_context": ctx}


def arjun_node(state):
    ctx = recall_from_memory(state["messages"][-1].content)
    resp = arjun_llm.invoke([SystemMessage(content=arjun_system(ctx))] + state["messages"])
    return {"messages": [resp], "current_agent": "arjun", "memory_context": ctx}
