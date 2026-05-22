import socket
from azazel.session import FTPSession

"""
Server Design
"""

# The actual Server itself
class FTPServer:
    def __init__(self, host='', port=2121, root ='/tmp/ftp', reuse_addr=False, password=None):
        self.host = host
        self.port = port
        self.socket = None       # the listening socket
        self.password = password # for password-protected servers
        self.sessions = []       # connected clients
        
        # Directory Stuff
        self.root = root

        self.reuse_addr = reuse_addr # dev flag, basically
    
    def start(self):
        # Behavior on Startup
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.reuse_addr: 
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f'listening on {self.host}:{self.port}')
    
        # Listen until we get a response
        while True:
            conn, addr = self.socket.accept()
            print(f'connection from {addr}')
            session = FTPSession(conn, addr, self.root)
            self.sessions.append(session)
            session.handle()

# for Testing
if __name__ == '__main__':
    ftp = FTPServer()   # builds the machine
    ftp.start()         # turns it on

