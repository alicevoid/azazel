"""
Session Design

    FTP custom implementation to-spec
    I'm just learning as i go

"""

import socket
from azazel.handler import FTPHandler
from azazel.log import get_logger


# The FTP Session Instance
class FTPSession:
    def __init__(self, conn, addr, root):
        self.conn = conn
        self.addr = addr
        self.state = "NOT_LOGGED_IN"
        self.authenticated = False
        self.pasv_mode = False
        self.pasv_sock = None

        # user info
        self.username = None

        # dir stuff
        self.root = root
        self.cwd = "/"

        # data transfer stuff
        self.data_addr = None
        self.transfer_type = "A"

        # handler
        self.handler = FTPHandler(self)

        # logger
        self.log = get_logger()

    def send(self, message):
        # Helper for encoding
        self.conn.send(f"{message}\r\n".encode())

    def handle(self):
        # What happens when Someone Connects
        self.handler.respond(220)
        self.log.info(f"session opened from {self.addr}")

        while True:
            # We Listen... Patiently
            data = self.conn.recv(1024)
            if data == b"":
                break

            # i.e: b'USER alice\r\n' -> verb='USER', args='alice'
            line = data.decode().strip()
            parts = line.split(" ", 1)
            verb = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ""

            # Handler Function
            handler = self.handler.commands.get(verb)
            self.log.debug(f">>> {verb} {args}")
            if handler:
                handler(args)
            else:
                self.handler.respond(502, f"{verb} not implemented")
