from datetime import datetime, timezone

class ClientSession():
    def __init__(self,driver_id,driver_guid,car_number,car_model,skin):
        self.game_session_id = None,
        self.session_start = datetime.now(timezone.utc),
        self.driver_id = driver_id,
        self.driver_guid = driver_guid,
        self.car_number = car_number,
        self.car_model = car_model,
        self.skin = skin
    def listItems(self):
        return ([self.game_session_id,self.session_start,self.driver_id,self.driver_guid,self.car_number,self.car_model,self.skin])

class Lap():
    def __init__(self,car_number,laptime,cuts):
        self.lap_timestamp = datetime.now(timezone.utc),
        self.client_session_id = None,
        self.game_session_id = None,
        self.car_number = car_number,
        self.laptime = laptime,
        self.cuts = cuts,
        self.grip_level = 0
    def listItems(self):
        return ([self.lap_timestamp,self.client_session_id,self.game_session_id,self.laptime,self.cuts,self.grip_level])

class GameSession():
    def __init__(self,session_index,current_session_index,session_count,server_name,track_name,track_config,session_time,session_name,session_type,lap_number,wait_time,ambient_temp,road_temp,weather_graphics,elapsed_ms):
        self.update_timestamp = datetime.now(timezone.utc),
        self.session_index = session_index,
        self.current_session_index = current_session_index,
        self.session_count = session_count,
        self.server_name = server_name,
        self.track_config = track_config,
        self.session_time = session_time,
        self.session_name = session_name,
        self.session_type = session_type,
        self.lap_number = lap_number,
        self.wait_time = wait_time,
        self.ambient_temp = ambient_temp,
        self.road_temp = road_temp,
        self.weather_graphics = weather_graphics,
        self.elapsed_ms = elapsed_ms
        if('../' in track_name):
            self.track_name = track_name.split('../')[1]
        else:
            self.track_name = track_name

    def listItems(self):
        return ([self.update_timestamp,self.session_index,self.current_session_index,self.session_count,self.server_name,self.track_name,self.track_config,self.session_time,self.session_name,self.session_type,self.lap_number,self.ambient_temp,self.road_temp,self.weather_graphics,self.elapsed_ms])