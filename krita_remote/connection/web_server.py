from random import randint
from threading import Thread
from typing import Optional
from socket import gethostname, gethostbyname
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from ..api_krita import Krita
from PyQt5.QtCore import pyqtSignal, pyqtProperty, pyqtSlot, QObject
import os

import socket
from contextlib import closing

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False

INDEX_DIR = os.path.join(Krita.instance.getAppDataLocation(), "pykrita", "krita_remote", "client")

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=INDEX_DIR, **kwargs)

    def log_message(self, format, *args, **kwargs):
        pass

class HTTPServer(ThreadingHTTPServer):
    address: str
    port: Optional[int] = None
    def __init__(self, port = None):
        ip = gethostbyname(gethostname().split(".")[-1])

        # other ports will give ERR_EMPTY_RESPONSE on a fresh Windows 10 VM
        port = 4001

        while check_socket(ip, port):
            port += 1
            if port == 4011:
                break
        assert check_socket(ip, port) == False
        self.port = port
        super().__init__(("0.0.0.0", port), Handler)
        self.address = "http://{}:{}".format(ip, port)

class WebServer(QObject):

    _server: HTTPServer
    _thread: Thread

    serverStarted = pyqtSignal(str)
    serverStopped = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._server = HTTPServer()
        self._thread = Thread(target=self._server.serve_forever)
        self._thread.daemon = True

    @pyqtSlot()
    def startServer(self):
        if not self._thread.is_alive():
            self._thread.start()
            self.serverStarted.emit(self._server.address)
        assert self._thread.is_alive() == True

    @pyqtSlot()
    def stopServer(self):
        pass

    @pyqtProperty(str)
    def address(self) -> str | None:
        if (self._thread and self._thread.is_alive()):
            return self._server.address
        else:
            return None