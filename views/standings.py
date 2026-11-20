import streamlit as st
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Team, Match
from core.repository import season_options
from analytics.standings import build_standings


def render():
    st.markdown(
        '<div class="ss-hero"><div class="ss-hero-kicker">LEAGUE CENTER / RANKINGS</div>'
        '<div class="ss-hero-title">Ligové tabulky</div>'
        '<div class="ss-hero-copy">Aktuální pořadí týmů, body a bilance v jednotlivých soutěžích.</div></div>',
        unsafe_allow_html=True,
    )
    opts = season_options()
    if not opts:
        st.info("Zatím nejsou žádné sezóny.")
        return
    sid, label = st.selectbox("Soutěž a sezóna", opts, format_func=lambda x: x[1])
    with SessionLocal() as db:
        teams = list(db.scalars(select(Team).where(Team.season_id == sid)))
        matches = list(db.scalars(select(Match).where(Match.season_id == sid)))
        df = build_standings(teams, matches)
        st.markdown(f'<div class="ss-section-head"><span class="ss-section-mark"></span><div><div class="ss-section-title">{label}</div><div class="ss-section-sub">Oficiální pořadí a bodová bilance soutěže</div></div></div>', unsafe_allow_html=True)
        played = sum(1 for match in matches if match.played)
        c1, c2, c3 = st.columns(3)
        c1.metric("Týmy", len(teams))
        c2.metric("Odehrané zápasy", played)
        c3.metric("Naplánované zápasy", len(matches) - played)
        if df.empty:
            st.info("Zatím nejsou k dispozici data.")
        else:
            df.insert(0, "Pořadí", range(1, len(df) + 1))
            st.dataframe(
                df[["Pořadí", "Tým", "Z", "V", "R", "P", "Skóre", "GD", "Body"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Pořadí": st.column_config.NumberColumn(" #", format="%d"),
                    "Body": st.column_config.NumberColumn("Body", format="%d"),
                    "GD": st.column_config.NumberColumn("Rozdíl", format="%+d"),
                },
            )
            st.caption("Pořadí je vypočítáno z odehraných zápasů podle bodů, rozdílu skóre a vstřelených gólů.")
