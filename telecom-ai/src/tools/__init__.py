from src.tools.billing import lookup_invoice, process_payment, upgrade_plan
from src.tools.technical import run_network_diagnostic, reset_network_settings, check_tower_status
from src.tools.retention import get_available_offers, process_cancellation_request
from src.tools.general import verify_customer, check_ticket_status

BILLING_TOOLS = [lookup_invoice, process_payment, upgrade_plan]
TECH_TOOLS = [run_network_diagnostic, reset_network_settings, check_tower_status]
RETAIN_TOOLS = [get_available_offers, process_cancellation_request]
NOVA_TOOLS = [verify_customer, check_ticket_status]
ALL_TOOLS = NOVA_TOOLS + BILLING_TOOLS + TECH_TOOLS + RETAIN_TOOLS
