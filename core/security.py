
import bcrypt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import streamlit as st
import extra_streamlit_components as stx
from sqlalchemy import select, delete

from .db import SessionLocal
from .config import setting
from .models import User, LoginSession


COOKIE_NAME = "sportstats_login"
SESSION_DAYS = 30



def get_cookie_manager():
    return stx.CookieManager()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _set_user_session(user):
    st.session_state.authenticated = True
    st.session_state.user_id = user.id
    st.session_state.username = user.username
    st.session_state.role = user.role


def _clear_user_session():
    for key in ("authenticated", "user_id", "username", "role"):
        st.session_state.pop(key, None)


def _create_login_session(user_id: int) -> str:
    token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)

    with SessionLocal() as db:
        db.add(LoginSession(
            user_id=user_id,
            token_hash=_token_hash(token),
            expires_at=expires_at
        ))
        db.commit()

    return token


def _restore_login(token: str) -> bool:
    if not token:
        return False

    with SessionLocal() as db:
        login_session = db.scalar(
            select(LoginSession).where(
                LoginSession.token_hash == _token_hash(token),
                LoginSession.expires_at > datetime.now(timezone.utc)
            )
        )

        if login_session is None:
            return False

        user = db.scalar(
            select(User).where(
                User.id == login_session.user_id,
                User.active.is_(True)
            )
        )

        if user is None:
            db.execute(
                delete(LoginSession).where(
                    LoginSession.id == login_session.id
                )
            )
            db.commit()
            return False

        _set_user_session(user)
        return True


def bootstrap_admin():
    username = setting("BOOTSTRAP_ADMIN_USERNAME", "admin").strip()
    password = setting("BOOTSTRAP_ADMIN_PASSWORD", "")

    if not password:
        return

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(User.username == username)
        )

        if existing is None:
            db.add(User(
                username=username,
                password_hash=hash_password(password),
                role="admin"
            ))
            db.commit()


def login_form():
    if st.session_state.get("authenticated"):
        return True

    cookie_manager = get_cookie_manager()
    cookies = cookie_manager.get_all()

    if cookies is None:
        st.info("Načítám přihlášení...")
        st.stop()

    token = cookies.get(COOKIE_NAME)

    if token and _restore_login(token):
        st.rerun()

    st.markdown(
        "<div class='login-wrap'><div class='eyebrow'>SPORT ANALYTICS PLATFORM</div>"
        "<h1>SportStats <span>2.1</span></h1>"
        "<p>Přihlášení do analytického centra</p></div>",
        unsafe_allow_html=True
    )

    with st.form("login"):
        username = st.text_input("Uživatelské jméno")
        password = st.text_input("Heslo", type="password")
        remember = st.checkbox("Zůstat přihlášen/a 30 dní", value=True)
        submitted = st.form_submit_button(
            "Přihlásit se",
            use_container_width=True
        )

    if submitted:
        with SessionLocal() as db:
            user = db.scalar(
                select(User).where(
                    User.username == username.strip(),
                    User.active.is_(True)
                )
            )

            if user and verify_password(password, user.password_hash):
                _set_user_session(user)

                if remember:
                    token = _create_login_session(user.id)
                    cookie_manager.set(
                        COOKIE_NAME,
                        token,
                        expires_at=datetime.now(timezone.utc)
                        + timedelta(days=SESSION_DAYS),
                        key="sportstats_login_cookie"
                    )

                st.rerun()
            else:
                st.error("Neplatné přihlašovací údaje.")

    return False


def logout():
    cookie_manager = get_cookie_manager()
    cookies = cookie_manager.get_all() or {}
    token = cookies.get(COOKIE_NAME)

    if token:
        with SessionLocal() as db:
            db.execute(
                delete(LoginSession).where(
                    LoginSession.token_hash == _token_hash(token)
                )
            )
            db.commit()

    _clear_user_session()

    cookie_manager.delete(COOKIE_NAME)
    st.rerun()
