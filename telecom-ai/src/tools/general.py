from datetime import datetime

from langchain_core.tools import tool

from src.memory import recall_from_memory, save_to_memory
from src.session import session_state


@tool
def verify_customer(customer_id: str, phone_last4: str) -> str:
    """Verify a customer's identity using their ID and last 4 digits of phone."""
    if len(phone_last4) == 4 and phone_last4.isdigit():
        session_state["customer_id"] = customer_id
        session_state["verified"] = True
        session_state["account_name"] = f"Customer-{customer_id}"
        save_to_memory(
            f"Customer {customer_id} verified at {datetime.now().strftime('%H:%M')}.",
            {"type": "verification", "customer_id": customer_id},
        )
        return f"Identity verified! Welcome, Customer {customer_id}."
    return "Verification failed. Please check your Customer ID and phone number."


@tool
def check_ticket_status(ticket_id: str) -> str:
    """Check the status of a support ticket."""
    for t in session_state["open_tickets"]:
        if t["ticket_id"] == ticket_id:
            return (
                f"Ticket {ticket_id}\n"
                f"  Issue: {t['issue_type']}\n"
                f"  Status: {t['status']}\n"
                f"  Agent: {t['assigned_to']}\n"
                f"  Created: {t['created_at']}"
            )
    mem = recall_from_memory(f"ticket {ticket_id}")
    if "No prior memory" not in mem:
        return f"From memory:\n{mem}"
    return f"Ticket {ticket_id} not found. Please check the ID."
