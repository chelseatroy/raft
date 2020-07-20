import sys

from src.server import Server

Server(name=str(sys.argv[1]), port=int(sys.argv[2]), leader=bool(sys.argv[3])).start()