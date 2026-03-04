import streamlit as st
import plotly.graph_objects as go
from data.mock_orders import get_all_orders
from agents.sla_monitor import check_sla
from agents.order_investigation import investigate_order
from agents.integration_diagnostic import diagnose_integrations

NAVY = "#041e42"
NAVY_LIGHT = "#0a2a5c"
BLUE_ACCENT = "#1a6fc4"
TEAL = "#0097a7"
GREEN = "#2e8b57"
AMBER = "#d4a017"
RED = "#c0392b"
GRAY_BG = "#f8f9fc"
CHART_FONT = dict(family="Inter, sans-serif", color="#334155")


def render():
    st.markdown("## Support Operations Dashboard")
    st.caption("Real-time operational metrics and trend analysis across the Electrolux order ecosystem")

    orders = get_all_orders()
    metrics = _compute_metrics(orders)

    _render_kpi_cards(metrics)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        _render_sla_distribution(metrics)
    with col2:
        _render_failure_categories(metrics)

    st.divider()

    col3, col4 = st.columns(2)
    with col3:
        _render_region_breakdown(metrics)
    with col4:
        _render_resolution_times(metrics)

    st.divider()
    _render_order_status_table(metrics)


def _compute_metrics(orders):
    order_metrics = []

    for order in orders:
        inv = investigate_order(order["order_id"])
        sla = check_sla(inv)
        diag = diagnose_integrations(inv)

        order_metrics.append({
            "order_id": order["order_id"],
            "customer": order["customer_name"],
            "region": order["region"],
            "priority": order["priority"],
            "order_value": order["order_value"],
            "sla_status": sla["sla_status"],
            "sla_ratio": sla["ratio"],
            "processing_time": order["processing_time"],
            "sla_threshold": order["sla_threshold"],
            "failure_category": diag["failure_category"],
            "has_issues": diag["has_issues"],
            "lifecycle_stage": inv["lifecycle_stage"],
            "payment_status": order["payment_status"],
            "erp_status": order["erp_status"],
            "fulfillment_status": order["fulfillment_status"],
            "shipment_status": order["shipment_status"],
            "critical_errors": len(diag.get("critical_errors", []))
        })

    total = len(order_metrics)
    with_issues = [o for o in order_metrics if o["has_issues"]]
    at_risk = [o for o in order_metrics if o["sla_status"] == "At Risk"]
    breached = [o for o in order_metrics if o["sla_status"] == "Breached"]
    avg_resolution = sum(o["processing_time"] for o in order_metrics) / total if total else 0

    failure_counts = {}
    for o in order_metrics:
        cat = o["failure_category"]
        if cat != "None":
            failure_counts[cat] = failure_counts.get(cat, 0) + 1

    most_common = max(failure_counts, key=failure_counts.get) if failure_counts else "None"

    return {
        "orders": order_metrics,
        "total": total,
        "with_issues": len(with_issues),
        "at_risk": len(at_risk),
        "breached": len(breached),
        "healthy": total - len(with_issues),
        "avg_resolution": round(avg_resolution, 1),
        "failure_counts": failure_counts,
        "most_common_failure": most_common
    }


def _render_kpi_cards(metrics):
    cols = st.columns(5)
    with cols[0]:
        st.metric("Total Orders", metrics["total"])
    with cols[1]:
        st.metric("With Issues", metrics["with_issues"], delta=f"-{metrics['healthy']} healthy", delta_color="inverse")
    with cols[2]:
        st.metric("At Risk", metrics["at_risk"])
    with cols[3]:
        st.metric("SLA Breached", metrics["breached"])
    with cols[4]:
        st.metric("Avg Processing", f"{metrics['avg_resolution']}h")


def _render_sla_distribution(metrics):
    st.markdown("#### SLA Status Distribution")
    sla_counts = {"On Track": 0, "At Risk": 0, "Breached": 0}
    for o in metrics["orders"]:
        sla_counts[o["sla_status"]] = sla_counts.get(o["sla_status"], 0) + 1

    fig = go.Figure(data=[go.Pie(
        labels=list(sla_counts.keys()),
        values=list(sla_counts.values()),
        marker=dict(colors=[GREEN, AMBER, RED]),
        hole=0.45,
        textinfo="label+value",
        textfont=dict(size=13, color="#334155"),
        pull=[0, 0.02, 0.04]
    )])
    fig.update_layout(
        height=350,
        margin=dict(t=30, b=30, l=20, r=20),
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, font=CHART_FONT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=CHART_FONT
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_failure_categories(metrics):
    st.markdown("#### Failure Categories")
    fc = metrics["failure_counts"]
    if not fc:
        st.info("No failures detected across all orders.")
        return

    categories = list(fc.keys())
    counts = list(fc.values())

    fig = go.Figure(data=[go.Bar(
        x=counts,
        y=categories,
        orientation="h",
        marker_color=BLUE_ACCENT,
        marker_line=dict(width=0),
        text=counts,
        textposition="outside",
        textfont=dict(color="#334155", size=12)
    )])
    fig.update_layout(
        height=350,
        margin=dict(t=30, b=30, l=20, r=120),
        xaxis_title="Count",
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=CHART_FONT,
        xaxis=dict(gridcolor="#e2e8f0"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_region_breakdown(metrics):
    st.markdown("#### Orders by Region")
    region_data = {}
    for o in metrics["orders"]:
        region = o["region"]
        if region not in region_data:
            region_data[region] = {"total": 0, "issues": 0}
        region_data[region]["total"] += 1
        if o["has_issues"]:
            region_data[region]["issues"] += 1

    regions = list(region_data.keys())
    issues = [region_data[r]["issues"] for r in regions]
    healthy = [region_data[r]["total"] - region_data[r]["issues"] for r in regions]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Healthy", x=regions, y=healthy, marker_color=TEAL))
    fig.add_trace(go.Bar(name="Issues", x=regions, y=issues, marker_color=RED))
    fig.update_layout(
        barmode="stack",
        height=350,
        margin=dict(t=30, b=30, l=20, r=20),
        legend=dict(orientation="h", y=-0.18, font=CHART_FONT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=CHART_FONT,
        yaxis=dict(gridcolor="#e2e8f0")
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_resolution_times(metrics):
    st.markdown("#### Processing Time vs SLA Threshold")
    order_ids = [o["order_id"] for o in metrics["orders"]]
    processing = [o["processing_time"] for o in metrics["orders"]]
    thresholds = [o["sla_threshold"] for o in metrics["orders"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Processing Time",
        x=order_ids,
        y=processing,
        marker_color=[RED if p > t else AMBER if p > t * 0.75 else GREEN
                       for p, t in zip(processing, thresholds)],
        marker_line=dict(width=0)
    ))
    fig.add_trace(go.Scatter(
        name="SLA Threshold",
        x=order_ids,
        y=thresholds,
        mode="lines+markers",
        line=dict(color=NAVY, dash="dash", width=2),
        marker=dict(size=8, color=NAVY)
    ))
    fig.update_layout(
        height=350,
        margin=dict(t=30, b=30, l=20, r=20),
        yaxis_title="Hours",
        legend=dict(orientation="h", y=-0.18, font=CHART_FONT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=CHART_FONT,
        yaxis=dict(gridcolor="#e2e8f0")
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_order_status_table(metrics):
    st.markdown("#### All Orders Overview")

    table_data = []
    for o in metrics["orders"]:
        sla_emoji = {"On Track": "🟢", "At Risk": "🟡", "Breached": "🔴"}.get(o["sla_status"], "⚪")
        table_data.append({
            "Order ID": o["order_id"],
            "Customer": o["customer"],
            "Region": o["region"],
            "Priority": o["priority"],
            "SLA": f"{sla_emoji} {o['sla_status']}",
            "Stage": o["lifecycle_stage"],
            "Issue": o["failure_category"] if o["has_issues"] else "None",
            "Value": f"${o['order_value']:,.0f}"
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True)
