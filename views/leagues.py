import streamlit as st
from sqlalchemy import select
from core.db import SessionLocal
from core.models import League, Season

def render():
    from core.permissions import require_editor
    require_editor()
    st.title("Ligy a sezóny")
    with st.expander("Vytvořit ligu", expanded=False):
        with st.form("new_league"):
            name = st.text_input("Název ligy")
            country = st.text_input("Země")
            ok = st.form_submit_button("Vytvořit ligu")
        if ok:
            clean = name.strip()
            if not clean:
                st.error("Zadej název.")
            else:
                with SessionLocal() as db:
                    exists = db.scalar(select(League).where(League.name == clean))
                    if exists:
                        st.error("Liga už existuje.")
                    else:
                        db.add(League(name=clean, country=country.strip()))
                        db.commit()
                        st.success("Liga vytvořena.")
                        st.rerun()
    with SessionLocal() as db:
        leagues = db.scalars(select(League).order_by(League.name)).all()
        for league in leagues:
            with st.container(border=True):
                st.subheader(league.name)
                st.caption(league.country or "Země neuvedena")
                seasons = list(db.scalars(select(Season).where(Season.league_id == league.id).order_by(Season.name.desc())))
                st.write("Sezóny: " + (", ".join(s.name for s in seasons) if seasons else "zatím žádné"))
                with st.form(f"season_{league.id}"):
                    new_season = st.text_input("Nová sezóna", key=f"season_name_{league.id}", placeholder="2026/2027")
                    add = st.form_submit_button("Přidat sezónu")
                if add:
                    clean = new_season.strip()
                    if clean and not any(s.name == clean for s in seasons):
                        db.add(Season(league_id=league.id, name=clean)); db.commit()
                        st.success("Sezóna přidána."); st.rerun()
                    else:
                        st.error("Zadej nový a platný název sezóny.")
