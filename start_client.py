import sys

from src.client import Client

Client(server_port=int(sys.argv[1])).start()