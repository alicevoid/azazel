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

    # TODO: add testing for login verification methods

    def test_Login(self):
        # tests the ability for the user to Log-In
        self.sample_USER()
        self.sample_PASS()

    def sample_USER(self):
        # Testing USER
        self.client.send(b'USER alice\r\n')
        response = self.client.recv(1024)
        self.assertIn(b'331 User name okay, need password\r\n', response)

    def sample_PASS(self):
        # Testing PASS
        self.client.send(b'PASS testpw\r\n')
        response = self.client.recv(1024)
        self.assertIn(b'230 User logged in\r\n', response)

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

