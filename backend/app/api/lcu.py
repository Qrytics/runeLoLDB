"""
League Client (LCU) proxy endpoint.

The Electron renderer cannot directly call the League Client API due to SSL
certificate issues, so the backend acts as a proxy.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.services.league_client import LeagueClientService

router = APIRouter()

_lcu_service: Optional[LeagueClientService] = None


def _get_lcu() -> LeagueClientService:
    global _lcu_service
    if _lcu_service is None or not _lcu_service.is_connected():
        _lcu_service = LeagueClientService()
        _lcu_service.connect()
    return _lcu_service


@router.get("/champ-select")
def get_champ_select_session():
    """
    Return the current champion-select session from the League client.

    Returns 204 (No Content) when not in champion select or when the League
    client is not running.
    """
    lcu = _get_lcu()
    if not lcu.is_connected():
        raise HTTPException(status_code=503, detail="League client not found.")

    session = lcu.get_champ_select_session()
    if not session:
        raise HTTPException(status_code=204, detail="Not in champion select.")
    return session


@router.post("/runes/import")
def import_rune_page(rune_page: dict):
    """
    Import the given rune page into the League client via the LCU API.

    The rune_page dict must conform to the LCU /lol-perks/v1/pages schema.
    """
    lcu = _get_lcu()
    if not lcu.is_connected():
        raise HTTPException(status_code=503, detail="League client not found.")

    success = lcu.replace_rune_page(rune_page)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to import rune page.")
    return {"success": True}
