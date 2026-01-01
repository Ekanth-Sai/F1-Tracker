-- Purpose:
-- - This SQL file defines the database schema for F1 tracker

-- It stores:
-- - Driver information
-- - F1 session details (race, qualifying, practice)
-- - High frequency live position data
-- - High frequency live telemetry data
-- - Pit stop events
-- - Aggregated driver statistics for dashboards and ML models

-- Database used:
-- - PostgreSQL

-- Important Notes:
-- - Positions table and telemetry table are high write table 
-- - session_id is the main foreign key across tables. It is on DELETE CASCADE ensuring easy cleanup when a session ends

CREATE TABLE IF NOT EXISTS drivers (
    id BIGSERIAL PRIMARY KEY,
    driver_number INTEGER NOT NULL UNIQUE, 
    name VARCHAR(255) NOT NULL, 
    team VARCHAR(255), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    session_key VARCHAR(255) NOT NULL UNIQUE,
    session_name VARCHAR(255) NOT NULL,
    session_type VARCHAR(50),
    circuit_name VARCHAR(255),
    country VARCHAR(100),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    is_live BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS positions (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    driver_number INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    date TIMESTAMP NOT NULL,
    position INTEGER,
    x DOUBLE PRECISION,
    y DOUBLE PRECISION,
    z DOUBLE PRECISION,
    normalized_x DOUBLE PRECISION,
    normalized_y DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_position_session FOREIGN KEY (session_id) REFERENCES sessions(id),
    INDEX idx_position_session_driver (session_id, driver_number),
    INDEX idx_position_timestamp (session_id, timestamp)
);

CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    driver_number INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    date TIMESTAMP NOT NULL,
    speed INTEGER,
    rpm INTEGER,
    n_gear INTEGER,
    throttle INTEGER,
    brake BOOLEAN,
    drs INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_telemetry_session FOREIGN KEY (session_id) REFERENCES sessions(id),
    INDEX idx_telemetry_session_driver (session_id, driver_number),
    INDEX idx_telemetry_timestamp (session_id, timestamp)
);

CREATE TABLE IF NOT EXISTS pitstops(
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    driver_number INTEGER NOT NULL,
    lap_number INTEGER,
    pit_duration DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pitstop_session FOREIGN KEY (session_id) REFERENCES sessions(id),
    INDEX idx_pitstop_session_driver (session_id, driver_number)
);

CREATE TABLE IF NOT EXISTS driver_stats (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    driver_number INTEGER NOT NULL,
    average_speed DOUBLE PRECISION,
    max_speed INTEGER,
    total_distance DOUBLE PRECISION,
    tyre_compound VARCHAR(50),
    tyre_age INTEGER,
    stint_laps INTEGER,
    position INTEGER,
    gap_to_leader VARCHAR(50),
    last_updated TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stats_session FOREIGN KEY (session_id) REFERENCES sessions(id),
    CONSTRAINT unique_session_driver_stats UNIQUE (session_id, driver_number),
    INDEX idx_stats_session (session_id)
);

CREATE INDEX idx_positions_lookup ON positions(session_id, driver_number, timestamp DESC);
CREATE INDEX idx_telemetry_lookup ON telemetry(session_id, driver_number, timestamp DESC);
CREATE INDEX idx_session_live ON sessions(is_live) WHERE is_live = TRUE;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_drivers_updated_at
BEFORE UPDATE ON drivers
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();