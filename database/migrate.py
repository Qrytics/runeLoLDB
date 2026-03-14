#!/usr/bin/env python3
"""Database migration runner for RuneLoLDB."""

import os
import sys
import psycopg2
from psycopg2 import sql
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_connection():
    """Create a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ.get("DB_NAME", "runeloldb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
    )


def ensure_migrations_table(conn):
    """Create the migrations tracking table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
    conn.commit()


def get_applied_migrations(conn):
    """Return the set of already-applied migration filenames."""
    with conn.cursor() as cur:
        cur.execute("SELECT filename FROM schema_migrations ORDER BY filename")
        return {row[0] for row in cur.fetchall()}


def apply_migration(conn, path: Path):
    """Apply a single SQL migration file."""
    with conn.cursor() as cur:
        sql_content = path.read_text(encoding="utf-8")
        cur.execute(sql_content)
        cur.execute(
            "INSERT INTO schema_migrations (filename) VALUES (%s)",
            (path.name,),
        )
    conn.commit()
    print(f"  Applied: {path.name}")


def run_migrations():
    """Run all pending database migrations in order."""
    conn = get_connection()
    try:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        pending = [f for f in migration_files if f.name not in applied]

        if not pending:
            print("No pending migrations.")
            return

        print(f"Applying {len(pending)} migration(s)...")
        for migration_path in pending:
            apply_migration(conn, migration_path)

        print("All migrations applied successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    run_migrations()
