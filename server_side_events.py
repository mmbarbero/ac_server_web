import socketio
from dotenv import load_dotenv
import os
import asyncio
import psycopg2
import queue
import threading
import time

load_dotenv()

DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']

class eventConsts():
    NEW_LAP="new_lap_added"
    CLIENT_CONNECTED="new_client_session_added"
    CLIENT_DISCONNECTED="new_client_session_updated"
    NEW_GAME_SESSION="new_game_session_added"

class channels():
    CLIENT_ACTIVITY='client_activity'
    LAP_ACTIVITY='lap_activity'
    GAME_SESSION_ACTIVITY='game_session_activity'
class SSEvents():
    def __init__(self):

        self.conn = psycopg2.connect(host=DB_HOST,
                                port=DB_PORT,
                                database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"LISTEN {eventConsts.NEW_LAP};")
        self.cursor.execute(f"LISTEN {eventConsts.CLIENT_CONNECTED};")
        self.cursor.execute(f"LISTEN {eventConsts.CLIENT_DISCONNECTED};")
        self.cursor.execute(f"LISTEN {eventConsts.NEW_GAME_SESSION};")

    async def sendEvent(self,channel,message,socketio):
            await socketio.emit(channel,message)

    async def event_listener(self,socketio):
        while True:
            self.conn.poll()
            if self.conn.notifies:
                notify = self.conn.notifies.pop(0)
                if(notify.channel == eventConsts.CLIENT_CONNECTED):
                    await self.sendEvent(channels.CLIENT_ACTIVITY,'CONNECTION',socketio)
                elif(notify.channel == eventConsts.CLIENT_DISCONNECTED):
                    await self.sendEvent(channels.CLIENT_ACTIVITY,'DISCONNECTION',socketio)
                elif(notify.channel == eventConsts.NEW_LAP):
                    await self.sendEvent(channels.LAP_ACTIVITY,'UPDATE',socketio)
                elif(notify.channel == eventConsts.NEW_GAME_SESSION):
                    await self.sendEvent(channels.GAME_SESSION_ACTIVITY,'UPDATE',socketio)
                time.sleep(1)
    def entrypoint(self,socketio):
        asyncio.run(self.event_listener(socketio))
                    
