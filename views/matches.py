import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Season, Team, Match
from core.repository import season_options

def render():
    from core.permissions import require_editor
    require_editor()
    st.title("Zápasy")
    opts = season_options()
    if not opts:
        st.info("Nejprve vytvoř ligu a sezónu."); return
    sid, label = st.selectbox("Soutěž a sezóna", opts, format_func=lambda x:x[1])
    with SessionLocal() as db:
        teams = list(db.scalars(select(Team).where(Team.season_id == sid).order_by(Team.name)))
        if len(teams) < 2:
            st.warning("Pro zadání zápasu přidej alespoň dva týmy."); return
        team_map = {t.name:t.id for t in teams}
        with st.form("create_match"):
            st.subheader("Naplánovat zápas / zadat výsledek")
            match_date = st.date_input("Datum", value=date.today())
            c1,c2 = st.columns(2)
            home = c1.selectbox("Domácí", list(team_map))
            away = c2.selectbox("Hosté", list(team_map), index=1)
            played = st.checkbox("Zápas je odehraný")
            s1,s2 = st.columns(2)
            hs = s1.number_input("Góly domácích", min_value=0, value=0, disabled=not played)
            aws = s2.number_input("Góly hostů", min_value=0, value=0, disabled=not played)
            notes = st.text_input("Poznámka (nepovinné)")
            submit = st.form_submit_button("Uložit zápas")
        if submit:
            if home == away:
                st.error("Domácí a hostující tým musí být rozdílné.")
            else:
                db.add(Match(season_id=sid, match_date=match_date,
                    home_team_id=team_map[home], away_team_id=team_map[away],
                    home_score=int(hs) if played else None,
                    away_score=int(aws) if played else None,
                    played=played, notes=notes.strip()))
                db.commit(); st.success("Zápas uložen."); st.rerun()
        st.divider()
        matches = list(db.scalars(select(Match).where(Match.season_id == sid).order_by(Match.match_date.desc())))
        rows = [{"ID":m.id,"Datum":m.match_date,"Domácí":m.home_team.name,
                 "Výsledek":f"{m.home_score}:{m.away_score}" if m.played else "–",
                 "Hosté":m.away_team.name,"Stav":"Odehráno" if m.played else "Naplánováno",
                 "Poznámka":m.notes} for m in matches]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if matches:
            ids = [m.id for m in matches]
            edit_id = st.selectbox("Zápas k úpravě / smazání", ids,
                format_func=lambda mid: next(f"#{m.id} · {m.match_date} · {m.home_team.name} – {m.away_team.name}" for m in matches if m.id == mid))
            match = db.get(Match, edit_id)
            with st.form("edit_match"):
                new_date = st.date_input("Datum zápasu", value=match.match_date)
                new_played = st.checkbox("Odehráno", value=match.played)
                ec1,ec2 = st.columns(2)
                new_hs = ec1.number_input("Góly domácích", min_value=0, value=match.home_score or 0, disabled=not new_played)
                new_as = ec2.number_input("Góly hostů", min_value=0, value=match.away_score or 0, disabled=not new_played)
                new_notes = st.text_input("Poznámka", value=match.notes or "")
                save = st.form_submit_button("Uložit změny")
            if save:
                match.match_date = new_date; match.played = new_played
                match.home_score = int(new_hs) if new_played else None
                match.away_score = int(new_as) if new_played else None
                match.notes = new_notes.strip()
                db.commit(); st.success("Změny uloženy."); st.rerun()
            if st.button("Smazat vybraný zápas"):
                db.delete(match); db.commit(); st.success("Zápas smazán."); st.rerun()
