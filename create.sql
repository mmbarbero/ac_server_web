

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

CREATE or REPLACE FUNCTION notify_new_lap()
    RETURNS trigger
     LANGUAGE 'plpgsql'
as $BODY$
declare
begin
    if (tg_op = 'INSERT') then
        NOTIFY new_lap_added;
    end if;
    return null;
end
$BODY$;

CREATE or REPLACE FUNCTION notify_client_session()
    RETURNS trigger
     LANGUAGE 'plpgsql'
as $BODY$
declare
begin
    if (tg_op = 'INSERT') then
        NOTIFY new_client_session_added;
    elsif (tg_op = 'UPDATE') then
        NOTIFY new_client_session_updated;
    end if;
    return null;
end
$BODY$;

CREATE or REPLACE FUNCTION notify_game_session()
    RETURNS trigger
     LANGUAGE 'plpgsql'
as $BODY$
declare
begin
    if (tg_op = 'INSERT') then
        NOTIFY new_game_session_added;
    end if;
    return null;
end
$BODY$;

CREATE TRIGGER after_added_lap
    AFTER INSERT
    ON laps
    FOR EACH ROW
    EXECUTE PROCEDURE notify_new_lap();

CREATE TRIGGER after_changed_client_session
    AFTER INSERT OR UPDATE
    ON client_sessions
    FOR EACH ROW
    EXECUTE PROCEDURE notify_client_session();

CREATE TRIGGER after_changed_game_session
    AFTER INSERT 
    ON game_sessions
    FOR EACH ROW
    EXECUTE PROCEDURE notify_game_session();