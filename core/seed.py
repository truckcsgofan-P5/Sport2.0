from datetime import date, timedelta
from sqlalchemy import select
from .db import SessionLocal
from .config import setting
from .models import League, Season, Team, Match

def seed_demo_data():
    if setting("SEED_DEMO_DATA", "true").lower() != "true":
        return
    with SessionLocal() as db:
        if db.scalar(select(League.id).limit(1)) is not None:
            return
        league = League(name="Ukázková liga", country="Česko")
        db.add(league); db.flush()
        season = Season(league_id=league.id, name="2026/2027")
        db.add(season); db.flush()
        names = ["Praha FC", "Brno United", "Ostrava SK", "Plzeň City"]
        teams = []
        for name in names:
            t = Team(season_id=season.id, name=name)
            db.add(t); teams.append(t)
        db.flush()
        today = date.today()
        sample = [
            (0, 1, 2, 1, True, 12),
            (2, 3, 0, 0, True, 10),
            (1, 3, None, None, False, 2),
            (0, 2, None, None, False, 4),
        ]
        for h, a, hs, aws, played, offset in sample:
            db.add(Match(
                season_id=season.id, match_date=today + timedelta(days=offset),
                home_team_id=teams[h].id, away_team_id=teams[a].id,
                home_score=hs, away_score=aws, played=played
            ))
        db.commit()
