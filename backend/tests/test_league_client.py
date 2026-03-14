"""Tests for the LeagueClientService (mocked LCU calls)."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.league_client import LeagueClientService, _parse_lockfile


class TestParseLockfile:
    def test_parses_correctly(self, tmp_path):
        lockfile = tmp_path / "lockfile"
        lockfile.write_text("LeagueClient:12345:50001:supersecret:https")
        result = _parse_lockfile(lockfile)
        assert result["port"] == 50001
        assert result["password"] == "supersecret"
        assert result["protocol"] == "https"


class TestLeagueClientService:
    def test_connect_returns_false_when_no_lockfile(self):
        service = LeagueClientService()
        with patch(
            "app.services.league_client._find_lockfile", return_value=None
        ):
            assert service.connect() is False
            assert not service.is_connected()

    def test_get_current_champion_returns_none_when_not_connected(self):
        service = LeagueClientService()
        assert service.get_current_champion() is None

    def test_get_champ_select_session_returns_none_when_client_none(self):
        service = LeagueClientService()
        assert service.get_champ_select_session() is None

    def test_import_rune_page_returns_false_when_not_connected(self):
        service = LeagueClientService()
        assert service.import_rune_page({}) is False

    def test_get_current_champion_parses_session(self):
        service = LeagueClientService()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "localPlayerCellId": 2,
            "myTeam": [
                {"cellId": 1, "championId": 100},
                {"cellId": 2, "championId": 157},
            ],
        }
        mock_client.get.return_value = mock_response
        service._client = mock_client

        result = service.get_current_champion()
        assert result == 157

    def test_replace_rune_page_deletes_oldest_editable(self):
        service = LeagueClientService()
        mock_client = MagicMock()

        # Simulate two existing pages, the oldest has id=1
        mock_pages_response = MagicMock()
        mock_pages_response.status_code = 200
        mock_pages_response.json.return_value = [
            {"id": 1, "isDeletable": True},
            {"id": 2, "isDeletable": True},
        ]

        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 204

        mock_create_response = MagicMock()
        mock_create_response.status_code = 201

        mock_client.get.return_value = mock_pages_response
        mock_client.delete.return_value = mock_delete_response
        mock_client.post.return_value = mock_create_response
        service._client = mock_client

        result = service.replace_rune_page({"name": "New Page"})
        assert result is True
        mock_client.delete.assert_called_once_with("/lol-perks/v1/pages/1")
