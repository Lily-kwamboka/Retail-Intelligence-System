"""
Msingi Retail System — Streamlit Dashboard
Connects to FastAPI backend at http://localhost:8000
Includes: Alerts, Recommendations, Scorecard, Data Quality, Floating Nuru Chat
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import jwt

# ── Configuration ────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Msingi Retail System",
    page_icon="📊",  # keep a simple icon but not emoji? Actually it's an emoji. We'll use a simple text icon.
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colors ───────────────────────────────────────────────────────────────────
PRIMARY = "#1A6B3C"      # Msingi green
SECONDARY = "#F4A62A"    # Amber accent
SUCCESS = "#2E7D32"
WARNING = "#ED6C02"
ERROR = "#D32F2F"
BG_LIGHT = "#F8F9FA"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1F2937"
TEXT_MUTED = "#6B7280"

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Global */
    .stApp {{
        background-color: {BG_LIGHT};
    }}
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT_DARK};
        font-weight: 600;
    }}
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {{
        background-color: {CARD_BG};
        border-right: 1px solid #E5E7EB;
    }}
    /* Metric Cards */
    [data-testid="stMetricValue"] {{
        color: {PRIMARY};
        font-weight: 700;
        font-size: 1.8rem;
    }}
    [data-testid="stMetricDelta"] {{
        color: {SECONDARY};
    }}
    /* Buttons */
    .stButton > button {{
        background-color: {PRIMARY};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background-color: #146b3a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .stButton > button:active {{
        transform: scale(0.98);
    }}
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        background-color: {CARD_BG};
        padding: 0.5rem 1rem 0 1rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 1rem;
        font-weight: 500;
        color: {TEXT_MUTED};
        padding: 0.5rem 0.25rem;
    }}
    .stTabs [aria-selected="true"] {{
        color: {PRIMARY};
        border-bottom-color: {PRIMARY};
        border-bottom-width: 2px;
    }}
    /* DataFrames */
    .dataframe {{
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    /* Alerts */
    .stAlert {{
        border-radius: 8px;
        border-left-width: 4px;
    }}
    /* Custom Card */
    .custom-card {{
        background-color: {CARD_BG};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }}
    /* Status Badge */
    .status-badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }}
    .status-ok {{
        background-color: #E8F5E9;
        color: {SUCCESS};
    }}
    .status-warning {{
        background-color: #FFF3E0;
        color: {WARNING};
    }}
    .status-error {{
        background-color: #FFEBEE;
        color: {ERROR};
    }}
</style>
""", unsafe_allow_html=True)

# ── Authentication Functions ─────────────────────────────────────────────────
def login_user(email: str, password: str):
    """Login and get access token"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data={"username": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            st.error(f"Login failed: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")
        return None

def is_token_expired(token):
    """Check if JWT token is expired"""
    if not token:
        return True
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        if exp:
            return exp < time.time()
        return True
    except:
        return True

def fetch_with_auth(endpoint: str, token: str):
    """Fetch data from API with authentication"""
    if not token:
        return None

    if is_token_expired(token):
        st.error("Your session has expired. Please login again.")
        st.session_state["logged_in"] = False
        st.session_state["token"] = None
        return None

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}{endpoint}", timeout=10, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state["logged_in"] = False
            st.session_state["token"] = None
            return None
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return None

# ── Nuru Chat API ─────────────────────────────────────────────────────────────
def ask_nuru(message: str, token: str, history: list):
    """Send message to Nuru API and return response"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE}/api/chat/analyst",
            json={"messages": history + [{"role": "user", "content": message}]},
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("reply", "Sorry, I couldn't process that.")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# ── Floating Nuru Chat Bubble ─────────────────────────────────────────────────
def floating_chat_bubble():
    """Floating Nuru chat — only visible after login. No chatbot on login page."""
    if not st.session_state.get("logged_in", False):
        return

    if "nuru_messages" not in st.session_state:
        st.session_state.nuru_messages = []
    if "nuru_chat_open" not in st.session_state:
        st.session_state.nuru_chat_open = False

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

    /* ── Chat window ── */
    .nuru-window {
        position: fixed;
        bottom: 92px;
        right: 26px;
        width: 332px;
        border-radius: 18px;
        background: #fff;
        box-shadow: 0 16px 48px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
        z-index: 9989;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #EDE8E3;
        font-family: 'DM Sans', sans-serif;
    }

    /* ── Header ── */
    .nuru-head {
        background: #1A6B3C;
        padding: 13px 15px;
        display: flex;
        align-items: center;
        gap: 11px;
    }
    .nuru-head-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: rgba(255,255,255,0.18);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    .nuru-head-name {
        font-size: 14px;
        font-weight: 600;
        color: #fff;
        line-height: 1.2;
    }
    .nuru-head-sub {
        font-size: 11px;
        color: rgba(255,255,255,0.72);
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 2px;
    }
    .nuru-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #7CFC00;
        flex-shrink: 0;
    }

    /* ── Messages ── */
    .nuru-msgs {
        padding: 14px 13px 8px;
        background: #F9F7F5;
        overflow-y: auto;
        max-height: 290px;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        gap: 9px;
    }
    .nuru-row      { display: flex; max-width: 86%; }
    .nuru-row.me   { align-self: flex-end;   justify-content: flex-end; }
    .nuru-row.bot  { align-self: flex-start; }
    .nuru-bub {
        padding: 9px 13px;
        border-radius: 14px;
        font-size: 13px;
        line-height: 1.55;
    }
    .nuru-row.me  .nuru-bub {
        background: #1A6B3C;
        color: #fff;
        border-bottom-right-radius: 4px;
    }
    .nuru-row.bot .nuru-bub {
        background: #fff;
        color: #1C1510;
        border: 1px solid #EAE5DF;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    </style>
    """, unsafe_allow_html=True)

    # ── FAB toggle button ────────────────────────────────────────────────────
    fab_col = st.columns([30, 1])
    with fab_col[1]:
        if st.button("✦", key="nuru_toggle", help="Chat with Nuru"):
            st.session_state.nuru_chat_open = not st.session_state.nuru_chat_open
            st.rerun()

    # ── Chat panel (only when open) ──────────────────────────────────────────
    if not st.session_state.nuru_chat_open:
        return

    # Build message bubbles
    if st.session_state.nuru_messages:
        msgs_html = ""
        for m in st.session_state.nuru_messages:
            cls  = "me" if m["role"] == "user" else "bot"
            safe = (m["content"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))
            msgs_html += f'<div class="nuru-row {cls}"><div class="nuru-bub">{safe}</div></div>\n'
    else:
        msgs_html = '<div class="nuru-row bot"><div class="nuru-bub">Hey, what would you like to know?</div></div>'

    st.markdown(f"""
    <div class="nuru-window">
      <div class="nuru-head">
        <div class="nuru-head-icon">✦</div>
        <div>
          <div class="nuru-head-name">Nuru</div>
          <div class="nuru-head-sub"><span class="nuru-dot"></span>Online</div>
        </div>
      </div>
      <div class="nuru-msgs">{msgs_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input row ────────────────────────────────────────────────────────────
    ic, sc, cc = st.columns([7, 1, 1])
    with ic:
        user_input = st.text_input(
            "", key="nuru_input",
            label_visibility="collapsed",
            placeholder="Ask anything…"
        )
    with sc:
        send = st.button("↑", key="nuru_send")
    with cc:
        close = st.button("✕", key="nuru_close")

    if close:
        st.session_state.nuru_chat_open = False
        st.rerun()

    if send and user_input:
        st.session_state.nuru_messages.append({"role": "user", "content": user_input})
        with st.spinner(""):
            reply = ask_nuru(
                user_input,
                st.session_state.token,
                st.session_state.nuru_messages[:-1]
            )
        st.session_state.nuru_messages.append({"role": "assistant", "content": reply})
        st.rerun()


# ── Session State ────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["token"] = None
    st.session_state["user_email"] = None

# ── Login Page ───────────────────────────────────────────────────────────────
if not st.session_state["logged_in"]:
    st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem;">
        <h1 style="color: {PRIMARY};">Msingi Retail System</h1>
        <p style="color: {TEXT_MUTED};">Retail Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        if st.button("Login", type="primary", use_container_width=True):
            if email and password:
                token = login_user(email, password)
                if token:
                    st.session_state["token"] = token
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = email
                    st.rerun()
            else:
                st.warning("Please enter email and password")

        st.markdown("---")
        st.caption("Don't have an account? Contact your administrator")

    st.stop()

# ── After login: floating Nuru bubble ────────────────────────────────────────
floating_chat_bubble()

# ── Main Dashboard ───────────────────────────────────────────────────────────
# Header
st.markdown(f"""
<div style="background: {CARD_BG}; padding: 1rem 2rem; border-radius: 12px; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; border: 1px solid #E5E7EB;">
    <div>
        <h2 style="margin: 0; color: {TEXT_DARK};">Msingi Retail System</h2>
        <p style="margin: 0; color: {TEXT_MUTED}; font-size: 0.85rem;">Intelligence Platform</p>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 0.9rem; color: {TEXT_DARK};">{st.session_state['user_email']}</div>
        <div style="font-size: 0.75rem; color: {TEXT_MUTED};">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"<h3 style='color: {PRIMARY};'>Dashboard Controls</h3>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["token"] = None
        st.session_state["nuru_messages"] = []
        st.session_state["nuru_chat_open"] = False
        st.rerun()

    st.markdown("---")
    st.markdown("### Data Status")

    token = st.session_state["token"]
    test_response = fetch_with_auth("/summary", token)
    if test_response:
        st.markdown('<span class="status-badge status-ok">Connected</span>', unsafe_allow_html=True)
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp_time = datetime.fromtimestamp(payload.get("exp"))
            if exp_time > datetime.now():
                st.info(f"Token expires: {exp_time.strftime('%H:%M:%S')}")
            else:
                st.warning("Token expired - please refresh")
        except:
            pass
    else:
        st.markdown('<span class="status-badge status-error">Disconnected</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Alert Settings")
    if st.button("Test Alert System", use_container_width=True):
        try:
            response = requests.post(
                f"{API_BASE}/alerts/test",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                st.success("Test alerts sent! Check email and SMS.")
            else:
                st.error("Failed to send test alerts")
        except Exception as e:
            st.error(f"Error: {e}")

# ── Fetch All Data ───────────────────────────────────────────────────────────
with st.spinner("Loading dashboard data..."):
    token = st.session_state["token"]

    summary      = fetch_with_auth("/summary", token)
    branches     = fetch_with_auth("/branches", token)
    departments  = fetch_with_auth("/departments", token)
    top_products = fetch_with_auth("/products/top?limit=10", token)
    low_margin   = fetch_with_auth("/products/low-margin", token)
    high_value   = fetch_with_auth("/products/high-value", token)
    anomalies    = fetch_with_auth("/anomalies/critical", token)
    stockout     = fetch_with_auth("/stockout/critical", token)
    forecast     = fetch_with_auth("/forecast", token)
    scorecard    = fetch_with_auth("/scorecard", token)
    data_quality = fetch_with_auth("/data-quality", token)

# ── If branches is empty, try to get branch data from scorecard ──────────────
if (not branches or len(branches) == 0) and scorecard and len(scorecard) > 0:
    branches = []
    for item in scorecard:
        branch_info = {
            "branch": item.get("branch"),
            "total_revenue": item.get("total_revenue", 0),
            "avg_margin": item.get("avg_margin", 0),
            "product_variety": item.get("product_variety", 0),
            "composite_score": item.get("composite_score", 0),
            "rank": item.get("rank", 0)
        }
        branches.append(branch_info)

# ── Check if we have data ────────────────────────────────────────────────────
if not summary:
    st.error("No data received from API. Please check your database and login.")
    if st.button("Refresh Login"):
        st.session_state["logged_in"] = False
        st.session_state["token"] = None
        st.rerun()
    st.stop()

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown("### Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue = summary.get('total_net_revenue', 0)
    st.metric("Total Revenue", f"KES {revenue:,.0f}")

with col2:
    branches_count = summary.get('total_branches', 0)
    if branches_count == 0 and branches:
        branches_count = len(branches)
    st.metric("Active Branches", branches_count)

with col3:
    products_count = summary.get('total_unique_products', 0)
    st.metric("Unique Products", products_count)

with col4:
    rows_count = summary.get('total_rows', 0)
    st.metric("Transactions", f"{rows_count:,}")

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Branch Analytics",
    "Products",
    "Alerts",
    "Recommendations",
    "Scorecard",
    "Data Quality"
])

# TAB 1: Branch Analytics
with tab1:
    display_branches = None
    if branches and len(branches) > 0:
        display_branches = branches
    elif scorecard and len(scorecard) > 0:
        display_branches = scorecard
    elif forecast and len(forecast) > 0:
        display_branches = forecast

    if display_branches and len(display_branches) > 0:
        df_branches = pd.DataFrame(display_branches)

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Revenue by Branch")
            revenue_column = None
            possible_revenue_cols = ['total_revenue', 'revenue', 'net_sale', 'current_revenue', 'total_net_revenue']
            for col in possible_revenue_cols:
                if col in df_branches.columns:
                    revenue_column = col
                    break
            if revenue_column is None:
                for col in df_branches.columns:
                    if 'revenue' in col.lower() or 'sale' in col.lower():
                        revenue_column = col
                        break

            if revenue_column and 'branch' in df_branches.columns:
                fig = px.bar(df_branches, x='branch', y=revenue_column,
                             title="Branch Revenue",
                             color=revenue_column,
                             color_continuous_scale='Greens',
                             text_auto='.2s')
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor=CARD_BG,
                    paper_bgcolor=CARD_BG,
                    font_color=TEXT_DARK
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df_branches.head())

        with col_right:
            st.subheader("Margin by Branch")
            margin_column = None
            possible_margin_cols = ['avg_margin', 'margin', 'margin_pct']
            for col in possible_margin_cols:
                if col in df_branches.columns:
                    margin_column = col
                    break
            if margin_column is None:
                for col in df_branches.columns:
                    if 'margin' in col.lower():
                        margin_column = col
                        break

            if margin_column and 'branch' in df_branches.columns:
                fig = px.bar(df_branches, x='branch', y=margin_column,
                             title="Margin % by Branch",
                             color=margin_column,
                             color_continuous_scale='RdYlGn')
                fig.add_hline(y=5, line_dash="dash", line_color=ERROR,
                              annotation_text="5% Threshold")
                fig.update_layout(
                    height=400,
                    plot_bgcolor=CARD_BG,
                    paper_bgcolor=CARD_BG,
                    font_color=TEXT_DARK
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No margin data available")

        st.subheader("Branch Performance Details")
        st.dataframe(df_branches, use_container_width=True)
    else:
        st.info("No branch data available")

# TAB 2: Products
with tab2:
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.subheader("Top 10 Products")
        if top_products and len(top_products) > 0:
            df_top = pd.DataFrame(top_products)
            st.dataframe(df_top, use_container_width=True)
        else:
            st.info("No product data available")

    with col_p2:
        st.subheader("Low Margin Products")
        if low_margin and len(low_margin) > 0:
            df_low = pd.DataFrame(low_margin)
            st.dataframe(df_low, use_container_width=True)
        else:
            st.info("No low margin products detected")

    st.subheader("High Value Products")
    if high_value and len(high_value) > 0:
        df_high = pd.DataFrame(high_value)
        st.dataframe(df_high, use_container_width=True)
    else:
        st.info("No high value products data")

# TAB 3: Alerts
with tab3:
    st.markdown("### Active Alerts")

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.subheader("Critical Anomalies")
        if anomalies and len(anomalies) > 0:
            df_anomalies = pd.DataFrame(anomalies)
            st.dataframe(df_anomalies, use_container_width=True)
            st.warning(f"{len(anomalies)} critical anomalies detected!")
        else:
            st.success("No critical anomalies detected")

    with col_a2:
        st.subheader("Stockout Risks")
        if stockout and len(stockout) > 0:
            df_stockout = pd.DataFrame(stockout)
            st.dataframe(df_stockout, use_container_width=True)
            st.warning(f"{len(stockout)} products at stockout risk!")
        else:
            st.success("No stockout risks detected")

    st.divider()

    st.subheader("Manual Alert Trigger")
    if st.button("Run Alert Checks Now", type="primary"):
        try:
            response = requests.get(
                f"{API_BASE}/alerts/run",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                st.success("Alert checks completed! Check logs for results.")
            else:
                st.error("Failed to run alerts")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 4: Recommendations
with tab4:
    with st.container():
        st.markdown(f"""
        <div style="background: {CARD_BG}; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h3>Product Recommendation Engine</h3>
            <p><em>AI-powered recommendations based on cross-branch performance</em></p>
        """, unsafe_allow_html=True)

        branch_list = []
        if scorecard and len(scorecard) > 0:
            branch_list = [item.get("branch") for item in scorecard if item.get("branch")]

        if branch_list:
            selected_branch = st.selectbox("Select Branch", options=sorted(branch_list))
            limit = st.slider("Number of Recommendations", min_value=1, max_value=20, value=5)

            if st.button("Get Recommendations", type="primary", use_container_width=True):
                with st.spinner(f"Analyzing cross-branch performance for {selected_branch}..."):
                    try:
                        headers = {"Authorization": f"Bearer {token}"}
                        response = requests.get(
                            f"{API_BASE}/recommendations/{selected_branch}",
                            headers=headers,
                            params={"limit": limit},
                            timeout=10
                        )

                        if response.status_code == 200:
                            data = response.json()
                            recommendations = data.get("recommendations", [])
                            benchmark = data.get("benchmark_branch", "top-performing branch")

                            if recommendations:
                                st.success(f"Found {len(recommendations)} recommendations based on **{benchmark}**")
                                df_rec = pd.DataFrame(recommendations)
                                st.dataframe(df_rec, use_container_width=True)

                                total_revenue = df_rec["revenue_at_benchmark"].sum()
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Recommendations", len(df_rec))
                                with col2:
                                    st.metric("Potential Revenue", f"KES {total_revenue:,.2f}")
                                with col3:
                                    st.metric("Benchmark Branch", benchmark)

                                st.info("These products perform well in other branches and could boost revenue!")
                            else:
                                st.info(f"No recommendations available for {selected_branch}")
                        else:
                            st.error(f"Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No branches found. Please check your data.")

        st.markdown("</div>", unsafe_allow_html=True)

# TAB 5: Scorecard
with tab5:
    with st.container():
        st.markdown(f"""
        <div style="background: {CARD_BG}; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h3>Branch Benchmarking Scorecard</h3>
            <p>Ranked performance across 5 key metrics</p>
        """, unsafe_allow_html=True)

        try:
            if scorecard and len(scorecard) > 0:
                df_score = pd.DataFrame(scorecard)
                st.subheader("Branch Rankings")
                st.dataframe(df_score, use_container_width=True)

                if 'composite_score' in df_score.columns:
                    fig = px.bar(df_score, x='branch', y='composite_score',
                                 title="Composite Performance Score (0-100)",
                                 color='composite_score',
                                 color_continuous_scale='RdYlGn',
                                 text='composite_score')
                    fig.update_layout(
                        height=400,
                        plot_bgcolor=CARD_BG,
                        paper_bgcolor=CARD_BG,
                        font_color=TEXT_DARK
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    top_branch = df_score.iloc[0]['branch']
                    top_score  = df_score.iloc[0]['composite_score']
                    st.success(f"Top Performer: **{top_branch}** with score **{top_score}**")
            else:
                st.info("No scorecard data available")
        except Exception as e:
            st.error(f"Error loading scorecard: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

# TAB 6: Data Quality
with tab6:
    with st.container():
        st.markdown(f"""
        <div style="background: {CARD_BG}; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h3>Data Quality Monitor</h3>
            <p>Track data completeness and pipeline health</p>
        """, unsafe_allow_html=True)

        if data_quality is None:
            with st.spinner("Fetching data quality metrics..."):
                data_quality = fetch_with_auth("/data-quality", token)

        if data_quality and isinstance(data_quality, dict):
            overall_status = data_quality.get("overall_status", "UNKNOWN")
            if overall_status == "OK":
                badge = '<span class="status-badge status-ok">OK</span>'
            elif overall_status == "FAIL":
                badge = '<span class="status-badge status-error">FAIL</span>'
            else:
                badge = '<span class="status-badge status-warning">WARNING</span>'

            st.markdown(f"Overall Data Quality Status: {badge}", unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{data_quality.get('total_rows', 0):,}")
            with col2:
                st.metric("Source Files", data_quality.get("source_files_loaded", 0))
            with col3:
                earliest = data_quality.get("earliest_sale", "N/A")
                if earliest and len(str(earliest)) > 10:
                    earliest = str(earliest)[:10]
                st.metric("Earliest Sale", earliest)
            with col4:
                latest = data_quality.get("latest_sale", "N/A")
                if latest and len(str(latest)) > 10:
                    latest = str(latest)[:10]
                st.metric("Latest Sale", latest)

            st.divider()

            if "columns" in data_quality and data_quality["columns"]:
                st.subheader("Column Quality Report")
                df_quality = pd.DataFrame(data_quality["columns"])
                st.dataframe(df_quality, use_container_width=True)

                failed_cols = df_quality[df_quality['status'] == 'FAIL']
                if len(failed_cols) > 0:
                    st.error(f"{len(failed_cols)} columns FAILED quality checks")
                else:
                    st.success("All columns passed quality checks!")
        else:
            st.warning("No data quality metrics available")
            if st.button("Refresh Data Quality", type="primary"):
                with st.spinner("Fetching data quality metrics..."):
                    data_quality = fetch_with_auth("/data-quality", token)
                    if data_quality:
                        st.rerun()

        st.divider()

        st.subheader("Revenue Forecast")
        if forecast and len(forecast) > 0:
            df_forecast = pd.DataFrame(forecast)
            st.dataframe(df_forecast, use_container_width=True)

            forecast_columns = ['current_revenue', 'month1_target', 'month2_target', 'month3_target']
            existing_columns = [col for col in forecast_columns if col in df_forecast.columns]

            if existing_columns:
                fig = px.bar(df_forecast, x='branch', y=existing_columns,
                             title="Revenue Forecast by Branch",
                             barmode='group')
                fig.update_layout(
                    height=500,
                    plot_bgcolor=CARD_BG,
                    paper_bgcolor=CARD_BG,
                    font_color=TEXT_DARK
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No forecast data available")

        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption(f"Msingi Retail System | Data refreshed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Alert checks run every 60 minutes")