import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Team, Match
from core.repository import season_options

def render():
    st.markdown('<div class="eyebrow">PERFORMANCE / DATA LAB</div>', unsafe_allow_html=True)
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
            gf=ga=w=d=l=home_gf=home_ga=away_gf=away_ga=0
            for m in games:
                is_home = m.home_team_id == t.id
                a,b=(m.home_score,m.away_score) if is_home else (m.away_score,m.home_score)
                gf+=a; ga+=b
                if is_home: home_gf+=a; home_ga+=b
                else: away_gf+=a; away_ga+=b
                if a>b:w+=1
                elif a==b:d+=1
                else:l+=1
            rows.append({"Tým":t.name,"Zápasy":len(games),"Výhry":w,"Remízy":d,
                         "Prohry":l,"Vstřelené góly":gf,"Obdržené góly":ga,
                         "Rozdíl":gf-ga,"Body":w*3+d,
                         "Průměr gólů":round(gf/len(games),2) if games else 0,
                         "Průměr obdržených":round(ga/len(games),2) if games else 0,
                         "Domácí góly":home_gf,"Domácí inkasované":home_ga,
                         "Venkovní góly":away_gf,"Venkovní inkasované":away_ga})
        df=pd.DataFrame(rows).sort_values(["Body","Rozdíl","Vstřelené góly"],ascending=False)
        best_attack=df.sort_values("Vstřelené góly",ascending=False).iloc[0]
        best_defence=df.sort_values("Obdržené góly",ascending=True).iloc[0]
        a,b,c=st.columns(3)
        a.metric("Nejlepší útok",best_attack["Tým"],f'{int(best_attack["Vstřelené góly"])} gólů')
        b.metric("Nejlepší obrana",best_defence["Tým"],f'{int(best_defence["Obdržené góly"])} inkasovaných')
        c.metric("Odehrané zápasy",len(played))
        st.subheader("Výkonnost týmů")
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.plotly_chart(px.bar(df.sort_values("Vstřelené góly",ascending=False),
            x="Tým",y=["Vstřelené góly","Obdržené góly"],barmode="group",
            title="Vstřelené a obdržené góly"),use_container_width=True)
        st.plotly_chart(px.scatter(df,x="Vstřelené góly",y="Obdržené góly",
            size="Zápasy",color="Tým",hover_data=["Body","Rozdíl"],
            title="Útočná a obranná výkonnost"),use_container_width=True)
        st.subheader("Domácí vs. venkovní výkonnost")
        split=df.melt(id_vars="Tým",value_vars=["Domácí góly","Domácí inkasované",
            "Venkovní góly","Venkovní inkasované"],var_name="Kategorie",value_name="Góly")
        st.plotly_chart(px.bar(split,x="Tým",y="Góly",color="Kategorie",barmode="group",
            title="Domácí a venkovní góly"),use_container_width=True)
