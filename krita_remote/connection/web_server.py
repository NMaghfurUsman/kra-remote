from random import randint
from threading import Thread
from typing import Optional
from socket import gethostname, gethostbyname
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from ..api_krita import Krita
from PyQt5.QtCore import pyqtSignal, pyqtProperty, pyqtSlot, QObject


INDEX_DIR = Krita.instance.getAppDataLocation() + "/pykrita/krita_remote/client"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=INDEX_DIR, **kwargs)

class HTTPServer(ThreadingHTTPServer):
    address: str
    port: Optional[int] = None
    def __init__(self, port = None):
        ip = gethostbyname(gethostname().split(".")[-1])
        port = port or randint(9999,pow(2,16))
        self.port = port
        super().__init__((ip, port), Handler)
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
            self.serverStarted.emit("{}:{}".format(self._server.address,self._server.port))

    @pyqtSlot()
    def stopServer(self):
        pass

    @pyqtProperty(str)
    def address(self) -> str | None:
        if (self._thread and self._thread.is_alive()):
            return self._server.address
        else:
            return None