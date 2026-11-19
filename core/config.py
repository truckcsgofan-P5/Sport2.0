"""Centralized configuration for local .env and Streamlit Cloud secrets."""
import os


def setting(name: str, default: str = "") -> str:
    """Read a setting from environment first, then Streamlit secrets."""
    value = os.getenv(name)
    if value is not None and value != "":
        return str(value)
    try:
        import streamlit as st
        value = st.secrets.get(name, default)
        return str(value) if value is not None else default
    except Exception:
        # Streamlit secrets are unavailable during local scripts/tests.
        return default
