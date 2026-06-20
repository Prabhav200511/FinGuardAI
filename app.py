"""
app.py — FinGuard AI  |  Streamlit Dashboard
Real-time UPI Fraud Detection with Explainable AI
Usage: streamlit run app.py
"""

import html
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

# ─────────────────────────────────────────────────────────────────────────────
# Page config — must come first
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinGuard AI",
    page_icon ="🛡️",
    layout    ="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS — Premium Glassmorphism UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

/* ── Background ─────────────────────────────────── */
[data-testid="stAppViewContainer"] {
  background: radial-gradient(ellipse at 20% 50%, #111832 0%, #0a0e1a 50%, #080c16 100%);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0d1225 0%, #10152a 100%);
  border-right: 1px solid rgba(255,255,255,0.06);
}
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
html { scroll-behavior: smooth; }

/* ── Scrollbars ─────────────────────────────────── */
* { scrollbar-width: thin; scrollbar-color: #2a3558 #0a0e1a; }
*::-webkit-scrollbar { width: 6px; height: 6px; }
*::-webkit-scrollbar-track { background: transparent; }
*::-webkit-scrollbar-thumb { background: #2a3558; border-radius: 10px; }
*::-webkit-scrollbar-thumb:hover { background: #4a5b88; }

/* ── Animations ──────────────────────────────────── */
@keyframes slideInUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,200,151,0.5); }
  50%      { opacity: 0.7; box-shadow: 0 0 0 6px rgba(0,200,151,0); }
}
@keyframes glow {
  0%, 100% { box-shadow: 0 0 12px rgba(74,122,255,0.15); }
  50%      { box-shadow: 0 0 24px rgba(74,122,255,0.3); }
}

/* ── Stat header cards ─────────────────────────── */
.stat-row {
  display: flex; gap: 14px; margin-bottom: 1.6rem;
  position: sticky; top: 0.5rem; z-index: 20;
  padding: 10px; border-radius: 16px;
  background: rgba(10,14,26,0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.stat-card {
  flex: 1;
  background: rgba(26,31,46,0.6);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 22px 20px 16px;
  text-align: center;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent, #4a7aff), transparent);
  opacity: 0.6;
}
.stat-card:hover {
  border-color: rgba(255,255,255,0.12);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.stat-value {
  font-size: 2em; font-weight: 800;
  color: #e8eaf6; margin: 0; line-height: 1.2;
  letter-spacing: -0.02em;
}
.stat-label {
  font-size: 0.75em; font-weight: 500;
  color: #6a7290; margin-top: 6px;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.stat-icon {
  font-size: 1.3em; margin-bottom: 4px;
  display: block;
}

/* ── Live indicator ──────────────────────────────── */
.live-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #00c897;
  animation: pulse 1.5s ease-in-out infinite;
  margin-right: 6px;
  vertical-align: middle;
}
.live-badge {
  display: inline-flex; align-items: center;
  background: rgba(0,200,151,0.1);
  border: 1px solid rgba(0,200,151,0.25);
  border-radius: 20px;
  padding: 4px 12px 4px 8px;
  font-size: 0.78em; font-weight: 600;
  color: #00c897;
  margin-left: 8px;
}
.offline-badge {
  display: inline-flex; align-items: center;
  background: rgba(120,128,160,0.1);
  border: 1px solid rgba(120,128,160,0.2);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.78em; font-weight: 500;
  color: #7880a0;
  margin-left: 8px;
}

/* ── Transaction cards (Live Feed) ───────────────── */
.txn-card {
  background: rgba(26,31,46,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 14px 18px;
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.25s ease;
  animation: slideInUp 0.4s ease-out;
  backdrop-filter: blur(8px);
}
.txn-card:hover {
  border-color: rgba(255,255,255,0.1);
  background: rgba(26,31,46,0.7);
  transform: translateX(4px);
}
.txn-card.fraud {
  border-left: 3px solid #ff4b4b;
  background: linear-gradient(135deg, rgba(40,12,12,0.6), rgba(26,31,46,0.5));
  box-shadow: -4px 0 20px rgba(255,75,75,0.08);
}
.txn-card.warn {
  border-left: 3px solid #ffd700;
  background: linear-gradient(135deg, rgba(40,35,8,0.6), rgba(26,31,46,0.5));
  box-shadow: -4px 0 16px rgba(255,215,0,0.06);
}
.txn-card.safe {
  border-left: 3px solid #00c897;
}
.txn-id { font-size: 0.8em; color: #6a7290; font-weight: 500; min-width: 100px; font-family: 'SF Mono', monospace !important; }
.txn-amount { font-weight: 700; color: #e8eaf6; min-width: 90px; font-size: 0.95em; }
.txn-meta { font-size: 0.82em; color: #7880a0; display: flex; gap: 14px; flex: 1; flex-wrap: wrap; }
.txn-meta span { white-space: nowrap; }
.risk-pill {
  border-radius: 8px; padding: 4px 12px;
  font-size: 0.78em; font-weight: 700;
  text-align: center; min-width: 70px;
  letter-spacing: 0.03em;
}
.risk-pill.high { background: rgba(255,75,75,0.15); color: #ff6b6b; border: 1px solid rgba(255,75,75,0.25); }
.risk-pill.med  { background: rgba(255,215,0,0.12); color: #ffdb4d; border: 1px solid rgba(255,215,0,0.2); }
.risk-pill.safe { background: rgba(0,200,151,0.12); color: #33d9a8; border: 1px solid rgba(0,200,151,0.2); }

/* ── Risk score bar ──────────────────────────────── */
.risk-bar-bg {
  width: 60px; height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 4px;
}
.risk-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* ── Fraud alert cards ───────────────────────────── */
.alert-card {
  background: rgba(26,31,46,0.6);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 20px 24px;
  margin: 12px 0;
  backdrop-filter: blur(12px);
  animation: fadeIn 0.5s ease-out;
  transition: all 0.3s ease;
}
.alert-card:hover {
  border-color: rgba(255,255,255,0.12);
  box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
.alert-card.critical {
  border-left: 4px solid #ff4b4b;
  box-shadow: 0 0 30px rgba(255,75,75,0.08);
}
.alert-card.warning {
  border-left: 4px solid #ffd700;
  box-shadow: 0 0 24px rgba(255,215,0,0.06);
}
.alert-header {
  display: flex; justify-content: space-between;
  align-items: center; flex-wrap: wrap; gap: 8px;
  margin-bottom: 14px;
}
.alert-title {
  font-size: 1.05em; font-weight: 700; color: #e8eaf6;
}
.alert-time {
  font-size: 0.78em; color: #6a7290; font-weight: 500;
}
.alert-details {
  display: flex; gap: 18px; flex-wrap: wrap;
  color: #8890a8; font-size: 0.85em;
  padding: 12px 0;
  border-top: 1px solid rgba(255,255,255,0.04);
}
.alert-details span { white-space: nowrap; }
.alert-details strong { color: #b0b8d4; }
.alert-score {
  font-size: 1.3em; font-weight: 800;
  letter-spacing: -0.02em;
}

/* ── Explanation box ─────────────────────────────── */
.explain-box {
  background: linear-gradient(135deg, rgba(26,36,64,0.7), rgba(20,28,52,0.5));
  border: 1px solid rgba(74,122,255,0.15);
  border-radius: 12px;
  padding: 16px 20px;
  font-size: 0.9em; line-height: 1.8;
  color: #c0c8e0;
  margin-top: 8px;
  backdrop-filter: blur(8px);
}

/* ── Chart container cards ───────────────────────── */
.chart-container {
  background: rgba(26,31,46,0.4);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 20px;
  margin: 8px 0;
  backdrop-filter: blur(8px);
}
.chart-title {
  font-size: 0.95em; font-weight: 700;
  color: #e8eaf6;
  margin-bottom: 12px;
  display: flex; align-items: center; gap: 8px;
}

/* ── Model metrics card ──────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin: 12px 0;
}
.metric-item {
  background: rgba(26,31,46,0.5);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 16px;
  text-align: center;
  transition: all 0.3s ease;
}
.metric-item:hover {
  border-color: rgba(74,122,255,0.3);
  transform: translateY(-2px);
}
.metric-val { font-size: 1.5em; font-weight: 800; color: #e8eaf6; }
.metric-lbl { font-size: 0.72em; color: #6a7290; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Risk tags ───────────────────────────────────── */
.tag-high { background: rgba(255,75,75,0.12); color: #ff6b6b;
            border: 1px solid rgba(255,75,75,0.25); border-radius: 6px;
            padding: 3px 10px; font-size: 0.76em; font-weight: 700; }
.tag-med  { background: rgba(255,215,0,0.1); color: #ffdb4d;
            border: 1px solid rgba(255,215,0,0.2); border-radius: 6px;
            padding: 3px 10px; font-size: 0.76em; font-weight: 700; }
.tag-safe { background: rgba(0,200,151,0.1); color: #33d9a8;
            border: 1px solid rgba(0,200,151,0.2); border-radius: 6px;
            padding: 3px 10px; font-size: 0.76em; font-weight: 700; }

/* ── Typography ──────────────────────────────────── */
h1, h2, h3, h4 { color: #e8eaf6 !important; letter-spacing: -0.01em; }
p, li { color: #b0b8cc; }
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── Sidebar ─────────────────────────────────────── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label { color: #b0b8cc !important; }

/* ── Sidebar branding ────────────────────────────── */
.sidebar-brand {
  text-align: center;
  padding: 8px 0 4px;
  margin-bottom: 8px;
}
.sidebar-brand h2 {
  background: linear-gradient(135deg, #4a7aff, #00c897);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.4em; font-weight: 800;
  margin: 0;
}
.sidebar-brand p {
  color: #6a7290; font-size: 0.78em; margin: 4px 0 0;
  letter-spacing: 0.06em; text-transform: uppercase;
}
.sidebar-version {
  text-align: center;
  font-size: 0.72em;
  color: #4a5570;
  padding: 2px 0 8px;
}

/* ── Tabs ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: rgba(26,31,46,0.4);
  border-radius: 12px;
  padding: 4px;
  border: 1px solid rgba(255,255,255,0.05);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  padding: 8px 20px;
  font-weight: 600;
  font-size: 0.88em;
  color: #7880a0;
  transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
  background: rgba(74,122,255,0.15) !important;
  color: #e8eaf6 !important;
  border-bottom: none !important;
}
.stTabs [data-baseweb="tab-highlight"] {
  display: none;
}

/* ── Buttons ─────────────────────────────────────── */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #4a7aff, #3d5afe) !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: all 0.25s ease !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 4px 20px rgba(74,122,255,0.35) !important;
  transform: translateY(-1px) !important;
}
.stButton > button {
  border-radius: 10px !important;
  font-weight: 500 !important;
  transition: all 0.25s ease !important;
}

/* ── Plotly transparent bg ───────────────────────── */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* ── Empty state ─────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6a7290;
}
.empty-state .icon { font-size: 3em; margin-bottom: 12px; opacity: 0.5; }
.empty-state p { font-size: 0.95em; max-width: 400px; margin: 0 auto; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Cached resource loaders
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🛡️ Loading FinGuard AI model…")
def _load_predictor():
    from predictor import FraudPredictor
    return FraudPredictor.instance()

@st.cache_resource(show_spinner=False)
def _load_groq():
    from groq_client import get_explanation
    return get_explanation

@st.cache_data(show_spinner=False)
def _load_model_params():
    """Load model performance metrics for the analytics tab."""
    params_path = BASE_DIR / "models" / "params.json"
    if params_path.exists():
        return json.loads(params_path.read_text(encoding="utf-8"))
    return {}


# ── Guard: models must exist ──────────────────────────────────────────────────
if not (BASE_DIR / "models" / "isolation_forest.pkl").exists():
    st.error("### ⚙️ Setup Required\nModels not found. Run in your terminal:")
    st.code("python generate_data.py\npython train.py\nstreamlit run app.py")
    st.stop()

predictor  = _load_predictor()
get_exp_fn = _load_groq()
model_params = _load_model_params()
FRAUD_THRESHOLD = predictor.threshold
MEDIUM_THRESHOLD = max(35.0, FRAUD_THRESHOLD - 20.0)


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "transactions": [],
        "alerts":       [],
        "live_active":  False,
        "language":     "english",
        "total_monitored": 0,
        "total_protected": 0.0,
        "demo_seeded": False,
        "weekly_volume": [6, 8, 5, 11, 7, 9, 4],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────
def risk_color(s: float) -> str:
    return "#ff4b4b" if s >= FRAUD_THRESHOLD else "#ffd700" if s >= MEDIUM_THRESHOLD else "#00c897"

def risk_label(s: float) -> str:
    return "HIGH" if s >= FRAUD_THRESHOLD else "MED" if s >= MEDIUM_THRESHOLD else "SAFE"

def risk_tag_html(s: float) -> str:
    if s >= FRAUD_THRESHOLD: return '<span class="tag-high">🔴 HIGH RISK</span>'
    if s >= MEDIUM_THRESHOLD: return '<span class="tag-med">🟡 MEDIUM</span>'
    return '<span class="tag-safe">🟢 SAFE</span>'

def card_class(s: float) -> str:
    return "fraud" if s >= FRAUD_THRESHOLD else "warn" if s >= MEDIUM_THRESHOLD else "safe"

def risk_pill_class(s: float) -> str:
    return "high" if s >= FRAUD_THRESHOLD else "med" if s >= MEDIUM_THRESHOLD else "safe"

def _add_txn(txn: dict, *, notify: bool = False):
    pred  = predictor.predict(txn)
    entry = {**txn, **pred, "ts": datetime.now()}
    st.session_state.transactions.insert(0, entry)
    st.session_state.transactions = st.session_state.transactions[:60]
    st.session_state.total_monitored += 1
    if pred["is_fraud"]:
        st.session_state.total_protected = round(
            st.session_state.total_protected + txn["amount"] / 1e5, 1
        )
        st.session_state.alerts.insert(0, entry)
        st.session_state.alerts = st.session_state.alerts[:25]
        if notify:
            st.toast(
                f"🚨 Fraud detected — ₹{txn['amount']:,.0f} · Score: {pred['risk_score']:.0f}",
                icon="🔴",
            )


if not st.session_state.demo_seeded:
    from generate_data import generate_demo_batch

    for demo_transaction in generate_demo_batch(12, fraud_ratio=0.33):
        _add_txn(demo_transaction)
    st.session_state.demo_seeded = True

def _shap_chart(top_features: list, language: str) -> go.Figure:
    if not top_features:
        return go.Figure()
    labels = [f["label_hi"] if language == "hindi" else f["label_en"] for f in top_features]
    values = [abs(f["shap_value"]) for f in top_features]
    colors = ["#ff6b6b" if f["increases_risk"] else "#33d9a8" for f in top_features]
    disp   = [f["display_value"] for f in top_features]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colors,
        marker_line=dict(width=0),
        text=disp, textposition="outside",
        textfont=dict(color="#8890a8", size=12, family="Inter"),
    ))
    fig.update_layout(
        margin=dict(l=5, r=15, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b0b8cc", size=13, family="Inter"), height=200,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, autorange="reversed"),
        showlegend=False,
        bargap=0.35,
    )
    return fig


def _render_txn_card_html(t: dict) -> str:
    """Render a single transaction as a styled HTML card."""
    s = t["risk_score"]
    cls = card_class(s)
    pill_cls = risk_pill_class(s)
    lbl = risk_label(s)
    txn_id = str(t.get("transaction_id", ""))[:14]
    bar_color = risk_color(s)
    bar_width = min(s, 100)

    return f"""
    <div class="txn-card {cls}">
      <div class="txn-id">{html.escape(txn_id)}</div>
      <div class="txn-amount">₹{t['amount']:,.0f}</div>
      <div class="txn-meta">
        <span>🕐 {t['hour']:02d}:00</span>
        <span>🏪 {html.escape(t['merchant_category'])}</span>
        <span>📱 {'New' if t['device_change'] else '—'}</span>
        <span>📍 {t['geo_distance_km']:.0f}km</span>
      </div>
      <div style="text-align:center;min-width:70px">
        <div class="risk-pill {pill_cls}">{lbl} {s:.0f}</div>
        <div class="risk-bar-bg" style="margin-top:4px">
          <div class="risk-bar-fill" style="width:{bar_width}%;background:{bar_color}"></div>
        </div>
      </div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown("""
    <div class="sidebar-brand">
      <h2>🛡️ FinGuard AI</h2>
      <p>UPI Fraud Detection · XAI</p>
    </div>
    """, unsafe_allow_html=True)

    mode = "Groq + Llama" if os.getenv("GROQ_API_KEY", "").strip() else "Offline"
    st.markdown(
        f'<div class="sidebar-version">v{predictor.params.get("model_version", "2")} · {mode}</div>',
        unsafe_allow_html=True,
    )

    # Live status badge
    if st.session_state.live_active:
        st.markdown(
            '<div style="text-align:center;margin-bottom:12px">'
            '<span class="live-badge"><span class="live-dot"></span> LIVE FEED ACTIVE</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align:center;margin-bottom:12px">'
            '<span class="offline-badge">● FEED PAUSED</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Language
    lang_sel = st.radio("🌐 Language / भाषा", ["English", "हिंदी"], horizontal=True)
    st.session_state.language = "hindi" if lang_sel == "हिंदी" else "english"
    lang = st.session_state.language
    st.divider()

    # Demo controls
    st.markdown("#### 🎮 Demo Controls")
    st.caption("Synthetic transactions only · no bank connection")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⚡ Fraud Txn", width="stretch", type="primary"):
            from generate_data import random_fraud_txn
            _add_txn(random_fraud_txn(), notify=True)
            st.rerun()
    with c2:
        if st.button("✅ Safe Txn", width="stretch"):
            from generate_data import random_normal_txn
            _add_txn(random_normal_txn())
            st.rerun()

    live_label = "⏹ Stop Feed" if st.session_state.live_active else "▶ Start Live Feed"
    live_type  = "secondary" if st.session_state.live_active else "primary"
    if st.button(live_label, width="stretch", type=live_type):
        st.session_state.live_active = not st.session_state.live_active
        st.rerun()

    if st.button("🗑️ Clear All", width="stretch"):
        st.session_state.transactions = []
        st.session_state.alerts       = []
        st.session_state.total_monitored = 0
        st.session_state.total_protected = 0.0
        st.rerun()

    st.divider()

    # Manual analysis form
    st.markdown("#### 🔍 Manual Analysis")
    with st.form("manual"):
        c1, c2 = st.columns(2)
        with c1:
            m_amt  = st.number_input("Amount (₹)", min_value=1.0,  value=28000.0, step=500.0, help="Transaction amount in rupees")
            m_geo  = st.number_input("Distance (km)", 0.0, 2000.0, 820.0, help="Distance from last known location")
        with c2:
            m_vel  = st.number_input("Txns / hr", 1, 30, 1, help="Transaction velocity per hour")
            m_cat  = st.selectbox("Category", [
                "electronics", "grocery", "restaurant", "fuel",
                "pharmacy", "transport", "utilities", "clothing", "education",
            ])
            
        m_hour = st.slider("Hour of day", 0, 23, 2)
        
        c3, c4 = st.columns(2)
        with c3:
            m_dev  = st.checkbox("New device", value=True)
        with c4:
            m_new  = st.checkbox("New merchant", value=True)
            
        ok = st.form_submit_button("Analyze 🔎", width="stretch", type="primary")

    if ok:
        _add_txn({
            "transaction_id": "MANUAL-CHECK",
            "amount": m_amt, "hour": m_hour, "merchant_category": m_cat,
            "device_change": int(m_dev), "geo_distance_km": m_geo,
            "velocity_per_hour": m_vel, "is_new_merchant": int(m_new),
        }, notify=True)
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Header stats
# ─────────────────────────────────────────────────────────────────────────────
total    = st.session_state.total_monitored
flagged  = len(st.session_state.alerts)
rate     = flagged / max(total, 1) * 100
protected= st.session_state.total_protected

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card" style="--accent:#4a7aff">
    <span class="stat-icon">📡</span>
    <p class="stat-value">{total:,}</p>
    <p class="stat-label">Transactions</p>
  </div>
  <div class="stat-card" style="--accent:#ff4b4b">
    <span class="stat-icon">🚨</span>
    <p class="stat-value" style="color:#ff6b6b">{flagged}</p>
    <p class="stat-label">Fraud Alerts</p>
  </div>
  <div class="stat-card" style="--accent:#ffd700">
    <span class="stat-icon">📊</span>
    <p class="stat-value" style="color:#ffdb4d">{rate:.1f}%</p>
    <p class="stat-label">Fraud Rate</p>
  </div>
  <div class="stat-card" style="--accent:#00c897">
    <span class="stat-icon">🛡️</span>
    <p class="stat-value" style="color:#33d9a8">₹{protected:.1f}L</p>
    <p class="stat-label">Flagged Value</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📡 Live Feed", "🚨 Fraud Alerts", "📊 Analytics"])


# ──────────────────────────────────────────────────
# TAB 1 — Live Feed (using @st.fragment for non-blocking updates)
# ──────────────────────────────────────────────────
with tab1:
    st.caption("Data source: locally generated synthetic UPI-like transactions.")

    @st.fragment(run_every=3 if st.session_state.live_active else None)
    def _live_feed_fragment():
        """Fragment that auto-refreshes only itself, not the entire page."""
        if st.session_state.live_active:
            from generate_data import random_fraud_txn, random_normal_txn
            txn = random_fraud_txn() if random.random() < 0.25 else random_normal_txn()
            _add_txn(txn, notify=True)

        txns = st.session_state.transactions
        if not txns:
            st.markdown("""
            <div class="empty-state">
              <div class="icon">📡</div>
              <p>Press <strong>▶ Start Live Feed</strong> in the sidebar, or use
              <strong>⚡ Fraud Txn / ✅ Safe Txn</strong> to add transactions.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Status bar
            feed_count = len(txns)
            fraud_count = sum(1 for t in txns if t["risk_score"] >= FRAUD_THRESHOLD)
            safe_count = feed_count - fraud_count

            cols = st.columns([1, 1, 1, 2])
            with cols[0]:
                st.metric("In Feed", feed_count)
            with cols[1]:
                st.metric("🔴 Fraud", fraud_count)
            with cols[2]:
                st.metric("🟢 Safe", safe_count)
            with cols[3]:
                if st.session_state.live_active:
                    st.markdown(
                        '<span class="live-badge" style="margin-top:12px;display:inline-block">'
                        '<span class="live-dot"></span> Auto-refreshing every 3s</span>',
                        unsafe_allow_html=True,
                    )

            # Transaction cards
            cards_html = ""
            for t in txns[:25]:
                cards_html += _render_txn_card_html(t)

            st.markdown(
                f'<div style="max-height:520px;overflow-y:auto;padding-right:4px">{cards_html}</div>',
                unsafe_allow_html=True,
            )

    _live_feed_fragment()


# ──────────────────────────────────────────────────
# TAB 2 — Fraud Alerts with SHAP + LLM explanation
# ──────────────────────────────────────────────────
with tab2:
    alerts = st.session_state.alerts
    if not alerts:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">🔍</div>
          <p>No fraud alerts yet. Add a suspicious transaction using the sidebar controls
          or start the live feed.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption(f"Showing {len(alerts)} fraud alert{'s' if len(alerts) != 1 else ''}")

        for i, alert in enumerate(alerts):
            s      = alert["risk_score"]
            cls    = "critical" if s >= FRAUD_THRESHOLD else "warning"
            tag    = risk_tag_html(s)
            txn_id = str(alert.get("transaction_id", ""))
            disp_id= txn_id[:20] + ("…" if len(txn_id) > 20 else "")

            st.markdown(f"""
<div class="alert-card {cls}">
  <div class="alert-header">
    <div>
      <span class="alert-title">#{i+1} &nbsp; {html.escape(disp_id)}</span>
      &nbsp;&nbsp;{tag}
    </div>
    <span class="alert-time">{alert['ts'].strftime('%d %b %Y  %H:%M:%S')}</span>
  </div>
  <div class="alert-details">
    <span>💰 <strong>₹{alert['amount']:,.0f}</strong></span>
    <span>🕐 {alert['hour']:02d}:00</span>
    <span>🏪 {html.escape(alert['merchant_category'])}</span>
    <span>📱 Device: {'Changed' if alert['device_change'] else 'Same'}</span>
    <span>📍 {alert['geo_distance_km']:.0f} km</span>
    <span>⚡ {alert['velocity_per_hour']} txns/hr</span>
    <span>🎯 Score: <span class="alert-score" style="color:{risk_color(s)}">{s:.1f}</span>/100</span>
  </div>
</div>""", unsafe_allow_html=True)

            col_chart, col_exp = st.columns([1, 1.4])

            with col_chart:
                top_f = alert.get("top_features", [])
                if top_f:
                    st.caption("🔍 SHAP Risk Factors  (🔴 increases risk  |  🟢 normal)")
                    st.plotly_chart(
                        _shap_chart(top_f, lang),
                        width="stretch",
                        key=f"shap_{i}_{lang}",
                    )
                else:
                    st.caption("SHAP values not available")

            with col_exp:
                exp_key = f"exp_{i}_{lang}"
                if exp_key not in st.session_state:
                    btn_lbl = "🤖 स्पष्टीकरण देखें" if lang == "hindi" else "🤖 Get AI Explanation"
                    if st.button(btn_lbl, key=f"btn_{i}_{lang}"):
                        with st.spinner("Generating explanation via Groq / Llama 3.3-70B…"):
                            exp = get_exp_fn(alert, alert, lang)
                            st.session_state[exp_key] = exp
                        st.rerun()
                else:
                    st.markdown(
                        f'<div class="explain-box">{html.escape(st.session_state[exp_key]).replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True,
                    )
                    regen_lbl = "🔄 पुनः उत्पन्न" if lang == "hindi" else "🔄 Regenerate"
                    if st.button(regen_lbl, key=f"regen_{i}_{lang}"):
                        del st.session_state[exp_key]
                        st.rerun()

            if i < len(alerts) - 1:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────
# TAB 3 — Analytics
# ──────────────────────────────────────────────────
with tab3:

    # ── Model Performance Card ────────────────────────
    if model_params:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🧠 Model Performance Metrics</div>', unsafe_allow_html=True)

        f1_val = model_params.get("f1", 0)
        auc_val = model_params.get("roc_auc", 0)
        prec_val = model_params.get("precision_fraud", 0)
        rec_val = model_params.get("recall_fraud", 0)
        thresh_val = model_params.get("threshold", 0)

        st.markdown(f"""
        <div class="metrics-grid">
          <div class="metric-item">
            <div class="metric-val" style="color:#4a7aff">{f1_val:.2%}</div>
            <div class="metric-lbl">F1 Score</div>
          </div>
          <div class="metric-item">
            <div class="metric-val" style="color:#00c897">{auc_val:.2%}</div>
            <div class="metric-lbl">ROC AUC</div>
          </div>
          <div class="metric-item">
            <div class="metric-val" style="color:#ffd700">{prec_val:.2%}</div>
            <div class="metric-lbl">Precision</div>
          </div>
          <div class="metric-item">
            <div class="metric-val" style="color:#ff6b6b">{rec_val:.2%}</div>
            <div class="metric-lbl">Recall</div>
          </div>
          <div class="metric-item">
            <div class="metric-val" style="color:#e8eaf6">{thresh_val:.1f}</div>
            <div class="metric-lbl">Threshold</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(model_params.get("evaluation_note", ""))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Row 1 — 7-day bar + fraud type pie
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🗓️ 7-Day Fraud Volume</div>', unsafe_allow_html=True)
        today = datetime.now()
        days  = [(today - timedelta(days=d)).strftime("%a %d") for d in range(6, -1, -1)]
        vol   = list(st.session_state.weekly_volume)
        vol[-1] = max(vol[-1], flagged)      # include today's alerts

        fig_bar = go.Figure(go.Bar(
            x=days, y=vol,
            marker_color=["#ff6b6b" if v > 10 else "#ffdb4d" if v > 6 else "#4a7aff" for v in vol],
            marker_line=dict(width=0),
            text=vol, textposition="outside",
            textfont=dict(color="#6a7290", size=11, family="Inter"),
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#b0b8cc", family="Inter"), height=270,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            bargap=0.35,
        )
        st.plotly_chart(fig_bar, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🎯 Fraud by Category (Session)</div>', unsafe_allow_html=True)

        # Dynamic pie from session alerts instead of hardcoded
        session_alerts = st.session_state.alerts
        if session_alerts:
            cat_counts = {}
            for a in session_alerts:
                cat = a.get("merchant_category", "unknown")
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            pie_labels = list(cat_counts.keys())
            pie_vals = list(cat_counts.values())
        else:
            pie_labels = ["Late-Night\nHigh Value", "Device +\nGeo Jump",
                          "Velocity\nAttack",       "Social\nEngineering"]
            pie_vals   = [30, 30, 25, 15]

        pie_colors = ["#ff6b6b", "#ff8c42", "#ffdb4d", "#4a7aff",
                      "#00c897", "#9b59b6", "#e74c8b", "#3498db",
                      "#1abc9c", "#f39c12"]

        fig_pie = go.Figure(go.Pie(
            labels=pie_labels, values=pie_vals,
            marker_colors=pie_colors[:len(pie_labels)],
            textinfo="label+percent",
            hole=0.5,
            textfont=dict(color="#e8eaf6", size=11, family="Inter"),
            pull=[0.02] * len(pie_labels),
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#b0b8cc", family="Inter"), height=270,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Row 2 — Risk score distribution
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Risk Score Distribution (Current Session)</div>', unsafe_allow_html=True)
    session_txns = st.session_state.transactions
    if session_txns:
        scores_all = [t["risk_score"] for t in session_txns]
        fig_hist = px.histogram(
            x=scores_all, nbins=25,
            color_discrete_sequence=["#4a7aff"],
            labels={"x": "Risk Score (0–100)", "count": "Count"},
        )
        fig_hist.add_vline(x=FRAUD_THRESHOLD, line_dash="dash", line_color="#ff6b6b",
                            annotation_text=f"Threshold ({FRAUD_THRESHOLD:.0f})",
                            annotation_font_color="#ff6b6b",
                            annotation_font=dict(size=12, family="Inter"))
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#b0b8cc", family="Inter"), height=240,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, range=[0, 100]),
            yaxis=dict(showgrid=False),
            bargap=0.1,
        )
        st.plotly_chart(fig_hist, width="stretch")
    else:
        st.info("Add transactions to see risk score distribution.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Row 3 — Fraud heatmap (Hour × Amount bracket)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🔥 Fraud Heatmap — Hour of Day vs Amount Bracket</div>', unsafe_allow_html=True)
    rng = np.random.default_rng(seed=7)
    heat_hour_weights = np.array([
        0.010,0.008,0.006,0.005,0.005,0.010,
        0.020,0.030,0.045,0.065,0.070,0.075,
        0.075,0.070,0.065,0.060,0.055,0.055,
        0.050,0.045,0.040,0.035,0.025,0.015,
    ], dtype=float)
    heat_hour_weights /= heat_hour_weights.sum()
    sim_hours = rng.choice(range(24), 1500, p=heat_hour_weights)
    sim_amounts = np.where(
        np.isin(sim_hours, [0, 1, 2, 3, 4]),
        rng.uniform(15_000, 90_000, 1500),
        np.clip(rng.lognormal(5.5, 1.0, 1500), 10, 150_000),
    )
    amt_bins = pd.cut(
        sim_amounts,
        bins=[0, 500, 2_000, 10_000, 30_000, 200_000],
        labels=["< ₹500", "₹500–2K", "₹2K–10K", "₹10K–30K", "> ₹30K"],
    )
    heat_df = pd.crosstab(sim_hours, amt_bins)

    fig_heat = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.astype(str),
        y=heat_df.index,
        colorscale=[[0, "#0d1525"], [0.25, "#1a2845"],
                    [0.5, "#4a7aff"],  [0.75, "#ff8c42"], [1.0, "#ff4b4b"]],
        showscale=True,
        colorbar=dict(tickfont=dict(color="#6a7290", family="Inter")),
    ))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b0b8cc", family="Inter"), height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="Amount Bracket",
        yaxis_title="Hour of Day",
    )
    st.plotly_chart(fig_heat, width="stretch")
    st.caption("Heatmap based on synthetic training distribution — "
               "shows concentration of fraudulent transactions in late-night high-value brackets.")
    st.markdown('</div>', unsafe_allow_html=True)
