import api_routes
import ac_server_monitor
import threading
import socket
from dotenv import load_dotenv
import os

load_dotenv()

UDP_IP = os.environ['UDP_IP']
UDP_PORT = int(os.environ['UDP_PORT'])
UDP_SEND_PORT = int(os.environ['UDP_SEND_PORT'])
WEB_SERVER_ADDRESS=os.environ['WEB_IP']
WEB_SERVER_PORT=int(os.environ['WEB_PORT'])

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", UDP_PORT))
    webServerThread = threading.Thread(target=api_routes.runServer,args=(sock,UDP_IP,UDP_SEND_PORT,WEB_SERVER_ADDRESS,WEB_SERVER_PORT,))
    webServerThread.start()
    server_monitor = ac_server_monitor.ServerMonitor()
    serverMonitorThread = threading.Thread(target=server_monitor.run,args=(sock,))
    serverMonitorThread.start()