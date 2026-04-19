import sys
import os
import json
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

# ── Config ────────────────────────────────────────────────
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title = "LexIQ — Legal Intelligence",
    page_icon  = "⚖️",
    layout     = "wide",
    initial_sidebar_state = "collapsed",
)

# ── Dark Glassmorphism CSS ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background: #050810;
    background-image:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(67, 113, 203, 0.15) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(139, 92, 246, 0.10) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(16, 185, 129, 0.04) 0%, transparent 70%);
    font-family: 'Sora', sans-serif;
    min-height: 100vh;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }
section[data-testid="stSidebar"] { display: none; }

/* ── Top Navigation Bar ── */
.lexiq-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 36px;
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 100;
    margin-bottom: 24px;
}

.lexiq-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.lexiq-logo-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #4371CB, #8B5CF6);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 20px rgba(67, 113, 203, 0.4);
}

.lexiq-logo-text {
    font-size: 1.4rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}

.lexiq-logo-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.4);
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ── Tab Pills ── */
.tab-pills {
    display: flex;
    gap: 4px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 4px;
}

.tab-pill {
    padding: 8px 20px;
    border-radius: 9px;
    font-size: 0.82rem;
    font-weight: 500;
    color: rgba(255,255,255,0.5);
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    background: transparent;
    font-family: 'Sora', sans-serif;
}

.tab-pill.active {
    background: linear-gradient(135deg, #4371CB, #8B5CF6);
    color: white;
    box-shadow: 0 2px 12px rgba(67,113,203,0.4);
}

/* ── Glass Cards ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    backdrop-filter: blur(20px);
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.glass-card:hover {
    border-color: rgba(67,113,203,0.3);
    box-shadow: 0 8px 32px rgba(67,113,203,0.08);
}

.glass-card-dark {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    backdrop-filter: blur(20px);
    padding: 24px;
    margin-bottom: 16px;
}

/* ── Section Headers ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}

.section-sub {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.4);
    margin-bottom: 20px;
    line-height: 1.5;
}

/* ── Chat Messages ── */
.chat-bubble-user {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
    justify-content: flex-end;
}

.chat-bubble-user .bubble {
    background: linear-gradient(135deg, rgba(67,113,203,0.3), rgba(139,92,246,0.2));
    border: 1px solid rgba(67,113,203,0.3);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    max-width: 80%;
    color: rgba(255,255,255,0.9);
    font-size: 0.88rem;
    line-height: 1.6;
}

.chat-bubble-ai {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 20px;
}

.ai-avatar {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #4371CB, #8B5CF6);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    box-shadow: 0 4px 16px rgba(67,113,203,0.3);
}

.chat-bubble-ai .bubble {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 18px 18px 18px;
    padding: 16px 20px;
    max-width: 90%;
    color: rgba(255,255,255,0.85);
    font-size: 0.88rem;
    line-height: 1.7;
    flex: 1;
}

/* ── Risk Badges ── */
.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-top: 10px;
}

.risk-high   { background: rgba(239,68,68,0.15);  border: 1px solid rgba(239,68,68,0.3);  color: #F87171; }
.risk-medium { background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); color: #FBBF24; }
.risk-low    { background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); color: #34D399; }

/* ── Source Pills ── */
.source-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.6);
    margin: 3px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Chat Input ── */
.stChatInput {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    color: white !important;
}

.stChatInput:focus {
    border-color: rgba(67,113,203,0.5) !important;
    box-shadow: 0 0 0 3px rgba(67,113,203,0.1) !important;
}

/* ── Upload Area ── */
.upload-area {
    border: 2px dashed rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
    background: rgba(255,255,255,0.02);
    transition: all 0.2s;
    cursor: pointer;
}

.upload-area:hover {
    border-color: rgba(67,113,203,0.4);
    background: rgba(67,113,203,0.04);
}

.upload-icon { font-size: 2rem; margin-bottom: 8px; }
.upload-title { font-size: 0.9rem; font-weight: 600; color: rgba(255,255,255,0.8); }
.upload-sub { font-size: 0.75rem; color: rgba(255,255,255,0.35); margin-top: 4px; }

/* ── Buttons ── */
.btn-primary {
    background: linear-gradient(135deg, #4371CB, #8B5CF6);
    border: none;
    border-radius: 12px;
    color: white;
    font-family: 'Sora', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 12px 24px;
    cursor: pointer;
    width: 100%;
    transition: all 0.2s;
    box-shadow: 0 4px 16px rgba(67,113,203,0.3);
    letter-spacing: 0.01em;
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(67,113,203,0.4);
}

.btn-secondary {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    color: rgba(255,255,255,0.7);
    font-family: 'Sora', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 9px 18px;
    cursor: pointer;
    width: 100%;
    text-align: left;
    transition: all 0.2s;
    margin-bottom: 6px;
}

.btn-secondary:hover {
    background: rgba(67,113,203,0.1);
    border-color: rgba(67,113,203,0.3);
    color: white;
}

/* ── Session Card ── */
.session-card {
    background: rgba(67,113,203,0.08);
    border: 1px solid rgba(67,113,203,0.2);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 16px;
}

.session-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(255,255,255,0.35);
    margin-bottom: 4px;
}

.session-value {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8);
    font-weight: 500;
}

.session-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #7CB9E8;
    background: rgba(124,185,232,0.1);
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-block;
    margin-top: 4px;
}

/* ── Risk Scanner ── */
.risk-summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 16px 0;
}

.risk-metric {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}

.risk-metric-num {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}

.risk-metric-label {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.clause-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.clause-item:hover {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.12);
}

.clause-item.high   { border-left: 3px solid #F87171; }
.clause-item.medium { border-left: 3px solid #FBBF24; }
.clause-item.low    { border-left: 3px solid #34D399; }

.clause-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.clause-num {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.35);
    font-family: 'JetBrains Mono', monospace;
}

.clause-text {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.65);
    line-height: 1.5;
}

/* ── Eval Table ── */
.eval-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    margin-top: 16px;
}

.eval-table th {
    background: rgba(67,113,203,0.15);
    color: rgba(255,255,255,0.6);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.eval-table td {
    padding: 10px 14px;
    color: rgba(255,255,255,0.75);
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.eval-table tr:hover td { background: rgba(255,255,255,0.02); }
.eval-table tr.best td { background: rgba(16,185,129,0.06); }
.eval-table .score { font-family: 'JetBrains Mono', monospace; font-weight: 500; }
.eval-table .best-score { color: #34D399; font-weight: 700; }

/* ── Streamlit overrides ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(255,255,255,0.45) !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    border: none !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4371CB, #8B5CF6) !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(67,113,203,0.35) !important;
}

.stFileUploader {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
}

.stButton button {
    background: linear-gradient(135deg, #4371CB, #8B5CF6) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 16px rgba(67,113,203,0.3) !important;
    transition: all 0.2s !important;
}

.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(67,113,203,0.4) !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: white !important;
    font-family: 'Sora', sans-serif !important;
}

[data-testid="stChatMessageContent"] {
    color: rgba(255,255,255,0.85) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.6) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.8rem !important;
}

/* Metric */
[data-testid="stMetricValue"] {
    color: white !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
}

[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.45) !important;
    font-family: 'Sora', sans-serif !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* Success / Info / Warning */
.stAlert {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.75) !important;
}

/* Spinner */
.stSpinner { color: #4371CB !important; }

/* General text */
p, li, span {
    color: rgba(255,255,255,0.75);
    font-family: 'Sora', sans-serif;
}

h1, h2, h3 {
    color: white;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────
if "messages"            not in st.session_state: st.session_state.messages            = []
if "session_id"          not in st.session_state: st.session_state.session_id          = None
if "uploaded_file_name"  not in st.session_state: st.session_state.uploaded_file_name  = None
if "scan_results"        not in st.session_state: st.session_state.scan_results        = None
if "active_tab"          not in st.session_state: st.session_state.active_tab          = "chat"


# ── Navbar ────────────────────────────────────────────────
st.markdown("""
<div class="lexiq-navbar">
    <div class="lexiq-logo">
        <div class="lexiq-logo-icon">⚖️</div>
        <div>
            <div class="lexiq-logo-text">LexIQ</div>
            <div class="lexiq-logo-sub">Legal Contract Intelligence for Indian SMBs</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Main Layout ───────────────────────────────────────────
col_main, col_side = st.columns([2.2, 1], gap="large")


# ══════════════════════════════════════════════════════════
# MAIN COLUMN
# ══════════════════════════════════════════════════════════
with col_main:

    tab_chat, tab_scan, tab_eval = st.tabs(["💬  Ask LexIQ", "🔍  Contract Scanner", "📊  Eval Results"])

    # ── TAB 1: CHAT ───────────────────────────────────────
    with tab_chat:
        st.markdown('<div class="section-title">Ask a Legal Question</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Get answers grounded in Indian contract law, GST rules, MSME regulations and more — with source citations and risk assessment.</div>', unsafe_allow_html=True)

        # Contract loaded banner
        if st.session_state.uploaded_file_name:
            st.markdown(f"""
            <div style="background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25);
                        border-radius: 12px; padding: 12px 16px; margin-bottom: 16px;
                        display: flex; align-items: center; gap: 10px;">
                <span style="font-size:1.2rem">📄</span>
                <div>
                    <div style="font-size:0.8rem; color: #34D399; font-weight:600;">Contract Loaded</div>
                    <div style="font-size:0.78rem; color:rgba(255,255,255,0.6);">
                        <b>{st.session_state.uploaded_file_name}</b> — questions reference this contract AND the legal corpus
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Chat history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])

                    # Risk badge
                    risk_level = msg.get("risk_level", "LOW")
                    risk_emoji = msg.get("risk_emoji", "🟢")
                    risk_class = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}.get(risk_level, "risk-low")
                    st.markdown(f'<span class="risk-badge {risk_class}">{risk_emoji} {risk_level} RISK</span>', unsafe_allow_html=True)

                    # Sources
                    if msg.get("sources"):
                        sources_html = "".join([
                            f'<span class="source-pill">📄 {s.get("filename","?")} · p{s.get("page","?")}</span>'
                            for s in msg["sources"]
                        ])
                        with st.expander("📚 Sources", expanded=False):
                            st.markdown(sources_html, unsafe_allow_html=True)

                    # No-RAG comparison
                    if msg.get("no_rag_answer"):
                        with st.expander("🔄 Without RAG (baseline)", expanded=False):
                            st.markdown(f'<div style="color:rgba(255,255,255,0.5); font-size:0.82rem; font-style:italic;">{msg["no_rag_answer"][:500]}...</div>', unsafe_allow_html=True)

        # ── Chat Input ────────────────────────────────────
        question = st.chat_input("Ask about Indian contracts, laws, or your uploaded document...")

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Searching legal corpus..."):
                    try:
                        payload = {
                            "question":   question,
                            "session_id": st.session_state.session_id,
                            "strategy":   "clause",
                            "top_k":      5,
                        }
                        resp   = requests.post(f"{API_URL}/query", json=payload, timeout=60)
                        result = resp.json()

                        answer     = result.get("answer", "Error getting answer.")
                        sources    = result.get("sources", [])
                        risk_level = result.get("risk_level", "LOW")
                        risk_emoji = result.get("risk_emoji", "🟢")
                        no_rag     = result.get("no_rag_answer", "")

                        st.markdown(answer)

                        risk_class = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}.get(risk_level, "risk-low")
                        st.markdown(f'<span class="risk-badge {risk_class}">{risk_emoji} {risk_level} RISK</span>', unsafe_allow_html=True)

                        if sources:
                            sources_html = "".join([
                                f'<span class="source-pill">📄 {s.get("filename","?")} · p{s.get("page","?")}</span>'
                                for s in sources
                            ])
                            with st.expander("📚 Sources Used", expanded=True):
                                st.markdown(sources_html, unsafe_allow_html=True)

                        if no_rag:
                            with st.expander("🔄 Without RAG (baseline)", expanded=False):
                                st.markdown(f'<div style="color:rgba(255,255,255,0.5); font-size:0.82rem; font-style:italic;">{no_rag[:500]}...</div>', unsafe_allow_html=True)

                        st.session_state.messages.append({
                            "role":          "assistant",
                            "content":       answer,
                            "sources":       sources,
                            "risk_level":    risk_level,
                            "risk_emoji":    risk_emoji,
                            "no_rag_answer": no_rag,
                        })

                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to LexIQ API. Make sure `python api/main.py` is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    # ── TAB 2: CONTRACT SCANNER ───────────────────────────
    with tab_scan:
        st.markdown('<div class="section-title">Automatic Contract Risk Scanner</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Upload a contract and every clause is automatically classified as HIGH, MEDIUM, or LOW risk — in seconds.</div>', unsafe_allow_html=True)

        if not st.session_state.session_id:
            st.markdown("""
            <div style="background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2);
                        border-radius: 14px; padding: 20px; text-align: center; margin-top: 20px;">
                <div style="font-size: 2rem; margin-bottom: 8px;">📄</div>
                <div style="font-size: 0.9rem; font-weight: 600; color: rgba(255,255,255,0.8);">No Contract Uploaded</div>
                <div style="font-size: 0.78rem; color: rgba(255,255,255,0.4); margin-top: 4px;">Upload a contract using the panel on the right to begin scanning</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2);
                        border-radius: 12px; padding: 12px 16px; margin-bottom: 20px;">
                <span style="color:#34D399; font-weight:600; font-size:0.82rem;">✓ Ready to scan:</span>
                <span style="color:rgba(255,255,255,0.7); font-size:0.82rem; margin-left:8px;">{st.session_state.uploaded_file_name}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔍 Scan All Clauses for Risk", type="primary"):
                with st.spinner("Analysing every clause..."):
                    try:
                        resp = requests.post(f"{API_URL}/scan", json={"session_id": st.session_state.session_id}, timeout=60)
                        st.session_state.scan_results = resp.json()
                    except Exception as e:
                        st.error(f"❌ Scan failed: {str(e)}")

            if st.session_state.scan_results:
                scan    = st.session_state.scan_results
                overall = scan.get("overall_risk", "LOW")
                emoji   = scan.get("overall_emoji", "🟢")
                summary = scan.get("summary", {})

                risk_class = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}.get(overall, "risk-low")

                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
                            border-radius: 18px; padding: 24px; margin: 16px 0;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em;
                                color:rgba(255,255,255,0.35); margin-bottom:8px;">Overall Contract Risk</div>
                    <span class="risk-badge {risk_class}" style="font-size:0.9rem; padding: 8px 20px;">
                        {emoji} {overall} RISK
                    </span>
                    <div style="display:grid; grid-template-columns: repeat(4,1fr); gap:12px; margin-top:20px;">
                        <div style="text-align:center; background:rgba(255,255,255,0.03); border-radius:12px; padding:14px;">
                            <div style="font-size:1.8rem; font-weight:800; color:white;">{summary.get('total_clauses',0)}</div>
                            <div style="font-size:0.7rem; color:rgba(255,255,255,0.35); text-transform:uppercase; letter-spacing:0.06em;">Total</div>
                        </div>
                        <div style="text-align:center; background:rgba(239,68,68,0.08); border-radius:12px; padding:14px;">
                            <div style="font-size:1.8rem; font-weight:800; color:#F87171;">{summary.get('high_risk',0)}</div>
                            <div style="font-size:0.7rem; color:rgba(248,113,113,0.6); text-transform:uppercase; letter-spacing:0.06em;">High Risk</div>
                        </div>
                        <div style="text-align:center; background:rgba(245,158,11,0.08); border-radius:12px; padding:14px;">
                            <div style="font-size:1.8rem; font-weight:800; color:#FBBF24;">{summary.get('medium_risk',0)}</div>
                            <div style="font-size:0.7rem; color:rgba(251,191,36,0.6); text-transform:uppercase; letter-spacing:0.06em;">Medium Risk</div>
                        </div>
                        <div style="text-align:center; background:rgba(16,185,129,0.08); border-radius:12px; padding:14px;">
                            <div style="font-size:1.8rem; font-weight:800; color:#34D399;">{summary.get('low_risk',0)}</div>
                            <div style="font-size:0.7rem; color:rgba(52,211,153,0.6); text-transform:uppercase; letter-spacing:0.06em;">Low Risk</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # High risk clauses
                high_clauses = scan.get("high_risk_clauses", [])
                if high_clauses:
                    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#F87171; margin:20px 0 10px;">🔴 High Risk Clauses</div>', unsafe_allow_html=True)
                    for clause in high_clauses:
                        with st.expander(f"Clause {clause['clause_number']} — Page {clause['page']}"):
                            st.markdown(f'<div style="font-size:0.82rem; color:rgba(255,255,255,0.7); line-height:1.6;">{clause["text"]}</div>', unsafe_allow_html=True)

                # Medium risk clauses
                med_clauses = scan.get("medium_risk_clauses", [])
                if med_clauses:
                    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FBBF24; margin:20px 0 10px;">🟡 Medium Risk Clauses</div>', unsafe_allow_html=True)
                    for clause in med_clauses:
                        with st.expander(f"Clause {clause['clause_number']} — Page {clause['page']}"):
                            st.markdown(f'<div style="font-size:0.82rem; color:rgba(255,255,255,0.7); line-height:1.6;">{clause["text"]}</div>', unsafe_allow_html=True)

                # Low risk
                low_clauses = scan.get("low_risk_clauses", [])
                if low_clauses:
                    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#34D399; margin:20px 0 10px;">🟢 Low Risk Clauses</div>', unsafe_allow_html=True)
                    for clause in low_clauses[:5]:
                        with st.expander(f"Clause {clause['clause_number']} — Page {clause['page']}"):
                            st.markdown(f'<div style="font-size:0.82rem; color:rgba(255,255,255,0.7); line-height:1.6;">{clause["text"]}</div>', unsafe_allow_html=True)
                    if len(low_clauses) > 5:
                        st.markdown(f'<div style="font-size:0.78rem; color:rgba(255,255,255,0.3); margin-top:8px;">...and {len(low_clauses)-5} more low risk clauses</div>', unsafe_allow_html=True)

    # ── TAB 3: EVAL RESULTS ───────────────────────────────
    with tab_eval:
        st.markdown('<div class="section-title">Evaluation Results</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">9-experiment ablation study across 3 chunking strategies × 3 retrieval methods. Measured on a hand-curated 51-question test set.</div>', unsafe_allow_html=True)

        if st.button("📊 Load Experiment Results"):
            try:
                resp    = requests.get(f"{API_URL}/results", timeout=10)
                results = resp.json().get("experiments", [])

                if results:
                    best_faith = max(r["faithfulness"] for r in results)

                    # Build table HTML
                    rows = ""
                    for r in results:
                        is_best   = r["faithfulness"] == best_faith
                        row_class = "best" if is_best else ""
                        star      = " ★" if is_best else ""
                        faith_cls = "best-score" if is_best else "score"
                        rows += f"""
                        <tr class="{row_class}">
                            <td><span style="background:rgba(67,113,203,0.15); padding:3px 10px; border-radius:6px; font-size:0.75rem; font-weight:600;">{r['strategy']}</span></td>
                            <td><span style="color:rgba(255,255,255,0.5);">{r['retriever']}</span></td>
                            <td class="{faith_cls}">{r['faithfulness']:.4f}{star}</td>
                            <td class="score">{r['answer_relevancy']:.4f}</td>
                            <td class="score">{r['context_precision']:.4f}</td>
                            <td class="score">{r['context_recall']:.4f}</td>
                        </tr>
                        """

                    st.markdown(f"""
                    <table class="eval-table">
                        <thead>
                            <tr>
                                <th>Chunking</th>
                                <th>Retriever</th>
                                <th>Faithfulness</th>
                                <th>Ans. Relevancy</th>
                                <th>Ctx. Precision</th>
                                <th>Ctx. Recall</th>
                            </tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                    """, unsafe_allow_html=True)

                    # Key metrics
                    best  = max(results, key=lambda x: x["faithfulness"])
                    worst = min(results, key=lambda x: x["faithfulness"])
                    impr  = ((best["faithfulness"] - worst["faithfulness"]) / max(worst["faithfulness"], 0.001)) * 100

                    st.markdown("<br>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Best Config", f"{best['strategy']} + {best['retriever']}", f"↑ {best['faithfulness']:.3f} faithfulness")
                    with c2:
                        st.metric("Worst Config", f"{worst['strategy']} + {worst['retriever']}", f"↓ {worst['faithfulness']:.3f} faithfulness")
                    with c3:
                        st.metric("Improvement", f"{impr:.1f}%", "worst → best config")

                    # Bar chart
                    st.markdown('<div style="margin-top:24px; font-size:0.85rem; font-weight:600; color:rgba(255,255,255,0.7); margin-bottom:8px;">Faithfulness by Configuration</div>', unsafe_allow_html=True)
                    import pandas as pd
                    chart_data = pd.DataFrame({
                        "Config":      [f"{r['strategy']}+{r['retriever']}" for r in results],
                        "Faithfulness": [r["faithfulness"] for r in results],
                    }).set_index("Config")
                    st.bar_chart(chart_data, color="#4371CB")

                else:
                    st.warning("No evaluation results found. Run `python evaluation/ragas_eval.py` first.")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API server.")
            except Exception as e:
                st.error(f"❌ Error loading results: {str(e)}")


# ══════════════════════════════════════════════════════════
# SIDE COLUMN
# ══════════════════════════════════════════════════════════
with col_side:

    # ── Upload Section ────────────────────────────────────
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">📄 Upload Your Contract</div>
        <div class="section-sub">Upload a PDF to get cross-referenced analysis against Indian law.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a PDF contract",
        type = ["pdf"],
        label_visibility = "collapsed",
    )

    if uploaded_file:
        if st.button("📤 Process Contract"):
            with st.spinner("Parsing and indexing..."):
                try:
                    files  = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    resp   = requests.post(f"{API_URL}/upload", files=files, timeout=120)
                    result = resp.json()

                    if resp.status_code == 200:
                        st.session_state.session_id         = result["session_id"]
                        st.session_state.uploaded_file_name = result["filename"]
                        st.session_state.scan_results       = None

                        st.markdown(f"""
                        <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25);
                                    border-radius:12px; padding:14px; margin-top:12px;">
                            <div style="color:#34D399; font-weight:600; font-size:0.82rem; margin-bottom:8px;">✓ Contract Processed</div>
                            <div style="font-size:0.78rem; color:rgba(255,255,255,0.55); line-height:1.8;">
                                📄 {result['filename']}<br>
                                📖 {result['pages']} pages<br>
                                🧩 {result['chunks']} chunks indexed
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Upload failed: {result.get('detail', 'Unknown error')}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ API not running. Start with `python api/main.py`")
                except Exception as e:
                    st.error(f"❌ {str(e)}")

    # ── Active Session ────────────────────────────────────
    if st.session_state.session_id:
        st.markdown(f"""
        <div class="session-card">
            <div class="session-label">Active Session</div>
            <div class="session-value">{st.session_state.uploaded_file_name}</div>
            <div class="session-id">{st.session_state.session_id}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Contract"):
            try:
                requests.delete(f"{API_URL}/session/{st.session_state.session_id}", timeout=10)
            except Exception:
                pass
            st.session_state.session_id         = None
            st.session_state.uploaded_file_name = None
            st.session_state.scan_results       = None
            st.rerun()

    st.markdown("---")

    # ── Sample Questions ──────────────────────────────────
    st.markdown('<div class="section-title">💡 Try These</div>', unsafe_allow_html=True)

    sample_questions = [
        "Penalty for breach of contract?",
        "MSME delayed payment interest rate?",
        "GST invoice mandatory fields?",
        "What is force majeure?",
        "How to void a contract in India?",
        "Non-compete clause enforceability?",
    ]

    for q in sample_questions:
        if st.button(q, key=f"sq_{q}"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()

    st.markdown("---")

    # ── About ─────────────────────────────────────────────
    with st.expander("ℹ️ About LexIQ"):
        st.markdown("""
        **LexIQ** is an AI-powered legal assistant for Indian SMBs built with a rigorous evaluation framework.

        **Corpus:** 38 documents — Indian Contract Act, GST Act, MSMED Act, 10+ contract templates.

        **Stack:** ChromaDB · BM25 · Llama 3.1 · Groq · FastAPI · Streamlit

        **Eval:** 9 experiments · 51 questions · 4 RAGAS-style metrics · 93% improvement from worst to best config.
        """)