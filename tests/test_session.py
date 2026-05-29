import socket
import threading
import time
import os
import unittest
from azazel.server import FTPServer

"""
Testing for the FTPSession Class
"""

# Test Root
TEST_ROOT = os.path.join(os.path.dirname(__file__), "..", "placeholder")


# Testing FTP Server Functionality
class TestFTPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = FTPServer(port=2121, reuse_addr=True, root=TEST_ROOT)
        cls.thread = threading.Thread(target=cls.server.start)
        cls.thread.daemon = True  # dies when the test process dies
        cls.thread.start()
        time.sleep(0.1)  # give the server a moment to start

    def setUp(self):
        # fresh client per test
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 2121))
        self.client.recv(1024)  # consume banner

    def tearDown(self):
        self.client.close()

    def test_NOOP(self):
        # Testing NOOP
        self.client.send(b"NOOP\r\n")
        response = self.client.recv(1024)
        self.assertIn(b"200", response)

    def test_RETR_Active(self):
        # 1. log in
        self.login()

        # 2. Set up the data socket
        ds = self.open_data_channel()

        # 3. issue RETR
        self.client.send(b"RETR test.txt\r\n")
        self.client.recv(1024)  # 150 opening...

        # 4. accept server's incoming data stream
        data_conn, _ = ds.accept()
        received = b""
        while True:
            chunk = data_conn.recv(4096)
            if not chunk:
                break
            received += chunk
        data_conn.close()
        ds.close()

        self.client.recv(1024)  # 226 transfer complete
        self.assertGreater(len(received), 0)

    def test_RETR_PASV(self):
        # 1. log in
        self.login()

        # 2. Set up the data socket
        ds = self.open_pasv_channel()

        # 3. issue RETR
        self.client.send(b"RETR test.txt\r\n")
        self.client.recv(1024)  # 150 opening...

        # 4. accept server's incoming data stream
        received = b""
        while True:
            chunk = ds.recv(4096)
            if not chunk:
                break
            received += chunk
        ds.close()

        self.client.recv(1024)  # 226 transfer complete
        self.assertGreater(len(received), 0)

    def test_STOR_PASV(self):
        # 1. log in
        self.login()

        # 2. Set up the data socket
        ds = self.open_pasv_channel()

        # 3. issue RETR
        self.client.send(b"STOR uploaded.txt\r\n")
        self.client.recv(1024)  # 125

        # 4. send the file contents
        ds.sendall(b"hello from test\n")
        ds.close()

        self.client.recv(1024)  # 226 transfer complete

        # 5. verify it landed
        uploaded = os.path.join(TEST_ROOT, "uploaded.txt")
        self.assertTrue(os.path.exists(uploaded))
        with open(uploaded, "rb") as f:
            self.assertEqual(f.read(), b"hello from test\n")

    def login(self):
        # Login Helper
        self.client.send(b"USER alice\r\n")
        self.client.recv(1024)
        self.client.send(b"PASS testpw\r\n")
        self.client.recv(1024)

    def open_data_channel(self):
        # Active Data Socket Helper, returns (data_server_socket, port)
        ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ds.bind(("127.0.0.1", 0))
        ds.listen(1)
        _, port = ds.getsockname()
        p1, p2 = port // 256, port % 256
        self.client.send(f"PORT 127,0,0,1,{p1},{p2}\r\n".encode())
        self.client.recv(1024)  # 200 PORT ok
        return ds

    def open_pasv_channel(self):
        # Passive Data Socket Helper
        self.client.send(b"PASV\r\n")
        response = self.client.recv(1024).decode()  # parse ip & port
        # expecting (127,0,0,1,p1,p2)
        start = response.index("(") + 1
        end = response.index(")")
        parts = response[start:end].split(",")
        port = int(parts[4]) * 256 + int(parts[5])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        return sock

    def test_Directory(self):
        # Testing Directory Methods
        self.sample_CWD()
        self.sample_PWD()

    def sample_CWD(self):
        # Testing CWD
        self.client.send(b"CWD /placeholder\r\n")
        response = self.client.recv(1024)
        self.assertIn(b'250 directory changed to "/placeholder"\r\n', response)

    def sample_PWD(self):
        # Testing PWD
        self.client.send(b"PWD\r\n")
        response = self.client.recv(1024)
        self.assertIn(b'257 "/placeholder" is current directory\r\n', response)

    def test_QUIT(self):
        # Testing QUIT
        self.client.send(b"QUIT\r\n")
        response = self.client.recv(1024)
        self.assertIn(b"221", response)


if __name__ == "__main__":
    unittest.main()
