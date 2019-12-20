# Send a message.  The message stays intact at all times.  No
# partial messages or fragments.   For example:  if you gave
# send_message a message with 10 million bytes, it is returned
# as 10 million byte message by recv_message() on the receiver. ​

def send_message(sock, msg):
    send_size(sock, len(msg))
    sock.sendall(msg)

# send_message(sock, b'Hello World')   ->>>  b"<size>Hello World"

def receive_message(sock):
    size = receive_size(sock)           # get the message size
    msg = receive_exactly(sock, size)   # Receive exactly this many bytes
    return msg

def send_size(sock, size):
    sock.sendall(size.to_bytes(8, "big"))

def receive_size(sock):
    message = receive_exactly(sock, 8)
    return int.from_bytes(message, "big")

def receive_exactly(sock, nbytes):
    '''
    Receive exactly nbytes of data on a socket
    '''
    msg = b''
    while nbytes > 0:
        chunk = sock.recv(nbytes)   # Might return partial data (whatever received so far)
        if not chunk:
            # Connection closed!
            raise IOError("The other side closed this connection.")
        msg += chunk
        nbytes -= len(chunk)
    return msg
