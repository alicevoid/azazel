import socket
import threading
import time
import unittest
from azazel.server import FTPServer 

# Testing FTP Server Functionality
class TestFTPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = FTPServer(port=2121, reuse_addr=True)
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

    def test_USER(self):
        pass

    def test_QUIT(self):
        # Testing QUIT
        self.client.send(b'QUIT\r\n')
        response = self.client.recv(1024)
        self.assertIn(b'221', response)

if __name__ == '__main__':
    unittest.main()

