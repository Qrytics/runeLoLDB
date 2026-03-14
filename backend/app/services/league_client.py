"""
League Client API service.

Polls the local League of Legends client REST API (LCU) to detect
champion select sessions and retrieve the current game state.

The LCU listens on a local HTTPS port with self-signed certificate and uses
HTTP Basic auth with the credentials found in the lockfile.
"""

from __future__ import annotations

import base64
import os
import re
import ssl
from pathlib import Path
from typing import Optional

import httpx


# Typical lockfile locations per OS
_LOCKFILE_PATHS = [
    Path("C:/Riot Games/League of Legends/lockfile"),  # Windows default
    Path.home() / "Applications/League of Legends.app/Contents/LoL/lockfile",  # macOS
    Path("/opt/riot/league-of-legends/lockfile"),  # Linux (unofficial)
]

# Allow override via env variable
_ENV_LOCKFILE = os.environ.get("LOL_LOCKFILE_PATH")


def _find_lockfile() -> Optional[Path]:
    if _ENV_LOCKFILE:
        p = Path(_ENV_LOCKFILE)
        return p if p.exists() else None
    for path in _LOCKFILE_PATHS:
        if path.exists():
            return path
    return None


def _parse_lockfile(path: Path) -> dict:
    """
    Parse the lockfile and return a dict with:
        process, pid, port, password, protocol
    """
    content = path.read_text(encoding="utf-8").strip()
    process, pid, port, password, protocol = content.split(":")
    return {
        "process": process,
        "pid": pid,
        "port": int(port),
        "password": password,
        "protocol": protocol,
    }


def _build_client(lock: dict) -> httpx.Client:
    """Build an httpx client pre-configured for the LCU."""
    credentials = base64.b64encode(f"riot:{lock['password']}".encode()).decode()
    # The LCU uses a self-signed certificate — we disable verification.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return httpx.Client(
        base_url=f"https://127.0.0.1:{lock['port']}",
        headers={"Authorization": f"Basic {credentials}"},
        verify=False,
        timeout=5,
    )


class LeagueClientService:
    """Wraps LCU API calls needed for champion-select detection and rune import."""

    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self._lock: Optional[dict] = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """
        Locate the lockfile and build the HTTP client.

        Returns True if the client connected successfully, False otherwise.
        """
        lockfile = _find_lockfile()
        if not lockfile:
            return False
        self._lock = _parse_lockfile(lockfile)
        self._client = _build_client(self._lock)
        return True

    def is_connected(self) -> bool:
        return self._client is not None

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    # ------------------------------------------------------------------
    # Champion select
    # ------------------------------------------------------------------

    def get_champ_select_session(self) -> Optional[dict]:
        """
        Return the current champion-select session, or None if not in champ select.
        """
        if not self._client:
            return None
        try:
            resp = self._client.get("/lol-champ-select/v1/session")
            if resp.status_code == 200:
                return resp.json()
        except httpx.RequestError:
            pass
        return None

    def get_current_champion(self) -> Optional[int]:
        """
        Return the Riot champion ID of the champion the local player has locked in,
        or None if not yet locked in or not in champ select.
        """
        session = self.get_champ_select_session()
        if not session:
            return None
        local_cell = session.get("localPlayerCellId")
        for pick in session.get("myTeam", []):
            if pick.get("cellId") == local_cell:
                return pick.get("championId") or None
        return None

    def get_current_summoner(self) -> Optional[dict]:
        """Return the local summoner's info dict."""
        if not self._client:
            return None
        try:
            resp = self._client.get("/lol-summoner/v1/current-summoner")
            if resp.status_code == 200:
                return resp.json()
        except httpx.RequestError:
            pass
        return None

    # ------------------------------------------------------------------
    # Rune import
    # ------------------------------------------------------------------

    def get_rune_pages(self) -> list[dict]:
        """Return all rune pages currently saved in the client."""
        if not self._client:
            return []
        try:
            resp = self._client.get("/lol-perks/v1/pages")
            if resp.status_code == 200:
                return resp.json()
        except httpx.RequestError:
            pass
        return []

    def import_rune_page(self, rune_page: dict) -> bool:
        """
        Import (create) a new rune page into the League client.

        rune_page should be a dict matching the LCU /lol-perks/v1/pages POST schema.
        Returns True on success, False otherwise.
        """
        if not self._client:
            return False
        try:
            resp = self._client.post("/lol-perks/v1/pages", json=rune_page)
            return resp.status_code in (200, 201)
        except httpx.RequestError:
            return False

    def delete_rune_page(self, page_id: int) -> bool:
        """Delete a rune page by ID."""
        if not self._client:
            return False
        try:
            resp = self._client.delete(f"/lol-perks/v1/pages/{page_id}")
            return resp.status_code in (200, 204)
        except httpx.RequestError:
            return False

    def replace_rune_page(self, rune_page: dict) -> bool:
        """
        Replace the oldest editable rune page slot with the given page.

        The LCU limits the number of custom rune pages; this method removes
        the oldest one before importing the new page.
        """
        pages = self.get_rune_pages()
        editable = [p for p in pages if p.get("isDeletable", False)]
        if editable:
            oldest = min(editable, key=lambda p: p.get("id", 0))
            self.delete_rune_page(oldest["id"])
        return self.import_rune_page(rune_page)
