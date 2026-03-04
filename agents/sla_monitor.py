from utils.logger import log_investigation


def check_sla(investigation_result):
    if not investigation_result:
        return None

    order = investigation_result["order"]
    order_id = order["order_id"]
    log_investigation(order_id, "SLAMonitorAgent", "Checking SLA compliance")

    threshold = order["sla_threshold"]
    processing = order["processing_time"]
    ratio = processing / threshold if threshold > 0 else 1.0

    if ratio >= 1.0:
        sla_status = "Breached"
        breach_hours = round(processing - threshold, 1)
        message = f"SLA breached by {breach_hours} hours ({processing}h vs {threshold}h threshold)"
    elif ratio >= 0.75:
        sla_status = "At Risk"
        remaining = round(threshold - processing, 1)
        message = f"SLA at risk – only {remaining} hours remaining ({int(ratio * 100)}% consumed)"
    else:
        sla_status = "On Track"
        remaining = round(threshold - processing, 1)
        message = f"SLA on track – {remaining} hours remaining ({int(ratio * 100)}% consumed)"

    result = {
        "sla_status": sla_status,
        "sla_threshold": threshold,
        "processing_time": processing,
        "ratio": round(ratio, 2),
        "message": message
    }

    log_investigation(order_id, "SLAMonitorAgent", f"SLA status: {sla_status}")
    return result
