import streamlit as st
import plotly.express as px
from sqlalchemy import select
from datetime import datetime
from core.db import SessionLocal
from core.models import Team, Match, PredictionEvaluation
from core.repository import season_options
from analytics.predictions import predict_match, elo_ratings


def render():
    st.markdown(
        '<div class="ss-hero"><div class="ss-hero-kicker">MATCH INTELLIGENCE / ELO + POISSON</div>'
        '<div class="ss-hero-title">Predikční centrum</div>'
        '<div class="ss-hero-copy">Pravděpodobnostní odhady výsledků, očekávané góly a síla týmů.</div></div>',
        unsafe_allow_html=True,
    )
    st.caption("Model Elo + Poisson. Výstupy jsou statistické odhady, nikoliv jisté výsledky.")
    opts = season_options()
    if not opts:
        st.info("Zatím nejsou žádné sezóny.")
        return
    sid, label = st.selectbox("Soutěž a sezóna", opts, format_func=lambda x: x[1])
    with SessionLocal() as db:
        teams = list(db.scalars(select(Team).where(Team.season_id == sid).order_by(Team.name)))
        matches = list(db.scalars(select(Match).where(Match.season_id == sid)))
        if len(teams) < 2:
            st.info("Přidej alespoň dva týmy.")
            return

        upcoming = sorted(
            [m for m in matches if not m.played],
            key=lambda m: (m.match_date, m.id)
        )
        selected_match = None
        if upcoming:
            selected_id = st.selectbox(
                "Naplánovaný zápas (predikce se uloží do historie)",
                [m.id for m in upcoming],
                format_func=lambda mid: next(
                    f"#{m.id} · {m.match_date} · {m.home_team.name} – {m.away_team.name}"
                    for m in upcoming if m.id == mid
                )
            )
            selected_match = db.get(Match, selected_id)
            home_id, away_id = selected_match.home_team_id, selected_match.away_team_id
            home_name, away_name = selected_match.home_team.name, selected_match.away_team.name
        else:
            st.info("V této sezóně není naplánovaný zápas. Můžeš si vyzkoušet nezávaznou predikci dvojice týmů.")
            names = {t.name: t.id for t in teams}
            c1, c2 = st.columns(2)
            home_name = c1.selectbox("Domácí tým", list(names))
            away_options = [name for name in names if name != home_name]
            away_name = c2.selectbox("Hostující tým", away_options)
            home_id, away_id = names[home_name], names[away_name]

        if st.button("Vypočítat predikci", type="primary", use_container_width=True):
            result = predict_match(home_id, away_id, teams, matches)
            p = result["probabilities"]
            if selected_match is not None:
                evaluation = db.scalar(select(PredictionEvaluation).where(
                    PredictionEvaluation.match_id == selected_match.id
                ))
                if evaluation is None:
                    evaluation = PredictionEvaluation(match_id=selected_match.id)
                    db.add(evaluation)
                evaluation.p_home = p["home"]
                evaluation.p_draw = p["draw"]
                evaluation.p_away = p["away"]
                evaluation.predicted_at = datetime.utcnow()
                evaluation.brier_score = None
                db.commit()
                st.success("Predikce byla uložena. Po zadání výsledku se automaticky vyhodnotí její přesnost.")

            cols = st.columns(3)
            cols[0].metric("Výhra domácích", f'{p["home"] * 100:.1f}%')
            cols[1].metric("Remíza", f'{p["draw"] * 100:.1f}%')
            cols[2].metric("Výhra hostů", f'{p["away"] * 100:.1f}%')
            st.plotly_chart(px.bar(
                x=["Domácí", "Remíza", "Hosté"],
                y=[p["home"] * 100, p["draw"] * 100, p["away"] * 100],
                labels={"x": "Výsledek", "y": "Pravděpodobnost (%)"},
                title="Pravděpodobnosti výsledku"
            ), use_container_width=True)
            a, b, c = st.columns(3)
            a.metric("Očekávané góly domácích", f'{result["expected_home_goals"]:.2f}')
            b.metric("Očekávané góly hostů", f'{result["expected_away_goals"]:.2f}')
            c.metric("Nejpravděpodobnější skóre", result["most_likely_score"])
            st.caption(f'Elo rating: {home_name} {result["elo_home"]:.0f} · {away_name} {result["elo_away"]:.0f}')
            st.info("Model vychází pouze z dat zadaných do této soutěže a sezóny. Bez dostatečného počtu zápasů jsou odhady silně regresované k průměru.")

        st.divider()
        ratings = elo_ratings(teams, matches)
        rating_rows = [{"Tým": t.name, "Elo": round(ratings.get(t.id, 1500))} for t in teams]
        st.markdown('<div class="ss-section-head"><span class="ss-section-mark"></span><div><div class="ss-section-title">Elo žebříček</div><div class="ss-section-sub">Relativní síla týmů podle historických výsledků</div></div></div>', unsafe_allow_html=True)
        st.dataframe(sorted(rating_rows, key=lambda x: x["Elo"], reverse=True),
                     use_container_width=True, hide_index=True)
