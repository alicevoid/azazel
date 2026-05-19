import socket
from azazel.session import FTPSession

"""
Server Design
"""

# The actual Server itself
class FTPServer:
    def __init__(self, host='', port=2121):
        self.host = host
        self.port = port
        self.socket = None      # the listening socket
        self.sessions = []      # connected clients
    
    def start(self):
        # Behavior on Startup
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f'listening on {self.host}:{self.port}')
    
        # Listen until we get a response
        while True:
            conn, addr = self.socket.accept()
            print(f'connection from {addr}')
            session = FTPSession(conn, addr)
            self.sessions.append(session)
            session.handle()

# for Testing
if __name__ == '__main__':
    ftp = FTPServer()   # builds the machine
    ftp.start()         # turns it on

