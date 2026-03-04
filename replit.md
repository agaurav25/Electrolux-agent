# Electrolux | AI Order Resolution Copilot (POC)

## Overview
A Streamlit-based demo application simulating an Agentic AI-powered L1 Support Assistant for tracking and resolving order issues in the Electrolux order management ecosystem. Branded with Electrolux's navy blue color scheme and professional enterprise styling.

## Architecture
- **app.py** – Main Streamlit entry point with sidebar navigation and Electrolux CSS theming
- **assets/favicon.ico** – Electrolux-branded favicon
- **data/mock_orders.py** – 10 mock orders with various failure scenarios
- **agents/** – Multi-agent simulation modules:
  - `order_investigation.py` – Fetches and analyzes order data across systems
  - `sla_monitor.py` – SLA compliance checking
  - `integration_diagnostic.py` – System log analysis and root cause identification
  - `resolution_recommendation.py` – Action recommendations and auto-resolve simulation
  - `customer_communication.py` – Customer-facing response generation (Groq LLM or simulated), signs off as Electrolux Order Support Team
  - `orchestrator.py` – Multi-agent pipeline coordinator
- **pages/** – UI pages:
  - `investigation.py` – L1 Order Investigation Console
  - `dashboard.py` – Operations Dashboard with Plotly charts (Electrolux color palette)
  - `customer_response.py` – Customer Response Generator with copy-to-clipboard
- **utils/logger.py** – Logging module for L1 interaction tracking

## Branding
- Primary navy: #041e42
- Secondary navy: #0a2a5c
- Accent blue: #1a6fc4
- Teal: #0097a7
- Custom CSS for sidebar, buttons, metrics, headings, charts

## Tech Stack
- Python 3.11, Streamlit, Plotly, Groq (optional)

## Running
```bash
streamlit run app.py --server.port 5000
```

## Environment Variables
- `GROQ_API_KEY` (optional) – Enables real LLM-powered customer responses. Can be set via sidebar UI. Falls back to simulated templates if not set.
