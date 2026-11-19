import streamlit as st
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Season, Team, Match
from core.repository import season_options
from analytics.standings import build_standings

def render():
    st.title("Ligové tabulky")
    opts = season_options()
    if not opts:
        st.info("Zatím nejsou žádné sezóny."); return
    sid,label = st.selectbox("Soutěž a sezóna", opts, format_func=lambda x:x[1])
    with SessionLocal() as db:
        teams = list(db.scalars(select(Team).where(Team.season_id == sid)))
        matches = list(db.scalars(select(Match).where(Match.season_id == sid)))
        df = build_standings(teams,matches)
        st.subheader(label)
        if df.empty: st.info("Zatím nejsou k dispozici data.")
        else:
            df.insert(0,"Pořadí",range(1,len(df)+1))
            st.dataframe(df[["Pořadí","Tým","Z","V","R","P","Skóre","GD","Body"]],
                         use_container_width=True,hide_index=True)
