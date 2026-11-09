-- ShortRoute PostgreSQL schema
-- Run this file once against both the development and test databases.

BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username VARCHAR(20) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    membership_tier TEXT NOT NULL DEFAULT 'free',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT users_membership_tier_check
        CHECK (membership_tier IN ('free', 'premium'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    token_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS links (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_id BIGINT REFERENCES users(id),
    destination_url TEXT NOT NULL,
    short_code TEXT NOT NULL UNIQUE,
    custom_slug VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ,
    click_count BIGINT NOT NULL DEFAULT 0,

    CONSTRAINT links_owner_custom_slug_key
        UNIQUE (owner_id, custom_slug),
    CONSTRAINT links_click_count_check
        CHECK (click_count >= 0)
);

-- PostgreSQL does not automatically index foreign-key columns.
CREATE INDEX IF NOT EXISTS sessions_user_id_idx
    ON sessions (user_id);

CREATE INDEX IF NOT EXISTS links_owner_id_idx
    ON links (owner_id);

-- Helps the manual cleanup command find expired or revoked sessions.
CREATE INDEX IF NOT EXISTS sessions_expires_at_idx
    ON sessions (expires_at);

CREATE INDEX IF NOT EXISTS sessions_revoked_at_idx
    ON sessions (revoked_at)
    WHERE revoked_at IS NOT NULL;

COMMIT;
