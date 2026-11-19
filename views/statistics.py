import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import select
from core.db import SessionLocal
from core.models import Team, Match, PredictionEvaluation
from core.repository import season_options


def render():
    st.markdown('<div class="eyebrow">PERFORMANCE / DATA LAB</div>', unsafe_allow_html=True)
    st.title("Statistiky a analytika")
    opts = season_options()
    if not opts:
        st.info("Zatím nejsou žádné sezóny.")
        return
    sid, label = st.selectbox("Soutěž a sezóna", opts, format_func=lambda x: x[1])
    with SessionLocal() as db:
        teams = list(db.scalars(select(Team).where(Team.season_id == sid).order_by(Team.name)))
        matches = list(db.scalars(select(Match).where(Match.season_id == sid)))
        played = [m for m in matches if m.played and m.home_score is not None and m.away_score is not None]
        if not played:
            st.info("Pro statistiky je potřeba alespoň jeden odehraný zápas.")
            return

        rows = []
        for t in teams:
            games = [m for m in played if t.id in (m.home_team_id, m.away_team_id)]
            gf = ga = w = d = l = 0
            home_gf = home_ga = away_gf = away_ga = 0
            hw = hd = hl = aw = ad = al = 0
            for m in games:
                is_home = m.home_team_id == t.id
                own, opp = (m.home_score, m.away_score) if is_home else (m.away_score, m.home_score)
                gf += own
                ga += opp
                if is_home:
                    home_gf += own
                    home_ga += opp
                else:
                    away_gf += own
                    away_ga += opp
                if own > opp:
                    w += 1
                    if is_home: hw += 1
                    else: aw += 1
                elif own == opp:
                    d += 1
                    if is_home: hd += 1
                    else: ad += 1
                else:
                    l += 1
                    if is_home: hl += 1
                    else: al += 1
            rows.append({
                "Tým": t.name, "Zápasy": len(games), "Výhry": w, "Remízy": d,
                "Prohry": l, "Vstřelené góly": gf, "Obdržené góly": ga,
                "Rozdíl": gf - ga, "Body": w * 3 + d,
                "Průměr gólů": round(gf / len(games), 2) if games else 0,
                "Průměr obdržených": round(ga / len(games), 2) if games else 0,
                "Domácí góly": home_gf, "Domácí inkasované": home_ga,
                "Venkovní góly": away_gf, "Venkovní inkasované": away_ga,
                "Domácí Z": hw + hd + hl, "Domácí V": hw, "Domácí R": hd,
                "Domácí P": hl, "Domácí body": hw * 3 + hd,
                "Venkovní Z": aw + ad + al, "Venkovní V": aw, "Venkovní R": ad,
                "Venkovní P": al, "Venkovní body": aw * 3 + ad,
            })

        df = pd.DataFrame(rows)
        if df.empty:
            st.info("V této sezóně nejsou týmy se statistikami.")
            return
        df = df.sort_values(["Body", "Rozdíl", "Vstřelené góly"], ascending=False)
        best_attack = df.sort_values("Vstřelené góly", ascending=False).iloc[0]
        best_defence = df.sort_values("Obdržené góly", ascending=True).iloc[0]
        a, b, c = st.columns(3)
        a.metric("Nejlepší útok", best_attack["Tým"], f'{int(best_attack["Vstřelené góly"])} gólů')
        b.metric("Nejlepší obrana", best_defence["Tým"], f'{int(best_defence["Obdržené góly"])} inkasovaných')
        c.metric("Odehrané zápasy", len(played))

        st.subheader("Celková výkonnost týmů")
        st.dataframe(df[[
            "Tým", "Zápasy", "Výhry", "Remízy", "Prohry", "Vstřelené góly",
            "Obdržené góly", "Rozdíl", "Body", "Průměr gólů", "Průměr obdržených"
        ]], use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(
            df.sort_values("Vstřelené góly", ascending=False),
            x="Tým", y=["Vstřelené góly", "Obdržené góly"], barmode="group",
            title="Vstřelené a obdržené góly"
        ), use_container_width=True)
        st.plotly_chart(px.scatter(
            df, x="Vstřelené góly", y="Obdržené góly", size="Zápasy",
            color="Tým", hover_data=["Body", "Rozdíl"],
            title="Útočná a obranná výkonnost"
        ), use_container_width=True)

        st.subheader("Domácí tabulka")
        st.dataframe(df[["Tým", "Domácí Z", "Domácí V", "Domácí R", "Domácí P",
                         "Domácí góly", "Domácí inkasované", "Domácí body"]]
                     .sort_values(["Domácí body", "Domácí góly"], ascending=False),
                     use_container_width=True, hide_index=True)
        st.subheader("Venkovní tabulka")
        st.dataframe(df[["Tým", "Venkovní Z", "Venkovní V", "Venkovní R", "Venkovní P",
                         "Venkovní góly", "Venkovní inkasované", "Venkovní body"]]
                     .sort_values(["Venkovní body", "Venkovní góly"], ascending=False),
                     use_container_width=True, hide_index=True)

        st.subheader("Domácí vs. venkovní góly")
        split = df.melt(
            id_vars="Tým",
            value_vars=["Domácí góly", "Domácí inkasované", "Venkovní góly", "Venkovní inkasované"],
            var_name="Kategorie", value_name="Góly"
        )
        st.plotly_chart(px.bar(
            split, x="Tým", y="Góly", color="Kategorie", barmode="group",
            title="Domácí a venkovní góly"
        ), use_container_width=True)

        evaluations = db.execute(
            select(PredictionEvaluation, Match)
            .join(Match, PredictionEvaluation.match_id == Match.id)
            .where(Match.season_id == sid, Match.played.is_(True),
                   PredictionEvaluation.brier_score.is_not(None))
            .order_by(Match.match_date.desc())
        ).all()
        st.divider()
        st.subheader("Přesnost predikcí")
        if evaluations:
            scores = [evaluation.brier_score for evaluation, match in evaluations]
            avg_score = sum(scores) / len(scores)
            x, y = st.columns(2)
            x.metric("Vyhodnocené predikce", len(scores))
            y.metric("Průměrné Brier skóre", f"{avg_score:.4f}", help="Nižší hodnota znamená přesnější predikce; 0 je perfektní výsledek.")
            evaluation_rows = []
            for evaluation, match in evaluations:
                evaluation_rows.append({
                    "Datum": match.match_date,
                    "Zápas": f"{match.home_team.name} – {match.away_team.name}",
                    "Výsledek": f"{match.home_score}:{match.away_score}",
                    "Predikce 1": f"{evaluation.p_home * 100:.1f}%",
                    "Predikce X": f"{evaluation.p_draw * 100:.1f}%",
                    "Predikce 2": f"{evaluation.p_away * 100:.1f}%",
                    "Brier skóre": round(evaluation.brier_score, 4),
                })
            st.dataframe(evaluation_rows, use_container_width=True, hide_index=True)
        else:
            st.info("Zatím nejsou vyhodnocené predikce. V Predikčním centru nejprve vypočítej predikci naplánovaného zápasu; po zadání výsledku se automaticky vyhodnotí.")
