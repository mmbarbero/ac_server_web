from fastapi import FastAPI
import uvicorn
from api_repository import ApiRepository
from server_side_events import SSEvents
import socket
import struct
import proto
import socketio
import threading
from fastapi.middleware.cors import CORSMiddleware
import os 
from dotenv import load_dotenv
load_dotenv()

FRONTEND_ADDRESS = os.environ['FRONTEND_ADDRESS']

app = FastAPI()
origins = [
    FRONTEND_ADDRESS
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

apiRepo = ApiRepository()
UDP_SEND_PORT = None
UDP_IP = None
sock = None
sio = socketio.AsyncServer(cors_allowed_origins=FRONTEND_ADDRESS, async_mode='asgi')
sio_app = socketio.ASGIApp(sio, app)

@app.get("/")
async def root():
    return 'Work in progress'

@app.get("/current_game_data/")
async def getCurentSessionData():
    result = apiRepo.getCurrentGameSessionData()
    return result

@app.get("/latest_connect/")
async def getCurentSessionData():
    result = apiRepo.getLatestClientConnection()
    return result

@app.get("/latest_disconnect/")
async def getCurentSessionData():
    result = apiRepo.getLatestClientDisconnection()
    return result

@app.get("/laptimes/")
async def getLaptimesForTrack(track_name: str,track_config: str, numberOfRecords: int):
    # /laptimes/?track_name=pk_gunma_cycle_sports_center&track_config=gcsc_full_attack&numberOfRecords=10
    result = apiRepo.getAllLapsFromTrackNameFormatted(track_name,track_config,numberOfRecords)
    return result

@app.get("/update_game_data/")
async def forceUpdateSessionData():
    data = struct.pack("<Bh",proto.ACSP_GET_SESSION_INFO,0)
    sock.sendto(data, (UDP_IP, UDP_SEND_PORT))
    return 'Updated server data'

@sio.on('connect')
async def connect_hanlder(sid,environ):
    print(f"Client connected")

@sio.on('disconnect')
async def disconnect_handler(sid):
    print(f"Client disconnected")

def runServer(socket,udp_address,udp_port,web_address,web_port):
    global sock
    global UDP_IP
    global UDP_SEND_PORT
    sse = SSEvents()
    eventsThread = threading.Thread(target=sse.entrypoint,args=(sio,))
    eventsThread.start()
    sock = socket
    UDP_IP = udp_address
    UDP_SEND_PORT = udp_port
    uvicorn.run(sio_app, host=web_address, port=web_port)


    