import streamlit as st

def apply_styles():
    theme = st.session_state.get("theme_mode", "Tmavý")
    if theme == "Světlý":
        bg, panel, text, muted, border = "#F4F7FB", "#FFFFFF", "#172033", "#64748B", "#E2E8F0"
    else:
        bg, panel, text, muted, border = "#0B1220", "#111C2E", "#F3F6FA", "#94A3B8", "#243247"
    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: {text}; }}
    [data-testid="stSidebar"] {{ background: {panel}; border-right: 1px solid {border}; }}
    [data-testid="stMetric"] {{ background: {panel}; padding: 16px; border: 1px solid {border}; border-radius: 14px; }}
    .block-container {{ padding-top: 1.6rem; max-width: 1500px; }}
    h1,h2,h3 {{ letter-spacing: -0.035em; }}
    .eyebrow {{ color: #16A34A; font-size: .72rem; letter-spacing: .18em; font-weight: 800; }}
    .login-wrap {{ text-align:center; padding: 3rem 0 1.5rem; }}
    .login-wrap h1 {{ font-size: 2.7rem; margin: .3rem 0; }}
    .login-wrap h1 span {{ color:#16A34A; }}
    .login-wrap p {{ color:{muted}; }}
    div[data-testid="stDataFrame"] {{ border: 1px solid {border}; border-radius: 12px; overflow: hidden; }}
    </style>
    """, unsafe_allow_html=True)
