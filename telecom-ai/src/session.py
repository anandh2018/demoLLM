from typing import Any, Dict, List

session_state: Dict[str, Any] = {
    "customer_id": None,
    "account_name": None,
    "open_tickets": [],
    "plan": None,
    "verified": False,
}


def reset_session_state():
    session_state.update({
        "customer_id": None,
        "account_name": None,
        "open_tickets": [],
        "plan": None,
        "verified": False,
    })
