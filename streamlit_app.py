import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from core.db import Base, engine
from core import models  # noqa: F401 - registruje SQLAlchemy modely
from core.security import bootstrap_admin, login_form, logout
from core.seed import seed_demo_data
from styles import apply_styles

st.set_page_config(page_title="SportStats 2.0", page_icon="⚽", layout="wide")
Base.metadata.create_all(bind=engine)
bootstrap_admin()
seed_demo_data()

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Tmavý"
apply_styles()

if not login_form():
    st.stop()

with st.sidebar:
    st.markdown("## ⚽ SportStats **2.0**")
    st.caption("FOOTBALL ANALYTICS")
    st.selectbox("Vzhled", ["Tmavý", "Světlý"],
                 key="theme_mode", on_change=apply_styles)
    st.divider()
    page = st.radio("Navigace", [
        "Přehled", "Ligy a sezóny", "Ligové tabulky", "Zápasy",
        "Týmy", "Statistiky", "Predikční centrum", "Administrace"
    ])
    st.divider()
    st.write(f"👤 **{st.session_state.username}**")
    st.caption(f"Role: {st.session_state.role}")
    if st.button("Odhlásit se", use_container_width=True):
        logout()

if page == "Přehled":
    from views.dashboard import render
elif page == "Ligy a sezóny":
    from views.leagues import render
elif page == "Ligové tabulky":
    from views.standings import render
elif page == "Zápasy":
    from views.matches import render
elif page == "Týmy":
    from views.teams import render
elif page == "Statistiky":
    from views.statistics import render
elif page == "Predikční centrum":
    from views.predictions import render
else:
    from views.admin import render
render()
