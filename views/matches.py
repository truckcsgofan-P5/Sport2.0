
import streamlit as st
from datetime import date
from html import escape
from sqlalchemy import select, func

from core.db import SessionLocal
from core.models import Team, Match, PredictionEvaluation
from core.repository import season_options
from analytics.predictions import calculate_brier_score


def render():
    from core.permissions import require_editor
    require_editor()

    st.markdown(
        '<div class="ss-hero">'
        '<div class="ss-hero-kicker">FIXTURES / RESULTS CENTER</div>'
        '<div class="ss-hero-title">Zápasy</div>'
        '<div class="ss-hero-copy">'
        'Plánuj utkání, zapisuj výsledky a spravuj odehrané zápasy.'
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
        format_func=lambda x: x[1],
    )

    with SessionLocal() as db:
        teams = list(db.scalars(
            select(Team)
            .where(Team.season_id == sid)
            .order_by(Team.name)
        ))

        if len(teams) < 2:
            st.warning("Pro zadání zápasu přidej alespoň dva týmy.")
            return

        team_map = {t.name: t.id for t in teams}
        team_names = list(team_map.keys())

        matches = list(db.scalars(
            select(Match)
            .where(Match.season_id == sid)
        ))

        upcoming = sorted(
            [m for m in matches if not m.played],
            key=lambda m: m.match_date,
        )

        completed = sorted(
            [m for m in matches if m.played],
            key=lambda m: m.match_date,
            reverse=True,
        )

        today_matches = [
            m for m in matches
            if m.match_date == date.today() and not m.played
        ]

        # Statistiky
        st.markdown(
            '<div class="ss-section-head">'
            '<span class="ss-section-mark"></span>'
            '<div><div class="ss-section-title">Přehled sezóny</div>'
            '<div class="ss-section-sub">Aktuální stav zápasů</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )

        stats = [
            ("Všechny zápasy", len(matches)),
            ("Odehrané", len(completed)),
            ("Naplánované", len(upcoming)),
            ("Dnes", len(today_matches)),
        ]

        cols = st.columns(4)
        for col, (name, value) in zip(cols, stats):
            with col:
                st.markdown(
                    f'<div class="ss-stat-card">'
                    f'<div class="ss-stat-label">{escape(name)}</div>'
                    f'<div class="ss-stat-value">{value}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Nový zápas
        st.markdown(
            '<div class="ss-divider"></div>'
            '<div class="ss-section-head">'
            '<span class="ss-section-mark"></span>'
            '<div><div class="ss-section-title">Nové utkání</div>'
            '<div class="ss-section-sub">'
            'Naplánuj duel nebo rovnou zapiš konečný výsledek'
            '</div></div></div>',
            unsafe_allow_html=True,
        )

        with st.expander("＋ Přidat nový zápas", expanded=False):
            with st.form("create_match"):
                match_date = st.date_input(
                    "Datum",
                    value=date.today(),
                    key="new_match_date",
                )

                c1, c2 = st.columns(2)
                home = c1.selectbox(
                    "Domácí tým",
                    team_names,
                    key="new_home",
                )
                away = c2.selectbox(
                    "Hostující tým",
                    team_names,
                    index=1,
                    key="new_away",
                )

                played = st.checkbox(
                    "Zápas je odehraný",
                    key="new_played",
                )

                s1, s2 = st.columns(2)
                hs = s1.number_input(
                    "Góly domácích",
                    min_value=0,
                    value=0,
                    step=1,
                    key="new_home_score",
                )
                aws = s2.number_input(
                    "Góly hostů",
                    min_value=0,
                    value=0,
                    step=1,
                    key="new_away_score",
                )

                notes = st.text_input(
                    "Poznámka (nepovinné)",
                    key="new_notes",
                )

                submit = st.form_submit_button(
                    "Uložit zápas",
                    use_container_width=True,
                )

            if submit:
                if home == away:
                    st.error(
                        "Domácí a hostující tým musí být rozdílné."
                    )
                else:
                    db.add(Match(
                        season_id=sid,
                        match_date=match_date,
                        home_team_id=team_map[home],
                        away_team_id=team_map[away],
                        home_score=int(hs) if played else None,
                        away_score=int(aws) if played else None,
                        played=played,
                        notes=notes.strip(),
                    ))
                    db.commit()
                    st.success("Zápas byl uložen.")
                    st.rerun()

        # Program a výsledky
        st.markdown(
            '<div class="ss-divider"></div>'
            '<div class="ss-section-head">'
            '<span class="ss-section-mark"></span>'
            '<div><div class="ss-section-title">Program a výsledky</div>'
            '<div class="ss-section-sub">'
            'Přehled všech utkání vybrané sezóny'
            '</div></div></div>',
            unsafe_allow_html=True,
        )

        tab_upcoming, tab_completed = st.tabs([
            f"◷ Neodehrané ({len(upcoming)})",
            f"✓ Odehrané ({len(completed)})",
        ])

        def render_match_cards(match_list):
            if not match_list:
                st.info("V této kategorii zatím nejsou žádné zápasy.")
                return

            for m in match_list:
                home_name = escape(m.home_team.name)
                away_name = escape(m.away_team.name)

                result = (
                    f"{m.home_score} : {m.away_score}"
                    if m.played else "VS"
                )

                status = (
                    "✓ ODEHRÁNO"
                    if m.played else "◷ NAPLÁNOVÁNO"
                )

                result_html = escape(str(result))
                date_html = escape(str(m.match_date))

                st.markdown(
                    f'<div class="ss-match-card">'
                    f'<div class="ss-match-top">'
                    f'<span>{date_html}</span>'
                    f'<span>{status}</span>'
                    f'</div>'
                    f'<div class="ss-match-body">'
                    f'<div class="ss-match-team">{home_name}</div>'
                    f'<div class="ss-match-result">{result_html}</div>'
                    f'<div class="ss-match-team">{away_name}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if m.notes:
                    st.caption(f"Poznámka: {m.notes}")

        with tab_upcoming:
            render_match_cards(upcoming)

        with tab_completed:
            render_match_cards(completed)

        # Úprava zápasů
        if matches:
            st.markdown(
                '<div class="ss-divider"></div>'
                '<div class="ss-section-head">'
                '<span class="ss-section-mark"></span>'
                '<div><div class="ss-section-title">'
                'Správa zápasů'
                '</div><div class="ss-section-sub">'
                'Úprava, oprava výsledků a mazání utkání'
                '</div></div></div>',
                unsafe_allow_html=True,
            )

            ordered_matches = upcoming + completed

            edit_id = st.selectbox(
                "Vyber zápas",
                [m.id for m in ordered_matches],
                format_func=lambda mid: next(
                    f"{'◷' if not m.played else '✓'} "
                    f"#{m.id} · {m.match_date} · "
                    f"{m.home_team.name} – {m.away_team.name}"
                    for m in ordered_matches if m.id == mid
                ),
            )

            match = db.get(Match, edit_id)

            if match is not None:
                with st.expander("✎ Upravit vybraný zápas", expanded=True):
                    with st.form("edit_match"):
                        new_date = st.date_input(
                            "Datum zápasu",
                            value=match.match_date,
                        )

                        home_current = next(
                            t.name for t in teams
                            if t.id == match.home_team_id
                        )
                        away_current = next(
                            t.name for t in teams
                            if t.id == match.away_team_id
                        )

                        ec1, ec2 = st.columns(2)
                        new_home = ec1.selectbox(
                            "Domácí tým",
                            team_names,
                            index=team_names.index(home_current),
                        )
                        new_away = ec2.selectbox(
                            "Hostující tým",
                            team_names,
                            index=team_names.index(away_current),
                        )

                        new_played = st.checkbox(
                            "Zápas je odehraný",
                            value=match.played,
                        )

                        sc1, sc2 = st.columns(2)
                        new_hs = sc1.number_input(
                            "Góly domácích",
                            min_value=0,
                            value=match.home_score or 0,
                            step=1,
                        )
                        new_as = sc2.number_input(
                            "Góly hostů",
                            min_value=0,
                            value=match.away_score or 0,
                            step=1,
                        )

                        new_notes = st.text_input(
                            "Poznámka",
                            value=match.notes or "",
                        )

                        save = st.form_submit_button(
                            "Uložit změny",
                            use_container_width=True,
                        )

                    if save:
                        if new_home == new_away:
                            st.error(
                                "Domácí a hostující tým musí být rozdílné."
                            )
                        else:
                            match.match_date = new_date
                            match.home_team_id = team_map[new_home]
                            match.away_team_id = team_map[new_away]
                            match.played = new_played
                            match.home_score = (
                                int(new_hs) if new_played else None
                            )
                            match.away_score = (
                                int(new_as) if new_played else None
                            )
                            match.notes = new_notes.strip()

                            evaluation = db.scalar(
                                select(PredictionEvaluation).where(
                                    PredictionEvaluation.match_id
                                    == match.id
                                )
                            )

                            if evaluation is not None:
                                if new_played:
                                    evaluation.brier_score = (
                                        calculate_brier_score(
                                            evaluation.p_home,
                                            evaluation.p_draw,
                                            evaluation.p_away,
                                            match.home_score,
                                            match.away_score,
                                        )
                                    )
                                else:
                                    evaluation.brier_score = None

                            db.commit()

                            if evaluation is not None and new_played:
                                st.success(
                                    "Výsledek uložen. "
                                    f"Brier skóre: "
                                    f"{evaluation.brier_score:.4f}."
                                )
                            else:
                                st.success("Změny byly uloženy.")

                            st.rerun()

                with st.expander("Smazat zápas", expanded=False):
                    st.warning(
                        "Tato akce je nevratná. "
                        "Zápas bude odstraněn z databáze."
                    )

                    confirm_delete = st.checkbox(
                        "Opravdu chci tento zápas smazat.",
                        key=f"confirm_delete_{match.id}",
                    )

                    if st.button(
                        "Smazat vybraný zápas",
                        type="secondary",
                        disabled=not confirm_delete,
                        use_container_width=True,
                    ):
                        db.delete(match)
                        db.commit()
                        st.success("Zápas byl smazán.")
                        st.rerun()
