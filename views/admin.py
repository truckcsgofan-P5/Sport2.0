
import streamlit as st
from sqlalchemy import select, delete

from core.db import SessionLocal
from core.models import User, LoginSession
from core.security import hash_password
from core.migration import import_legacy_json


def render():
    st.title("Administrace")

    from core.permissions import require_admin
    require_admin()

    st.subheader("Uživatelé")

    with st.form("create_user"):
        username = st.text_input("Nové uživatelské jméno")
        password = st.text_input("Dočasné heslo", type="password")
        role = st.selectbox("Role", ["editor", "viewer", "admin"])
        create = st.form_submit_button("Vytvořit uživatele")

    if create:
        with SessionLocal() as db:
            if not username.strip() or len(password) < 12:
                st.error(
                    "Uživatelské jméno je povinné a heslo musí mít alespoň 12 znaků."
                )
            elif db.scalar(
                select(User).where(User.username == username.strip())
            ):
                st.error("Uživatel už existuje.")
            else:
                db.add(User(
                    username=username.strip(),
                    password_hash=hash_password(password),
                    role=role
                ))
                db.commit()
                st.success("Uživatel vytvořen.")
                st.rerun()

    with SessionLocal() as db:
        users = db.scalars(
            select(User).order_by(User.username)
        ).all()

        st.dataframe(
            [
                {"Uživatel": u.username, "Role": u.role, "Aktivní": u.active}
                for u in users
            ],
            use_container_width=True,
            hide_index=True
        )

        usernames = [u.username for u in users]

    st.divider()
    st.subheader("Změna hesla člena")

    if usernames:
        with st.form("reset_user_password"):
            selected_user = st.selectbox("Vyber člena", usernames)
            new_password = st.text_input("Nové heslo", type="password")
            confirm_password = st.text_input(
                "Potvrzení nového hesla",
                type="password"
            )

            change_password = st.form_submit_button("Změnit heslo")

        if change_password:
            if len(new_password) < 12:
                st.error("Nové heslo musí mít alespoň 12 znaků.")
            elif new_password != confirm_password:
                st.error("Zadaná hesla se neshodují.")
            else:
                with SessionLocal() as db:
                    user = db.scalar(
                        select(User).where(User.username == selected_user)
                    )

                    if user is None:
                        st.error("Uživatel nebyl nalezen.")
                    else:
                        user.password_hash = hash_password(new_password)

                        # Zrušení všech zapamatovaných přihlášení uživatele.
                        db.execute(
                            delete(LoginSession).where(
                                LoginSession.user_id == user.id
                            )
                        )

                        db.commit()

                        st.success(
                            f"Heslo uživatele {selected_user} bylo změněno. "
                            "Všechna zapamatovaná přihlášení byla zrušena."
                        )
                        st.rerun()
    else:
        st.info("Zatím nejsou vytvořeni žádní uživatelé.")

    st.divider()
    st.subheader("Import původních dat")

    st.write(
        "Importuje `sports_data.json` z kořenové složky projektu. "
        "Existující záznamy nepřepisuje a duplicitní zápasy podle "
        "sezóny, data a domácího/hostujícího týmu přeskočí."
    )

    if st.button("Spustit import sports_data.json"):
        try:
            result = import_legacy_json()

            if result["status"] == "missing":
                st.warning("Soubor sports_data.json nebyl nalezen.")
            else:
                st.success("Import dokončen.")
                st.json(result)

        except Exception as exc:
            st.error(f"Import selhal: {exc}")
