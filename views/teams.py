
import streamlit as st
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Team, Match
from core.repository import season_options


def render():
    from core.permissions import require_editor
    require_editor()

    st.markdown(
        '<div class="ss-hero">'
        '<div class="ss-hero-kicker">CLUB MANAGEMENT / SQUADS</div>'
        '<div class="ss-hero-title">Týmy</div>'
        '<div class="ss-hero-copy">'
        'Správa klubů a účastníků jednotlivých soutěží.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    opts = season_options()

    if not opts:
        st.info("Nejprve vytvoř ligu a sezónu.")
        return

    sid, label = st.selectbox(
        "Soutěž a sezóna",
        opts,
        format_func=lambda x: x[1]
    )

    with SessionLocal() as db:
        teams = list(
            db.scalars(
                select(Team)
                .where(Team.season_id == sid)
                .order_by(Team.name)
            )
        )

        matches_count = db.scalar(
            select(__import__("sqlalchemy").func.count(Match.id))
            .where(Match.season_id == sid)
        ) or 0

        st.markdown(
            f'<div class="ss-section-head">'
            f'<span class="ss-section-mark"></span>'
            f'<div><div class="ss-section-title">Soupiska · {label}</div>'
            f'<div class="ss-section-sub">Registrované kluby vybrané soutěže</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="ss-metrics-grid">'
            f'<div class="ss-metric-card">'
            f'<div class="ss-metric-label">Registrované týmy</div>'
            f'<div class="ss-metric-value">{len(teams)}</div>'
            f'</div>'
            f'<div class="ss-metric-card">'
            f'<div class="ss-metric-label">Zápasy soutěže</div>'
            f'<div class="ss-metric-value">{matches_count}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        with st.expander("➕ Přidat nový tým"):
            with st.form("add_team"):
                name = st.text_input(
                    "Název týmu",
                    placeholder="Např. FC Sparta"
                )
                add = st.form_submit_button(
                    "Přidat tým",
                    use_container_width=True
                )

            if add:
                clean = name.strip()

                if not clean:
                    st.error("Název týmu nesmí být prázdný.")
                elif any(
                    team.name.casefold() == clean.casefold()
                    for team in teams
                ):
                    st.error("Tým s tímto názvem už existuje.")
                else:
                    db.add(Team(season_id=sid, name=clean))
                    db.commit()
                    st.success("Tým byl přidán.")
                    st.rerun()

        st.markdown(
            '<div class="ss-section-head">'
            '<span class="ss-section-mark"></span>'
            '<div><div class="ss-section-title">Registrované kluby</div>'
            '<div class="ss-section-sub">Přehled účastníků soutěže</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        if teams:
            for index, team in enumerate(teams, 1):
                with st.container(border=True):
                    st.markdown(
                        f'<div class="ss-mini-label">TÝM {index:02d}</div>'
                        f'<div style="font-size:1.2rem;font-weight:850;'
                        f'margin-top:.35rem;">{team.name}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("V této sezóně zatím nejsou žádné týmy.")

        if teams:
            st.divider()

            st.markdown(
                '<div class="ss-section-head">'
                '<span class="ss-section-mark"></span>'
                '<div><div class="ss-section-title">Správa účastníků</div>'
                '<div class="ss-section-sub">Bezpečné odebrání klubu ze soutěže'
                '</div></div></div>',
                unsafe_allow_html=True,
            )

            with st.expander("🗑️ Odebrat tým"):
                st.warning(
                    "Smazáním týmu se odstraní také všechny jeho "
                    "související zápasy."
                )

                selected = st.selectbox(
                    "Vybrat tým",
                    [team.id for team in teams],
                    format_func=lambda team_id: next(
                        team.name for team in teams
                        if team.id == team_id
                    ),
                )

                confirm = st.checkbox(
                    "Potvrzuji smazání týmu a všech jeho zápasů",
                    key="confirm_team_delete"
                )

                if st.button(
                    "Smazat tým",
                    type="secondary",
                    use_container_width=True,
                    disabled=not confirm
                ):
                    db.query(Match).filter(
                        (Match.home_team_id == selected)
                        | (Match.away_team_id == selected)
                    ).delete(synchronize_session=False)

                    db.query(Team).filter(
                        Team.id == selected
                    ).delete(synchronize_session=False)

                    db.commit()
                    st.success(
                        "Tým a související zápasy byly smazány."
                    )
                    st.rerun()
