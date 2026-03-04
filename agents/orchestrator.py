from agents.order_investigation import investigate_order
from agents.sla_monitor import check_sla
from agents.integration_diagnostic import diagnose_integrations
from agents.resolution_recommendation import recommend_resolution, simulate_auto_resolve
from agents.customer_communication import generate_customer_response
from utils.logger import log_investigation


def run_full_investigation(order_id):
    log_investigation(order_id, "Orchestrator", "Starting multi-agent investigation pipeline")

    investigation = investigate_order(order_id)
    if not investigation:
        return {"error": f"Order '{order_id}' not found in the system."}

    sla = check_sla(investigation)
    diagnostics = diagnose_integrations(investigation)
    resolution = recommend_resolution(investigation, sla, diagnostics)
    customer_response = generate_customer_response(investigation, sla, diagnostics, resolution)

    agent_trace = [
        {"agent": "Order Investigation Agent", "status": "Complete", "action": "Retrieved order data from Commerce, ERP, Payment, and Logistics systems"},
        {"agent": "SLA Monitoring Agent", "status": "Complete", "action": f"SLA assessment: {sla['sla_status']}"},
        {"agent": "Integration Diagnostic Agent", "status": "Complete", "action": f"Failure category: {diagnostics['failure_category']}"},
        {"agent": "Resolution Recommendation Agent", "status": "Complete", "action": f"Generated {len(resolution['recommendations'])} recommendations"},
        {"agent": "Customer Communication Agent", "status": "Complete", "action": "Customer response generated"}
    ]

    log_investigation(order_id, "Orchestrator", "Multi-agent pipeline complete")

    return {
        "investigation": investigation,
        "sla": sla,
        "diagnostics": diagnostics,
        "resolution": resolution,
        "customer_response": customer_response,
        "agent_trace": agent_trace
    }


def run_auto_resolve(order_id, auto_actions):
    log_investigation(order_id, "Orchestrator", f"Initiating auto-resolve with actions: {auto_actions}")
    results = simulate_auto_resolve(order_id, auto_actions)
    log_investigation(order_id, "Orchestrator", "Auto-resolve complete")
    return results
