import psycopg2
from datetime import datetime, timezone
from data_schemas import GameSession, ClientSession, Lap
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']

class Database(object):
    def __init__(self):
        self.conn = psycopg2.connect(host=DB_HOST,
                                port=DB_PORT,
                                database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS)
        self.cursor = self.conn.cursor()

    def getLatestGameSessionId(self):
        query = 'SELECT game_session_id FROM game_sessions ORDER BY update_timestamp DESC LIMIT 1'
        self.cursor.execute(query)
        session_id = int(self.cursor.fetchone()[0])
        return session_id
    
    def getClientCurrentSessionIdByCarNumber(self,car_number):
        query = 'SELECT client_session_id FROM client_sessions WHERE car_number = %s and session_end IS NULL ORDER BY session_start DESC LIMIT 1;'
        self.cursor.execute(query,(car_number))
        session_id = int(self.cursor.fetchone()[0])
        return session_id

    def saveClientConnection(self,clientSession):
        query = 'INSERT INTO client_sessions (game_session_id,session_start,driver_id,driver_guid,car_number,car_model,skin) VALUES (%s,%s,%s,%s,%s,%s,%s);'
        clientSession.game_session_id = self.getLatestGameSessionId()
        self.cursor.execute(query,(clientSession.listItems()))
        self.conn.commit()
        print('Inserted client connect')

    def saveClientDisconnection(self,driver_guid):
        query = 'UPDATE client_sessions SET session_end = %s WHERE driver_guid = %s AND session_end IS NULL;'
        self.cursor.execute(query,(datetime.now(timezone.utc),driver_guid))   
        self.conn.commit()
        print('Updated client disconnect')

    def saveLap(self,lap):
        lap.client_session_id = self.getClientCurrentSessionIdByCarNumber(lap.car_number)
        lap.game_session_id = self.getLatestGameSessionId()
        query = 'INSERT INTO laps (lap_timestamp,client_session_id,game_session_id,laptime,cuts,grip_level) VALUES (%s,%s,%s,%s,%s,%s);'
        self.cursor.execute(query,(lap.listItems()))
        self.conn.commit()
        print('Inserted new lap')

    def saveNewGameSession(self,sessionInfo):
        query = 'INSERT INTO game_sessions (update_timestamp,session_index,current_session_index,session_count,server_name,track_name,track_config,session_time,session_name,session_type,lap_number,ambient_temp,road_temp,weather_graphics,elapsed_ms) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        self.cursor.execute(query,(sessionInfo.listItems()))
        self.conn.commit()
        print('Inserted new game session data')

    def updateGameSession(self,sessionInfo):
        session_id = self.getLatestGameSessionId()
        query = 'UPDATE game_sessions SET update_timestamp = %s, session_index = %s,current_session_index = %s,session_count = %s,server_name = %s,track_name = %s,track_config = %s,session_time = %s,session_name = %s,session_type = %s,lap_number = %s,ambient_temp = %s,road_temp = %s,weather_graphics = %s,elapsed_ms = %s WHERE game_session_id = %s;'
        paramList = sessionInfo.listItems()
        paramList.append(session_id)
        self.cursor.execute(query,(paramList))
        print('Updated game session data')
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()



