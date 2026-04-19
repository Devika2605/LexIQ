import sys
import os
import json
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="LexIQ — Legal Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ─────────────────────────────────────────
for k, v in [
    ("messages", []),
    ("session_id", None),
    ("uploaded_file_name", None),
    ("scan_results", None),
    ("pending_question", None),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════
# GLOBAL STYLES
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --sidebar-bg:     #3D2814;
    --sidebar-active: #5C3D1E;
    --sidebar-hover:  #4A3020;
    --sidebar-text:   #F5EDE0;
    --sidebar-muted:  #9E8070;
    --bg:             #F2EDE6;
    --surface:        #FFFFFF;
    --border:         #E5DDD5;
    --border2:        #CEC5BA;
    --text:           #1C1410;
    --text2:          #6B5F55;
    --text3:          #A09285;
    --brown:          #5C3D1E;
    --brown-dk:       #3D2814;
    --brown-lt:       #7B5230;
    --brown-bg:       #F5EDE0;
    --red:            #C0392B;
    --red-bg:         #FDF0EE;
    --amber:          #B7770D;
    --amber-bg:       #FFFBF0;
    --green:          #1A7A4A;
    --green-bg:       #EDF7F2;
    --radius:         10px;
    --shadow:         0 1px 3px rgba(0,0,0,0.08),0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:      0 4px 16px rgba(0,0,0,0.10),0 2px 4px rgba(0,0,0,0.05);
}

*, *::before, *::after { box-sizing: border-box; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

.stApp { background: var(--bg) !important; font-family: 'DM Sans', sans-serif !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    width: 240px !important;
    min-width: 240px !important;
    border-right: none !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.12) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    background: var(--sidebar-bg) !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] * { color: var(--sidebar-muted) !important; font-family: 'DM Sans', sans-serif !important; }
section[data-testid="stSidebar"] ::-webkit-scrollbar { width: 0; }

/* ════════════════════════════════════════
   TOPBAR
════════════════════════════════════════ */
.lex-topbar {
    position: sticky; top: 0;
    background: #fff;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center;
    padding: 0 24px; height: 60px; gap: 14px;
    z-index: 99;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.lex-search-box {
    flex: 1; max-width: 420px;
    display: flex; align-items: center; gap: 7px;
    height: 36px; background: #F7F3EF;
    border: 1px solid var(--border); border-radius: 8px;
    padding: 0 10px;
    color: var(--text3); font-size: 0.83rem; font-family: 'DM Sans', sans-serif;
}
.lex-search-kbd {
    margin-left: auto; font-family: 'DM Mono', monospace;
    font-size: 0.66rem; background: #EDE8E2;
    color: var(--text3); border-radius: 4px; padding: 1px 5px;
}
.lex-topbar-right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
.lex-icon-btn {
    width: 34px; height: 34px; border: 1px solid var(--border);
    border-radius: 8px; background: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; cursor: pointer; color: var(--text2);
}
.lex-user-chip { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.lex-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #7B5230, #3D2814);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    color: white !important; font-size: 0.74rem; font-weight: 700;
}
.lex-user-name { font-size: 0.82rem; font-weight: 600; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
.lex-user-plan { font-size: 0.68rem; color: var(--text3) !important; }

/* ════════════════════════════════════════
   TABS
════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important; padding: 0 !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--text3) !important;
    border-radius: 0 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important; font-weight: 500 !important;
    padding: 10px 18px !important; border: none !important;
    border-bottom: 2px solid transparent !important; margin-bottom: -1px !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important; color: var(--brown) !important;
    font-weight: 700 !important; border-bottom: 2px solid var(--brown) !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 20px 0 0 0 !important; }

/* ════════════════════════════════════════
   CHAT INPUT
════════════════════════════════════════ */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stChatInput"] {
    background: var(--surface) !important; border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important; box-shadow: var(--shadow) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--brown-lt) !important;
    box-shadow: 0 0 0 3px rgba(92,61,30,0.08) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text) !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important; background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text3) !important; }

/* ════════════════════════════════════════
   CHAT MESSAGE STYLES
════════════════════════════════════════ */
.chat-msg-user {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 14px 0; border-bottom: 1px solid var(--border);
}
.chat-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: var(--brown-dk); color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
}
.chat-q-text { font-size: 0.87rem; color: var(--text); line-height: 1.6; padding-top: 4px; }

/* ════════════════════════════════════════
   RESULT CARD
════════════════════════════════════════ */
.result-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden;
    box-shadow: var(--shadow); margin: 4px 0 16px;
}
.result-card-top {
    display: flex; align-items: center; gap: 8px;
    background: #FAFAF8; border-bottom: 1px solid var(--border);
    padding: 9px 14px; font-size: 0.77rem; color: var(--text2);
}
.risk-pill {
    display: inline-flex; align-items: center; gap: 5px;
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.71rem; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
}
.rp-high   { background: #FEF2F2; color: #DC2626 !important; border: 1px solid #FECACA; }
.rp-medium { background: #FFFBEB; color: #D97706 !important; border: 1px solid #FDE68A; }
.rp-low    { background: #F0FDF4; color: #16A34A !important; border: 1px solid #BBF7D0; }
.risk-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.rd-high { background: #DC2626; }
.rd-medium { background: #D97706; }
.rd-low { background: #16A34A; }
.result-body { padding: 16px 16px 12px; }
.result-assess-row {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    font-size: 0.8rem; font-weight: 700; color: var(--text); margin-bottom: 12px;
}
.result-assess-sub { font-size: 0.71rem; color: var(--text3); font-weight: 400; }
.sources-section { border-top: 1px solid var(--border); padding: 12px 16px; }
.sources-hd { display: flex; align-items: center; justify-content: space-between; font-size: 0.77rem; font-weight: 600; color: var(--text2); margin-bottom: 9px; }
.source-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.source-chip {
    display: flex; align-items: center; gap: 6px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 6px; padding: 4px 9px; font-size: 0.69rem; color: var(--text2);
}

/* ════════════════════════════════════════
   BUTTONS (main area)
════════════════════════════════════════ */
.stButton button {
    background: var(--brown-dk) !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 0.82rem !important; box-shadow: var(--shadow) !important;
    transition: all 0.14s !important; padding: 10px 18px !important;
}
.stButton button:hover {
    background: var(--brown-lt) !important; transform: translateY(-1px) !important;
    box-shadow: var(--shadow-md) !important;
}
.btn-outline .stButton button {
    background: var(--surface) !important; color: var(--text2) !important;
    border: 1px solid var(--border) !important;
}
.btn-outline .stButton button:hover {
    background: var(--bg) !important; color: var(--text) !important;
    transform: none !important; box-shadow: none !important;
}
.btn-danger .stButton button {
    background: var(--surface) !important; color: #DC2626 !important;
    border: 1px solid #FECACA !important;
}
.btn-danger .stButton button:hover {
    background: #FEF2F2 !important; transform: none !important; box-shadow: none !important;
}
.chip-btn .stButton button {
    background: var(--surface) !important; color: var(--text2) !important;
    border: 1px solid var(--border) !important; font-weight: 500 !important;
    font-size: 0.81rem !important; padding: 9px 14px !important;
}
.chip-btn .stButton button:hover {
    background: var(--brown-bg) !important; color: var(--brown) !important;
    border-color: var(--border2) !important; transform: none !important; box-shadow: none !important;
}

/* ════════════════════════════════════════
   RIGHT PANEL
════════════════════════════════════════ */
.panel-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden;
    box-shadow: var(--shadow); margin-bottom: 14px;
}
.panel-card-head {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 16px; border-bottom: 1px solid var(--border);
}
.panel-icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: var(--brown-bg);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}
.panel-title { font-family: 'Lora', serif; font-size: 0.95rem; font-weight: 600; color: var(--text) !important; }
.panel-body { padding: 14px 16px; }
.panel-desc { font-size: 0.79rem; color: var(--text2); line-height: 1.5; margin-bottom: 12px; }
.panel-label {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; color: var(--text3); margin-bottom: 8px;
    display: flex; align-items: center; justify-content: space-between;
}
.file-chip {
    display: flex; align-items: center; gap: 9px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 8px 12px; margin-bottom: 10px;
}
.file-chip-name { font-size: 0.79rem; font-weight: 600; color: var(--text); flex: 1; }
.file-chip-size { font-size: 0.68rem; color: var(--text3); }
.session-row { font-size: 0.81rem; color: var(--text2); margin-bottom: 5px; }
.session-row strong { color: var(--text) !important; }
.session-id { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--brown-lt) !important; }
.view-all {
    font-size: 0.78rem; font-weight: 600; color: var(--brown-lt);
    margin-top: 8px; cursor: pointer; display: flex; align-items: center; gap: 4px;
}
.q-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0; border-bottom: 1px solid var(--border);
    font-size: 0.81rem; color: var(--text); cursor: pointer;
}
.q-item:last-child { border-bottom: none; }

/* Override button styles inside the panel Q card specifically */
.qs-panel .stButton button {
    background: transparent !important; color: var(--text) !important;
    border: none !important; border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important; text-align: left !important;
    padding: 10px 0 !important; font-weight: 400 !important;
    font-size: 0.81rem !important; box-shadow: none !important; width: 100% !important;
}
.qs-panel .stButton button:hover {
    background: transparent !important; color: var(--brown-lt) !important;
    transform: none !important; box-shadow: none !important;
}

/* ════════════════════════════════════════
   SCAN + EVAL
════════════════════════════════════════ */
.scan-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin: 14px 0; }
.scan-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px 10px; text-align: center; }
.scan-num { font-size: 1.5rem; font-weight: 700; color: var(--text); line-height: 1; }
.scan-lbl { font-size: 0.66rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px; }

.eval-tbl { width: 100%; border-collapse: collapse; font-size: 0.81rem; }
.eval-tbl th { background: #FAFAF8; color: var(--text3); font-size: 0.67rem; text-transform: uppercase; letter-spacing: 0.07em; padding: 10px 13px; text-align: left; border-bottom: 1px solid var(--border); font-weight: 600; }
.eval-tbl td { padding: 10px 13px; color: var(--text); border-bottom: 1px solid var(--border); }
.eval-tbl tr:hover td { background: #FAFAF8; }
.eval-tbl tr.best-row td { background: #F0FDF4; }
.eval-tbl .mono { font-family: 'DM Mono', monospace; }
.eval-tbl .best-val { color: #16A34A; font-weight: 700; }
.chip-strategy { background: var(--brown-bg); color: var(--brown); border: 1px solid #DDD0BE; border-radius: 5px; padding: 2px 8px; font-size: 0.71rem; font-weight: 600; }

/* ════════════════════════════════════════
   MISC
════════════════════════════════════════ */
.stAlert { background: var(--bg) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; font-family: 'DM Sans', sans-serif !important; }
.stSpinner > div { border-top-color: var(--brown-lt) !important; }
[data-testid="stMetricValue"] { font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; color: var(--text) !important; }
[data-testid="stMetricLabel"] { font-family: 'DM Sans', sans-serif !important; color: var(--text3) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
details summary {
    background: #FAFAF8 !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text2) !important;
    font-size: 0.79rem !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
}
[data-testid="stFileUploader"] {
    background: var(--bg) !important; border: 1.5px dashed var(--border2) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SIDEBAR  (Streamlit native)
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 16px 16px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:8px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:38px;height:38px;background:#7B5230;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">⚖️</div>
            <div>
                <div style="font-family:'Lora',serif;font-size:1.2rem;color:#F5EDE0 !important;font-weight:600;line-height:1.1;">LexIQ</div>
                <div style="font-size:0.6rem;color:#9E8070 !important;margin-top:1px;line-height:1.3;">Legal Intelligence for Indian SMBs</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("", "Dashboard", True),
        ("", "Ask LexIQ", False, True),   # last bool = show dot
        ("", "Contract Scanner", False, False),
        ("", "Eval Results", False, False),
        ("", "Document Library", False, False),
    ]

    for item in nav_items:
        icon, label, active = item[0], item[1], item[2]
        dot = item[3] if len(item) > 3 else False
        dot_html = '<span style="width:7px;height:7px;background:#E86C3A;border-radius:50%;margin-left:auto;display:inline-block;"></span>' if dot else ""
        bg = "#281B0D" if active else "transparent"
        col = "#F5EDE0" if active else "#9E8070"
        fw = "600" if active else "500"
        st.markdown(f"""
        <div style="background:{bg};display:flex;align-items:center;gap:9px;padding:9px 12px;border-radius:8px;
                    font-size:0.83rem;font-family:'DM Sans',sans-serif;cursor:pointer;margin-bottom:1px;">
            <span style="font-size:0.95rem;width:18px;text-align:center;color:{col} !important;">{icon}</span>
            <span style="color:{col} !important;font-weight:{fw};">{label}</span>
            {dot_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.07);margin:10px 0;"></div>', unsafe_allow_html=True)

    # Clickable quick questions
    st.markdown('<div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#9E8070 !important;padding:0 12px;margin-bottom:4px;">Quick Questions</div>', unsafe_allow_html=True)
    sidebar_qs = [
        "Penalty for breach of contract?",
        "MSME 45-day payment rule?",
        "GST invoice fields?",
        "What is force majeure?",
        "Void vs voidable contract?",
    ]
    for q in sidebar_qs:
        if st.button(q, key=f"sb_{q}"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.07);margin:10px 0;"></div>', unsafe_allow_html=True)

    # Upgrade card
    st.markdown("""
    <div style="margin:0 6px 8px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:14px;">
        <div style="width:30px;height:30px;background:#7B5230;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;margin-bottom:9px;">👑</div>
        <div style="font-size:0.82rem;font-weight:700;color:#F5EDE0 !important;margin-bottom:3px;">Upgrade to Pro</div>
        <div style="font-size:0.71rem;color:#9E8070 !important;line-height:1.5;margin-bottom:10px;">Unlock advanced analysis, bulk uploads, and priority support.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Upgrade Now →", key="upgrade_btn"):
        pass

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.07);margin:8px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:8px;padding:10px 14px;font-size:0.79rem;color:#9E8070 !important;cursor:pointer;">🎧 <span style="color:#9E8070 !important;">Support</span> <span style="margin-left:auto;color:#9E8070 !important;">›</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════

# Handle pending question
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.messages.append({"role": "user", "content": q})


# Content columns
col_center, col_right = st.columns([2.7, 1], gap="medium")

# ── CENTER ────────────────────────────────────────────────
with col_center:
    st.markdown('<div style="padding:24px 4px 24px 20px;">', unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:20px;gap:12px;">
        <div>
            <div style="font-family:'Lora',serif;font-size:1.5rem;font-weight:600;color:#1C1410;letter-spacing:-0.02em;line-height:1.2;">Ask a Legal Question</div>
            <div style="font-size:0.79rem;color:#A09285;margin-top:4px;">Get instant, accurate answers backed by Indian law.</div>
        </div>
        <button style="display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid #E5DDD5;border-radius:8px;padding:7px 14px;font-size:0.78rem;font-weight:500;color:#6B5F55;white-space:nowrap;cursor:pointer;font-family:'DM Sans',sans-serif;margin-top:4px;">▷ How it works</button>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.uploaded_file_name:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;background:#fff;border:1px solid #E5DDD5;border-radius:10px;padding:10px 14px;font-size:0.81rem;color:#6B5F55;margin-bottom:18px;">
            📄 Contract loaded: <strong style="color:#1C1410;">{st.session_state.uploaded_file_name}</strong>
            — questions will reference this contract AND the legal corpus.
        </div>
        """, unsafe_allow_html=True)

    tab_chat, tab_scan, tab_eval = st.tabs(["💬 Ask LexIQ", "🔍 Contract Scanner", "📊 Eval Results"])

    # ── CHAT TAB ─────────────────────────────────────────
    with tab_chat:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align:center;padding:40px 0 24px;">
                <div style="width:52px;height:52px;background:#fff;border:1px solid #E5DDD5;border-radius:13px;display:inline-flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,0.07);">⚖️</div>
                <div style="font-family:'Lora',serif;font-size:1.3rem;color:#1C1410;margin-bottom:6px;">How can I help you today?</div>
                <div style="font-size:0.8rem;color:#A09285;max-width:340px;margin:0 auto 26px;line-height:1.6;">Ask about contracts, laws, or upload your contract for detailed risk analysis.</div>
            </div>
            """, unsafe_allow_html=True)

            chips = [
                "Penalty for breach of contract?", "MSME delayed payment rule?",
                "GST invoice mandatory fields?", "Force majeure explained",
                "Void vs voidable contract?", "NDA obligations in India",
            ]
            c1, c2 = st.columns(2)
            for i, chip in enumerate(chips):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                    if st.button(chip, key=f"chip_{i}"):
                        st.session_state.pending_question = chip
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-msg-user">
                    <div class="chat-avatar">A</div>
                    <div class="chat-q-text">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                rl = msg.get("risk_level", "LOW")
                rp_cls = {"HIGH": "rp-high", "MEDIUM": "rp-medium", "LOW": "rp-low"}.get(rl, "rp-low")
                rd_cls = {"HIGH": "rd-high", "MEDIUM": "rd-medium", "LOW": "rd-low"}.get(rl, "rd-low")

                sources_html = ""
                if msg.get("sources"):
                    cmap = {"HIGH": "#DC2626", "MEDIUM": "#D97706", "LOW": "#16A34A"}
                    chips_html = "".join([
                        f'<div class="source-chip"><span style="width:8px;height:8px;border-radius:50%;background:{cmap.get(s.get("risk","LOW"),"#A09285")};flex-shrink:0;display:inline-block;"></span>{s.get("filename","?")} — p{s.get("page","?")}</div>'
                        for s in msg["sources"]
                    ])
                    sources_html = f'<div class="sources-section"><div class="sources-hd"><span>📖 Sources Used</span><span style="color:#A09285;cursor:pointer;">∧</span></div><div class="source-grid">{chips_html}</div></div>'

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-card-top">📊 Result: <span class="risk-pill {rp_cls}"><span class="risk-dot {rd_cls}" style="display:inline-block;"></span>{rl} RISK</span></div>
                    <div class="result-body">
                        <div class="result-assess-row">
                            Risk Assessment: <span class="risk-pill {rp_cls}">⚠️ {rl} RISK</span>
                            <span class="result-assess-sub">These clauses can expose the business to significant liability if not properly addressed.</span>
                        </div>
                        <div style="font-size:0.84rem;color:#1C1410;line-height:1.75;">{msg["content"]}</div>
                    </div>
                    {sources_html}
                </div>
                """, unsafe_allow_html=True)

                if msg.get("no_rag_answer"):
                    with st.expander("Without RAG (baseline)", expanded=False):
                        st.markdown(f'<div style="font-size:0.79rem;color:#6B5F55;line-height:1.6;background:#FAFAF8;border-radius:8px;padding:12px;">{msg["no_rag_answer"][:600]}...</div>', unsafe_allow_html=True)

        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            question = st.session_state.messages[-1]["content"]
            with st.spinner("Searching legal corpus..."):
                try:
                    resp   = requests.post(f"{API_URL}/query", json={"question": question, "session_id": st.session_state.session_id, "strategy": "clause", "top_k": 5}, timeout=60)
                    result = resp.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result.get("answer", "Error."),
                        "sources": result.get("sources", []),
                        "risk_level": result.get("risk_level", "LOW"),
                        "risk_emoji": result.get("risk_emoji", "🟢"),
                        "no_rag_answer": result.get("no_rag_answer", ""),
                    })
                    st.rerun()
                except requests.exceptions.ConnectionError:
                    st.error("❌ API not running. Start with: `python api/main.py`")
                except Exception as e:
                    st.error(f"❌ {str(e)}")

        question = st.chat_input("Ask about Indian contracts, laws, or your uploaded document...")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

    # ── SCANNER TAB ───────────────────────────────────────
    with tab_scan:
        st.markdown('<div style="margin-bottom:14px;"><div style="font-family:\'Lora\',serif;font-size:1.05rem;color:#1C1410;margin-bottom:3px;">Contract Risk Scanner</div><div style="font-size:0.77rem;color:#A09285;">Every clause classified automatically in seconds.</div></div>', unsafe_allow_html=True)

        if not st.session_state.session_id:
            st.markdown('<div style="background:#FFFBF0;border:1px solid #FDE68A;border-radius:10px;padding:22px;text-align:center;"><div style="font-size:1.4rem;margin-bottom:8px;">📂</div><div style="font-size:0.88rem;font-weight:600;color:#1C1410;">Upload a contract first</div><div style="font-size:0.77rem;color:#A09285;margin-top:3px;">Use the upload panel on the right →</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#EDF7F2;border:1px solid #BBF7D0;border-radius:8px;padding:9px 13px;margin-bottom:13px;font-size:0.81rem;color:#1A7A4A;font-weight:500;">✓ Ready: <strong>{st.session_state.uploaded_file_name}</strong></div>', unsafe_allow_html=True)
            if st.button("🔍 Scan All Clauses"):
                with st.spinner("Analysing clauses..."):
                    try:
                        resp = requests.post(f"{API_URL}/scan", json={"session_id": st.session_state.session_id}, timeout=60)
                        st.session_state.scan_results = resp.json()
                    except Exception as e:
                        st.error(f"❌ {str(e)}")

            if st.session_state.scan_results:
                scan = st.session_state.scan_results
                overall = scan.get("overall_risk", "LOW")
                emoji   = scan.get("overall_emoji", "🟢")
                summary = scan.get("summary", {})
                rp_cls  = {"HIGH": "rp-high", "MEDIUM": "rp-medium", "LOW": "rp-low"}.get(overall, "rp-low")
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #E5DDD5;border-radius:10px;padding:18px;margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,0.07);">
                    <div style="font-size:0.67rem;text-transform:uppercase;letter-spacing:0.08em;color:#A09285;margin-bottom:8px;">Overall Assessment</div>
                    <span class="risk-pill {rp_cls}" style="font-size:0.78rem;padding:4px 14px;">{emoji} {overall} Risk Contract</span>
                    <div class="scan-grid">
                        <div class="scan-card"><div class="scan-num">{summary.get('total_clauses',0)}</div><div class="scan-lbl">Total</div></div>
                        <div class="scan-card" style="border-left:3px solid #DC2626;"><div class="scan-num" style="color:#DC2626;">{summary.get('high_risk',0)}</div><div class="scan-lbl">High</div></div>
                        <div class="scan-card" style="border-left:3px solid #D97706;"><div class="scan-num" style="color:#D97706;">{summary.get('medium_risk',0)}</div><div class="scan-lbl">Medium</div></div>
                        <div class="scan-card" style="border-left:3px solid #16A34A;"><div class="scan-num" style="color:#16A34A;">{summary.get('low_risk',0)}</div><div class="scan-lbl">Low</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                for label, color, key in [("🔴 High Risk Clauses", "#DC2626", "high_risk_clauses"), ("🟡 Medium Risk Clauses", "#D97706", "medium_risk_clauses"), ("🟢 Low Risk Clauses", "#16A34A", "low_risk_clauses")]:
                    clauses = scan.get(key, [])
                    if clauses:
                        st.markdown(f'<div style="font-size:0.81rem;font-weight:600;color:{color};margin:16px 0 7px;">{label}</div>', unsafe_allow_html=True)
                        show = clauses[:5] if key == "low_risk_clauses" else clauses
                        for c in show:
                            with st.expander(f"Clause {c['clause_number']} — p.{c['page']}"):
                                st.markdown(f'<div style="font-size:0.79rem;color:#6B5F55;line-height:1.6;">{c["text"]}</div>', unsafe_allow_html=True)
                        if key == "low_risk_clauses" and len(clauses) > 5:
                            st.markdown(f'<div style="font-size:0.74rem;color:#A09285;">+ {len(clauses)-5} more low risk clauses</div>', unsafe_allow_html=True)

    # ── EVAL TAB ──────────────────────────────────────────
    with tab_eval:
        st.markdown('<div style="margin-bottom:14px;"><div style="font-family:\'Lora\',serif;font-size:1.05rem;color:#1C1410;margin-bottom:3px;">Evaluation Results</div><div style="font-size:0.77rem;color:#A09285;">9 experiments · 51 questions · 4 metrics.</div></div>', unsafe_allow_html=True)

        if st.button("Load Results"):
            try:
                resp    = requests.get(f"{API_URL}/results", timeout=10)
                results = resp.json().get("experiments", [])
                if results:
                    best_faith = max(r["faithfulness"] for r in results)
                    rows = ""
                    for r in results:
                        is_best = r["faithfulness"] == best_faith
                        vc = "best-val mono" if is_best else "mono"
                        rc = "best-row" if is_best else ""
                        star = " ★" if is_best else ""
                        rows += f'<tr class="{rc}"><td><span class="chip-strategy">{r["strategy"]}</span></td><td style="color:#6B5F55;">{r["retriever"]}</td><td class="{vc}">{r["faithfulness"]:.4f}{star}</td><td class="mono">{r["answer_relevancy"]:.4f}</td><td class="mono">{r["context_precision"]:.4f}</td><td class="mono">{r["context_recall"]:.4f}</td></tr>'
                    st.markdown(f'<div style="background:#fff;border:1px solid #E5DDD5;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.07);margin-bottom:18px;"><table class="eval-tbl"><thead><tr><th>Chunking</th><th>Retriever</th><th>Faithfulness</th><th>Ans. Rel.</th><th>Ctx. Prec.</th><th>Ctx. Rec.</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
                    best  = max(results, key=lambda x: x["faithfulness"])
                    worst = min(results, key=lambda x: x["faithfulness"])
                    impr  = ((best["faithfulness"] - worst["faithfulness"]) / max(worst["faithfulness"], 0.001)) * 100
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("Best Config", f"{best['strategy']} + {best['retriever']}", f"↑ {best['faithfulness']:.3f}")
                    with c2: st.metric("Worst Config", f"{worst['strategy']} + {worst['retriever']}", f"↓ {worst['faithfulness']:.3f}")
                    with c3: st.metric("Improvement", f"{impr:.1f}%", "worst → best")
                    import pandas as pd
                    df = pd.DataFrame({"Config": [f"{r['strategy']}+{r['retriever']}" for r in results], "Faithfulness": [r["faithfulness"] for r in results]}).set_index("Config")
                    st.bar_chart(df)
                else:
                    st.info("No results yet. Run `python evaluation/ragas_eval.py` first.")
            except requests.exceptions.ConnectionError:
                st.error("❌ API not running.")
            except Exception as e:
                st.error(f"❌ {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)


# ── RIGHT PANEL ───────────────────────────────────────────
with col_right:
    st.markdown('<div style="padding:24px 16px 24px 4px;">', unsafe_allow_html=True)

    # Upload card
    st.markdown("""
    <div class="panel-card">
        <div class="panel-card-head">
            <div class="panel-icon">📄</div>
            <div class="panel-title">Upload Your Contract</div>
        </div>
        <div class="panel-body">
            <div class="panel-desc">Upload a PDF contract to get cross-referenced analysis against Indian law.</div>
            <div class="panel-label">Choose a PDF contract <span>ℹ️</span></div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("PDF contract", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        sz = round(len(uploaded.getvalue()) / 1024, 1)
        st.markdown(f"""
        <div class="file-chip">
            <span style="font-size:1rem;">📄</span>
            <span class="file-chip-name">{uploaded.name}</span>
            <span class="file-chip-size">{sz}KB</span>
            <span style="color:#A09285;cursor:pointer;">✕</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚙️ Process Contract", key="process_btn"):
            with st.spinner("Parsing PDF..."):
                try:
                    files  = {"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
                    resp   = requests.post(f"{API_URL}/upload", files=files, timeout=120)
                    result = resp.json()
                    if resp.status_code == 200:
                        st.session_state.session_id         = result["session_id"]
                        st.session_state.uploaded_file_name = result["filename"]
                        st.session_state.scan_results       = None
                        st.success(f"✓ {result['pages']} pages · {result['chunks']} chunks")
                        st.rerun()
                    else:
                        st.error(result.get("detail", "Upload failed"))
                except requests.exceptions.ConnectionError:
                    st.error("❌ Start API: `python api/main.py`")
                except Exception as e:
                    st.error(f"❌ {str(e)}")

    st.markdown('</div></div>', unsafe_allow_html=True)

    # Active session card
    if st.session_state.session_id:
        st.markdown(f"""
        <div class="panel-card">
            <div class="panel-card-head">
                <div class="panel-icon">🔗</div>
                <div class="panel-title">Active Session</div>
            </div>
            <div class="panel-body">
                <div class="session-row">File: <strong>{st.session_state.uploaded_file_name}</strong></div>
                <div class="session-row">Session ID: <span class="session-id">{st.session_state.session_id[:12]}...</span></div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="btn-danger" style="margin-top:10px;">', unsafe_allow_html=True)
        if st.button("🗑 Clear Contract", key="clear_btn"):
            try:
                requests.delete(f"{API_URL}/session/{st.session_state.session_id}", timeout=10)
            except Exception:
                pass
            st.session_state.session_id = None
            st.session_state.uploaded_file_name = None
            st.session_state.scan_results = None
            st.rerun()
        st.markdown('</div></div></div>', unsafe_allow_html=True)

    # Try These Questions card
    st.markdown("""
    <div class="panel-card">
        <div class="panel-card-head">
            <div class="panel-icon">💡</div>
            <div class="panel-title">Try These Questions</div>
        </div>
        <div class="panel-body" style="padding:0 16px 2px;">
    """, unsafe_allow_html=True)

    st.markdown('<div class="qs-panel">', unsafe_allow_html=True)
    panel_qs = [
        "What is the penalty for breach of contract?",
        "How many days to pay an MSME supplier?",
        "What are the GST invoice requirements?",
        "Explain force majeure clause",
        "What makes a contract void in India?",
    ]
    for q in panel_qs:
        if st.button(q, key=f"pq_{q}"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        </div>
        <div style="padding:4px 16px 14px;">
            <div class="view-all">View all questions →</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)