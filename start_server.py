import sys

from src.sendything import SendyThing

SendyThing(name=str(sys.argv[1]), port=int(sys.argv[2]), leader=bool(sys.argv[3])).start()