import streamlit as st
import plotly.express as px
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Team, Match
from core.repository import season_options
from analytics.predictions import predict_match, elo_ratings

def render():
    st.title("Predikční centrum")
    st.caption("Kombinovaný model Elo + Poisson. Výstupy jsou statistické odhady, nikoliv jisté výsledky.")
    opts=season_options()
    if not opts:
        st.info("Zatím nejsou žádné sezóny."); return
    sid,label=st.selectbox("Soutěž a sezóna",opts,format_func=lambda x:x[1])
    with SessionLocal() as db:
        teams=list(db.scalars(select(Team).where(Team.season_id==sid).order_by(Team.name)))
        matches=list(db.scalars(select(Match).where(Match.season_id==sid)))
        if len(teams)<2:
            st.info("Přidej alespoň dva týmy."); return
        names={t.name:t.id for t in teams}
        c1,c2=st.columns(2)
        home=c1.selectbox("Domácí tým",list(names))
        away=c2.selectbox("Hostující tým",list(names),index=1)
        if home==away:
            st.warning("Vyber dva rozdílné týmy."); return
        if st.button("Vypočítat predikci",type="primary",use_container_width=True):
            result=predict_match(names[home],names[away],teams,matches)
            p=result["probabilities"]
            cols=st.columns(3)
            cols[0].metric("Výhra domácích",f'{p["home"]*100:.1f}%')
            cols[1].metric("Remíza",f'{p["draw"]*100:.1f}%')
            cols[2].metric("Výhra hostů",f'{p["away"]*100:.1f}%')
            st.plotly_chart(px.bar(x=["Domácí","Remíza","Hosté"],
                y=[p["home"]*100,p["draw"]*100,p["away"]*100],
                labels={"x":"Výsledek","y":"Pravděpodobnost (%)"},
                title="Pravděpodobnosti výsledku"),use_container_width=True)
            a,b,c=st.columns(3)
            a.metric("Očekávané góly domácích",f'{result["expected_home_goals"]:.2f}')
            b.metric("Očekávané góly hostů",f'{result["expected_away_goals"]:.2f}')
            c.metric("Nejpravděpodobnější skóre",result["most_likely_score"])
            st.caption(f'Elo rating: {home} {result["elo_home"]:.0f} · {away} {result["elo_away"]:.0f}')
            st.info("Model vychází pouze z dat zadaných do této soutěže a sezóny. Bez dostatečného počtu zápasů jsou odhady silně regresované k průměru.")
        st.divider()
        ratings=elo_ratings(teams,matches)
        rating_rows=[{"Tým":t.name,"Elo":round(ratings.get(t.id,1500))} for t in teams]
        st.subheader("Elo žebříček")
        st.dataframe(sorted(rating_rows,key=lambda x:x["Elo"],reverse=True),use_container_width=True,hide_index=True)
