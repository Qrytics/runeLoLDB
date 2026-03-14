"""Champion list endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Champion
from app.schemas import ChampionResponse

router = APIRouter()


@router.get("", response_model=list[ChampionResponse])
def list_champions(db: Session = Depends(get_db)):
    """Return all known champions."""
    return db.query(Champion).order_by(Champion.name).all()


@router.get("/{champion_id}", response_model=ChampionResponse)
def get_champion(champion_id: int, db: Session = Depends(get_db)):
    """Return a single champion by its Riot champion ID."""
    champion = (
        db.query(Champion)
        .filter(Champion.champion_id == champion_id)
        .first()
    )
    if not champion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Champion {champion_id} not found.",
        )
    return champion
