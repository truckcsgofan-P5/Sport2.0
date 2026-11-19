from sqlalchemy import select, func
from .db import SessionLocal
from .models import League, Season, Team, Match

def list_leagues():
    with SessionLocal() as db:
        return db.scalars(select(League).order_by(League.name)).all()

def get_season(season_id):
    with SessionLocal() as db:
        return db.get(Season, int(season_id))

def season_options():
    with SessionLocal() as db:
        rows = db.execute(
            select(Season.id, Season.name, League.name)
            .join(League).order_by(League.name, Season.name)
        ).all()
        return [(r[0], f"{r[2]} · {r[1]}") for r in rows]

def dashboard_metrics():
    with SessionLocal() as db:
        return {
            "leagues": db.scalar(select(func.count(League.id))) or 0,
            "teams": db.scalar(select(func.count(Team.id))) or 0,
            "matches": db.scalar(select(func.count(Match.id))) or 0,
            "played": db.scalar(select(func.count(Match.id)).where(Match.played.is_(True))) or 0,
        }
