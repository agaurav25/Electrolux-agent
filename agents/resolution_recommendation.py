import random
from datetime import datetime
from utils.logger import log_investigation, log_resolution


def recommend_resolution(investigation_result, sla_result, diagnostic_result):
    if not investigation_result:
        return None

    order = investigation_result["order"]
    order_id = order["order_id"]
    log_investigation(order_id, "ResolutionAgent", "Generating resolution recommendations")

    recommendations = []
    auto_actions = []

    if not diagnostic_result or not diagnostic_result["has_issues"]:
        return {
            "recommendations": [
                {
                    "action": "Monitor",
                    "description": "No issues detected. Continue monitoring order progression.",
                    "priority": "Low",
                    "auto_resolve": False
                }
            ],
            "auto_actions": [],
            "escalation_required": False,
            "estimated_resolution": "No action needed"
        }

    category = diagnostic_result["failure_category"]
    sla_status = sla_result["sla_status"] if sla_result else "Unknown"

    if "Payment" in category and "Timeout" in category:
        recommendations.append({
            "action": "Retry Payment Validation",
            "description": "Re-trigger payment authorization through the payment gateway. The timeout may be transient.",
            "priority": "High",
            "auto_resolve": True
        })
        auto_actions.append("retry_payment")
        recommendations.append({
            "action": "Check Gateway Status",
            "description": "Verify payment gateway service health dashboard for ongoing incidents.",
            "priority": "Medium",
            "auto_resolve": False
        })

    elif "Payment Authorization" in category:
        recommendations.append({
            "action": "Contact Customer for Payment Update",
            "description": "Reach out to customer to update payment method or resolve funding issue.",
            "priority": "High",
            "auto_resolve": False
        })
        recommendations.append({
            "action": "Re-trigger Payment Validation",
            "description": "After customer updates payment, re-initiate payment authorization.",
            "priority": "High",
            "auto_resolve": True
        })
        auto_actions.append("retry_payment")

    elif "Fraud" in category:
        recommendations.append({
            "action": "Escalate to L2 – Fraud Review",
            "description": "Order requires manual fraud review by the L2 risk team.",
            "priority": "Critical",
            "auto_resolve": False
        })
        recommendations.append({
            "action": "Raise ServiceNow Ticket",
            "description": "Create incident ticket for fraud review team with order details.",
            "priority": "High",
            "auto_resolve": True
        })
        auto_actions.append("create_ticket")

    elif "ERP" in category:
        recommendations.append({
            "action": "Retry ERP Submission",
            "description": "Re-submit the order to the ERP system. Service may have recovered.",
            "priority": "High",
            "auto_resolve": True
        })
        auto_actions.append("retry_erp")
        recommendations.append({
            "action": "Verify ERP System Health",
            "description": "Check ERP service status and confirm system availability before retry.",
            "priority": "High",
            "auto_resolve": False
        })
        if sla_status == "Breached":
            recommendations.append({
                "action": "Escalate to L2 – ERP Team",
                "description": "SLA breached. Escalate to L2 ERP support for priority handling.",
                "priority": "Critical",
                "auto_resolve": False
            })

    elif "Logistics" in category or "Carrier" in category:
        recommendations.append({
            "action": "Contact Carrier for Update",
            "description": "Request updated pickup/delivery timeline from logistics provider.",
            "priority": "Medium",
            "auto_resolve": False
        })
        recommendations.append({
            "action": "Evaluate Alternative Routing",
            "description": "Check availability of alternative carriers or shipping routes.",
            "priority": "Medium",
            "auto_resolve": True
        })
        auto_actions.append("reroute_shipment")

    elif "Inventory" in category or "Stock" in category:
        recommendations.append({
            "action": "Trigger Inventory Sync",
            "description": "Force synchronization between ERP and WMS inventory records.",
            "priority": "High",
            "auto_resolve": True
        })
        auto_actions.append("sync_inventory")
        recommendations.append({
            "action": "Evaluate Partial Shipment",
            "description": "Ship available items immediately and backorder remaining items.",
            "priority": "Medium",
            "auto_resolve": False
        })

    elif "Combined" in category:
        recommendations.append({
            "action": "Escalate to L2 – Multi-System Failure",
            "description": "Cascading failure across payment and ERP. Requires L2 intervention.",
            "priority": "Critical",
            "auto_resolve": False
        })
        recommendations.append({
            "action": "Raise ServiceNow Ticket",
            "description": "Create P1 incident ticket for combined payment/ERP failure.",
            "priority": "Critical",
            "auto_resolve": True
        })
        auto_actions.append("create_ticket")

    else:
        recommendations.append({
            "action": "Investigate Further",
            "description": "Review system logs in detail and identify specific failure point.",
            "priority": "Medium",
            "auto_resolve": False
        })

    if sla_status == "Breached" and not any(r["action"].startswith("Escalate") for r in recommendations):
        recommendations.append({
            "action": "Escalate to L2 – SLA Breach",
            "description": "SLA has been breached. Escalate for priority resolution.",
            "priority": "Critical",
            "auto_resolve": False
        })

    escalation_required = any(r["action"].startswith("Escalate") for r in recommendations)
    est_resolution = _estimate_resolution_time(category, sla_status)

    result = {
        "recommendations": recommendations,
        "auto_actions": auto_actions,
        "escalation_required": escalation_required,
        "estimated_resolution": est_resolution
    }

    log_investigation(order_id, "ResolutionAgent",
                      f"Generated {len(recommendations)} recommendations, escalation: {escalation_required}")
    return result


def simulate_auto_resolve(order_id, auto_actions):
    log_resolution(order_id, "AutoResolve", f"Initiating auto-resolution: {auto_actions}")
    results = []

    for action in auto_actions:
        if action == "retry_payment":
            success = random.random() > 0.3
            results.append({
                "action": "Retry Payment Validation",
                "status": "Success" if success else "Failed – Retry Required",
                "details": "Payment re-authorized successfully." if success else "Payment gateway still declining. Manual intervention needed.",
                "timestamp": datetime.now().isoformat()
            })
        elif action == "retry_erp":
            success = random.random() > 0.2
            results.append({
                "action": "Retry ERP Submission",
                "status": "Success" if success else "Failed – Service Still Unavailable",
                "details": "ERP submission accepted. Order confirmed." if success else "ERP service still experiencing issues.",
                "timestamp": datetime.now().isoformat()
            })
        elif action == "create_ticket":
            ticket_id = f"INC{random.randint(100000, 999999)}"
            results.append({
                "action": "Create ServiceNow Ticket",
                "status": "Success",
                "details": f"ServiceNow ticket {ticket_id} created and assigned to L2 team.",
                "timestamp": datetime.now().isoformat()
            })
        elif action == "reroute_shipment":
            success = random.random() > 0.2
            results.append({
                "action": "Reroute Shipment",
                "status": "Success" if success else "Pending – Awaiting Carrier Confirmation",
                "details": "Shipment rerouted via secondary hub. New ETA: +4 hours." if success else "Rerouting request submitted. Awaiting carrier confirmation.",
                "timestamp": datetime.now().isoformat()
            })
        elif action == "sync_inventory":
            results.append({
                "action": "Inventory Sync",
                "status": "Success",
                "details": "ERP-WMS inventory sync completed. Stock levels reconciled.",
                "timestamp": datetime.now().isoformat()
            })

    log_resolution(order_id, "AutoResolve",
                   f"Completed {len(results)} actions – "
                   f"{sum(1 for r in results if r['status'] == 'Success')} successful")
    return results


def _estimate_resolution_time(category, sla_status):
    estimates = {
        "Payment Authorization Failure": "2-4 hours (pending customer action)",
        "Payment Gateway Timeout": "30 minutes - 1 hour (pending gateway recovery)",
        "Fraud Detection Block": "4-8 hours (requires L2 fraud review)",
        "Payment + ERP Combined Failure": "4-6 hours (requires L2 multi-system investigation)",
        "ERP Service Outage": "1-2 hours (pending service recovery)",
        "ERP Submission Error": "1-3 hours (pending data correction)",
        "Logistics/Carrier Delay": "4-8 hours (dependent on carrier)",
        "Logistics Hub Congestion": "6-12 hours (dependent on hub capacity)",
        "Inventory/Stock Issue": "2-4 hours (pending inventory sync)",
        "Fulfillment Processing Error": "1-3 hours (pending manual review)"
    }
    return estimates.get(category, "2-4 hours (under investigation)")
