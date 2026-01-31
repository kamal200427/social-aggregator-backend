-- ./database/schema.sql

-- Table: posts
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,          -- youtube, twitter, facebook, linkedin, instagram
    author TEXT NOT NULL,          -- Author / channel / page / username
    title TEXT,                    -- Short title or truncated content
    url TEXT NOT NULL UNIQUE,      -- Original post URL (unique to prevent duplicates)
    timestamp DATETIME,            -- Post published date
    content TEXT,                  -- Full content / description
    media TEXT                     -- Media URL (image/video thumbnail)
);

-- Optional: Index for faster queries by source
CREATE INDEX IF NOT EXISTS idx_posts_source ON posts(source);

-- Optional: Index for faster queries by timestamp
CREATE INDEX IF NOT EXISTS idx_posts_timestamp ON posts(timestamp);
