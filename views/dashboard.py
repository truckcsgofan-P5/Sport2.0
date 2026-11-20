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
    return " · ".join(out) if out else "—"


def _match_rows(matches):
    return [{
        "Datum": match.match_date,
        "Domácí": match.home_team.name,
        "Výsledek": f"{match.home_score}:{match.away_score}" if match.played else "VS",
        "Hosté": match.away_team.name,
        "Stav": "Odehráno" if match.played else "Naplánováno",
    } for match in matches]


def render():
    st.markdown(
        '<div class="ss-hero">'
        '<div class="ss-hero-kicker">SPORTS INTELLIGENCE · MATCH CENTER</div>'
        '<div class="ss-hero-title">Přehled soutěží</div>'
        '<p class="ss-hero-copy">Všechno důležité o tvých ligách na jednom místě. '
        'Výsledky, forma týmů a nadcházející zápasy v přehledném centru SportStats.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    metrics = dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Soutěže", metrics["leagues"])
    c2.metric("Týmy", metrics["teams"])
    c3.metric("Zápasy celkem", metrics["matches"])
    c4.metric("Odehráno", metrics["played"], delta=f'{metrics["matches"] - metrics["played"]} zbývá')

    options = season_options()
    if not options:
        st.info("Zatím nejsou vytvořené žádné soutěže. Začni v sekci Ligy a sezóny.")
        return

    selected = st.selectbox("VYBRAT SOUTĚŽ A SEZÓNU", options, format_func=lambda x: x[1])
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
        left, right = st.columns([1.35, 1], gap="large")
        with left:
            st.subheader("Tabulka a aktuální forma")
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
            st.subheader("Průběh sezóny")
            status = pd.DataFrame({
                "Stav": ["Odehráno", "Naplánováno"],
                "Počet": [len(played), len(upcoming)]
            })
            fig = px.pie(
                status, names="Stav", values="Počet", hole=.72,
                color_discrete_sequence=["#56F28F", "#315B40"]
            )
            fig.update_traces(textposition="inside", textinfo="percent")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#DDEBE1", margin=dict(t=22, b=8, l=8, r=8),
                legend_title_text="", height=300,
                annotations=[dict(text=f"{len(played)}<br><span style='font-size:11px'>odehráno</span>",
                                  x=.5, y=.5, showarrow=False, font=dict(size=25, color="#F2F8F3"))]
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        recent_col, upcoming_col = st.columns(2, gap="large")
        with recent_col:
            st.subheader("Poslední výsledky")
            if recent:
                st.dataframe(_match_rows(recent), use_container_width=True, hide_index=True)
            else:
                st.info("Zatím nebyl odehrán žádný zápas.")
        with upcoming_col:
            st.subheader("Nadcházející zápasy")
            if next_matches:
                st.dataframe(_match_rows(next_matches), use_container_width=True, hide_index=True)
            else:
                st.info("Nejsou naplánované žádné další zápasy.")
