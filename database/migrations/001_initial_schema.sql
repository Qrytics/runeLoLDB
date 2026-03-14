-- RuneLoLDB Initial Schema
-- Creates all tables needed for the rune optimization system

CREATE TABLE IF NOT EXISTS champions (
    id SERIAL PRIMARY KEY,
    champion_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    key VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS default_runes (
    id SERIAL PRIMARY KEY,
    champion_id INTEGER NOT NULL REFERENCES champions(champion_id),
    role VARCHAR(50) NOT NULL DEFAULT 'ANY',
    runes JSONB NOT NULL,
    patch VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (champion_id, role)
);

CREATE TABLE IF NOT EXISTS player_runes (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(100) NOT NULL,
    champion_id INTEGER NOT NULL REFERENCES champions(champion_id),
    enemy_champion_id INTEGER NOT NULL REFERENCES champions(champion_id),
    role VARCHAR(50) NOT NULL DEFAULT 'ANY',
    runes JSONB NOT NULL,
    win BOOLEAN,
    match_id VARCHAR(100),
    played_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_player_runes_lookup
    ON player_runes (player_id, champion_id, enemy_champion_id, role);

CREATE TABLE IF NOT EXISTS pro_runes (
    id SERIAL PRIMARY KEY,
    champion_id INTEGER NOT NULL REFERENCES champions(champion_id),
    enemy_champion_id INTEGER NOT NULL REFERENCES champions(champion_id),
    role VARCHAR(50) NOT NULL DEFAULT 'ANY',
    runes JSONB NOT NULL,
    pick_rate FLOAT NOT NULL DEFAULT 0,
    win_rate FLOAT NOT NULL DEFAULT 0,
    sample_size INTEGER NOT NULL DEFAULT 0,
    min_rank VARCHAR(20) NOT NULL DEFAULT 'MASTER',
    patch VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pro_runes_lookup
    ON pro_runes (champion_id, enemy_champion_id, role, win_rate DESC);

CREATE TABLE IF NOT EXISTS matchup_stats (
    id SERIAL PRIMARY KEY,
    champion_id INTEGER NOT NULL REFERENCES champions(champion_id),
    enemy_champion_id INTEGER NOT NULL REFERENCES champions(champion_id),
    role VARCHAR(50) NOT NULL DEFAULT 'ANY',
    win_rate FLOAT,
    difficulty VARCHAR(20),
    sample_size INTEGER DEFAULT 0,
    patch VARCHAR(20),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (champion_id, enemy_champion_id, role, patch)
);
