import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, HumanMessage

from src.graph.builder import graph
from src.memory import recall_from_memory, save_to_memory
from src.session import reset_session_state, session_state

AGENT_DISPLAY = {
    "nova": "Nova  (Supervisor)",
    "rajan": "Rajan (Billing)",
    "priya": "Priya (Tech Support)",
    "arjun": "Arjun (Retention)",
}

conversation_history: List = []


def chat(user_input: str) -> str:
    global conversation_history
    if session_state.get("customer_id"):
        save_to_memory(
            f"User said: {user_input}",
            {"type": "conversation", "customer_id": session_state["customer_id"]},
        )
    conversation_history.append(HumanMessage(content=user_input))
    result = graph.invoke(
        {"messages": conversation_history, "current_agent": "nova", "memory_context": ""},
        config={"recursion_limit": 20},
    )
    final_msg = None
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            final_msg = msg
            break
    conversation_history = result["messages"]
    agent = result.get("current_agent", "nova")
    label = AGENT_DISPLAY.get(agent, "Agent")
    text = final_msg.content if final_msg else "(no response)"
    print(f"\n{'='*60}")
    print(f"You   : {user_input}")
    print(f"{'-'*60}")
    print(f"{label}:")
    print(text)
    print(f"{'='*60}")
    return text


def reset_session():
    global conversation_history
    conversation_history = []
    reset_session_state()
    print("Session reset! (Vector memory preserved)")


def show_memory(query: str = "customer ticket billing"):
    print("\nMemory recall:")
    print(recall_from_memory(query, k=5))


def show_state():
    print("\nSession State:")
    for k, v in session_state.items():
        if k != "open_tickets":
            print(f"  {k}: {v}")
    print(f"\nOpen Tickets ({len(session_state['open_tickets'])}):")
    for t in session_state["open_tickets"]:
        print(f"  [{t['ticket_id']}] {t['issue_type']} | {t['status']} | {t['assigned_to']}")


if __name__ == "__main__":
    print("TelecomAI — Multi-Agent Customer Service System")
    print("Commands: 'exit', 'reset', 'memory', 'state'")
    print("=" * 60)
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Thanks for using TelecomAI!")
            break
        elif user_input.lower() == "reset":
            reset_session()
        elif user_input.lower() == "memory":
            show_memory()
        elif user_input.lower() == "state":
            show_state()
        else:
            chat(user_input)
