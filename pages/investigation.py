import streamlit as st
import streamlit.components.v1 as components
import time
from data.mock_orders import get_order_ids
from agents.orchestrator import run_full_investigation, run_auto_resolve

BRAND_NAVY = "#041e42"

HEALTH_COLORS = {
    "Healthy": {"bg": "#e8f5e9", "border": "#2e8b57", "icon": "#2e8b57", "glow": "rgba(46,139,87,0.15)", "label": "Healthy"},
    "Degraded": {"bg": "#fff8e1", "border": "#d4a017", "icon": "#d4a017", "glow": "rgba(212,160,23,0.15)", "label": "Degraded"},
    "Critical": {"bg": "#fce4ec", "border": "#c0392b", "icon": "#c0392b", "glow": "rgba(192,57,43,0.2)", "label": "Critical"}
}

SYSTEM_ICONS = {
    "Commerce/OMS": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="32" height="32"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    "Payment Gateway": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="32" height="32"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>',
    "ERP System": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="32" height="32"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4.03 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/></svg>',
    "Fulfillment/WMS": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="32" height="32"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
    "Logistics": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="32" height="32"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>'
}

PIPELINE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .health-pipeline {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        padding: 20px 8px;
        overflow-x: auto;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .sys-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 128px;
        max-width: 148px;
        padding: 16px 10px 14px;
        border-radius: 14px;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .sys-node:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(4,30,66,0.12) !important;
    }
    .sys-icon { margin-bottom: 8px; }
    .sys-name {
        font-size: 11.5px;
        font-weight: 700;
        color: #041e42;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .sys-badge {
        font-size: 9.5px;
        font-weight: 600;
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .sys-detail {
        font-size: 10px;
        color: #64748b;
        line-height: 1.3;
    }
    .arrow-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        min-width: 44px;
        position: relative;
    }
    .break-x {
        position: absolute;
        top: -2px;
        font-size: 14px;
        color: #c0392b;
        font-weight: 800;
    }
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 4px 16px rgba(192,57,43,0.2); }
        50% { box-shadow: 0 4px 24px rgba(192,57,43,0.45); }
    }
    @keyframes pulse-amber {
        0%, 100% { box-shadow: 0 4px 16px rgba(212,160,23,0.15); }
        50% { box-shadow: 0 4px 20px rgba(212,160,23,0.35); }
    }
    .pulse-critical { animation: pulse-red 2s ease-in-out infinite; }
    .pulse-warning { animation: pulse-amber 2.5s ease-in-out infinite; }
</style>
"""


def _build_node_html(sys_name, sys_info):
    health = sys_info["health"]
    colors = HEALTH_COLORS.get(health, HEALTH_COLORS["Healthy"])
    status_text = sys_info["status"]
    if len(status_text) > 24:
        status_text = status_text[:22] + "..."
    icon_svg = SYSTEM_ICONS.get(sys_name, SYSTEM_ICONS["Commerce/OMS"]).replace("{color}", colors["icon"])
    pulse = "pulse-critical" if health == "Critical" else ("pulse-warning" if health == "Degraded" else "")
    return (
        f'<div class="sys-node {pulse}" style="background:{colors["bg"]};'
        f'border:2px solid {colors["border"]};box-shadow:0 4px 16px {colors["glow"]};">'
        f'<div class="sys-icon">{icon_svg}</div>'
        f'<div class="sys-name">{sys_name}</div>'
        f'<div class="sys-badge" style="background:{colors["border"]};">{colors["label"]}</div>'
        f'<div class="sys-detail">{status_text}</div>'
        f'</div>'
    )


def _build_arrow_html(idx, from_health, to_health):
    is_broken = from_health == "Critical"
    color = "#c0392b" if from_health == "Critical" or to_health == "Critical" else (
        "#d4a017" if from_health == "Degraded" or to_health == "Degraded" else "#2e8b57")
    dash = ' stroke-dasharray="6,4"' if is_broken else ""
    x_mark = '<span class="break-x">&#10005;</span>' if is_broken else ""
    return (
        f'<div class="arrow-wrap">'
        f'<svg width="44" height="24" viewBox="0 0 44 24">'
        f'<defs><marker id="ah{idx}" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">'
        f'<polygon points="0 0, 8 3, 0 6" fill="{color}"/></marker></defs>'
        f'<line x1="0" y1="12" x2="32" y2="12" stroke="{color}" stroke-width="2.5"{dash} marker-end="url(#ah{idx})"/>'
        f'</svg>{x_mark}</div>'
    )


def _render_integration_health_visual(systems):
    sys_list = list(systems.items())
    body = ""
    for i, (name, info) in enumerate(sys_list):
        body += _build_node_html(name, info)
        if i < len(sys_list) - 1:
            next_health = sys_list[i + 1][1]["health"]
            body += _build_arrow_html(i, info["health"], next_health)

    html = PIPELINE_CSS + '<div class="health-pipeline">' + body + '</div>'
    components.html(html, height=210, scrolling=False)


def render():
    st.markdown("## Order Investigation Console")
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
    _render_integration_health_visual(investigation["systems"])

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
