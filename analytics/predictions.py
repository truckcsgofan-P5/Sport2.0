import math
from collections import defaultdict
from scipy.stats import poisson

def elo_ratings(teams, matches, initial=1500, k=24, home_advantage=65):
    ratings = {t.id: float(initial) for t in teams}
    played = sorted(
        [m for m in matches if m.played and m.home_score is not None and m.away_score is not None],
        key=lambda x: (x.match_date, x.id)
    )
    for m in played:
        rh, ra = ratings[m.home_team_id], ratings[m.away_team_id]
        expected_home = 1 / (1 + 10 ** ((ra - (rh + home_advantage)) / 400))
        if m.home_score > m.away_score:
            actual = 1.0
        elif m.home_score == m.away_score:
            actual = 0.5
        else:
            actual = 0.0
        margin = abs(m.home_score - m.away_score)
        multiplier = math.log(margin + 1) * (2.2 / (2.2 + 0.001 * abs(rh - ra))) if margin else 1.0
        delta = k * multiplier * (actual - expected_home)
        ratings[m.home_team_id] += delta
        ratings[m.away_team_id] -= delta
    return ratings

def _team_goal_rates(team_id, matches, league_avg=1.35):
    home_scored, home_conceded, away_scored, away_conceded = [], [], [], []
    for m in matches:
        if not m.played or m.home_score is None or m.away_score is None:
            continue
        if m.home_team_id == team_id:
            home_scored.append(m.home_score); home_conceded.append(m.away_score)
        if m.away_team_id == team_id:
            away_scored.append(m.away_score); away_conceded.append(m.home_score)
    scored = (sum(home_scored + away_scored) + league_avg * 3) / (len(home_scored + away_scored) + 3)
    conceded = (sum(home_conceded + away_conceded) + league_avg * 3) / (len(home_conceded + away_conceded) + 3)
    home_attack = (sum(home_scored) / len(home_scored)) if home_scored else scored * 1.08
    away_attack = (sum(away_scored) / len(away_scored)) if away_scored else scored * 0.92
    home_def = (sum(home_conceded) / len(home_conceded)) if home_conceded else conceded * 0.92
    away_def = (sum(away_conceded) / len(away_conceded)) if away_conceded else conceded * 1.08
    return scored, conceded, home_attack, away_attack, home_def, away_def

def predict_match(home_id, away_id, teams, matches):
    if home_id == away_id:
        raise ValueError("Tým nemůže hrát sám proti sobě.")
    ratings = elo_ratings(teams, matches)
    rh, ra = ratings.get(home_id, 1500), ratings.get(away_id, 1500)
    elo_home = 1 / (1 + 10 ** ((ra - (rh + 65)) / 400))
    _, _, h_attack, a_attack, h_def, a_def = _team_goal_rates(home_id, matches)
    _, _, ah_attack, aa_attack, ah_def, aa_def = _team_goal_rates(away_id, matches)
    # Smíšené útočné a obranné síly s regresí k průměru.
    lambda_home = max(0.15, min(4.0, 0.55 * (h_attack + aa_def) / 2 + 0.45 * 1.45))
    lambda_away = max(0.15, min(4.0, 0.55 * (aa_attack + h_def) / 2 + 0.45 * 1.15))
    p_home = p_draw = p_away = 0.0
    scorelines = []
    for hg in range(8):
        for ag in range(8):
            p = poisson.pmf(hg, lambda_home) * poisson.pmf(ag, lambda_away)
            scorelines.append((hg, ag, p))
            if hg > ag: p_home += p
            elif hg == ag: p_draw += p
            else: p_away += p
    # Elo upraví poměr výhra/prohra, remízu nechá odvodit z Poissonova modelu.
    directional = p_home + p_away
    target_home = elo_home
    if directional > 0:
        scale = (1 - p_draw) / directional
        p_home = (0.65 * p_home + 0.35 * target_home * directional) * scale
        p_away = 1 - p_draw - p_home
    total = p_home + p_draw + p_away
    probs = {"home": p_home / total, "draw": p_draw / total, "away": p_away / total}
    best = max(scorelines, key=lambda x: x[2])
    return {
        "probabilities": probs,
        "expected_home_goals": lambda_home,
        "expected_away_goals": lambda_away,
        "most_likely_score": f"{best[0]}:{best[1]}",
        "elo_home": ratings.get(home_id, 1500),
        "elo_away": ratings.get(away_id, 1500),
    }
