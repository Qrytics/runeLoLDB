"""SQLAlchemy ORM models for RuneLoLDB."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    Index,
)

from app.database import Base


def _now():
    return datetime.now(timezone.utc)


class Champion(Base):
    __tablename__ = "champions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    champion_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    key = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class DefaultRune(Base):
    __tablename__ = "default_runes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    champion_id = Column(Integer, nullable=False, index=True)
    role = Column(String(50), nullable=False, default="ANY")
    runes = Column(JSON, nullable=False)
    patch = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (UniqueConstraint("champion_id", "role"),)


class PlayerRune(Base):
    __tablename__ = "player_runes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(100), nullable=False, index=True)
    champion_id = Column(Integer, nullable=False)
    enemy_champion_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False, default="ANY")
    runes = Column(JSON, nullable=False)
    win = Column(Boolean)
    match_id = Column(String(100))
    played_at = Column(DateTime(timezone=True), default=_now)
    created_at = Column(DateTime(timezone=True), default=_now)

    __table_args__ = (
        Index(
            "idx_player_runes_lookup",
            "player_id",
            "champion_id",
            "enemy_champion_id",
            "role",
        ),
    )


class ProRune(Base):
    __tablename__ = "pro_runes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    champion_id = Column(Integer, nullable=False)
    enemy_champion_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False, default="ANY")
    runes = Column(JSON, nullable=False)
    pick_rate = Column(Float, nullable=False, default=0)
    win_rate = Column(Float, nullable=False, default=0)
    sample_size = Column(Integer, nullable=False, default=0)
    min_rank = Column(String(20), nullable=False, default="MASTER")
    patch = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        Index(
            "idx_pro_runes_lookup",
            "champion_id",
            "enemy_champion_id",
            "role",
        ),
    )


class MatchupStat(Base):
    __tablename__ = "matchup_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    champion_id = Column(Integer, nullable=False)
    enemy_champion_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False, default="ANY")
    win_rate = Column(Float)
    difficulty = Column(String(20))
    sample_size = Column(Integer, default=0)
    patch = Column(String(20))
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        UniqueConstraint("champion_id", "enemy_champion_id", "role", "patch"),
    )
