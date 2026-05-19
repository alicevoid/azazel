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

        # dispatch table
        self.commands = {
            'NOOP': self.handle_noop, 
            'QUIT': self.handle_quit, 
            'USER': self.handle_user, 
        }
    
    def send(self, message):
        # Helper for encoding
        self.conn.send(message.encode())

    def handle(self):
        # What happens when Someone Connects
        self.send('220 Ready\r\n') 

        while True:
            # We Listen... Patiently
            data = self.conn.recv(1024) 
            if data == b'':
                break
            
            # i.e: b'USER alice\r\n' -> verb='USER', args='alice' 
            line = data.decode().strip()
            parts = line.split(' ', 1)
            verb = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ''

            # Dispatch Table -> Handler Function
            handler = self.commands.get(verb)
            if handler:
                handler(args)
            else:
                self.send(f'502 {verb} not implemented\r\n')

    def handle_noop(self, args):
        # No Operation
        self.send('200 OK\r\n')

    def handle_quit(self, args):
        # Terminate
        self.send('221 Goodbye\r\n')

    def handle_user(self, args):
        # Establish User Connection
        self.username = args
        self.send('331 User name okay, need password\r\n')

