
import streamlit as st
from sqlalchemy import select, func
from core.db import SessionLocal
from core.models import League, Season, Team, Match


def render():
    from core.permissions import require_editor
    require_editor()

    st.title("Správa lig a sezón")
    st.caption("SportStats 2.3 · Správa soutěží")

    # Vytvoření nové ligy
    with st.expander("➕ Vytvořit novou ligu"):
        with st.form("new_league"):
            name = st.text_input("Název ligy")
            country = st.text_input("Země")
            create = st.form_submit_button("Vytvořit ligu")

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
                        db.add(League(name=clean, country=country.strip()))
                        db.commit()
                        st.success("Liga byla vytvořena.")
                        st.rerun()

    st.divider()

    with SessionLocal() as db:
        leagues = db.scalars(
            select(League).order_by(League.name)
        ).all()

        if not leagues:
            st.info("Zatím nejsou vytvořeny žádné ligy.")

        for league in leagues:
            with st.container(border=True):
                st.subheader(league.name)
                st.caption(league.country or "Země neuvedena")

                # Úprava ligy
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
                        save = st.form_submit_button("Uložit změny")

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

                seasons = db.scalars(
                    select(Season)
                    .where(Season.league_id == league.id)
                    .order_by(Season.name.desc())
                ).all()

                st.markdown("**Sezóny**")

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

                    with st.expander(
                        f"📅 {season.name} · {teams_count} týmů · "
                        f"{matches_count} zápasů"
                    ):
                        # Úprava sezóny
                        with st.form(f"edit_season_{season.id}"):
                            new_name = st.text_input(
                                "Název sezóny",
                                value=season.name,
                                key=f"season_edit_{season.id}"
                            )
                            update = st.form_submit_button(
                                "Uložit sezónu"
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
                                st.error("Název sezóny nesmí být prázdný.")
                            elif duplicate:
                                st.error("Tato sezóna už existuje.")
                            else:
                                season.name = clean
                                db.commit()
                                st.success("Sezóna byla upravena.")
                                st.rerun()

                        # Bezpečné mazání sezóny
                        if teams_count or matches_count:
                            st.warning(
                                "Tuto sezónu nelze smazat. Obsahuje týmy "
                                "nebo zápasy. Historická data jsou chráněna."
                            )
                        else:
                            confirm = st.checkbox(
                                "Potvrzuji smazání této sezóny",
                                key=f"confirm_season_{season.id}"
                            )
                            if st.button(
                                "🗑️ Smazat sezónu",
                                key=f"delete_season_{season.id}"
                            ):
                                if confirm:
                                    db.delete(season)
                                    db.commit()
                                    st.success("Sezóna byla smazána.")
                                    st.rerun()
                                else:
                                    st.error("Nejdříve potvrď smazání.")

                # Přidání sezóny
                with st.form(f"add_season_{league.id}"):
                    season_name = st.text_input(
                        "Nová sezóna",
                        placeholder="2026/2027",
                        key=f"new_season_{league.id}"
                    )
                    add = st.form_submit_button("➕ Přidat sezónu")

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
                            Season(league_id=league.id, name=clean)
                        )
                        db.commit()
                        st.success("Sezóna byla přidána.")
                        st.rerun()

                # Bezpečné mazání ligy
                if seasons:
                    st.warning(
                        "Ligu nelze smazat, dokud obsahuje sezóny."
                    )
                else:
                    confirm_league = st.checkbox(
                        "Potvrzuji smazání ligy",
                        key=f"confirm_league_{league.id}"
                    )
                    if st.button(
                        "🗑️ Smazat ligu",
                        key=f"delete_league_{league.id}"
                    ):
                        if confirm_league:
                            db.delete(league)
                            db.commit()
                            st.success("Liga byla smazána.")
                            st.rerun()
                        else:
                            st.error("Nejdříve potvrď smazání.")
