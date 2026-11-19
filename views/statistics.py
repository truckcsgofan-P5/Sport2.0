import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Team, Match
from core.repository import season_options

def render():
    st.title("Statistiky a analytika")
    opts = season_options()
    if not opts:
        st.info("Zatím nejsou žádné sezóny."); return
    sid,label = st.selectbox("Soutěž a sezóna",opts,format_func=lambda x:x[1])
    with SessionLocal() as db:
        teams = list(db.scalars(select(Team).where(Team.season_id==sid).order_by(Team.name)))
        matches = list(db.scalars(select(Match).where(Match.season_id==sid)))
        played = [m for m in matches if m.played and m.home_score is not None and m.away_score is not None]
        if not played:
            st.info("Pro statistiky je potřeba alespoň jeden odehraný zápas."); return
        rows=[]
        for t in teams:
            games=[m for m in played if t.id in (m.home_team_id,m.away_team_id)]
            gf=ga=w=d=l=0
            for m in games:
                if m.home_team_id==t.id: a,b=m.home_score,m.away_score
                else: a,b=m.away_score,m.home_score
                gf+=a;ga+=b
                if a>b:w+=1
                elif a==b:d+=1
                else:l+=1
            rows.append({"Tým":t.name,"Zápasy":len(games),"Výhry":w,"Remízy":d,
                         "Prohry":l,"Vstřelené góly":gf,"Obdržené góly":ga,
                         "Průměr gólů":round(gf/len(games),2) if games else 0})
        df=pd.DataFrame(rows)
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.plotly_chart(px.bar(df.sort_values("Vstřelené góly",ascending=False),
            x="Tým",y="Vstřelené góly",title="Vstřelené góly podle týmů"),use_container_width=True)
        st.plotly_chart(px.scatter(df,x="Vstřelené góly",y="Obdržené góly",
            size="Zápasy",color="Tým",title="Útočná a obranná výkonnost"),use_container_width=True)
