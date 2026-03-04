import os
import streamlit as st

st.set_page_config(
    page_title="Electrolux | AI Order Resolution Copilot",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

ELECTROLUX_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f8f9fc 0%, #eef1f8 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #041e42 0%, #0a2a5c 100%);
    }

    [data-testid="stSidebar"] * {
        color: #e8edf5 !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #b8c7de !important;
    }

    [data-testid="stSidebar"] .stRadio label span {
        color: #ffffff !important;
        font-weight: 500;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
    }

    [data-testid="stSidebar"] .stExpander {
        border-color: rgba(255,255,255,0.15) !important;
    }

    [data-testid="stSidebar"] .stExpander [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] .stExpander summary span {
        color: #c8d6e8 !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #041e42 !important;
        border: none !important;
        color: white !important;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #0a2a5c !important;
    }

    .stButton > button[kind="secondary"] {
        border: 2px solid #041e42 !important;
        color: #041e42 !important;
        font-weight: 600;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #041e42 !important;
        color: white !important;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(4,30,66,0.06);
    }

    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #041e42 !important;
        font-weight: 700;
    }

    h1 {
        color: #041e42 !important;
        font-weight: 700 !important;
    }

    h2, h3 {
        color: #0a2a5c !important;
        font-weight: 600 !important;
    }

    .stProgress > div > div {
        background-color: #041e42 !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        background: white !important;
    }

    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }

    [data-testid="stStatusWidget"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        background: white;
    }

    div[data-testid="stTextArea"] textarea {
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
    }

    .electrolux-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 4px 0 8px 0;
    }
    .electrolux-logo-text {
        font-size: 1.35rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
    }
    .electrolux-subtitle {
        font-size: 0.75rem;
        color: #8da4c4;
        letter-spacing: 0.8px;
        margin-top: 2px;
    }
    .electrolux-badge {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.65rem;
        color: #8da4c4;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
</style>
"""

st.markdown(ELECTROLUX_CSS, unsafe_allow_html=True)

from pages import investigation, dashboard, customer_response

st.sidebar.markdown(
    '<div class="electrolux-header">'
    '<div>'
    '<div class="electrolux-logo-text">Electrolux</div>'
    '<div class="electrolux-subtitle">Order Resolution Copilot</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    options=[
        "Order Investigation",
        "Operations Dashboard",
        "Customer Response"
    ],
    index=0
)

st.sidebar.divider()

with st.sidebar.expander("LLM Configuration", expanded=not bool(os.environ.get("GROQ_API_KEY"))):
    current_key = os.environ.get("GROQ_API_KEY", "")
    has_key = bool(current_key)
    if has_key:
        st.success("Groq API key is configured")
    else:
        st.warning("No API key — using simulated AI")

    new_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        key="groq_key_input"
    )
    if st.button("Save API Key", use_container_width=True):
        if new_key.strip():
            os.environ["GROQ_API_KEY"] = new_key.strip()
            st.success("Saved for this session")
            st.rerun()
        else:
            st.error("Please enter a valid API key")

st.sidebar.divider()
st.sidebar.markdown("**How It Works**")
st.sidebar.markdown(
    "This copilot orchestrates 5 specialized AI agents "
    "to investigate order issues across Commerce, ERP, "
    "Payment, and Logistics systems — delivering instant "
    "root cause analysis and resolution recommendations."
)
st.sidebar.divider()
st.sidebar.markdown(
    '<div class="electrolux-badge">Agentic AI &bull; Proof of Concept</div>',
    unsafe_allow_html=True
)

if page == "Order Investigation":
    investigation.render()
elif page == "Operations Dashboard":
    dashboard.render()
elif page == "Customer Response":
    customer_response.render()
