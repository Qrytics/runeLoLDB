"""Tests for the three-layer rune recommendation logic."""

import pytest
from sqlalchemy.orm import Session

from app.models import Champion, DefaultRune, PlayerRune, ProRune
from app.services.rune_recommender import recommend_runes
from tests.conftest import SAMPLE_RUNE_PAGE

CHAMPION_ID = 157       # Yone
ENEMY_ID = 238          # Zed
PLAYER_ID = "TestPlayer"
ROLE = "MID"


def _seed_champion(db: Session, champion_id: int, name: str, key: str):
    c = Champion(champion_id=champion_id, name=name, key=key)
    db.add(c)
    db.commit()


class TestLayerPlayerHistory:
    """Layer 1: player history should be used when available."""

    def test_returns_player_rune_when_available(self, db: Session):
        record = PlayerRune(
            player_id=PLAYER_ID,
            champion_id=CHAMPION_ID,
            enemy_champion_id=ENEMY_ID,
            role=ROLE,
            runes=SAMPLE_RUNE_PAGE,
            win=True,
        )
        db.add(record)
        db.commit()

        result = recommend_runes(db, PLAYER_ID, CHAMPION_ID, ENEMY_ID, ROLE)
        assert result.source == "player_history"
        assert result.runes.primaryPath.keystone.name == "Conqueror"

    def test_prefers_winning_rune_page(self, db: Session):
        losing_page = dict(SAMPLE_RUNE_PAGE)
        losing_page["primaryPath"] = dict(SAMPLE_RUNE_PAGE["primaryPath"])
        losing_page["primaryPath"]["keystone"] = {"id": 9999, "name": "LosingRune"}

        db.add(
            PlayerRune(
                player_id=PLAYER_ID,
                champion_id=CHAMPION_ID,
                enemy_champion_id=ENEMY_ID,
                role=ROLE,
                runes=losing_page,
                win=False,
            )
        )
        db.add(
            PlayerRune(
                player_id=PLAYER_ID,
                champion_id=CHAMPION_ID,
                enemy_champion_id=ENEMY_ID,
                role=ROLE,
                runes=SAMPLE_RUNE_PAGE,
                win=True,
            )
        )
        db.commit()

        result = recommend_runes(db, PLAYER_ID, CHAMPION_ID, ENEMY_ID, ROLE)
        assert result.source == "player_history"
        assert result.runes.primaryPath.keystone.name == "Conqueror"


class TestLayerDefault:
    """Layer 2: default rune page should be used when no player history exists."""

    def test_falls_back_to_default_rune(self, db: Session):
        db.add(
            DefaultRune(
                champion_id=CHAMPION_ID,
                role=ROLE,
                runes=SAMPLE_RUNE_PAGE,
                patch="14.24",
            )
        )
        db.commit()

        result = recommend_runes(db, PLAYER_ID, CHAMPION_ID, ENEMY_ID, ROLE)
        assert result.source == "default"
        assert result.runes.primaryPath.name == "Precision"

    def test_generic_role_fallback(self, db: Session):
        """A page stored under role='ANY' should be returned for any role."""
        db.add(
            DefaultRune(
                champion_id=CHAMPION_ID,
                role="ANY",
                runes=SAMPLE_RUNE_PAGE,
            )
        )
        db.commit()

        result = recommend_runes(db, PLAYER_ID, CHAMPION_ID, ENEMY_ID, "JUNGLE")
        assert result.source == "default"


class TestLayerPro:
    """Layer 3: pro / high-elo data should be used as the last resort."""

    def test_falls_back_to_pro_rune(self, db: Session):
        db.add(
            ProRune(
                champion_id=CHAMPION_ID,
                enemy_champion_id=ENEMY_ID,
                role=ROLE,
                runes=SAMPLE_RUNE_PAGE,
                win_rate=0.54,
                pick_rate=0.35,
                sample_size=1000,
            )
        )
        db.commit()

        result = recommend_runes(db, PLAYER_ID, CHAMPION_ID, ENEMY_ID, ROLE)
        assert result.source == "pro_data"
        assert result.win_rate == pytest.approx(0.54)
        assert result.sample_size == 1000

    def test_chooses_highest_win_rate_pro_rune(self, db: Session):
        low_wr_page = dict(SAMPLE_RUNE_PAGE)
        low_wr_page["primaryPath"] = dict(SAMPLE_RUNE_PAGE["primaryPath"])
        low_wr_page["primaryPath"]["keystone"] = {"id": 111, "name": "LowWinRate"}

        db.add(
            ProRune(
                champion_id=CHAMPION_ID,
                enemy_champion_id=ENEMY_ID,
                role=ROLE,
                runes=low_wr_page,
                win_rate=0.42,
                pick_rate=0.50,
                sample_size=500,
            )
        )
        db.add(
            ProRune(
                champion_id=CHAMPION_ID,
                enemy_champion_id=ENEMY_ID,
                role=ROLE,
                runes=SAMPLE_RUNE_PAGE,
                win_rate=0.58,
                pick_rate=0.30,
                sample_size=300,
            )
        )
        db.commit()

        result = recommend_runes(db, PLAYER_ID, CHAMPION_ID, ENEMY_ID, ROLE)
        assert result.source == "pro_data"
        assert result.runes.primaryPath.keystone.name == "Conqueror"


class TestNoRuneFound:
    """When no rune page exists at any layer a ValueError must be raised."""

    def test_raises_value_error(self, db: Session):
        with pytest.raises(ValueError, match="No rune page found"):
            recommend_runes(db, PLAYER_ID, CHAMPION_ID, ENEMY_ID, ROLE)
