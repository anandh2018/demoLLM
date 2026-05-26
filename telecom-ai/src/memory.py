import random
from datetime import datetime
from typing import Any, Dict

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from src.config import MEMORY_K
from src.models import embeddings
from src.session import session_state

memory_store = FAISS.from_documents(
    [Document(page_content="TelecomAI memory initialized.", metadata={"type": "init"})],
    embeddings,
)


def save_to_memory(content: str, metadata: Dict[str, Any]):
    doc = Document(page_content=content, metadata=metadata)
    memory_store.add_documents([doc])


def recall_from_memory(query: str, k: int = MEMORY_K) -> str:
    results = memory_store.similarity_search(query, k=k)
    relevant = [r for r in results if r.metadata.get("type") != "init"]
    if not relevant:
        return "No prior memory found."
    lines = []
    for r in relevant:
        meta_str = ", ".join(f"{mk}: {mv}" for mk, mv in r.metadata.items())
        lines.append(f"[{meta_str}] {r.page_content}")
    return "\n".join(lines)


def create_ticket(issue_type: str, description: str, agent: str) -> Dict[str, Any]:
    ticket = {
        "ticket_id": f"TKT-{random.randint(10000, 99999)}",
        "issue_type": issue_type,
        "description": description,
        "status": "Open",
        "assigned_to": agent,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "customer_id": session_state.get("customer_id", "Unknown"),
    }
    session_state["open_tickets"].append(ticket)
    save_to_memory(
        f"Ticket {ticket['ticket_id']}: {issue_type} - {description}. Status: Open. Agent: {agent}.",
        {"type": "ticket", "ticket_id": ticket["ticket_id"], "status": "Open", "agent": agent},
    )
    return ticket
