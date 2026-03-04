from utils.logger import log_investigation


def diagnose_integrations(investigation_result):
    if not investigation_result:
        return None

    order = investigation_result["order"]
    order_id = order["order_id"]
    log_investigation(order_id, "IntegrationDiagnosticAgent", "Analyzing integration logs")

    error_logs = order["integration_error_logs"]

    if not error_logs:
        return {
            "has_issues": False,
            "failure_category": "None",
            "affected_systems": [],
            "critical_errors": [],
            "root_cause": "No integration issues detected. All systems operating normally.",
            "error_timeline": []
        }

    critical_errors = [l for l in error_logs if l["severity"] == "Critical"]
    warning_errors = [l for l in error_logs if l["severity"] == "Warning"]
    affected_systems = list(set(l["system"] for l in error_logs))

    failure_category = _categorize_failure(error_logs, order)
    root_cause = _analyze_root_cause(failure_category, error_logs, order)

    result = {
        "has_issues": True,
        "failure_category": failure_category,
        "affected_systems": affected_systems,
        "critical_errors": critical_errors,
        "warning_count": len(warning_errors),
        "total_errors": len(error_logs),
        "root_cause": root_cause,
        "error_timeline": error_logs
    }

    log_investigation(order_id, "IntegrationDiagnosticAgent",
                      f"Diagnosis complete – category: {failure_category}")
    return result


def _categorize_failure(error_logs, order):
    systems_affected = set(l["system"] for l in error_logs if l["severity"] == "Critical")
    error_codes = [l["error_code"] for l in error_logs]

    if "Payment Gateway" in systems_affected and "ERP" in systems_affected:
        return "Payment + ERP Combined Failure"
    if "Payment Gateway" in systems_affected:
        if any("timeout" in l["message"].lower() for l in error_logs):
            return "Payment Gateway Timeout"
        if any("fraud" in l["message"].lower() for l in error_logs):
            return "Fraud Detection Block"
        return "Payment Authorization Failure"
    if "ERP" in systems_affected:
        if any("timeout" in l["message"].lower() or "unavailable" in l["message"].lower()
               for l in error_logs):
            return "ERP Service Outage"
        return "ERP Submission Error"
    if "Logistics" in systems_affected or any("LOG" in c for c in error_codes):
        if any("congestion" in l["message"].lower() for l in error_logs):
            return "Logistics Hub Congestion"
        return "Logistics/Carrier Delay"
    if "Fulfillment" in systems_affected:
        if any("partial" in l["message"].lower() or "stock" in l["message"].lower()
               for l in error_logs):
            return "Inventory/Stock Issue"
        return "Fulfillment Processing Error"

    return "General Integration Error"


def _analyze_root_cause(category, error_logs, order):
    root_causes = {
        "Payment Authorization Failure": (
            f"Payment authorization was declined for order {order['order_id']}. "
            f"The payment gateway returned decline responses across {len([l for l in error_logs if l['severity'] == 'Critical'])} attempts. "
            f"This has blocked downstream ERP processing and fulfillment. "
            f"Root cause: Customer payment method lacks sufficient funds or has restrictions."
        ),
        "Payment Gateway Timeout": (
            f"The payment gateway experienced API timeouts for order {order['order_id']}. "
            f"Multiple retry attempts failed with timeout errors. "
            f"Root cause: Payment gateway service degradation or network connectivity issues "
            f"between the OMS and payment processor."
        ),
        "Fraud Detection Block": (
            f"Order {order['order_id']} was flagged by the fraud detection system. "
            f"Payment was declined and the order was subsequently rejected by ERP. "
            f"Root cause: Transaction characteristics triggered fraud risk rules. "
            f"Manual review and customer verification required."
        ),
        "Payment + ERP Combined Failure": (
            f"Order {order['order_id']} experienced cascading failures across payment and ERP systems. "
            f"Initial payment failure triggered ERP rejection, resulting in order cancellation. "
            f"Root cause: Payment validation failure propagated through the order pipeline."
        ),
        "ERP Service Outage": (
            f"ERP system was unavailable when processing order {order['order_id']}. "
            f"Multiple submission attempts resulted in timeout/unavailability errors. "
            f"Root cause: ERP service outage or infrastructure issue preventing order confirmation."
        ),
        "ERP Submission Error": (
            f"Order {order['order_id']} failed during ERP submission phase. "
            f"The ERP system rejected or could not process the order data. "
            f"Root cause: Data validation error or system configuration issue in ERP."
        ),
        "Logistics/Carrier Delay": (
            f"Shipment for order {order['order_id']} is experiencing carrier-side delays. "
            f"The logistics provider has rescheduled pickup due to operational constraints. "
            f"Root cause: Warehouse congestion or carrier capacity limitations affecting pickup scheduling."
        ),
        "Logistics Hub Congestion": (
            f"Order {order['order_id']} shipment is delayed due to regional hub congestion. "
            f"The logistics network is experiencing high volume at the distribution hub. "
            f"Root cause: Regional logistics hub at capacity, requiring alternative routing."
        ),
        "Inventory/Stock Issue": (
            f"Order {order['order_id']} cannot be fully fulfilled due to inventory discrepancies. "
            f"Stock levels in the warehouse management system do not match ERP records. "
            f"Root cause: Inventory sync mismatch between ERP and WMS, causing partial fulfillment."
        ),
        "Fulfillment Processing Error": (
            f"Fulfillment processing encountered errors for order {order['order_id']}. "
            f"The warehouse management system reported issues during order picking/packing. "
            f"Root cause: Fulfillment system processing error requiring manual intervention."
        )
    }
    return root_causes.get(category,
                          f"Integration issues detected for order {order['order_id']}. "
                          f"Multiple system errors found across {len(set(l['system'] for l in error_logs))} systems. "
                          f"Further investigation recommended.")
