from data_schemas import GameSession, ClientSession, Lap
import psycopg2.extras
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']

class ApiRepository():

    def __init__(self):
        self.conn = psycopg2.connect(host=DB_HOST,
                                port=DB_PORT,
                                database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS)
        self.cursor = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    
    def getAllLaps(self):
        query = 'SELECT * FROM laps;'
        self.cursor.execute(query)
        result = json.loads(json.dumps(self.cursor.fetchall(),default=str))
        return result

    def getAllLapsFromTrackNameFormatted(self,track_name,track_config,numberOfRecords):
        numberOfRecords = 100 if (numberOfRecords > 100) else numberOfRecords
        query =f'SELECT cs.driver_id,l.laptime,cs.car_model,l.cuts,l.lap_timestamp FROM laps AS l LEFT JOIN game_sessions AS gs ON l.game_session_id = gs.game_session_id AND gs.track_name = %s AND gs.track_config = %s LEFT JOIN client_sessions AS cs ON l.client_session_id = cs.client_session_id ORDER BY l.laptime ASC LIMIT {numberOfRecords};'
        self.cursor.execute(query,([track_name,track_config]))
        result = json.loads(json.dumps(self.cursor.fetchall(),default=str))
        return result
    
    def getCurrentGameSessionData(self):
        query ='SELECT game_session_id,server_name,track_name,track_config,session_time,session_name,lap_number,ambient_temp,road_temp,weather_graphics,elapsed_ms from game_sessions ORDER BY update_timestamp DESC LIMIT 1;'
        self.cursor.execute(query)
        result = json.loads(json.dumps(self.cursor.fetchall(),default=str))
        return result
    
    def getLatestClientConnection(self):
        query = 'SELECT session_start,client_session_id,driver_id,car_model FROM client_sessions ORDER BY session_start DESC LIMIT 1'
        self.cursor.execute(query)
        result = json.loads(json.dumps(self.cursor.fetchall(),default=str))
        return result

    def getLatestClientDisconnection(self):
        query = 'SELECT session_end,client_session_id,driver_id,car_model FROM client_sessions ORDER BY session_end DESC LIMIT 1'
        self.cursor.execute(query)
        result = json.loads(json.dumps(self.cursor.fetchall(),default=str))
        return result

    def __del__(self):
        self.cursor.close()
        self.conn.close()
