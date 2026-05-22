import socket

"""
Data Transfer Protocol Session
"""

class DataTransferProcess:
    def __init__(self, sock):
        # TODO: TLS Socket
        self.sock = sock 

    def send_file(self, filepath):
        # open file, send bytes over self.sock
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                self.sock.sendall(chunk)

    def recv_file(self, filepath):
        # recieve bytes froms self.sock, write to file
        with open(filepath, 'wb') as f:
            while True:
                chunk = self.sock.recv(8192)
                if not chunk:
                    break
                f.write(chunk)

    def send_listing(self, lines):
        # send dir listing over self.sock
        payload = '\r\n'.join(lines) + '\r\n'
        self.sock.sendall(payload.encode())
    
    def close(self):
        self.sock.close()
        
