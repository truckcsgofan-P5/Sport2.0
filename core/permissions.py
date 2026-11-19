import streamlit as st

def require_editor():
    if st.session_state.get("role") not in {"editor", "admin"}:
        st.error("K této akci nemáš oprávnění. Je vyžadována role editor nebo admin.")
        st.stop()

def require_admin():
    if st.session_state.get("role") != "admin":
        st.error("Tato akce je dostupná pouze administrátorovi.")
        st.stop()
