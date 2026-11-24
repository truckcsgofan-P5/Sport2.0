
import streamlit as st
from sqlalchemy import select, func

from core.db import SessionLocal
from core.models import League, Season, Team, Match


def render():
    from core.permissions import require_editor
    require_editor()

    st.markdown(
        """
        <div class="ss-hero">
            <div class="ss-hero-kicker">COMPETITIONS / SEASON MANAGEMENT</div>
            <div class="ss-hero-title">Správa lig a sezón</div>
            <p class="ss-hero-copy">
                Kompletní správa soutěží, sezón a jejich struktury
                na jednom místě.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Souhrn soutěží
    with SessionLocal() as db:
        leagues_count = db.scalar(
            select(func.count(League.id))
        ) or 0

        seasons_count = db.scalar(
            select(func.count(Season.id))
        ) or 0

        teams_count = db.scalar(
            select(func.count(Team.id))
        ) or 0

    st.markdown(
        f"""
        <div class="ss-metrics-grid">
            <div class="ss-metric-card">
                <div class="ss-metric-label">Soutěže</div>
                <div class="ss-metric-value">{leagues_count}</div>
                <div class="ss-metric-note">Registrované ligy</div>
            </div>
            <div class="ss-metric-card">
                <div class="ss-metric-label">Sezóny</div>
                <div class="ss-metric-value">{seasons_count}</div>
                <div class="ss-metric-note">Všechny ročníky</div>
            </div>
            <div class="ss-metric-card">
                <div class="ss-metric-label">Týmy</div>
                <div class="ss-metric-value">{teams_count}</div>
                <div class="ss-metric-note">Registrované týmy</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="ss-section-head">'
        '<div class="ss-section-mark"></div>'
        '<div><div class="ss-section-title">Vytvoření soutěže</div>'
        '<div class="ss-section-sub">Přidání nové ligy do SportStats</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    with st.expander("➕ Vytvořit novou ligu"):
        with st.form("new_league"):
            name = st.text_input("Název ligy")
            country = st.text_input("Země")
            create = st.form_submit_button(
                "Vytvořit ligu",
                use_container_width=True
            )

        if create:
            clean = name.strip()

            if not clean:
                st.error("Zadej název ligy.")
            else:
                with SessionLocal() as db:
                    exists = db.scalar(
                        select(League).where(League.name == clean)
                    )

                    if exists:
                        st.error("Liga už existuje.")
                    else:
                        db.add(
                            League(
                                name=clean,
                                country=country.strip()
                            )
                        )
                        db.commit()
                        st.success("Liga byla vytvořena.")
                        st.rerun()

    st.markdown(
        '<div class="ss-divider"></div>'
        '<div class="ss-section-head">'
        '<div class="ss-section-mark"></div>'
        '<div><div class="ss-section-title">Registrované soutěže</div>'
        '<div class="ss-section-sub">Přehled všech lig a jejich sezón</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    with SessionLocal() as db:
        leagues = db.scalars(
            select(League).order_by(League.name)
        ).all()

        if not leagues:
            st.info("Zatím nejsou vytvořeny žádné ligy.")

        for league in leagues:
            seasons = db.scalars(
                select(Season)
                .where(Season.league_id == league.id)
                .order_by(Season.name.desc())
            ).all()

            total_teams = db.scalar(
                select(func.count(Team.id))
                .join(Season, Team.season_id == Season.id)
                .where(Season.league_id == league.id)
            ) or 0

            total_matches = db.scalar(
                select(func.count(Match.id))
                .join(Season, Match.season_id == Season.id)
                .where(Season.league_id == league.id)
            ) or 0

            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="ss-hero-kicker">LEAGUE / COMPETITION</div>
                    <div style="font-size:1.55rem;font-weight:850;
                    letter-spacing:-.04em;color:#F2F8F3;margin:.3rem 0;">
                        {league.name}
                    </div>
                    <div style="color:#91A99A;font-size:.9rem;">
                        🌍 {league.country or "Země neuvedena"}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Souhrn ligy
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("Sezóny", len(seasons))

                with c2:
                    st.metric("Týmy", total_teams)

                with c3:
                    st.metric("Zápasy", total_matches)

                with st.expander("✏️ Upravit ligu"):
                    with st.form(f"edit_league_{league.id}"):
                        edited_name = st.text_input(
                            "Název ligy",
                            value=league.name,
                            key=f"edit_name_{league.id}"
                        )

                        edited_country = st.text_input(
                            "Země",
                            value=league.country or "",
                            key=f"edit_country_{league.id}"
                        )

                        save = st.form_submit_button(
                            "Uložit změny",
                            use_container_width=True
                        )

                    if save:
                        clean = edited_name.strip()

                        duplicate = db.scalar(
                            select(League).where(
                                League.name == clean,
                                League.id != league.id
                            )
                        )

                        if not clean:
                            st.error("Název ligy nesmí být prázdný.")
                        elif duplicate:
                            st.error("Liga s tímto názvem už existuje.")
                        else:
                            league.name = clean
                            league.country = edited_country.strip()
                            db.commit()
                            st.success("Liga byla upravena.")
                            st.rerun()

                st.markdown(
                    '<div class="ss-section-head">'
                    '<div class="ss-section-mark"></div>'
                    '<div><div class="ss-section-title">Sezóny</div>'
                    '<div class="ss-section-sub">Ročníky této soutěže</div>'
                    '</div></div>',
                    unsafe_allow_html=True
                )

                for season in seasons:
                    teams_count = db.scalar(
                        select(func.count(Team.id)).where(
                            Team.season_id == season.id
                        )
                    ) or 0

                    matches_count = db.scalar(
                        select(func.count(Match.id)).where(
                            Match.season_id == season.id
                        )
                    ) or 0

                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style="font-size:1.15rem;font-weight:800;
                            color:#F2F8F3;margin-bottom:.7rem;">
                                📅 {season.name}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        sc1, sc2 = st.columns(2)

                        with sc1:
                            st.metric("Týmy", teams_count)

                        with sc2:
                            st.metric("Zápasy", matches_count)

                        with st.expander("Správa sezóny"):
                            with st.form(f"edit_season_{season.id}"):
                                new_name = st.text_input(
                                    "Název sezóny",
                                    value=season.name,
                                    key=f"season_edit_{season.id}"
                                )

                                update = st.form_submit_button(
                                    "Uložit sezónu",
                                    use_container_width=True
                                )

                            if update:
                                clean = new_name.strip()

                                duplicate = db.scalar(
                                    select(Season).where(
                                        Season.league_id == league.id,
                                        Season.name == clean,
                                        Season.id != season.id
                                    )
                                )

                                if not clean:
                                    st.error(
                                        "Název sezóny nesmí být prázdný."
                                    )
                                elif duplicate:
                                    st.error(
                                        "Tato sezóna už existuje."
                                    )
                                else:
                                    season.name = clean
                                    db.commit()
                                    st.success("Sezóna byla upravena.")
                                    st.rerun()

                            if teams_count or matches_count:
                                st.warning(
                                    "Tuto sezónu nelze smazat. Obsahuje "
                                    "týmy nebo zápasy. Historická data "
                                    "jsou chráněna."
                                )
                            else:
                                confirm = st.checkbox(
                                    "Potvrzuji smazání této sezóny",
                                    key=f"confirm_season_{season.id}"
                                )

                                if st.button(
                                    "🗑️ Smazat sezónu",
                                    key=f"delete_season_{season.id}",
                                    use_container_width=True
                                ):
                                    if confirm:
                                        db.delete(season)
                                        db.commit()
                                        st.success(
                                            "Sezóna byla smazána."
                                        )
                                        st.rerun()
                                    else:
                                        st.error(
                                            "Nejdříve potvrď smazání."
                                        )

                # Přidání sezóny
                with st.expander("➕ Přidat novou sezónu"):
                    with st.form(f"add_season_{league.id}"):
                        season_name = st.text_input(
                            "Název sezóny",
                            placeholder="2026/2027",
                            key=f"new_season_{league.id}"
                        )

                        add = st.form_submit_button(
                            "Přidat sezónu",
                            use_container_width=True
                        )

                    if add:
                        clean = season_name.strip()

                        exists = db.scalar(
                            select(Season).where(
                                Season.league_id == league.id,
                                Season.name == clean
                            )
                        )

                        if not clean:
                            st.error("Zadej název sezóny.")
                        elif exists:
                            st.error("Tato sezóna už existuje.")
                        else:
                            db.add(
                                Season(
                                    league_id=league.id,
                                    name=clean
                                )
                            )
                            db.commit()
                            st.success("Sezóna byla přidána.")
                            st.rerun()

                # Bezpečné mazání ligy
                st.divider()

                if seasons:
                    st.caption(
                        "Ligu nelze smazat, dokud obsahuje sezóny."
                    )
                else:
                    confirm_league = st.checkbox(
                        "Potvrzuji smazání této ligy",
                        key=f"confirm_league_{league.id}"
                    )

                    if st.button(
                        "🗑️ Smazat ligu",
                        key=f"delete_league_{league.id}",
                        use_container_width=True
                    ):
                        if confirm_league:
                            db.delete(league)
                            db.commit()
                            st.success("Liga byla smazána.")
                            st.rerun()
                        else:
                            st.error("Nejdříve potvrď smazání.")
