
import streamlit as st
from sqlalchemy import select

from core.db import SessionLocal
from core.models import Team, Match
from core.repository import season_options
from analytics.standings import build_standings


def render():
    st.markdown(
        """
        <div class="ss-hero">
            <div class="ss-hero-kicker">LEAGUE CENTER / RANKINGS</div>
            <div class="ss-hero-title">Ligové tabulky</div>
            <div class="ss-hero-copy">
                Aktuální pořadí týmů, body a bilance v jednotlivých soutěžích.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    opts = season_options()

    if not opts:
        st.info("Zatím nejsou žádné sezóny.")
        return

    sid, label = st.selectbox(
        "Soutěž a sezóna",
        opts,
        format_func=lambda x: x[1]
    )

    with SessionLocal() as db:
        teams = list(
            db.scalars(
                select(Team).where(Team.season_id == sid)
            )
        )

        matches = list(
            db.scalars(
                select(Match).where(Match.season_id == sid)
            )
        )

        df = build_standings(teams, matches)

        played = sum(1 for match in matches if match.played)
        planned = len(matches) - played

        st.markdown(
            f"""
            <div class="ss-section-head">
                <div class="ss-section-mark"></div>
                <div>
                    <div class="ss-section-title">{label}</div>
                    <div class="ss-section-sub">
                        Oficiální pořadí a bodová bilance soutěže
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Kompaktní statistiky soutěže
        st.markdown(
            f"""
            <div style="
                display:grid;
                grid-template-columns:repeat(3,minmax(0,1fr));
                gap:8px;
                margin:12px 0 20px;
            ">
                <div class="ss-metric-card">
                    <div class="ss-metric-label">Týmy</div>
                    <div class="ss-metric-value">{len(teams)}</div>
                </div>
                <div class="ss-metric-card">
                    <div class="ss-metric-label">Odehráno</div>
                    <div class="ss-metric-value">{played}</div>
                </div>
                <div class="ss-metric-card">
                    <div class="ss-metric-label">Naplánováno</div>
                    <div class="ss-metric-value">{planned}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if df.empty:
            st.info("Zatím nejsou k dispozici data.")
            return

        df.insert(0, "Pořadí", range(1, len(df) + 1))

        table_df = df[
            ["Pořadí", "Tým", "Z", "V", "R", "P",
             "Skóre", "GD", "Body"]
        ]

        st.markdown(
            """
            <div class="ss-section-head">
                <div class="ss-section-mark"></div>
                <div>
                    <div class="ss-section-title">Ligová tabulka</div>
                    <div class="ss-section-sub">
                        Kompletní pořadí všech týmů
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Mobilní tabulka s vodorovným posouváním
        table_html = table_df.to_html(
            index=False,
            escape=True,
            border=0,
            classes="ss-standings-table"
        )

        st.markdown(
            """
            <style>
            .ss-table-scroll {
                width: 100%;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                border: 1px solid rgba(125,185,145,.20);
                border-radius: 14px;
                background: rgba(10,22,14,.72);
            }

            .ss-standings-table {
                width: 100%;
                min-width: 650px;
                border-collapse: collapse;
                color: #F2F8F3;
                font-size: .9rem;
                white-space: nowrap;
            }

            .ss-standings-table th {
                background: #14251A;
                color: #91A99A;
                font-weight: 750;
                padding: 13px 12px;
                text-align: center;
                border: 1px solid rgba(125,185,145,.16);
                position: sticky;
                top: 0;
            }

            .ss-standings-table td {
                padding: 12px;
                text-align: center;
                border: 1px solid rgba(125,185,145,.13);
            }

            .ss-standings-table td:nth-child(2),
            .ss-standings-table th:nth-child(2) {
                text-align: left;
                min-width: 145px;
            }

            .ss-standings-table td:first-child {
                color: #56F28F;
                font-weight: 800;
            }

            .ss-standings-table td:last-child {
                color: #56F28F;
                font-weight: 850;
            }

            .ss-standings-table tbody tr:nth-child(even) {
                background: rgba(86,242,143,.035);
            }

            @media (max-width: 700px) {
                .ss-standings-table {
                    font-size: .82rem;
                    min-width: 650px;
                }

                .ss-standings-table th,
                .ss-standings-table td {
                    padding: 11px 10px;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="ss-table-scroll">{table_html}</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Na mobilu posuň tabulku vodorovně pro zobrazení všech "
            "statistických sloupců. Pořadí se vypočítává podle bodů, "
            "rozdílu skóre a vstřelených gólů."
        )
