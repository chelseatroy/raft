import queue
from config import server_nodes
import message_pass
import threading
from socket import *

class SockNetwork:
    def __init__(self):
        self.socks = {}

    def send(self, destination, msg):
        '''
        Send a message to another server in the cluster
        '''
        # if not connected, try to connect.  Then send.
        # Maybe keep a cache of active connections
        if destination not in self.socks:
            self.socks[destination] = socket(AF_INET, SOCK_STREAM)
            self.socks[destination].connect(config.server_nodes[destination])
        message_pass.send_message(self.socks[destination], msg)


def start_receiver(self, server):
    threading.Thread(target=self._server, args=(server,), daemon=True).start()


def _server(self, server):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(config.server_nodes[server.address])
    sock.listen(1)
    while True:
        client, addr = sock.accept()
        threading.Thread(target=self.get_messages, args=(server, client,), daemon=True).start()


def get_messages(self, server, sock):
    while True:
        msg = message_pass.receive_message(sock)
        server.inbox.put(msg)



class RaftServer:
    def __init__(self, address, net):
        self.inbox = queue.Queue()
        self.address = address
        self.net = net


def start(self):
    self.net.start_receiver(self)


def send(self, dest, msg):
    self.net.send(dest, msg)


def recv(self):
    '''
    Receive a message from any other server
    '''
    return self.inbox.get()


# Thoughts:  how can you test this?
#            can you make a "fake" network that operates "in process"
#
# node0 = RaftNetwork(0)
# node1 = RaftNetwork(1)
# node0.send(1, b'hello')
# msg = node1.recv()
# assert msg == b'hello'

