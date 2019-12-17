import sys
from server import Server

Server(name=str(sys.argv[1]), port=int(sys.argv[2])).start()