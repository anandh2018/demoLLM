import random

from langchain_core.tools import tool

from src.memory import save_to_memory
from src.session import session_state


@tool
def lookup_invoice(customer_id: str) -> str:
    """Look up the latest invoice for a customer."""
    dummy = {
        "C001": {"id": "INV-8821", "amount": "999 INR", "due": "2025-06-01", "status": "Unpaid"},
        "C002": {"id": "INV-9934", "amount": "1499 INR", "due": "2025-05-20", "status": "Paid"},
    }
    inv = dummy.get(
        customer_id,
        {"id": "INV-0000", "amount": "599 INR", "due": "2025-06-10", "status": "Unpaid"},
    )
    result = f"Invoice {inv['id']} | Amount: {inv['amount']} | Due: {inv['due']} | Status: {inv['status']}"
    save_to_memory(
        f"Customer {customer_id} invoice: {result}",
        {"type": "billing", "customer_id": customer_id},
    )
    return result


@tool
def process_payment(customer_id: str, amount: str) -> str:
    """Process a payment for the customer."""
    txn_id = f"TXN-{random.randint(100000, 999999)}"
    result = f"Payment of {amount} processed! Transaction ID: {txn_id}"
    save_to_memory(
        f"Customer {customer_id} paid {amount}. TXN: {txn_id}",
        {"type": "payment", "txn_id": txn_id, "customer_id": customer_id},
    )
    return result


@tool
def upgrade_plan(customer_id: str, new_plan: str) -> str:
    """Upgrade or change the customer's telecom plan."""
    plans = {
        "basic": "399 INR/mo - 2GB/day",
        "standard": "699 INR/mo - 3GB/day",
        "premium": "999 INR/mo - Unlimited",
        "ultra": "1499 INR/mo - Unlimited + OTT",
    }
    details = plans.get(new_plan.lower(), f"{new_plan} - custom pricing")
    session_state["plan"] = new_plan.lower()
    result = f"Plan upgraded to {new_plan.upper()} ({details}) for customer {customer_id}."
    save_to_memory(result, {"type": "plan_change", "customer_id": customer_id, "plan": new_plan})
    return result
