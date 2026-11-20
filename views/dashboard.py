import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Season, Team, Match
from core.repository import dashboard_metrics, season_options
from analytics.standings import build_standings


def _form(team_id, matches, limit=5):
    played = sorted(
        [m for m in matches if m.played and m.home_score is not None and m.away_score is not None
         and team_id in (m.home_team_id, m.away_team_id)],
        key=lambda m: (m.match_date, m.id), reverse=True
    )[:limit]
    out = []
    for match in reversed(played):
        own, opp = ((match.home_score, match.away_score) if match.home_team_id == team_id
                    else (match.away_score, match.home_score))
        out.append("V" if own > opp else "R" if own == opp else "P")
    return " ".join(out) if out else "—"


def _match_rows(matches):
    return [{
        "Datum": match.match_date,
        "Domácí": match.home_team.name,
        "Výsledek": f"{match.home_score}:{match.away_score}" if match.played else "vs",
        "Hosté": match.away_team.name,
        "Stav": "Odehráno" if match.played else "Naplánováno",
    } for match in matches]


def render():
    st.markdown('<div class="eyebrow">SPORTS INTELLIGENCE / OVERVIEW</div>', unsafe_allow_html=True)
    st.title("SportStats Dashboard")
    st.caption("Centrální přehled soutěží, zápasů a aktuální výkonnosti.")
    metrics = dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Soutěže", metrics["leagues"])
    c2.metric("Týmy", metrics["teams"])
    c3.metric("Zápasy celkem", metrics["matches"])
    c4.metric("Odehráno", metrics["played"], delta=f'{metrics["matches"] - metrics["played"]} čeká')

    options = season_options()
    if not options:
        st.info("Zatím nejsou vytvořené žádné soutěže. Začni v sekci Ligy a sezóny.")
        return
    selected = st.selectbox("Soutěž a sezóna", options, format_func=lambda x: x[1])
    with SessionLocal() as db:
        season = db.get(Season, selected[0])
        matches = list(db.scalars(select(Match).where(Match.season_id == season.id)))
        teams = list(db.scalars(
            select(Team).where(Team.season_id == season.id).order_by(Team.name)
        ))
        played = [m for m in matches if m.played and m.home_score is not None and m.away_score is not None]
        upcoming = [m for m in matches if not m.played]
        recent = sorted(played, key=lambda m: (m.match_date, m.id), reverse=True)[:5]
        next_matches = sorted(upcoming, key=lambda m: (m.match_date, m.id))[:5]

        st.divider()
        left, right = st.columns([1.35, 1])
        with left:
            st.subheader("Forma týmů · posledních 5 zápasů")
            if played and teams:
                table = build_standings(teams, matches)
                table["Forma · posledních 5"] = table.apply(
                    lambda row: _form(
                        next(team.id for team in teams if team.name == row["Tým"]), matches
                    ), axis=1
                )
                st.dataframe(
                    table[["Tým", "Z", "V", "R", "P", "Skóre", "Body", "Forma · posledních 5"]],
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("Po zadání odehraných výsledků se zde zobrazí tabulka a forma týmů.")
        with right:
            st.subheader("Stav sezóny")
            status = pd.DataFrame({
                "Stav": ["Odehráno", "Naplánováno"],
                "Počet": [len(played), len(upcoming)]
            })
            fig = px.pie(
                status, names="Stav", values="Počet", hole=.68,
                color_discrete_sequence=["#48E184", "#315B40"]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#DDEBE1", margin=dict(t=30, b=10, l=10, r=10),
                legend_title_text=""
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Poslední odehrané zápasy")
        if recent:
            st.dataframe(_match_rows(recent), use_container_width=True, hide_index=True)
        else:
            st.info("Zatím nebyl odehrán žádný zápas.")

        st.subheader("Nadcházející zápasy")
        if next_matches:
            st.dataframe(_match_rows(next_matches), use_container_width=True, hide_index=True)
        else:
            st.info("Nejsou naplánované žádné další zápasy.")
