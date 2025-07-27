-- db/init.sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- In real app, store proper hashes!
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optional: Add some dummy data for initial testing
INSERT INTO users (username, password_hash) VALUES ('testuser1', 'hashedpass1') ON CONFLICT (username) DO NOTHING;
INSERT INTO users (username, password_hash) VALUES ('testuser2', 'hashedpass2') ON CONFLICT (username) DO NOTHING;
INSERT INTO events (name, description, event_date) VALUES ('DevOps Conference', 'Annual gathering for DevOps enthusiasts', '2025-10-26 09:00:00+00') ON CONFLICT DO NOTHING;
INSERT INTO events (name, description, event_date) VALUES ('Cloud Native Meetup', 'Discussing Kubernetes and serverless', '2025-11-10 18:00:00+00') ON CONFLICT DO NOTHING;
