"""Pydantic schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Rune schemas
# ---------------------------------------------------------------------------

class RuneSlot(BaseModel):
    id: int
    name: str


class RunePath(BaseModel):
    id: int
    name: str
    keystone: Optional[RuneSlot] = None
    slots: list[RuneSlot] = Field(default_factory=list)


class RunePage(BaseModel):
    primaryPath: RunePath
    secondaryPath: RunePath
    statShards: list[RuneSlot] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Recommendation request / response
# ---------------------------------------------------------------------------

class RecommendRequest(BaseModel):
    player_id: str = Field(..., description="Summoner name or PUUID")
    champion_id: int = Field(..., description="Riot champion ID for the player's champion")
    enemy_champion_id: int = Field(..., description="Riot champion ID for the enemy champion")
    role: str = Field("ANY", description="Role/lane (TOP, JUNGLE, MID, BOTTOM, SUPPORT, ANY)")


class RecommendResponse(BaseModel):
    runes: RunePage
    source: str = Field(
        ...,
        description="Source of recommendation: player_history | default | pro_data",
    )
    win_rate: Optional[float] = None
    sample_size: Optional[int] = None
    matchup_difficulty: Optional[str] = None
    matchup_win_rate: Optional[float] = None


# ---------------------------------------------------------------------------
# Player rune schemas
# ---------------------------------------------------------------------------

class PlayerRuneCreate(BaseModel):
    player_id: str
    champion_id: int
    enemy_champion_id: int
    role: str = "ANY"
    runes: RunePage
    win: Optional[bool] = None
    match_id: Optional[str] = None


class PlayerRuneResponse(BaseModel):
    id: int
    player_id: str
    champion_id: int
    enemy_champion_id: int
    role: str
    runes: Any
    win: Optional[bool]
    match_id: Optional[str]
    played_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Match result schemas
# ---------------------------------------------------------------------------

class MatchResultCreate(BaseModel):
    player_id: str
    match_id: str
    champion_id: int
    enemy_champion_id: int
    role: str = "ANY"
    runes: RunePage
    win: bool


class MatchResultResponse(BaseModel):
    id: int
    player_id: str
    match_id: str
    champion_id: int
    enemy_champion_id: int
    win: bool
    played_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Champion schemas
# ---------------------------------------------------------------------------

class ChampionResponse(BaseModel):
    champion_id: int
    name: str
    key: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Default rune schemas
# ---------------------------------------------------------------------------

class DefaultRuneCreate(BaseModel):
    champion_id: int
    role: str = "ANY"
    runes: RunePage
    patch: Optional[str] = None


class DefaultRuneResponse(BaseModel):
    id: int
    champion_id: int
    role: str
    runes: Any
    patch: Optional[str]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Pro rune schemas
# ---------------------------------------------------------------------------

class ProRuneCreate(BaseModel):
    champion_id: int
    enemy_champion_id: int
    role: str = "ANY"
    runes: RunePage
    pick_rate: float = 0
    win_rate: float = 0
    sample_size: int = 0
    min_rank: str = "MASTER"
    patch: Optional[str] = None


class ProRuneResponse(BaseModel):
    id: int
    champion_id: int
    enemy_champion_id: int
    role: str
    runes: Any
    pick_rate: float
    win_rate: float
    sample_size: int
    patch: Optional[str]

    model_config = ConfigDict(from_attributes=True)
