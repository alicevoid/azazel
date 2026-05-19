"""
Session Design

    FTP custom implementation to-spec
    see RFC 959 for reference

    at some point, i plan to implement FTPS (see RFC 4217)
    but for now, i'm just learning as i go 

"""

# The FTP Session Instance 
class FTPSession:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.state = 'NOT_LOGGED_IN'
    
    def handle(self):
        # What happens when Someone Connects
        self.conn.send(b'220 Ready\r\n')     # Speak First
        self.conn.recv(1024)                 # Then Listen 
        pass
