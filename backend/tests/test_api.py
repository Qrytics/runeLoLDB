"""Integration tests for the rune API endpoints."""

import pytest
from tests.conftest import SAMPLE_RUNE_PAGE

CHAMPION_ID = 157
ENEMY_ID = 238
PLAYER_ID = "SummonerTest"
ROLE = "MID"


class TestRecommendEndpoint:
    def test_recommend_returns_404_when_no_runes(self, client):
        resp = client.post(
            "/api/runes/recommend",
            json={
                "player_id": PLAYER_ID,
                "champion_id": CHAMPION_ID,
                "enemy_champion_id": ENEMY_ID,
                "role": ROLE,
            },
        )
        assert resp.status_code == 404

    def test_recommend_uses_default_rune(self, client, db):
        from app.models import DefaultRune

        db.add(
            DefaultRune(
                champion_id=CHAMPION_ID,
                role=ROLE,
                runes=SAMPLE_RUNE_PAGE,
                patch="14.24",
            )
        )
        db.commit()

        resp = client.post(
            "/api/runes/recommend",
            json={
                "player_id": PLAYER_ID,
                "champion_id": CHAMPION_ID,
                "enemy_champion_id": ENEMY_ID,
                "role": ROLE,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] == "default"
        assert data["runes"]["primaryPath"]["keystone"]["name"] == "Conqueror"


class TestPlayerRuneEndpoint:
    def test_save_and_retrieve_player_rune(self, client):
        payload = {
            "player_id": PLAYER_ID,
            "champion_id": CHAMPION_ID,
            "enemy_champion_id": ENEMY_ID,
            "role": ROLE,
            "runes": SAMPLE_RUNE_PAGE,
            "win": True,
        }
        post_resp = client.post("/api/runes/player", json=payload)
        assert post_resp.status_code == 201
        created = post_resp.json()
        assert created["player_id"] == PLAYER_ID
        assert created["win"] is True

        get_resp = client.get(f"/api/runes/player/{PLAYER_ID}")
        assert get_resp.status_code == 200
        records = get_resp.json()
        assert len(records) == 1
        assert records[0]["champion_id"] == CHAMPION_ID


class TestMatchResultEndpoint:
    def test_record_match_result(self, client):
        payload = {
            "player_id": PLAYER_ID,
            "match_id": "EUW1_12345",
            "champion_id": CHAMPION_ID,
            "enemy_champion_id": ENEMY_ID,
            "role": ROLE,
            "runes": SAMPLE_RUNE_PAGE,
            "win": False,
        }
        resp = client.post("/api/matches", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["win"] is False
        assert data["match_id"] == "EUW1_12345"


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestDefaultRuneEndpoint:
    def test_create_and_retrieve_default_rune(self, client):
        payload = {
            "champion_id": CHAMPION_ID,
            "role": ROLE,
            "runes": SAMPLE_RUNE_PAGE,
            "patch": "14.24",
        }
        post_resp = client.post("/api/runes/default", json=payload)
        assert post_resp.status_code == 201

        get_resp = client.get(f"/api/runes/default/{CHAMPION_ID}")
        assert get_resp.status_code == 200
        records = get_resp.json()
        assert len(records) >= 1
        assert records[0]["role"] == ROLE
