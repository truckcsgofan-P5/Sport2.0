import bcrypt
import streamlit as st
from sqlalchemy import select
from .db import SessionLocal
from .config import setting
from .models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def bootstrap_admin():
    username = setting("BOOTSTRAP_ADMIN_USERNAME", "admin").strip()
    password = setting("BOOTSTRAP_ADMIN_PASSWORD", "")
    if not password:
        return
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.username == username))
        if existing is None:
            db.add(User(username=username, password_hash=hash_password(password), role="admin"))
            db.commit()


def login_form():
    if st.session_state.get("authenticated"):
        return True

    st.markdown(
        "<div class='login-wrap'><div class='eyebrow'>SPORT ANALYTICS PLATFORM</div>"
        "<h1>SportStats <span>2.1</span></h1><p>Přihlášení do analytického centra</p></div>",
        unsafe_allow_html=True
    )
    with st.form("login"):
        username = st.text_input("Uživatelské jméno")
        password = st.text_input("Heslo", type="password")
        submitted = st.form_submit_button("Přihlásit se", use_container_width=True)
    if submitted:
        with SessionLocal() as db:
            user = db.scalar(select(User).where(
                User.username == username.strip(), User.active.is_(True)
            ))
            if user and verify_password(password, user.password_hash):
                st.session_state.authenticated = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.rerun()
            else:
                st.error("Neplatné přihlašovací údaje.")
    return False


def logout():
    for key in ("authenticated", "user_id", "username", "role"):
        st.session_state.pop(key, None)
    st.rerun()
