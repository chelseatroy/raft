import sys

from src.server import Server

voting = True
if len(sys.argv) > 3 and sys.argv[3] == 'False':
    voting = False

Server(name=str(sys.argv[1]), port=int(sys.argv[2]), voting=voting).start()