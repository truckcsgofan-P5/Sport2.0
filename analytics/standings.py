import pandas as pd

def build_standings(teams, matches):
    stats = {
        t.id: {"Tým": t.name, "Z": 0, "V": 0, "R": 0, "P": 0,
               "VG": 0, "OG": 0, "Body": 0}
        for t in teams
    }
    for m in matches:
        if not m.played or m.home_score is None or m.away_score is None:
            continue
        h, a = stats.get(m.home_team_id), stats.get(m.away_team_id)
        if h is None or a is None:
            continue
        hs, aws = m.home_score, m.away_score
        h["Z"] += 1; a["Z"] += 1
        h["VG"] += hs; h["OG"] += aws
        a["VG"] += aws; a["OG"] += hs
        if hs > aws:
            h["V"] += 1; h["Body"] += 3; a["P"] += 1
        elif hs < aws:
            a["V"] += 1; a["Body"] += 3; h["P"] += 1
        else:
            h["R"] += 1; a["R"] += 1
            h["Body"] += 1; a["Body"] += 1
    rows = []
    for s in stats.values():
        s["GD"] = s["VG"] - s["OG"]
        s["Skóre"] = f'{s["VG"]}:{s["OG"]}'
        rows.append(s)
    return pd.DataFrame(rows).sort_values(
        ["Body", "GD", "VG"], ascending=False
    ).reset_index(drop=True) if rows else pd.DataFrame()
