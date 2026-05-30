"""
Handler Design

    Architecture for overall argument parsing
    Designed to play nicely with interface

"""

import socket
import os
import time
from azazel.dtp import DataTransferProcess

RESPONSES = {
    125: "Data connection already open",
    150: "Opening data connection",
    200: "OK",
    220: "Ready",
    221: "Goodbye",
    226: "Transfer complete",
    227: "Entering Passive Mode",
    230: "User logged in",
    250: "OK",
    257: "is current directory",
    331: "User name okay, need password",
    425: "Use PORT or PASV first",
    502: "Command not implemented",
    504: "Type not supported",
    530: "Not logged in",
    550: "File not found",
}


class FTPHandler:
    def __init__(self, session):

        self.session = session

        # TODO: auth checking probably happens here

        # dispatch table
        self.commands = {
            "NOOP": self.ftp_noop,
            "QUIT": self.ftp_quit,
            "USER": self.ftp_user,
            "PASS": self.ftp_pass,
            "PWD": self.ftp_pwd,
            "CWD": self.ftp_cwd,
            "PORT": self.ftp_port,
            "LIST": self.ftp_list,
            "RETR": self.ftp_retr,
            "STOR": self.ftp_stor,
            "TYPE": self.ftp_type,
            "PASV": self.ftp_pasv,
        }

    def respond(self, code, message=None):
        msg = message or RESPONSES.get(code, "")
        self.session.send(f"{code} {msg}")

    def require_auth(self):
        # Do we require Authentification or not?
        if not self.session.authenticated:
            self.respond(530)
            return False
        return True

    def open_data_connection(self):
        # Sets up the Data Transfer Process
        if self.session.pasv_mode and self.session.pasv_sock:
            conn, _ = self.session.pasv_sock.accept()  # Client initiates
            self.session.pasv_sock.close()
            self.session.pasv_sock = None
            self.session.pasv_mode = False
            return conn
        elif self.session.data_addr:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.session.data_addr)  # set during PORT
            return sock
        else:
            self.respond(425)
            return None

    def list_dir(self, path):
        # Handle extended listing display {i.e: ls -l}
        entries = []
        for name in os.listdir(path):
            full = os.path.join(path, name)
            s = os.stat(full)
            size = s.st_size
            mtime = time.strftime("%b %d %H:%M", time.localtime(s.st_mtime))
            kind = "d" if os.path.isdir(full) else "-"
            entries.append(f"{kind}rwxr-xr-x 1 ftp ftp {size:>8} {mtime} {name}")
        return entries

    def ftp_noop(self, args):
        # No Operation
        self.respond(200)

    def ftp_quit(self, args):
        # Terminate
        self.respond(221)

    def ftp_user(self, args):
        # Establish User Connection
        # TODO: Error Handling
        self.session.username = args
        self.respond(331)

    def ftp_pass(self, args):
        # Authenticate User
        # TODO: Authentication Methods
        self.session.authenticated = True
        self.session.state = "LOGGED_IN"
        self.respond(230)

    def ftp_pwd(self, args):
        # Print working directory
        self.respond(257, f'"{self.session.cwd}" is current directory')

    def ftp_cwd(self, args):
        self.session.cwd = args
        self.respond(250, f'directory changed to "{self.session.cwd}"')

    def ftp_port(self, args):
        # Handle IP / PORT setting
        parts = args.split(",")  # i.e: 192.168.0.1:50185 -> 192,168,0,1,196,9
        ip = ".".join(parts[:4])
        port = (int(parts[4]) * 256) + int(parts[5])
        self.session.data_addr = (ip, port)
        self.respond(200)

    def ftp_list(self, args):
        if not self.require_auth():
            return
        if not self.session.data_addr and not self.session.pasv_mode:
            self.respond(425)
            return

        # filepath resolution
        filepath = os.path.join(self.session.root, self.session.cwd.lstrip("/"), args)
        if not os.path.exists(filepath):
            self.respond(550)
            return

        self.respond(150)
        sock = self.open_data_connection()
        dtp = DataTransferProcess(sock)
        dtp.send_listing(self.list_dir(filepath))
        sock.close()
        self.respond(226)

    def ftp_stor(self, args):
        if not self.require_auth():
            return
        if not self.session.data_addr and not self.session.pasv_mode:
            self.respond(425)
            return

        # filepath resolution
        filepath = os.path.join(self.session.root, self.session.cwd.lstrip("/"), args)
        if not os.path.exists(os.path.dirname(filepath)):
            self.respond(550)
            return

        self.respond(125)
        sock = self.open_data_connection()
        dtp = DataTransferProcess(sock)
        dtp.recv_file(filepath)
        dtp.close()
        self.respond(226)

    def ftp_retr(self, args):
        if not self.require_auth():
            return
        if not self.session.data_addr and not self.session.pasv_mode:
            self.respond(425)
            return

        # filepath resolution
        filepath = os.path.join(self.session.root, self.session.cwd.lstrip("/"), args)
        if not os.path.exists(filepath):
            self.respond(550)
            return

        self.respond(150)
        sock = self.open_data_connection()
        dtp = DataTransferProcess(sock)
        dtp.send_file(filepath)
        dtp.close()
        self.respond(226)

    def ftp_type(self, args):
        # A=ASCII, I=Binary/Img
        if args in ("A", "I"):
            self.session.transfer_type = args
            self.respond(200, f"Type set to {args}")
        else:
            self.respond(504)

    def ftp_pasv(self, args):
        # handles passive port setting
        self.session.pasv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.session.pasv_sock.bind(("", 0))  # OS picks port
        self.session.pasv_sock.listen(1)

        _, port = self.session.pasv_sock.getsockname()
        p1, p2 = port // 256, port % 256

        # TODO: change sent command for actual production
        self.respond(227, f"Entering Passive Mode (127,0,0,1,{p1},{p2})")
        self.session.pasv_mode = True
