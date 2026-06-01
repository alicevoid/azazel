"""
Client Design

    pla-cehol-dert-ext
"""

import socket


class FTPClient:
    def __init__(self, host, port=2121):
        self.host = host
        self.port = port
        self.sock = None
        self.data_addr = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        return self.sock.recv(1024).decode()

    def send(self, command):
        self.sock.send(f"{command}\r\n".encode())
        return self.sock.recv(1024).decode()

    def login(self, user, password):
        self.send(f"USER {user}")
        return self.send(f"PASS {password}")

    def quit(self):
        self.send("QUIT")
        self.sock.close()
