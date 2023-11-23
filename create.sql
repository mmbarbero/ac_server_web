

CREATE TABLE IF NOT EXISTS client_sessions (
    client_session_id SERIAL PRIMARY KEY,
    game_session_id int,
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    driver_id varchar,
    driver_guid varchar,
    car_number int,
    car_model varchar,
    skin varchar
);

CREATE TABLE IF NOT EXISTS laps (
    lap_id SERIAL PRIMARY KEY,
    lap_timestamp TIMESTAMP,
    client_session_id int,
    game_session_id int,
    laptime int,
    cuts int,
    grip_level int
);

CREATE TABLE IF NOT EXISTS game_sessions (
    game_session_id SERIAL PRIMARY KEY,
    update_timestamp TIMESTAMP,
    session_index int,
    current_session_index int,
    session_count int,
    server_name varchar,
    track_name varchar,
    track_config varchar,
    session_time int,
    session_name varchar,
    session_type varchar,
    lap_number int,
    ambient_temp int,
    road_temp int,
    weather_graphics varchar,
    elapsed_ms int
);