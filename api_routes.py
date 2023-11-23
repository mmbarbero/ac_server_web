from fastapi import FastAPI
import uvicorn
from api_repository import ApiRepository
import socket
import struct
import proto

app = FastAPI()
apiRepo = ApiRepository()
UDP_SEND_PORT = None
UDP_IP = None
sock = None


@app.get("/")
async def root():
    return 'Work in progress'

@app.get("/current_game_data/")
async def getCurentSessionData():
    result = apiRepo.getCurrentGameSessionData()
    return result

@app.get("/laptimes/")
async def getLaptimesForTrack(track_name: str,track_config: str):
    #/laptimes/?track_name=pk_gunma_cycle_sports_center&track_config=gcsc_full_attack
    result = apiRepo.getAllLapsFromTrackNameFormatted(track_name,track_config)
    return result


@app.get("/update_game_data/")
async def forceUpdateSessionData():
    data = struct.pack("<Bh",proto.ACSP_GET_SESSION_INFO,0)
    sock.sendto(data, (UDP_IP, UDP_SEND_PORT))
    return 'Updated server data'

def runServer(socket,udp_address,udp_port,web_address,web_port):
    global sock
    global UDP_IP
    global UDP_SEND_PORT
    sock = socket
    UDP_IP = udp_address
    UDP_SEND_PORT = udp_port
    uvicorn.run(app, host=web_address, port=web_port)


    