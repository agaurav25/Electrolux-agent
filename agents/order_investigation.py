from datetime import datetime
from data.mock_orders import get_order_by_id
from utils.logger import log_investigation


def investigate_order(order_id):
    log_investigation(order_id, "OrderInvestigationAgent", "Starting order investigation")
    order = get_order_by_id(order_id)

    if not order:
        log_investigation(order_id, "OrderInvestigationAgent", "Order not found")
        return None

    created = datetime.fromisoformat(order["order_created_time"])
    elapsed = (datetime.now() - created).total_seconds() / 3600

    lifecycle_stage = _determine_lifecycle_stage(order)
    systems = _check_system_statuses(order)

    result = {
        "order": order,
        "lifecycle_stage": lifecycle_stage,
        "elapsed_hours": round(elapsed, 1),
        "systems": systems
    }

    log_investigation(order_id, "OrderInvestigationAgent",
                      f"Investigation complete – stage: {lifecycle_stage}")
    return result


def _determine_lifecycle_stage(order):
    if order["shipment_status"] in ["In Transit", "Delivered"]:
        return "Shipment"
    if order["fulfillment_status"] in ["Shipped", "Packed", "Partially Fulfilled"]:
        return "Fulfillment"
    if order["erp_status"] == "Confirmed":
        return "Processing"
    if order["payment_status"] == "Authorized":
        return "ERP Submission"
    if order["payment_status"] in ["Processing", "Failed"]:
        return "Payment"
    return "Order Created"


def _check_system_statuses(order):
    systems = {
        "Commerce/OMS": _evaluate_health("OMS", order),
        "Payment Gateway": _evaluate_health("Payment", order),
        "ERP System": _evaluate_health("ERP", order),
        "Fulfillment/WMS": _evaluate_health("Fulfillment", order),
        "Logistics": _evaluate_health("Logistics", order)
    }
    return systems


def _evaluate_health(system_key, order):
    status_map = {
        "Payment": order["payment_status"],
        "ERP": order["erp_status"],
        "Fulfillment": order["fulfillment_status"],
        "Logistics": order["shipment_status"],
        "OMS": "Active"
    }

    current_status = status_map.get(system_key, "Unknown")

    has_errors = any(
        log["system"].lower().startswith(system_key.lower()[:3])
        for log in order["integration_error_logs"]
        if log["severity"] in ["Critical", "Warning"]
    )

    failed_keywords = ["failed", "stuck", "rejected", "delayed", "error", "cancelled"]
    is_failed = any(kw in current_status.lower() for kw in failed_keywords)

    if is_failed:
        health = "Critical"
    elif has_errors:
        health = "Degraded"
    else:
        health = "Healthy"

    return {
        "status": current_status,
        "health": health,
        "has_errors": has_errors
    }
