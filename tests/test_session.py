import socket
import threading
import time
import unittest
from azazel.server import FTPServer 

# Testing FTP Server Functionality
class TestFTPServer(unittest.TestCase):
    def setUp(self):
        self.server = FTPServer(port=2121)
        self.thread = threading.Thread(target=self.server.start)
        self.thread.daemon = True  # dies when the test process dies
        self.thread.start()

    def test_banner(self):
        # give the server a moment to start
        time.sleep(0.1)
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 2121))
        response = client.recv(1024)
        client.close()
        
        self.assertIn(b'220', response)


if __name__ == '__main__':
    unittest.main()
