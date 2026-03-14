"""
Three-layer rune recommendation service.

Layer 1 — Player History   : runes the player has previously used for this matchup
Layer 2 — Default Runes    : champion-specific default rune pages
Layer 3 — Pro / High-Elo   : aggregated high-elo rune statistics
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import DefaultRune, MatchupStat, PlayerRune, ProRune
from app.schemas import RecommendResponse, RunePage


def _select_best_player_rune(
    db: Session,
    player_id: str,
    champion_id: int,
    enemy_champion_id: int,
    role: str,
) -> PlayerRune | None:
    """
    Return the player's best-performing rune page for the given matchup.

    Prefers rune pages with wins; falls back to the most recent page if none
    have a recorded result.
    """
    query = (
        db.query(PlayerRune)
        .filter(
            PlayerRune.player_id == player_id,
            PlayerRune.champion_id == champion_id,
            PlayerRune.enemy_champion_id == enemy_champion_id,
            PlayerRune.role.in_([role, "ANY"]),
        )
        .order_by(PlayerRune.played_at.desc())
        .all()
    )

    if not query:
        return None

    # Among entries that have a win recorded, pick the most frequently used
    # rune setup with the highest win rate.
    wins = [r for r in query if r.win is True]
    return wins[0] if wins else query[0]


def _get_default_rune(
    db: Session,
    champion_id: int,
    role: str,
) -> DefaultRune | None:
    """Return the default rune page for a champion, preferring role-specific pages."""
    page = (
        db.query(DefaultRune)
        .filter(
            DefaultRune.champion_id == champion_id,
            DefaultRune.role == role,
        )
        .first()
    )
    if page:
        return page
    # Fall back to generic "ANY" role page
    return (
        db.query(DefaultRune)
        .filter(
            DefaultRune.champion_id == champion_id,
            DefaultRune.role == "ANY",
        )
        .first()
    )


def _get_pro_rune(
    db: Session,
    champion_id: int,
    enemy_champion_id: int,
    role: str,
) -> ProRune | None:
    """Return the highest win-rate pro rune page for this matchup."""
    page = (
        db.query(ProRune)
        .filter(
            ProRune.champion_id == champion_id,
            ProRune.enemy_champion_id == enemy_champion_id,
            ProRune.role.in_([role, "ANY"]),
        )
        .order_by(ProRune.win_rate.desc(), ProRune.pick_rate.desc())
        .first()
    )
    return page


def _get_matchup_stats(
    db: Session,
    champion_id: int,
    enemy_champion_id: int,
    role: str,
) -> MatchupStat | None:
    """Return matchup difficulty / win-rate statistics if available."""
    return (
        db.query(MatchupStat)
        .filter(
            MatchupStat.champion_id == champion_id,
            MatchupStat.enemy_champion_id == enemy_champion_id,
            MatchupStat.role.in_([role, "ANY"]),
        )
        .first()
    )


def recommend_runes(
    db: Session,
    player_id: str,
    champion_id: int,
    enemy_champion_id: int,
    role: str = "ANY",
) -> RecommendResponse:
    """
    Return the best rune recommendation using the three-layer algorithm.

    Raises ValueError if no rune page can be found for the champion.
    """
    matchup = _get_matchup_stats(db, champion_id, enemy_champion_id, role)
    matchup_difficulty = matchup.difficulty if matchup else None
    matchup_win_rate = matchup.win_rate if matchup else None

    # Layer 1 — Player history
    player_rune = _select_best_player_rune(
        db, player_id, champion_id, enemy_champion_id, role
    )
    if player_rune:
        return RecommendResponse(
            runes=RunePage.model_validate(player_rune.runes),
            source="player_history",
            matchup_difficulty=matchup_difficulty,
            matchup_win_rate=matchup_win_rate,
        )

    # Layer 2 — Default rune page for champion
    default_rune = _get_default_rune(db, champion_id, role)
    if default_rune:
        return RecommendResponse(
            runes=RunePage.model_validate(default_rune.runes),
            source="default",
            matchup_difficulty=matchup_difficulty,
            matchup_win_rate=matchup_win_rate,
        )

    # Layer 3 — Pro / high-elo data
    pro_rune = _get_pro_rune(db, champion_id, enemy_champion_id, role)
    if pro_rune:
        return RecommendResponse(
            runes=RunePage.model_validate(pro_rune.runes),
            source="pro_data",
            win_rate=pro_rune.win_rate,
            sample_size=pro_rune.sample_size,
            matchup_difficulty=matchup_difficulty,
            matchup_win_rate=matchup_win_rate,
        )

    raise ValueError(
        f"No rune page found for champion {champion_id} vs {enemy_champion_id} "
        f"in role {role}."
    )
