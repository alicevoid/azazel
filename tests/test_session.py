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
TEST_ROOT = os.path.join(os.path.dirname(__file__), '..', 'placeholder')

# Testing FTP Server Functionality
class TestFTPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = FTPServer(port=2121, reuse_addr=True, root=TEST_ROOT)
        cls.thread = threading.Thread(target=cls.server.start)
        cls.thread.daemon = True  # dies when the test process dies
        cls.thread.start()
        time.sleep(0.1) # give the server a moment to start

    def setUp(self):
        # fresh client per test 
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', 2121))
        self.client.recv(1024) # consume banner

    def tearDown(self):
        self.client.close()

    def test_NOOP(self):
        # Testing NOOP
        self.client.send(b'NOOP\r\n')
        response = self.client.recv(1024)
        self.assertIn(b'200', response)

    def test_RETR(self):
        # 1. log in
        self.login()

        # 2. Set up the data socket
        ds = self.open_data_channel()

        # 3. issue RETR
        self.client.send(b'RETR test.txt\r\n')
        self.client.recv(1024) # 150 opening...

        # 4. accept server's incoming data stream
        data_conn, _ = ds.accept()
        received = b''
        while True:
            chunk = data_conn.recv(4096)
            if not chunk:
                break
            received += chunk
        data_conn.close()
        ds.close()

        self.client.recv(1024) # 226 transfer complete
        self.assertGreater(len(received), 0) 

    def login(self):
        # Login Helper
        self.client.send(b'USER alice\r\n')
        self.client.recv(1024)
        self.client.send(b'PASS testpw\r\n')
        self.client.recv(1024)

    def open_data_channel(self):
        # Data Socket Helper, returns (data_server_socket, port)
        ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ds.bind(('127.0.0.1', 0))
        ds.listen(1)
        _, port = ds.getsockname()
        p1, p2 = port // 256, port % 256
        self.client.send(f'PORT 127,0,0,1,{p1},{p2}\r\n'.encode())
        self.client.recv(1024)  # 200 PORT ok
        return ds

    def test_Directory(self):
        # Testing Directory Methods
        self.sample_CWD()
        self.sample_PWD()

    def sample_CWD(self):
        # Testing CWD
        self.client.send(b'CWD /placeholder\r\n')
        response = self.client.recv(1024)
        self.assertIn(b'250 directory changed to "/placeholder"\r\n', response)

    def sample_PWD(self):
        # Testing PWD 
        self.client.send(b'PWD\r\n')
        response = self.client.recv(1024)
        self.assertIn(b'250 current directory is "/placeholder"\r\n', response)

    def test_QUIT(self):
        # Testing QUIT
        self.client.send(b'QUIT\r\n')
        response = self.client.recv(1024)
        self.assertIn(b'221', response)

if __name__ == '__main__':
    unittest.main()

