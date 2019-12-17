import queue
from config import *

members = []

class RaftNetwork:
    def __init__(self, myself):
        self.address = myself
        self.inbox = queue.Queue()

    def send(self, destination, message):


        """
        send a message to amother server in the cluseter

        """
        pass

    def receive(self):
        """
        receive a message from any other server
        """
        return self.inbox.get()