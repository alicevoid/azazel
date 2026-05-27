"""
Session Design

    FTP custom implementation to-spec
    see RFC 959 for reference

    at some point, i plan to implement FTPS (see RFC 4217)
    but for now, i'm just learning as i go 

"""

import socket
import os
import stat
import time
from azazel.dtp import DataTransferProcess

# The FTP Session Instance 
class FTPSession:
    def __init__(self, conn, addr, root):
        self.conn = conn
        self.addr = addr
        self.state = 'NOT_LOGGED_IN'
        self.authenticated = False
        self.pasv_mode = False
        self.pasv_sock = None

        # dir stuff
        self.root = root
        self.cwd = '/'

        # data transfer stuff
        self.data_addr = None
        self.transfer_type = 'A'

        # dispatch table
        self.commands = {
            'NOOP': self.handle_noop, 
            'QUIT': self.handle_quit, 
            'USER': self.handle_user, 
            'PASS': self.handle_pass,
            'PWD' : self.handle_pwd,
            'CWD' : self.handle_cwd,
            'PORT': self.handle_port,
            'LIST': self.handle_list,
            'RETR': self.handle_retr,
            'STOR': self.handle_stor,
            'TYPE': self.handle_type,
            'PASV': self.handle_pasv,
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
        # TODO: Error Handling
        self.username = args
        self.send('331 User name okay, need password\r\n')

    def handle_pass(self, args):
        # Authenticate User 
        # TODO: Authentication Methods
        self.authenticated = True
        self.state = 'LOGGED_IN'
        self.send('230 User logged in\r\n')

    def handle_pwd(self, args):
        # Print working directory
        self.send(f'257 "{self.cwd}" is current directory\r\n')

    def handle_cwd(self, args):
        self.cwd = args
        self.send(f'250 directory changed to "{self.cwd}"\r\n')

    def handle_port(self, args):
        # Handle IP / PORT setting
        parts = args.split(',') # i.e: 192.168.0.1:50185 -> 192,168,0,1,196,9
        ip = '.'.join(parts[:4])
        port = (int(parts[4]) * 256) + int(parts[5])
        self.data_addr = (ip, port)
        self.send('200 PORT command successful\r\n')
        pass

    def require_auth(self):
        # Do we require Authentification or not? 
        if not self.authenticated:
            self.send('530 Not logged in\r\n')
            return False
        return True

    def open_data_connection(self):
        # Sets up the Data Transfer Process
        if self.pasv_mode and self.pasv_sock:
            conn, _ = self.pasv_sock.accept() # Client initiates
            self.pasv_sock.close()
            self.pasv_sock = None
            self.pasv_mode = False
            return conn
        elif self.data_addr: 
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.data_addr) # set during PORT
            return sock
        else:
            self.send('425 Use PORT first\r\n')
            return None

    def handle_list(self, args): 
        if not self.require_auth():
            return
        if not self.data_addr and not self.pasv_mode:
            self.send('425 Use PORT or PASV first\r\n')
            return

        # filepath resolution
        filepath = os.path.join(self.root, self.cwd.lstrip('/'), args)
        if not os.path.exists(filepath):
            self.send('550 File not found\r\n')
            return

        self.send('150 Opening data connection\r\n')
        sock = self.open_data_connection()
        dtp = DataTransferProcess(sock)
        dtp.send_listing(self.list_dir(filepath))
        sock.close()
        self.send('226 Transfer complete\r\n')

    def list_dir(self, path):
        # Handle extended listing display {i.e: ls -l}
        entries = []
        for name in os.listdir(path):
            full = os.path.join(path, name)
            s = os.stat(full)
            size = s.st_size
            mtime = time.strftime('%b %d %H:%M', time.localtime(s.st_mtime))
            kind = 'd' if os.path.isdir(full) else '-'
            entries.append(f'{kind}rwxr-xr-x 1 ftp ftp {size:>8} {mtime} {name}')
        return entries

    def handle_stor(self, args):
        if not self.require_auth():
            return
        if not self.data_addr and not self.pasv_mode:
            self.send('425 Use PORT or PASV first\r\n')
            return

        # filepath resolution
        filepath = os.path.join(self.root, self.cwd.lstrip('/'), args)
        if not os.path.exists(os.path.dirname(filepath)):
            self.send('550 File not found\r\n')
            return

        self.send('125 Data connection already open\r\n')
        sock = self.open_data_connection()
        dtp = DataTransferProcess(sock)
        dtp.recv_file(filepath)
        dtp.close()
        self.send('226 Transfer complete\r\n')

    def handle_retr(self, args):
        if not self.require_auth():
            return
        if not self.data_addr and not self.pasv_mode:
            self.send('425 Use PORT or PASV first\r\n')
            return

        # filepath resolution
        filepath = os.path.join(self.root, self.cwd.lstrip('/'), args)
        if not os.path.exists(filepath):
            self.send('550 File not found\r\n')
            return

        self.send('150 Opening data connection\r\n')
        sock = self.open_data_connection()
        dtp = DataTransferProcess(sock)
        dtp.send_file(filepath)
        dtp.close()
        self.send('226 Transfer complete\r\n')

    def handle_type(self, args):
        # A=ASCII, I=Binary/Img
        if args in ('A', 'I'):
            self.transfer_type = args
            self.send(f'200 Type set to {args}\r\n')
        else:
            self.send('504 Type not supported\r\n')

    def handle_pasv(self, args):
        # handles passive port setting
        self.pasv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pasv_sock.bind(('', 0)) # OS picks port
        self.pasv_sock.listen(1)

        _, port = self.pasv_sock.getsockname()
        p1, p2 = port // 256, port % 256

        # TODO: change sent command for actual production
        self.send(f'227 Entering Passive Mode (127,0,0,1,{p1},{p2})\r\n')
        self.pasv_mode = True


