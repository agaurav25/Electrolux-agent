import streamlit as st
import time
from data.mock_orders import get_order_ids
from agents.orchestrator import run_full_investigation, run_auto_resolve

BRAND_NAVY = "#041e42"


def render():
    st.markdown(f"## Order Investigation Console")
    st.caption("Agentic AI-powered multi-system investigation for rapid order issue diagnosis")

    col1, col2 = st.columns([2, 1])
    with col1:
        order_id = st.selectbox(
            "Select Order ID",
            options=[""] + get_order_ids(),
            format_func=lambda x: "-- Select an Order ID --" if x == "" else x
        )
    with col2:
        st.write("")
        st.write("")
        investigate = st.button("Investigate Issue", type="primary", disabled=not order_id, use_container_width=True)

    if investigate and order_id:
        _run_investigation(order_id)

    if "investigation_result" in st.session_state and st.session_state.investigation_result:
        _display_results(st.session_state.investigation_result)


def _run_investigation(order_id):
    with st.status("Running multi-agent investigation...", expanded=True) as status:
        st.write("Agent 1: Order Investigation Agent — Querying Commerce, ERP, Payment, Logistics...")
        time.sleep(0.5)

        st.write("Agent 2: SLA Monitoring Agent — Evaluating SLA compliance thresholds...")
        time.sleep(0.3)

        st.write("Agent 3: Integration Diagnostic Agent — Analyzing system integration logs...")
        time.sleep(0.4)

        st.write("Agent 4: Resolution Recommendation Agent — Computing optimal resolution path...")
        time.sleep(0.3)

        st.write("Agent 5: Customer Communication Agent — Drafting customer-ready response...")
        time.sleep(0.3)

        result = run_full_investigation(order_id)

        if "error" in result:
            status.update(label="Investigation failed", state="error")
            st.error(result["error"])
            return

        status.update(label="Investigation complete — All 5 agents finished", state="complete")

    st.session_state.investigation_result = result


def _display_results(result):
    investigation = result["investigation"]
    sla = result["sla"]
    diagnostics = result["diagnostics"]
    resolution = result["resolution"]
    order = investigation["order"]

    st.divider()

    st.markdown(f"### {order['order_id']} — {order['customer_name']}")
    info_cols = st.columns(4)
    with info_cols[0]:
        st.metric("Region", order["region"])
    with info_cols[1]:
        st.metric("Order Value", f"${order['order_value']:,.2f}")
    with info_cols[2]:
        st.metric("Priority", order["priority"])
    with info_cols[3]:
        st.metric("Processing Time", f"{order['processing_time']}h")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Order Lifecycle")
        stages = ["Order Created", "Payment", "ERP Submission", "Processing", "Fulfillment", "Shipment"]
        current = investigation["lifecycle_stage"]
        current_idx = stages.index(current) if current in stages else 0

        for i, stage in enumerate(stages):
            if i < current_idx:
                st.markdown(f"~~:green[{stage}]~~")
            elif i == current_idx:
                st.markdown(f"**:blue[{stage}]** :blue[<< Current Stage]")
            else:
                st.markdown(f":gray[{stage}]")

    with col_right:
        st.markdown("#### SLA Status")
        sla_color = {"On Track": "green", "At Risk": "orange", "Breached": "red"}.get(sla["sla_status"], "gray")
        st.markdown(f"### :{sla_color}[{sla['sla_status']}]")
        st.progress(min(sla["ratio"], 1.0))
        st.caption(sla["message"])

    st.divider()

    st.markdown("#### Integration Health Monitor")
    sys_cols = st.columns(5)
    systems = investigation["systems"]
    for i, (sys_name, sys_info) in enumerate(systems.items()):
        with sys_cols[i]:
            health = sys_info["health"]
            icon = {"Healthy": ":green_circle:", "Degraded": ":orange_circle:", "Critical": ":red_circle:"}.get(health, ":white_circle:")
            st.markdown(f"{icon} **{sys_name}**")
            st.caption(f"Status: {sys_info['status']}")

    st.divider()

    if diagnostics and diagnostics["has_issues"]:
        st.markdown("#### Root Cause Analysis")
        st.info(f"**Failure Category:** {diagnostics['failure_category']}")
        st.markdown(diagnostics["root_cause"])

        if diagnostics["error_timeline"]:
            with st.expander("View Error Timeline", expanded=False):
                for log in diagnostics["error_timeline"]:
                    severity_icon = {"Critical": ":red_circle:", "Warning": ":orange_circle:", "Info": ":blue_circle:"}.get(log["severity"], ":white_circle:")
                    st.markdown(f"{severity_icon} **[{log['system']}]** {log['error_code']} — {log['message']}")
                    st.caption(f"Timestamp: {log['timestamp']}")
    else:
        st.markdown("#### Root Cause Analysis")
        st.success("No integration issues detected. All systems operating normally.")

    st.divider()

    st.markdown("#### Recommended Actions")
    for rec in resolution["recommendations"]:
        priority_color = {"Critical": "red", "High": "orange", "Medium": "blue", "Low": "green"}.get(rec["priority"], "gray")
        auto_badge = " :robot_face:" if rec["auto_resolve"] else ""
        st.markdown(f":{priority_color}[**{rec['priority']}**] — **{rec['action']}**{auto_badge}")
        st.caption(rec["description"])

    if resolution.get("estimated_resolution"):
        st.info(f"**Estimated Resolution Time:** {resolution['estimated_resolution']}")

    if resolution.get("auto_actions"):
        st.divider()
        if st.button("Simulate Auto-Resolve", type="secondary", use_container_width=True):
            _run_auto_resolve(order["order_id"], resolution["auto_actions"])

    if "auto_resolve_results" in st.session_state and st.session_state.auto_resolve_results:
        st.divider()
        st.markdown("#### Auto-Resolution Results")
        for ar in st.session_state.auto_resolve_results:
            status_icon = ":white_check_mark:" if ar["status"] == "Success" else ":warning:"
            st.markdown(f"{status_icon} **{ar['action']}** — {ar['status']}")
            st.caption(ar["details"])

    st.divider()
    with st.expander("Agent Execution Trace", expanded=False):
        for trace in result.get("agent_trace", []):
            st.markdown(f":white_check_mark: **{trace['agent']}** — {trace['action']}")


def _run_auto_resolve(order_id, auto_actions):
    with st.spinner("Executing auto-resolution actions..."):
        time.sleep(1)
        results = run_auto_resolve(order_id, auto_actions)
        st.session_state.auto_resolve_results = results
        st.rerun()
