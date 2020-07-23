import sys

from src.server import Server

am_i_the_leader = False
if len(sys.argv) > 3 and sys.argv[3] == 'True':
    am_i_the_leader = True

Server(name=str(sys.argv[1]), port=int(sys.argv[2]), leader=am_i_the_leader).start()