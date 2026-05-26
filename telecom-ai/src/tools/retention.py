import random

from langchain_core.tools import tool

from src.memory import create_ticket, save_to_memory


@tool
def get_available_offers(customer_id: str) -> str:
    """Fetch personalized retention offers for the customer."""
    offers = [
        "30% off next 3 months if you stay on Premium.",
        "Free 6-month OTT bundle (Netflix + Hotstar) with upgrade.",
        "Double data for 60 days at no extra charge.",
        "Cashback of 500 INR on next recharge.",
    ]
    selected = random.sample(offers, k=2)
    result = "\n".join(f"- {o}" for o in selected)
    save_to_memory(
        f"Offers shown to {customer_id}: {result}",
        {"type": "offer", "customer_id": customer_id},
    )
    return result


@tool
def process_cancellation_request(customer_id: str, reason: str) -> str:
    """Log a cancellation or port-out request."""
    ticket = create_ticket("Cancellation Request", reason, "Arjun")
    return (
        f"Cancellation request logged. Ticket: {ticket['ticket_id']}\n"
        "A retention specialist will call you within 24 hours."
    )
