import json
from pathlib import Path
from datetime import date
from sqlalchemy import select
from .db import SessionLocal
from .models import League, Season, Team, Match

def import_legacy_json(path="sports_data.json"):
    source = Path(path)
    if not source.exists():
        return {"status": "missing", "leagues": 0, "seasons": 0, "teams": 0, "matches": 0}
    with source.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ValueError("Kořen JSON musí být objekt s ligami.")

    counts = {"leagues": 0, "seasons": 0, "teams": 0, "matches": 0}
    with SessionLocal() as db:
        for league_name, seasons_data in raw.items():
            league = db.scalar(select(League).where(League.name == str(league_name)))
            if league is None:
                league = League(name=str(league_name).strip(), country="")
                db.add(league); db.flush()
                counts["leagues"] += 1

            # Podpora starého plochého formátu {league: {teams, matches}}
            if isinstance(seasons_data, dict) and ("teams" in seasons_data or "matches" in seasons_data):
                seasons_iter = [("2025/2026", seasons_data)]
            elif isinstance(seasons_data, dict):
                seasons_iter = list(seasons_data.items())
            else:
                continue

            for season_name, payload in seasons_iter:
                payload = payload or {}
                season = db.scalar(select(Season).where(
                    Season.league_id == league.id, Season.name == str(season_name)
                ))
                if season is None:
                    season = Season(league_id=league.id, name=str(season_name))
                    db.add(season); db.flush()
                    counts["seasons"] += 1

                team_map = {}
                for team_name in payload.get("teams", []) or []:
                    clean = str(team_name).strip()
                    if not clean:
                        continue
                    team = db.scalar(select(Team).where(
                        Team.season_id == season.id, Team.name == clean
                    ))
                    if team is None:
                        team = Team(season_id=season.id, name=clean)
                        db.add(team); db.flush()
                        counts["teams"] += 1
                    team_map[clean] = team.id

                for item in payload.get("matches", []) or []:
                    home = str(item.get("Domácí", "")).strip()
                    away = str(item.get("Hosté", "")).strip()
                    if not home or not away or home == away:
                        continue
                    for name in (home, away):
                        if name not in team_map:
                            team = db.scalar(select(Team).where(
                                Team.season_id == season.id, Team.name == name
                            ))
                            if team is None:
                                team = Team(season_id=season.id, name=name)
                                db.add(team); db.flush()
                                counts["teams"] += 1
                            team_map[name] = team.id
                    raw_date = item.get("Datum") or date.today().isoformat()
                    try:
                        match_date = date.fromisoformat(str(raw_date)[:10])
                    except ValueError:
                        match_date = date.today()
                    played = bool(item.get("Odehráno", True))
                    try:
                        hs = int(item.get("Skóre Domácí", 0)) if played else None
                        aws = int(item.get("Skóre Hosté", 0)) if played else None
                        if hs is not None and (hs < 0 or aws < 0):
                            raise ValueError
                    except (ValueError, TypeError):
                        played, hs, aws = False, None, None

                    duplicate = db.scalar(select(Match).where(
                        Match.season_id == season.id,
                        Match.match_date == match_date,
                        Match.home_team_id == team_map[home],
                        Match.away_team_id == team_map[away]
                    ))
                    if duplicate is None:
                        db.add(Match(
                            season_id=season.id, match_date=match_date,
                            home_team_id=team_map[home], away_team_id=team_map[away],
                            home_score=hs, away_score=aws, played=played
                        ))
                        counts["matches"] += 1
        db.commit()
    return {"status": "ok", **counts}
