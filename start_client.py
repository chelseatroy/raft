import sys
from client import Client

Client(server_port=int(sys.argv[1])).start()