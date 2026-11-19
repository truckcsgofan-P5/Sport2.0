import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import select
from core.db import SessionLocal
from core.models import League, Season, Team, Match
from core.repository import dashboard_metrics, season_options

def render():
    st.title("Přehled")
    st.caption("Centrální přehled soutěží, zápasů a výkonnosti.")
    m = dashboard_metrics()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Soutěže", m["leagues"])
    c2.metric("Týmy", m["teams"])
    c3.metric("Zápasy celkem", m["matches"])
    c4.metric("Odehrané zápasy", m["played"])
    options = season_options()
    if not options:
        st.info("Zatím nejsou vytvořené žádné soutěže. Začni v sekci Ligy.")
        return
    selected = st.selectbox("Soutěž a sezóna", options, format_func=lambda x: x[1])
    with SessionLocal() as db:
        season = db.get(Season, selected[0])
        matches = list(db.scalars(select(Match).where(Match.season_id == season.id)))
        rows = []
        for match in matches:
            rows.append({
                "Datum": match.match_date,
                "Domácí": match.home_team.name,
                "Výsledek": f"{match.home_score}:{match.away_score}" if match.played else "–",
                "Hosté": match.away_team.name,
                "Stav": "Odehráno" if match.played else "Naplánováno",
            })
        df = pd.DataFrame(rows)
    if not df.empty:
        st.subheader("Poslední a nadcházející zápasy")
        st.dataframe(df.sort_values("Datum", ascending=False), use_container_width=True, hide_index=True)
        counts = df["Stav"].value_counts().rename_axis("Stav").reset_index(name="Počet")
        st.plotly_chart(px.pie(counts, names="Stav", values="Počet", hole=.62,
                               title="Rozložení zápasů"), use_container_width=True)
