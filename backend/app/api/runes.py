"""Rune recommendation and management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DefaultRune, PlayerRune, ProRune
from app.schemas import (
    DefaultRuneCreate,
    DefaultRuneResponse,
    PlayerRuneCreate,
    PlayerRuneResponse,
    ProRuneCreate,
    ProRuneResponse,
    RecommendRequest,
    RecommendResponse,
)
from app.services.rune_recommender import recommend_runes

router = APIRouter()


# ---------------------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------------------


@router.post("/recommend", response_model=RecommendResponse)
def get_recommendation(
    req: RecommendRequest,
    db: Session = Depends(get_db),
):
    """
    Return a rune recommendation using the three-layer algorithm:

    1. Player history for this matchup
    2. Champion default rune page
    3. High-elo / pro aggregated data
    """
    try:
        return recommend_runes(
            db=db,
            player_id=req.player_id,
            champion_id=req.champion_id,
            enemy_champion_id=req.enemy_champion_id,
            role=req.role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# Player rune history
# ---------------------------------------------------------------------------


@router.post("/player", response_model=PlayerRuneResponse, status_code=status.HTTP_201_CREATED)
def save_player_rune(
    body: PlayerRuneCreate,
    db: Session = Depends(get_db),
):
    """Save a rune page to player history."""
    record = PlayerRune(
        player_id=body.player_id,
        champion_id=body.champion_id,
        enemy_champion_id=body.enemy_champion_id,
        role=body.role,
        runes=body.runes.model_dump(),
        win=body.win,
        match_id=body.match_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/player/{player_id}", response_model=list[PlayerRuneResponse])
def get_player_runes(
    player_id: str,
    champion_id: int | None = None,
    db: Session = Depends(get_db),
):
    """List all rune history entries for a player, optionally filtered by champion."""
    query = db.query(PlayerRune).filter(PlayerRune.player_id == player_id)
    if champion_id is not None:
        query = query.filter(PlayerRune.champion_id == champion_id)
    return query.order_by(PlayerRune.played_at.desc()).all()


# ---------------------------------------------------------------------------
# Default rune pages
# ---------------------------------------------------------------------------


@router.post(
    "/default",
    response_model=DefaultRuneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_default_rune(
    body: DefaultRuneCreate,
    db: Session = Depends(get_db),
):
    """Create or replace a default rune page for a champion/role combination."""
    existing = (
        db.query(DefaultRune)
        .filter(
            DefaultRune.champion_id == body.champion_id,
            DefaultRune.role == body.role,
        )
        .first()
    )
    if existing:
        existing.runes = body.runes.model_dump()
        existing.patch = body.patch
        db.commit()
        db.refresh(existing)
        return existing

    record = DefaultRune(
        champion_id=body.champion_id,
        role=body.role,
        runes=body.runes.model_dump(),
        patch=body.patch,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/default/{champion_id}", response_model=list[DefaultRuneResponse])
def get_default_runes(
    champion_id: int,
    db: Session = Depends(get_db),
):
    """Get all default rune pages for a champion."""
    return (
        db.query(DefaultRune)
        .filter(DefaultRune.champion_id == champion_id)
        .all()
    )


# ---------------------------------------------------------------------------
# Pro rune data
# ---------------------------------------------------------------------------


@router.post(
    "/pro",
    response_model=ProRuneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pro_rune(
    body: ProRuneCreate,
    db: Session = Depends(get_db),
):
    """Ingest a pro/high-elo rune entry."""
    record = ProRune(
        champion_id=body.champion_id,
        enemy_champion_id=body.enemy_champion_id,
        role=body.role,
        runes=body.runes.model_dump(),
        pick_rate=body.pick_rate,
        win_rate=body.win_rate,
        sample_size=body.sample_size,
        min_rank=body.min_rank,
        patch=body.patch,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/pro/{champion_id}", response_model=list[ProRuneResponse])
def get_pro_runes(
    champion_id: int,
    enemy_champion_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Get pro rune pages for a champion, optionally filtered by enemy champion."""
    query = db.query(ProRune).filter(ProRune.champion_id == champion_id)
    if enemy_champion_id is not None:
        query = query.filter(ProRune.enemy_champion_id == enemy_champion_id)
    return (
        query.order_by(ProRune.win_rate.desc(), ProRune.pick_rate.desc()).all()
    )
