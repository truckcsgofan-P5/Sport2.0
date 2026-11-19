import streamlit as st


def apply_styles():
    """Jednotný tmavý DarkGreen vzhled SportStats 2.1."""
    bg = "#050D08"
    panel = "#0B1710"
    panel2 = "#102319"
    text = "#F2F8F3"
    muted = "#91A99A"
    border = "#203B2A"
    accent = "#48E184"
    accent_soft = "rgba(72,225,132,.12)"
    st.markdown(f"""
    <style>
    :root {{ color-scheme: dark; }}
    .stApp {{ background: radial-gradient(ellipse at 80% 0%, {accent_soft}, transparent 38%), {bg}; color: {text}; }}
    [data-testid="stSidebar"] {{ background: {panel}; border-right: 1px solid {border}; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color: {muted}; }}
    [data-testid="stMetric"] {{ background: linear-gradient(145deg, {panel2}, {panel}); padding: 18px; border: 1px solid {border}; border-radius: 16px; }}
    [data-testid="stMetricLabel"] {{ color: {muted}; font-weight: 650; }}
    [data-testid="stMetricValue"] {{ color: {text}; font-weight: 800; }}
    .block-container {{ padding-top: 1.7rem; max-width: 1500px; }}
    h1,h2,h3 {{ letter-spacing: -.035em; }}
    h1 {{ font-weight: 850 !important; }}
    .eyebrow {{ color: {accent}; font-size: .72rem; letter-spacing: .18em; font-weight: 850; text-transform: uppercase; }}
    .login-wrap {{ text-align:center; padding: 3rem 0 1.5rem; }}
    .login-wrap h1 {{ font-size: 2.7rem; margin: .3rem 0; }}
    .login-wrap h1 span {{ color:{accent}; }}
    .login-wrap p {{ color:{muted}; }}
    div[data-testid="stDataFrame"] {{ border: 1px solid {border}; border-radius: 14px; overflow: hidden; }}
    div[data-testid="stPlotlyChart"] {{ background: {panel}; border: 1px solid {border}; border-radius: 16px; padding: 8px; }}
    .stButton > button[kind="primary"] {{ background: {accent}; color: #06110A; border: 0; font-weight: 800; }}
    a {{ color: {accent} !important; }}
    </style>
    """, unsafe_allow_html=True)
