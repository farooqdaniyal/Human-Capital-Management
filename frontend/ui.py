import html
import pandas as pd
import streamlit as st

MUTED = "#8c9ac4"


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 0%, rgba(79,70,229,.20), transparent 28%),
                radial-gradient(circle at 90% 10%, rgba(34,211,238,.12), transparent 25%),
                linear-gradient(135deg, #050a1f 0%, #08112d 45%, #0b1024 100%);
            color: #e8edff;
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #050a1f 0%, #06102b 100%);
            border-right: 1px solid rgba(126,166,255,.18);
        }

        section[data-testid="stSidebar"] * {
            color: #e8edff !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        .sidebar-brand {
            display: flex;
            gap: .75rem;
            align-items: center;
            padding: .95rem;
            border-radius: 18px;
            margin-bottom: .8rem;
        }

        .brand-logo {
            width: 48px;
            height: 48px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(79,109,245,.13);
            border: 1px solid rgba(126,166,255,.38);
            font-size: 1.35rem;
        }

        .brand-title {
            font-size: 1rem;
            font-weight: 900;
            color: #ffffff !important;
            letter-spacing: .2px;
        }

        .brand-title b {
            color: #22d3ee !important;
        }

        .brand-sub {
            color: #93a4d8 !important;
            font-size: .72rem;
            line-height: 1.35;
            margin-top: .2rem;
        }

        .system-box {
            padding: .85rem .95rem;
            border-radius: 14px;
            background: rgba(12, 24, 64, .85);
            border: 1px solid rgba(79,109,245,.35);
            margin-bottom: 1rem;
        }

        .system-online {
            display: flex;
            align-items: center;
            gap: .45rem;
            font-size: .82rem;
            font-weight: 900;
            color: #3cff9a !important;
        }

        .pulse-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 0 rgba(34,197,94,.6);
            animation: pulse 1.8s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(34,197,94,.65); }
            70% { box-shadow: 0 0 0 9px rgba(34,197,94,0); }
            100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
        }

        .system-sub {
            margin-left: 1.05rem;
            margin-top: .25rem;
            color: #8c9ac4 !important;
            font-size: .72rem;
        }

        .nav-label {
            color: #8c9ac4 !important;
            font-size: .72rem;
            font-weight: 900;
            letter-spacing: .12rem;
            text-transform: uppercase;
            margin: .25rem 0 .45rem .25rem;
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            justify-content: flex-start !important;
            text-align: left !important;
            border-radius: 12px !important;
            padding: .68rem .8rem !important;
            font-weight: 800 !important;
            margin-bottom: .18rem !important;
            transition: all .16s ease !important;
            border: 1px solid transparent !important;
        }

        section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
            background: transparent !important;
            color: #dbe7ff !important;
        }

        section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
            background: rgba(79,109,245,.13) !important;
            transform: translateX(4px);
            border-color: rgba(126,166,255,.15) !important;
        }

        section[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #4338ca, #4f46e5) !important;
            color: #ffffff !important;
            border: 1px solid rgba(126,166,255,.30) !important;
            box-shadow: 0 14px 35px rgba(79,70,229,.28);
        }

        .sidebar-user {
            margin-top: 1rem;
            padding: .9rem;
            border-radius: 18px;
            background: rgba(12, 24, 64, .82);
            border: 1px solid rgba(79,109,245,.35);
            display: flex;
            gap: .7rem;
            align-items: center;
        }

        .user-avatar {
            width: 45px;
            height: 45px;
            border-radius: 999px;
            background: linear-gradient(135deg, #2563eb, #06b6d4);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white !important;
            font-weight: 900;
        }

        .user-name {
            color: white !important;
            font-weight: 900;
            font-size: .86rem;
            max-width: 145px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .user-role {
            color: #8c9ac4 !important;
            font-size: .72rem;
            margin-top: .15rem;
        }

        .sidebar-footer {
            color: #64748b !important;
            font-size: .72rem;
            text-align: center;
            padding: 1rem 0 .3rem 0;
        }

        /* ---------- Page text ---------- */
        .page-title {
            font-size: 2rem;
            font-weight: 950;
            letter-spacing: -.5px;
            color: #ffffff !important;
            margin-bottom: .1rem;
        }

        .page-title .accent {
            color: #22d3ee !important;
        }

        .page-subtitle {
            color: #9fb0e6 !important;
            font-size: .93rem;
            margin-bottom: 1.15rem;
        }

        .glass-card {
            background: rgba(7, 15, 42, .88);
            border: 1px solid rgba(126,166,255,.20);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 18px 50px rgba(0,0,0,.22);
        }

        /* ---------- Inputs dark fix ---------- */
        label, .stTextInput label, .stTextArea label, .stSelectbox label,
        .stDateInput label, .stNumberInput label {
            color: #9fb0e6 !important;
            font-weight: 700 !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            background: rgba(8, 19, 50, .95) !important;
            border: 1px solid rgba(79,109,245,.38) !important;
            border-radius: 13px !important;
            color: #e8edff !important;
        }

        input, textarea {
            color: #e8edff !important;
            caret-color: #22d3ee !important;
        }

        input::placeholder, textarea::placeholder {
            color: #7f8dbb !important;
            opacity: 1 !important;
        }

        div[data-baseweb="select"] span {
            color: #e8edff !important;
        }

        div[data-baseweb="popover"] {
            background: #081332 !important;
            border: 1px solid rgba(79,109,245,.38) !important;
        }

        div[role="listbox"] {
            background: #081332 !important;
            color: #e8edff !important;
        }

        /* ---------- Buttons ---------- */
        div.stButton > button,
        div.stFormSubmitButton > button {
            border-radius: 12px !important;
            font-weight: 850 !important;
            border: 1px solid rgba(126,166,255,.26) !important;
            background: linear-gradient(135deg, #4338ca, #2563eb) !important;
            color: white !important;
            transition: all .15s ease !important;
        }

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 15px 35px rgba(37,99,235,.28);
        }

        div.stButton > button:disabled,
        div.stFormSubmitButton > button:disabled {
            background: rgba(30,41,59,.7) !important;
            color: #7f8dbb !important;
            border-color: rgba(148,163,184,.18) !important;
        }

        /* ---------- KPI Cards ---------- */
        .kpi-card {
            background: rgba(10, 20, 55, .92);
            border: 1px solid rgba(79,109,245,.30);
            border-radius: 18px;
            padding: 1.05rem;
            min-height: 128px;
            box-shadow: 0 18px 45px rgba(0,0,0,.22);
            position: relative;
            overflow: hidden;
        }

        .kpi-icon {
            width: 54px;
            height: 54px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            margin-bottom: .7rem;
            background: rgba(79,109,245,.18);
            border: 1px solid rgba(126,166,255,.25);
        }

        .kpi-label {
            font-size: .78rem;
            color: #cbd7ff !important;
            font-weight: 800;
        }

        .kpi-value {
            font-size: 2rem;
            line-height: 1.05;
            font-weight: 950;
            color: #ffffff !important;
            margin-top: .25rem;
        }

        .kpi-help {
            font-size: .75rem;
            color: #8c9ac4 !important;
            margin-top: .35rem;
        }

        .panel-title {
            font-size: 1rem;
            color: #ffffff !important;
            font-weight: 900;
            margin-bottom: .2rem;
        }

        .panel-sub {
            color: #8c9ac4 !important;
            font-size: .78rem;
            margin-bottom: .8rem;
        }

        /* ---------- Custom professional tables ---------- */
        .hcm-table-wrap {
            width: 100%;
            overflow-x: auto;
            border-radius: 16px;
            border: 1px solid rgba(126,166,255,.22);
            background: rgba(7, 15, 42, .90);
            box-shadow: 0 18px 50px rgba(0,0,0,.22);
        }

        table.hcm-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 720px;
        }

        .hcm-table thead tr {
            background: linear-gradient(180deg, rgba(20,38,88,.92), rgba(11,24,62,.92));
        }

        .hcm-table th {
            padding: .9rem 1rem;
            text-align: left;
            color: #8fb3ff !important;
            font-size: .72rem;
            letter-spacing: .12rem;
            text-transform: uppercase;
            font-weight: 900;
            border-bottom: 1px solid rgba(126,166,255,.22);
            white-space: nowrap;
        }

        .hcm-table td {
            padding: .85rem 1rem;
            color: #e8edff !important;
            font-size: .86rem;
            border-bottom: 1px solid rgba(126,166,255,.10);
            white-space: nowrap;
        }

        .hcm-table tbody tr {
            background: rgba(8, 19, 50, .38);
            transition: all .15s ease;
        }

        .hcm-table tbody tr:hover {
            background: rgba(79,109,245,.16);
        }

        .hcm-table tbody tr:last-child td {
            border-bottom: none;
        }

        .hcm-table td:first-child {
            color: #69a7ff !important;
            font-weight: 900;
        }

        .hcm-muted {
            color: #8c9ac4 !important;
        }

        .hcm-empty {
            padding: 1rem;
            border-radius: 14px;
            background: rgba(8,19,50,.72);
            border: 1px solid rgba(126,166,255,.16);
            color: #8c9ac4;
        }

        .status-pill {
            display: inline-block;
            padding: .22rem .65rem;
            border-radius: 999px;
            font-size: .76rem;
            font-weight: 800;
        }

        .pill-pending {
            background: rgba(245,158,11,.14);
            border: 1px solid rgba(245,158,11,.38);
            color: #fcd34d !important;
        }

        .pill-approved,
        .pill-active {
            background: rgba(34,197,94,.14);
            border: 1px solid rgba(34,197,94,.38);
            color: #86efac !important;
        }

        .pill-rejected,
        .pill-inactive,
        .pill-exited {
            background: rgba(239,68,68,.14);
            border: 1px solid rgba(239,68,68,.38);
            color: #fca5a5 !important;
        }

        .pill-hr {
            background: rgba(34,211,238,.14);
            border: 1px solid rgba(34,211,238,.38);
            color: #67e8f9 !important;
        }

        .pill-admin {
            background: rgba(139,92,246,.14);
            border: 1px solid rgba(139,92,246,.38);
            color: #c4b5fd !important;
        }

        .pill-employee {
            background: rgba(59,130,246,.14);
            border: 1px solid rgba(59,130,246,.38);
            color: #93c5fd !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value, help_text: str = "", icon: str = "📊", color: str = "#4f46e5"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="color:{color};border-color:{color}66;background:{color}22">{icon}</div>
            <div class="kpi-label">{html.escape(str(label))}</div>
            <div class="kpi-value">{html.escape(str(value))}</div>
            <div class="kpi-help">{html.escape(str(help_text))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel_start(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="panel-title">{html.escape(str(title))}</div>
        <div class="panel-sub">{html.escape(str(subtitle))}</div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(status: str):
    s = str(status or "").lower().strip()
    cls = "pill-pending"

    if s in ["approved", "active", "present", "verified"]:
        cls = "pill-approved"
    elif s in ["rejected", "inactive", "exited", "absent"]:
        cls = "pill-rejected"
    elif s == "admin":
        cls = "pill-admin"
    elif s == "hr":
        cls = "pill-hr"
    elif s == "employee":
        cls = "pill-employee"

    return f'<span class="status-pill {cls}">{html.escape(str(status))}</span>'


def _format_cell(col, value):
    if value is None or str(value) == "nan":
        return '<span class="hcm-muted">—</span>'

    col_l = str(col).lower()
    val = str(value)

    if col_l in ["status", "role", "leave_status"]:
        return status_pill(val)

    if "salary" in col_l or "cost" in col_l or "pay" in col_l:
        try:
            return f"{float(value):,.0f}"
        except Exception:
            return html.escape(val)

    return html.escape(val)


def data_table(df, columns=None, headers=None, max_rows=50, empty_text="No records found."):
    """
    Professional dark HTML table.
    Use this instead of st.dataframe for better UI.
    """
    if df is None:
        st.markdown(f'<div class="hcm-empty">{empty_text}</div>', unsafe_allow_html=True)
        return

    if isinstance(df, list):
        df = pd.DataFrame(df)

    if df.empty:
        st.markdown(f'<div class="hcm-empty">{empty_text}</div>', unsafe_allow_html=True)
        return

    data = df.copy()

    if columns:
        available = [c for c in columns if c in data.columns]
        data = data[available]

    data = data.head(max_rows)

    headers = headers or {}

    thead = "<thead><tr>"
    for col in data.columns:
        title = headers.get(col, str(col).replace("_", " ").title())
        thead += f"<th>{html.escape(str(title))}</th>"
    thead += "</tr></thead>"

    tbody = "<tbody>"
    for _, row in data.iterrows():
        tbody += "<tr>"
        for col in data.columns:
            tbody += f"<td>{_format_cell(col, row[col])}</td>"
        tbody += "</tr>"
    tbody += "</tbody>"

    table = f"""
    <div class="hcm-table-wrap">
        <table class="hcm-table">
            {thead}
            {tbody}
        </table>
    </div>
    """

    st.markdown(table, unsafe_allow_html=True)