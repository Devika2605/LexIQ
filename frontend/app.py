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
    ("active_nav", "Ask LexIQ"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════
# GLOBAL STYLES — Darker brown, refined light theme
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    /* Sidebar — deep espresso */
    --sb-bg:          #1E1108;
    --sb-active:      #2E1A0A;
    --sb-hover:       #261409;
    --sb-text:        #F0E6D6;
    --sb-muted:       #7A6350;
    --sb-border:      rgba(255,255,255,0.06);
    --sb-accent:      #C17E45;

    /* Main surface */
    --bg:             #F4EFE8;
    --bg2:            #EDE6DC;
    --surface:        #FFFFFF;
    --border:         #DDD5C8;
    --border2:        #C9BDB0;

    /* Typography */
    --text:           #180E06;
    --text2:          #5C4C3C;
    --text3:          #9A8878;

    /* Brown palette */
    --brown:          #4A2C10;
    --brown-md:       #6B3E1E;
    --brown-lt:       #8B5229;
    --brown-bg:       #F0E6D4;
    --brown-accent:   #C17E45;

    /* Status */
    --red:            #B91C1C;
    --red-bg:         #FEF2F2;
    --red-border:     #FECACA;
    --amber:          #B45309;
    --amber-bg:       #FFFBEB;
    --amber-border:   #FCD34D;
    --green:          #166534;
    --green-bg:       #F0FDF4;
    --green-border:   #86EFAC;

    --radius:         10px;
    --radius-lg:      14px;
    --shadow:         0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:      0 4px 20px rgba(0,0,0,0.10), 0 2px 6px rgba(0,0,0,0.06);
}

*, *::before, *::after { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ─── APP BASE ─── */
.stApp { background: var(--bg) !important; font-family: 'DM Sans', sans-serif !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ─── SIDEBAR ─── */
section[data-testid="stSidebar"] {
    background: var(--sb-bg) !important;
    width: 248px !important;
    min-width: 248px !important;
    border-right: none !important;
    box-shadow: 3px 0 16px rgba(0,0,0,0.22) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background: var(--sb-bg) !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] * {
    color: var(--sb-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
}
section[data-testid="stSidebar"] ::-webkit-scrollbar { width: 0; }

/* Fix sidebar button appearance */
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: var(--sb-muted) !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    padding: 9px 10px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    box-shadow: none !important;
    width: 100% !important;
    transition: all 0.12s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--sb-hover) !important;
    color: var(--sb-text) !important;
    transform: none !important;
}
section[data-testid="stSidebar"] .nav-active .stButton button {
    background: var(--sb-active) !important;
    color: var(--sb-text) !important;
    font-weight: 600 !important;
    border-left: 3px solid var(--sb-accent) !important;
    border-radius: 0 8px 8px 0 !important;
}
section[data-testid="stSidebar"] .qs-btn .stButton button {
    padding: 7px 10px !important;
    font-size: 0.78rem !important;
    color: var(--sb-muted) !important;
    border-left: none !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] .qs-btn .stButton button:hover {
    color: var(--sb-text) !important;
    background: var(--sb-hover) !important;
}
section[data-testid="stSidebar"] .upgrade-btn .stButton button {
    background: var(--sb-accent) !important;
    color: #fff !important;
    width: 100% !important;
    border-radius: 8px !important;
    padding: 9px 14px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}
section[data-testid="stSidebar"] .upgrade-btn .stButton button:hover {
    background: #D49050 !important;
    color: #fff !important;
}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important; padding: 0 !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--text3) !important;
    border-radius: 0 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    padding: 10px 20px !important; border: none !important;
    border-bottom: 2px solid transparent !important; margin-bottom: -1px !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important; color: var(--brown) !important;
    font-weight: 700 !important; border-bottom: 2px solid var(--brown) !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 22px 0 0 0 !important; }

/* ─── CHAT INPUT ─── */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 1.5px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--brown-lt) !important;
    box-shadow: 0 0 0 3px rgba(74,44,16,0.10) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text3) !important; }

/* ─── MAIN BUTTONS ─── */
.stButton button {
    background: var(--brown) !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 0.82rem !important; box-shadow: var(--shadow) !important;
    transition: all 0.14s !important; padding: 10px 18px !important;
}
.stButton button:hover {
    background: var(--brown-md) !important; transform: translateY(-1px) !important;
    box-shadow: var(--shadow-md) !important;
}
.btn-outline .stButton button {
    background: var(--surface) !important; color: var(--text2) !important;
    border: 1px solid var(--border) !important;
}
.btn-outline .stButton button:hover {
    background: var(--bg2) !important; color: var(--text) !important;
    transform: none !important; box-shadow: none !important;
}
.btn-danger .stButton button {
    background: var(--surface) !important; color: var(--red) !important;
    border: 1px solid var(--red-border) !important;
}
.btn-danger .stButton button:hover {
    background: var(--red-bg) !important; transform: none !important; box-shadow: none !important;
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

/* ─── CHAT MESSAGES ─── */
.chat-msg-user {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 14px 0; border-bottom: 1px solid var(--border);
}
.chat-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: var(--brown); color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
}
.chat-q-text { font-size: 0.875rem; color: var(--text); line-height: 1.65; padding-top: 3px; }

/* ─── RESULT CARD ─── */
.result-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); overflow: hidden;
    box-shadow: var(--shadow); margin: 4px 0 18px;
}
.result-card-top {
    display: flex; align-items: center; gap: 8px;
    background: #FAFAF7; border-bottom: 1px solid var(--border);
    padding: 9px 16px; font-size: 0.76rem; color: var(--text2);
    font-weight: 500;
}
.risk-pill {
    display: inline-flex; align-items: center; gap: 5px;
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
}
.rp-high   { background: var(--red-bg);   color: var(--red)   !important; border: 1px solid var(--red-border); }
.rp-medium { background: var(--amber-bg); color: var(--amber) !important; border: 1px solid var(--amber-border); }
.rp-low    { background: var(--green-bg); color: var(--green) !important; border: 1px solid var(--green-border); }
.risk-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.rd-high   { background: var(--red); }
.rd-medium { background: var(--amber); }
.rd-low    { background: var(--green); }
.result-body { padding: 16px 18px 14px; }
.result-answer { font-size: 0.855rem; color: var(--text); line-height: 1.78; }
.sources-section { border-top: 1px solid var(--border); padding: 12px 18px; background: #FAFAF7; }
.sources-hd { font-size: 0.75rem; font-weight: 600; color: var(--text2); margin-bottom: 9px; }
.source-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.source-chip {
    display: flex; align-items: center; gap: 6px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 6px; padding: 5px 10px; font-size: 0.69rem; color: var(--text2);
}

/* ─── PANEL CARDS (right col) ─── */
.panel-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); overflow: hidden;
    box-shadow: var(--shadow); margin-bottom: 14px;
}
.panel-card-head {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-bottom: 1px solid var(--border);
    background: #FAFAF7;
}
.panel-icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: var(--brown-bg);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}
.panel-title {
    font-family: 'Lora', serif; font-size: 0.93rem;
    font-weight: 600; color: var(--text) !important;
}
.panel-body { padding: 16px 18px; }
.panel-desc { font-size: 0.79rem; color: var(--text2); line-height: 1.55; margin-bottom: 14px; }
.panel-label {
    font-size: 0.67rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text3); margin-bottom: 8px;
    display: flex; align-items: center; justify-content: space-between;
}
.file-chip {
    display: flex; align-items: center; gap: 9px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 9px 12px; margin-bottom: 12px;
}
.file-chip-name { font-size: 0.79rem; font-weight: 600; color: var(--text); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-chip-size { font-size: 0.67rem; color: var(--text3); flex-shrink: 0; }
.session-row { font-size: 0.8rem; color: var(--text2); margin-bottom: 6px; }
.session-row strong { color: var(--text) !important; }
.session-id { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--brown-lt) !important; }

/* ─── PANEL QUESTIONS ─── */
.qs-panel .stButton button {
    background: transparent !important; color: var(--text2) !important;
    border: none !important; border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important; text-align: left !important;
    padding: 11px 0 !important; font-weight: 400 !important;
    font-size: 0.8rem !important; box-shadow: none !important; width: 100% !important;
}
.qs-panel .stButton button:hover {
    background: transparent !important; color: var(--brown) !important;
    transform: none !important; box-shadow: none !important;
}

/* ─── SCAN GRID ─── */
.scan-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin: 16px 0; }
.scan-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 10px; text-align: center;
}
.scan-num { font-size: 1.6rem; font-weight: 700; color: var(--text); line-height: 1; font-family: 'DM Sans', sans-serif; }
.scan-lbl { font-size: 0.64rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.07em; margin-top: 5px; }

/* ─── EVAL TABLE ─── */
.eval-tbl { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.eval-tbl th {
    background: #FAFAF7; color: var(--text3); font-size: 0.66rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); font-weight: 600;
}
.eval-tbl td { padding: 10px 14px; color: var(--text); border-bottom: 1px solid var(--border); }
.eval-tbl tr:hover td { background: #FAFAF7; }
.eval-tbl tr.best-row td { background: var(--green-bg); }
.eval-tbl .mono { font-family: 'DM Mono', monospace; font-size: 0.78rem; }
.eval-tbl .best-val { color: var(--green); font-weight: 700; }
.chip-strategy {
    background: var(--brown-bg); color: var(--brown);
    border: 1px solid #D4C4B0; border-radius: 5px;
    padding: 2px 8px; font-size: 0.7rem; font-weight: 600;
}

/* ─── EMPTY STATE ─── */
.empty-state {
    text-align: center; padding: 52px 24px 40px;
}
.empty-state-icon {
    width: 60px; height: 60px;
    background: var(--surface); border: 1.5px solid var(--border);
    border-radius: 16px; display: inline-flex; align-items: center;
    justify-content: center; font-size: 26px; margin-bottom: 18px;
    box-shadow: var(--shadow);
}
.empty-state-title {
    font-family: 'Lora', serif; font-size: 1.2rem; color: var(--text);
    margin-bottom: 8px; font-weight: 600;
}
.empty-state-sub {
    font-size: 0.8rem; color: var(--text3);
    max-width: 320px; margin: 0 auto 26px; line-height: 1.65;
}

/* ─── NOTICE BANNERS ─── */
.notice-warn {
    background: var(--amber-bg); border: 1px solid var(--amber-border);
    border-radius: 10px; padding: 14px 18px;
    font-size: 0.82rem; color: var(--amber); display: flex; align-items: center; gap: 10px;
}
.notice-ok {
    background: var(--green-bg); border: 1px solid var(--green-border);
    border-radius: 10px; padding: 10px 14px;
    font-size: 0.81rem; color: var(--green); font-weight: 500;
    display: flex; align-items: center; gap: 8px;
}
.notice-info {
    background: var(--brown-bg); border: 1px solid #D4C4B0;
    border-radius: 10px; padding: 10px 14px;
    font-size: 0.81rem; color: var(--brown); display: flex; align-items: center; gap: 8px;
}

/* ─── MISC ─── */
.stAlert {
    background: var(--bg) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; font-family: 'DM Sans', sans-serif !important;
}
.stSpinner > div { border-top-color: var(--brown-lt) !important; }
[data-testid="stMetricValue"] { font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; color: var(--text) !important; }
[data-testid="stMetricLabel"] { font-family: 'DM Sans', sans-serif !important; color: var(--text3) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
details summary {
    background: #FAFAF7 !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text2) !important;
    font-size: 0.79rem !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}
[data-testid="stFileUploader"] {
    background: var(--bg) !important;
    border: 1.5px dashed var(--border2) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:20px 16px 18px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:11px;">
            <div style="width:40px;height:40px;background:#6B3E1E;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:19px;flex-shrink:0;
                        box-shadow:0 2px 8px rgba(0,0,0,0.30);">⚖️</div>
            <div>
                <div style="font-family:'Lora',serif;font-size:1.25rem;color:#F0E6D6 !important;font-weight:600;line-height:1;">LexIQ</div>
                <div style="font-size:0.59rem;color:#7A6350 !important;margin-top:3px;letter-spacing:0.04em;text-transform:uppercase;">Legal Intelligence · India</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav section label
    st.markdown('<div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#4A3520 !important;padding:8px 14px 4px;">Navigation</div>', unsafe_allow_html=True)

    # Nav items with working state
    nav_items = [
        ("💬", "Ask LexIQ"),
        ("🔍", "Contract Scanner"),
        ("📊", "Eval Results"),
    ]

    for icon, label in nav_items:
        is_active = st.session_state.active_nav == label
        css_class = "nav-active" if is_active else ""
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"nav_{label}"):
            st.session_state.active_nav = label
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:12px 0;"></div>', unsafe_allow_html=True)

    # Quick Questions
    st.markdown('<div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#4A3520 !important;padding:0 14px 6px;">Quick Questions</div>', unsafe_allow_html=True)
    sidebar_qs = [
        "Penalty for breach of contract?",
        "MSME 45-day payment rule?",
        "GST invoice fields?",
        "What is force majeure?",
        "Void vs voidable contract?",
    ]
    for q in sidebar_qs:
        st.markdown('<div class="qs-btn">', unsafe_allow_html=True)
        if st.button(q, key=f"sb_{q}"):
            st.session_state.active_nav = "Ask LexIQ"
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:12px 0;"></div>', unsafe_allow_html=True)

    # Upgrade card
    st.markdown("""
    <div style="margin:0 10px 14px;background:rgba(193,126,69,0.12);border:1px solid rgba(193,126,69,0.22);border-radius:12px;padding:16px 14px;">
        <div style="width:30px;height:30px;background:#6B3E1E;border-radius:7px;
                    display:flex;align-items:center;justify-content:center;font-size:13px;margin-bottom:10px;">👑</div>
        <div style="font-size:0.84rem;font-weight:700;color:#F0E6D6 !important;margin-bottom:4px;font-family:'Lora',serif;">Upgrade to Pro</div>
        <div style="font-size:0.71rem;color:#7A6350 !important;line-height:1.55;margin-bottom:12px;">Bulk uploads, advanced risk reports, and priority analysis.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="upgrade-btn" style="margin:0 10px 12px;">', unsafe_allow_html=True)
    if st.button("Upgrade Now →", key="upgrade_btn"):
        pass
    st.markdown('</div>', unsafe_allow_html=True)

    # Support row
    st.markdown('<div style="padding:8px 14px;font-size:0.78rem;color:#4A3520 !important;">🎧 <span style="color:#7A6350 !important;"> Support & Docs</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HANDLE PENDING QUESTION
# ══════════════════════════════════════════════════════════
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.messages.append({"role": "user", "content": q})


# ══════════════════════════════════════════════════════════
# MAIN LAYOUT
# ══════════════════════════════════════════════════════════
col_center, col_right = st.columns([2.7, 1], gap="medium")

# ── CENTER ────────────────────────────────────────────────
with col_center:
    st.markdown('<div style="padding:26px 4px 28px 22px;">', unsafe_allow_html=True)

    # ── PAGE HEADER ───────────────────────────────────────
    page_meta = {
        "Ask LexIQ":         ("Ask a Legal Question",      "Get instant answers backed by Indian law and your uploaded contract."),
        "Contract Scanner":  ("Contract Risk Scanner",     "Every clause classified automatically in seconds."),
        "Eval Results":      ("Evaluation Benchmark",      "9 experiments · 51 questions · 4 metrics across chunking & retrieval strategies."),
    }
    title, subtitle = page_meta.get(st.session_state.active_nav, ("LexIQ", ""))

    st.markdown(f"""
    <div style="margin-bottom:22px;">
        <div style="font-family:'Lora',serif;font-size:1.55rem;font-weight:600;color:#180E06;
                    letter-spacing:-0.02em;line-height:1.15;">{title}</div>
        <div style="font-size:0.79rem;color:#9A8878;margin-top:5px;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

    # Contract context banner
    if st.session_state.uploaded_file_name:
        st.markdown(f"""
        <div class="notice-info" style="margin-bottom:18px;">
            📄 <span>Contract loaded: <strong style="color:#4A2C10;">{st.session_state.uploaded_file_name}</strong>
            — questions will cross-reference this document against Indian law.</span>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # ASK LEXIQ PAGE
    # ══════════════════════════════════════════════════════
    if st.session_state.active_nav == "Ask LexIQ":

        # Empty state
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">⚖️</div>
                <div class="empty-state-title">How can I help you today?</div>
                <div class="empty-state-sub">Ask about contracts, Indian business law, or upload a contract for detailed clause-by-clause risk analysis.</div>
            </div>
            """, unsafe_allow_html=True)

            chips = [
                ("📋", "Penalty for breach of contract?"),
                ("🏭", "MSME delayed payment rule?"),
                ("🧾", "GST invoice mandatory fields?"),
                ("🌪️", "Force majeure explained"),
                ("❌", "Void vs voidable contract?"),
                ("🤫", "NDA obligations in India"),
            ]
            c1, c2 = st.columns(2)
            for i, (emoji, chip) in enumerate(chips):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                    if st.button(f"{emoji}  {chip}", key=f"chip_{i}"):
                        st.session_state.pending_question = chip
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # Message history
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
                    cmap = {"HIGH": "#B91C1C", "MEDIUM": "#B45309", "LOW": "#166534"}
                    chips_html = "".join([
                        f'<div class="source-chip"><span style="width:7px;height:7px;border-radius:50%;background:{cmap.get(s.get("risk","LOW"),"#9A8878")};flex-shrink:0;display:inline-block;"></span>'
                        f'{s.get("filename","?")} — p.{s.get("page","?")}</div>'
                        for s in msg["sources"]
                    ])
                    sources_html = f'<div class="sources-section"><div class="sources-hd">📖 Sources Used</div><div class="source-grid">{chips_html}</div></div>'

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-card-top">
                        ⚖️ LexIQ Analysis &nbsp;·&nbsp;
                        <span class="risk-pill {rp_cls}">
                            <span class="risk-dot {rd_cls}"></span>{rl} Risk
                        </span>
                    </div>
                    <div class="result-body">
                        <div class="result-answer">{msg["content"]}</div>
                    </div>
                    {sources_html}
                </div>
                """, unsafe_allow_html=True)

                if msg.get("no_rag_answer"):
                    with st.expander("📎 Baseline (without RAG)", expanded=False):
                        st.markdown(f'<div style="font-size:0.79rem;color:#5C4C3C;line-height:1.65;background:#FAFAF7;border-radius:8px;padding:14px;">{msg["no_rag_answer"][:600]}…</div>', unsafe_allow_html=True)

        # Fire query on new user message
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            question = st.session_state.messages[-1]["content"]
            with st.spinner("Searching legal corpus…"):
                try:
                    resp = requests.post(
                        f"{API_URL}/query",
                        json={"question": question, "session_id": st.session_state.session_id, "strategy": "clause", "top_k": 5},
                        timeout=60,
                    )
                    result = resp.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result.get("answer", "Error."),
                        "sources": result.get("sources", []),
                        "risk_level": result.get("risk_level", "LOW"),
                        "no_rag_answer": result.get("no_rag_answer", ""),
                    })
                    st.rerun()
                except requests.exceptions.ConnectionError:
                    st.error("❌ API not running. Start with: `python api/main.py`")
                except Exception as e:
                    st.error(f"❌ {str(e)}")

        question = st.chat_input("Ask about Indian contracts, laws, or your uploaded document…")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

    # ══════════════════════════════════════════════════════
    # CONTRACT SCANNER PAGE
    # ══════════════════════════════════════════════════════
    elif st.session_state.active_nav == "Contract Scanner":

        if not st.session_state.session_id:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📂</div>
                <div class="empty-state-title">No contract uploaded yet</div>
                <div class="empty-state-sub">Upload a PDF contract using the panel on the right. LexIQ will parse every clause and score it for legal risk under Indian law.</div>
            </div>
            """, unsafe_allow_html=True)

            # Show what it does
            st.markdown("""
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;max-width:560px;margin:0 auto;">
                <div style="background:#fff;border:1px solid #DDD5C8;border-radius:10px;padding:14px;text-align:center;">
                    <div style="font-size:1.4rem;margin-bottom:6px;">🔍</div>
                    <div style="font-size:0.76rem;font-weight:600;color:#180E06;margin-bottom:3px;">Clause Detection</div>
                    <div style="font-size:0.7rem;color:#9A8878;line-height:1.5;">Every clause extracted and numbered</div>
                </div>
                <div style="background:#fff;border:1px solid #DDD5C8;border-radius:10px;padding:14px;text-align:center;">
                    <div style="font-size:1.4rem;margin-bottom:6px;">⚠️</div>
                    <div style="font-size:0.76rem;font-weight:600;color:#180E06;margin-bottom:3px;">Risk Scoring</div>
                    <div style="font-size:0.7rem;color:#9A8878;line-height:1.5;">HIGH / MEDIUM / LOW on each clause</div>
                </div>
                <div style="background:#fff;border:1px solid #DDD5C8;border-radius:10px;padding:14px;text-align:center;">
                    <div style="font-size:1.4rem;margin-bottom:6px;">📜</div>
                    <div style="font-size:0.76rem;font-weight:600;color:#180E06;margin-bottom:3px;">Law Cross-ref</div>
                    <div style="font-size:0.7rem;color:#9A8878;line-height:1.5;">Matched against Indian Contract Act</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="notice-ok" style="margin-bottom:16px;">✓ Ready to scan: <strong>{st.session_state.uploaded_file_name}</strong></div>', unsafe_allow_html=True)

            if st.button("🔍  Scan All Clauses"):
                with st.spinner("Analysing clauses…"):
                    try:
                        resp = requests.post(f"{API_URL}/scan", json={"session_id": st.session_state.session_id}, timeout=60)
                        st.session_state.scan_results = resp.json()
                    except Exception as e:
                        st.error(f"❌ {str(e)}")

            if st.session_state.scan_results:
                scan    = st.session_state.scan_results
                overall = scan.get("overall_risk", "LOW")
                emoji   = scan.get("overall_emoji", "🟢")
                summary = scan.get("summary", {})
                rp_cls  = {"HIGH": "rp-high", "MEDIUM": "rp-medium", "LOW": "rp-low"}.get(overall, "rp-low")

                st.markdown(f"""
                <div style="background:#fff;border:1px solid #DDD5C8;border-radius:12px;padding:20px;margin:14px 0;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                    <div style="font-size:0.66rem;text-transform:uppercase;letter-spacing:0.09em;color:#9A8878;margin-bottom:10px;font-weight:700;">Overall Contract Assessment</div>
                    <span class="risk-pill {rp_cls}" style="font-size:0.78rem;padding:5px 14px;">{emoji} {overall} Risk Contract</span>
                    <div class="scan-grid" style="margin-top:16px;">
                        <div class="scan-card"><div class="scan-num">{summary.get('total_clauses',0)}</div><div class="scan-lbl">Total</div></div>
                        <div class="scan-card" style="border-top:3px solid #B91C1C;"><div class="scan-num" style="color:#B91C1C;">{summary.get('high_risk',0)}</div><div class="scan-lbl">High</div></div>
                        <div class="scan-card" style="border-top:3px solid #B45309;"><div class="scan-num" style="color:#B45309;">{summary.get('medium_risk',0)}</div><div class="scan-lbl">Medium</div></div>
                        <div class="scan-card" style="border-top:3px solid #166534;"><div class="scan-num" style="color:#166534;">{summary.get('low_risk',0)}</div><div class="scan-lbl">Low</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                for label, color, key in [
                    ("🔴  High Risk Clauses",   "#B91C1C", "high_risk_clauses"),
                    ("🟡  Medium Risk Clauses", "#B45309", "medium_risk_clauses"),
                    ("🟢  Low Risk Clauses",    "#166634", "low_risk_clauses"),
                ]:
                    clauses = scan.get(key, [])
                    if clauses:
                        st.markdown(f'<div style="font-size:0.82rem;font-weight:700;color:{color};margin:20px 0 8px;">{label} <span style="font-weight:400;color:#9A8878;font-size:0.75rem;">({len(clauses)})</span></div>', unsafe_allow_html=True)
                        show = clauses[:5] if key == "low_risk_clauses" else clauses
                        for c in show:
                            with st.expander(f"Clause {c['clause_number']} — p.{c['page']}"):
                                st.markdown(f'<div style="font-size:0.8rem;color:#5C4C3C;line-height:1.68;padding:4px 0;">{c["text"]}</div>', unsafe_allow_html=True)
                        if key == "low_risk_clauses" and len(clauses) > 5:
                            st.markdown(f'<div style="font-size:0.73rem;color:#9A8878;margin-top:4px;">+ {len(clauses)-5} more low-risk clauses not shown</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # EVAL RESULTS PAGE
    # ══════════════════════════════════════════════════════
    elif st.session_state.active_nav == "Eval Results":

        # Key findings summary
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:22px;">
            <div style="background:#fff;border:1px solid #DDD5C8;border-radius:10px;padding:16px;">
                <div style="font-size:0.64rem;text-transform:uppercase;letter-spacing:0.08em;color:#9A8878;margin-bottom:6px;font-weight:700;">Best Config</div>
                <div style="font-size:0.97rem;font-weight:700;color:#180E06;font-family:'DM Mono',monospace;">fixed + dense</div>
                <div style="font-size:0.72rem;color:#166534;margin-top:4px;font-weight:600;">Faithfulness: 0.598</div>
            </div>
            <div style="background:#fff;border:1px solid #DDD5C8;border-radius:10px;padding:16px;">
                <div style="font-size:0.64rem;text-transform:uppercase;letter-spacing:0.08em;color:#9A8878;margin-bottom:6px;font-weight:700;">Worst Config</div>
                <div style="font-size:0.97rem;font-weight:700;color:#180E06;font-family:'DM Mono',monospace;">fixed + sparse</div>
                <div style="font-size:0.72rem;color:#B91C1C;margin-top:4px;font-weight:600;">Faithfulness: 0.310</div>
            </div>
            <div style="background:#fff;border:1px solid #DDD5C8;border-radius:10px;padding:16px;">
                <div style="font-size:0.64rem;text-transform:uppercase;letter-spacing:0.08em;color:#9A8878;margin-bottom:6px;font-weight:700;">Improvement</div>
                <div style="font-size:0.97rem;font-weight:700;color:#180E06;">93%</div>
                <div style="font-size:0.72rem;color:#9A8878;margin-top:4px;">worst → best faithfulness</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("↻  Load Latest Results from API"):
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
                        rows += (
                            f'<tr class="{rc}">'
                            f'<td><span class="chip-strategy">{r["strategy"]}</span></td>'
                            f'<td style="color:#5C4C3C;">{r["retriever"]}</td>'
                            f'<td class="{vc}">{r["faithfulness"]:.4f}{star}</td>'
                            f'<td class="mono">{r["answer_relevancy"]:.4f}</td>'
                            f'<td class="mono">{r["context_precision"]:.4f}</td>'
                            f'<td class="mono">{r["context_recall"]:.4f}</td>'
                            f'</tr>'
                        )
                    st.markdown(f"""
                    <div style="background:#fff;border:1px solid #DDD5C8;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.06);margin-bottom:20px;">
                        <table class="eval-tbl">
                            <thead><tr>
                                <th>Chunking</th><th>Retriever</th>
                                <th>Faithfulness</th><th>Ans. Rel.</th>
                                <th>Ctx. Prec.</th><th>Ctx. Rec.</th>
                            </tr></thead>
                            <tbody>{rows}</tbody>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)

                    best  = max(results, key=lambda x: x["faithfulness"])
                    worst = min(results, key=lambda x: x["faithfulness"])
                    impr  = ((best["faithfulness"] - worst["faithfulness"]) / max(worst["faithfulness"], 0.001)) * 100
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("Best Config",   f"{best['strategy']} + {best['retriever']}",   f"↑ {best['faithfulness']:.3f}")
                    with c2: st.metric("Worst Config",  f"{worst['strategy']} + {worst['retriever']}", f"↓ {worst['faithfulness']:.3f}")
                    with c3: st.metric("Improvement",   f"{impr:.1f}%", "worst → best")

                    import pandas as pd
                    df = pd.DataFrame({
                        "Config": [f"{r['strategy']}+{r['retriever']}" for r in results],
                        "Faithfulness": [r["faithfulness"] for r in results],
                    }).set_index("Config")
                    st.bar_chart(df)
                else:
                    st.info("No results yet — run `python evaluation/ragas_eval.py` first.")
            except requests.exceptions.ConnectionError:
                st.error("❌ API not running. Start with: `python api/main.py`")
            except Exception as e:
                st.error(f"❌ {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Key findings
        st.markdown("""
        <div style="background:#fff;border:1px solid #DDD5C8;border-radius:12px;padding:20px;margin-top:10px;">
            <div style="font-family:'Lora',serif;font-size:0.98rem;font-weight:600;color:#180E06;margin-bottom:14px;">Key Findings</div>
            <div style="font-size:0.82rem;color:#5C4C3C;line-height:1.75;">
                <div style="display:flex;gap:10px;margin-bottom:8px;"><span style="color:#B91C1C;flex-shrink:0;">→</span> BM25 sparse retrieval consistently underperforms due to vocabulary mismatch between user questions and Indian legal terminology.</div>
                <div style="display:flex;gap:10px;margin-bottom:8px;"><span style="color:#B45309;flex-shrink:0;">→</span> Dense retrieval beats hybrid — sparse component pulls hybrid scores down. Pure dense embeddings better capture semantic meaning.</div>
                <div style="display:flex;gap:10px;margin-bottom:8px;"><span style="color:#166534;flex-shrink:0;">→</span> Query expansion fixed Q07 (minor contracts) and Q10 (NDA) from 0.00 to meaningful scores by mapping lay terms to legal terminology.</div>
                <div style="display:flex;gap:10px;"><span style="color:#4A2C10;flex-shrink:0;">→</span> Dominant failure mode is retrieval (wrong chunks pulled), not LLM hallucination — invest in query expansion over prompt engineering.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── RIGHT PANEL ───────────────────────────────────────────
with col_right:
    st.markdown('<div style="padding:26px 18px 28px 4px;">', unsafe_allow_html=True)

    # ── Upload card ───────────────────────────────────────
    st.markdown("""
    <div class="panel-card">
        <div class="panel-card-head">
            <div class="panel-icon">📄</div>
            <div class="panel-title">Upload Contract</div>
        </div>
        <div class="panel-body">
            <div class="panel-desc">Upload a PDF to get clause-by-clause risk analysis cross-referenced against Indian law.</div>
            <div class="panel-label">PDF contract file <span style="cursor:help;" title="Max 50MB">ℹ️</span></div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("PDF contract", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        sz = round(len(uploaded.getvalue()) / 1024, 1)
        st.markdown(f"""
        <div class="file-chip">
            <span style="font-size:1.05rem;">📄</span>
            <span class="file-chip-name">{uploaded.name}</span>
            <span class="file-chip-size">{sz} KB</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚙️  Process Contract", key="process_btn"):
            with st.spinner("Parsing PDF…"):
                try:
                    files  = {"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
                    resp   = requests.post(f"{API_URL}/upload", files=files, timeout=120)
                    result = resp.json()
                    if resp.status_code == 200:
                        st.session_state.session_id         = result["session_id"]
                        st.session_state.uploaded_file_name = result["filename"]
                        st.session_state.scan_results       = None
                        st.success(f"✓ {result['pages']} pages · {result['chunks']} chunks ready")
                        st.rerun()
                    else:
                        st.error(result.get("detail", "Upload failed"))
                except requests.exceptions.ConnectionError:
                    st.error("❌ Start API: `python api/main.py`")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    else:
        # Placeholder when no file chosen
        st.markdown("""
        <div style="border:1.5px dashed #C9BDB0;border-radius:8px;padding:22px 14px;text-align:center;background:#F4EFE8;margin-bottom:4px;">
            <div style="font-size:1.5rem;margin-bottom:6px;">☁️</div>
            <div style="font-size:0.78rem;font-weight:600;color:#5C4C3C;">Drop your PDF here</div>
            <div style="font-size:0.71rem;color:#9A8878;margin-top:3px;">or use the file picker above</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── Active session card ───────────────────────────────
    if st.session_state.session_id:
        st.markdown(f"""
        <div class="panel-card">
            <div class="panel-card-head">
                <div class="panel-icon">🔗</div>
                <div class="panel-title">Active Session</div>
            </div>
            <div class="panel-body">
                <div class="session-row">File: <strong>{st.session_state.uploaded_file_name}</strong></div>
                <div class="session-row" style="margin-bottom:12px;">ID: <span class="session-id">{st.session_state.session_id[:14]}…</span></div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑  Clear Contract", key="clear_btn"):
            try:
                requests.delete(f"{API_URL}/session/{st.session_state.session_id}", timeout=10)
            except Exception:
                pass
            st.session_state.session_id         = None
            st.session_state.uploaded_file_name = None
            st.session_state.scan_results       = None
            st.rerun()
        st.markdown('</div></div></div>', unsafe_allow_html=True)

    # ── Try These Questions card ──────────────────────────
    st.markdown("""
    <div class="panel-card">
        <div class="panel-card-head">
            <div class="panel-icon">💡</div>
            <div class="panel-title">Try These Questions</div>
        </div>
        <div class="panel-body" style="padding:0 18px 2px;">
    """, unsafe_allow_html=True)

    st.markdown('<div class="qs-panel">', unsafe_allow_html=True)
    panel_qs = [
        "What is the penalty for breach of contract?",
        "How many days to pay an MSME supplier?",
        "GST invoice mandatory requirements?",
        "Explain force majeure clause",
        "What makes a contract void in India?",
    ]
    for q in panel_qs:
        if st.button(q, key=f"pq_{q}"):
            st.session_state.active_nav = "Ask LexIQ"
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        </div>
        <div style="padding:2px 18px 14px;">
            <div style="font-size:0.76rem;font-weight:600;color:#8B5229;cursor:pointer;display:inline-flex;align-items:center;gap:4px;">View all questions →</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)