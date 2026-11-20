import streamlit as st
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Team, Match
from core.repository import season_options


def render():
    from core.permissions import require_editor
    require_editor()
    st.markdown(
        '<div class="ss-hero"><div class="ss-hero-kicker">CLUB MANAGEMENT / SQUADS</div>'
        '<div class="ss-hero-title">Týmy</div>'
        '<div class="ss-hero-copy">Správa klubů a účastníků vybrané soutěže.</div></div>',
        unsafe_allow_html=True,
    )
    opts = season_options()
    if not opts:
        st.info("Nejprve vytvoř ligu a sezónu.")
        return
    sid, label = st.selectbox("Soutěž a sezóna", opts, format_func=lambda x: x[1])
    with SessionLocal() as db:
        teams = list(db.scalars(select(Team).where(Team.season_id == sid).order_by(Team.name)))
        st.markdown(f"### Soupiska · {label}")
        left, right = st.columns([1, 1.6], gap="large")
        with left:
            st.metric("Počet týmů", len(teams))
            with st.form("add_team"):
                st.markdown("#### Přidat nový tým")
                name = st.text_input("Název týmu", placeholder="Např. FC Sparta")
                add = st.form_submit_button("＋ Přidat tým", use_container_width=True)
            if add:
                clean = name.strip()
                if not clean:
                    st.error("Název nesmí být prázdný.")
                elif any(t.name.casefold() == clean.casefold() for t in teams):
                    st.error("Tým s tímto názvem už existuje.")
                else:
                    db.add(Team(season_id=sid, name=clean))
                    db.commit()
                    st.success("Tým přidán.")
                    st.rerun()
        with right:
            st.markdown("#### Přehled klubů")
            if teams:
                st.dataframe(
                    [{"#": i, "Tým": team.name, "Soutěž": label} for i, team in enumerate(teams, 1)],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("V této sezóně zatím nejsou žádné týmy.")
        if teams:
            st.divider()
            st.markdown("#### Odebrání týmu")
            st.warning("Smazáním týmu se odstraní také všechny jeho související zápasy.")
            selected = st.selectbox(
                "Vybrat tým ke smazání",
                [t.id for t in teams],
                format_func=lambda tid: next(t.name for t in teams if t.id == tid),
            )
            confirm = st.checkbox("Potvrzuji smazání týmu a všech jeho zápasů", key="confirm_team_delete")
            if st.button("Smazat tým", type="secondary", disabled=not confirm):
                db.query(Match).filter(
                    (Match.home_team_id == selected) | (Match.away_team_id == selected)
                ).delete(synchronize_session=False)
                db.query(Team).filter(Team.id == selected).delete()
                db.commit()
                st.success("Tým a související zápasy byly smazány.")
                st.rerun()
