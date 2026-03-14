"""Match result endpoints — records the outcome of a game for the learning system."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PlayerRune
from app.schemas import MatchResultCreate, MatchResultResponse

router = APIRouter()


@router.post("", response_model=MatchResultResponse, status_code=status.HTTP_201_CREATED)
def record_match_result(
    body: MatchResultCreate,
    db: Session = Depends(get_db),
):
    """
    Record a finished match result.

    Stores the runes used and whether the player won so the recommendation
    engine can learn from the player's history over time.
    """
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
