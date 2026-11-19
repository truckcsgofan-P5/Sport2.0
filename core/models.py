from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, ForeignKey, UniqueConstraint,
    CheckConstraint, Float, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="editor")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class League(Base):
    __tablename__ = "leagues"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    country: Mapped[str] = mapped_column(String(100), default="")
    seasons: Mapped[list["Season"]] = relationship(
        back_populates="league", cascade="all, delete-orphan"
    )

class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("league_id", "name", name="uq_season_league_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(40))
    league: Mapped["League"] = relationship(back_populates="seasons")
    teams: Mapped[list["Team"]] = relationship(back_populates="season", cascade="all, delete-orphan")
    matches: Mapped[list["Match"]] = relationship(back_populates="season", cascade="all, delete-orphan")

class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("season_id", "name", name="uq_team_season_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    season: Mapped["Season"] = relationship(back_populates="teams")

class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("home_team_id <> away_team_id", name="ck_match_different_teams"),
        CheckConstraint(
            "(played = false) OR (home_score IS NOT NULL AND away_score IS NOT NULL)",
            name="ck_played_match_has_score"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"), index=True)
    match_date: Mapped[date] = mapped_column(Date, index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"))
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    played: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id])
    season: Mapped["Season"] = relationship(back_populates="matches")

class PredictionEvaluation(Base):
    __tablename__ = "prediction_evaluations"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), unique=True)
    p_home: Mapped[float] = mapped_column(Float)
    p_draw: Mapped[float] = mapped_column(Float)
    p_away: Mapped[float] = mapped_column(Float)
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    brier_score: Mapped[float | None] = mapped_column(Float, nullable=True)
