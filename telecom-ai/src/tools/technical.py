import random

from langchain_core.tools import tool

from src.memory import create_ticket, save_to_memory


@tool
def run_network_diagnostic(customer_id: str, issue_type: str) -> str:
    """Run a network diagnostic for a customer's connection issue."""
    findings = [
        "Signal strength 72% - slight interference detected.",
        "Network congestion in your zone during peak hours (7PM-10PM).",
        "SIM card may need re-seating. Try removing and reinserting.",
        "Tower maintenance scheduled nearby. ETA: 2 hours.",
    ]
    finding = random.choice(findings)
    ticket = create_ticket("Network Issue", f"{issue_type} - Diagnostic: {finding}", "Priya")
    return f"Diagnostic complete. Finding: {finding}\nTicket raised: {ticket['ticket_id']}"


@tool
def reset_network_settings(customer_id: str) -> str:
    """Reset the customer's network settings remotely."""
    result = (
        f"Network settings reset for customer {customer_id}. "
        "Please restart your device. Takes ~2 minutes."
    )
    save_to_memory(
        result,
        {"type": "tech_action", "customer_id": customer_id, "action": "network_reset"},
    )
    return result


@tool
def check_tower_status(area_code: str) -> str:
    """Check telecom tower status for a given area."""
    statuses = [
        "All towers operational.",
        "Partial outage - 1 tower under maintenance.",
        "Major outage - engineers dispatched.",
    ]
    return f"Tower status for area {area_code}: {random.choice(statuses)}"
