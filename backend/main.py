"""RuneLoLDB FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import champions, runes, matches, lcu

app = FastAPI(
    title="RuneLoLDB API",
    description="League of Legends rune optimization backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(champions.router, prefix="/api/champions", tags=["champions"])
app.include_router(runes.router, prefix="/api/runes", tags=["runes"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(lcu.router, prefix="/lcu", tags=["lcu"])


@app.get("/health")
def health_check():
    """Health-check endpoint."""
    return {"status": "ok", "service": "RuneLoLDB API"}
