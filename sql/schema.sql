-- Database schema for audio fingerprinting system

-- Songs table: stores metadata about reference songs
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fingerprints table: stores audio fingerprint hashes
CREATE TABLE IF NOT EXISTS fingerprints (
    id SERIAL PRIMARY KEY,
    hash VARCHAR(40) NOT NULL,  -- SHA1 hash (40 hex characters)
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    time_offset FLOAT NOT NULL,  -- Time offset in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index on hash for fast lookups during recognition
CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON fingerprints(hash);

-- Index on song_id for efficient joins
CREATE INDEX IF NOT EXISTS idx_fingerprints_song_id ON fingerprints(song_id);

-- Composite index for hash + song_id queries
CREATE INDEX IF NOT EXISTS idx_fingerprints_hash_song ON fingerprints(hash, song_id);
