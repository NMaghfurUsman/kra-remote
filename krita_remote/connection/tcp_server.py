from abc import abstractmethod
from threading import Thread
from typing import Protocol, Optional
from random import randint
from socket import gethostbyname, gethostname
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtCore import pyqtProperty
from krita_remote.websockets.src.websockets.exceptions import ConnectionClosedError
from ..websockets.src.websockets.sync.server import serve, ServerConnection, WebSocketServer
from socketserver import TCPServer, BaseRequestHandler, ThreadingMixIn
from functools import partial

class ServerListener(Protocol):

    @abstractmethod
    @pyqtSlot()
    def onServerStopped(self) -> None:
        pass

    @abstractmethod
    @pyqtSlot(str)
    def onServerListening(self, address: str) -> None:
        pass

class ClientListener(Protocol):

    @abstractmethod
    @pyqtSlot()
    def onClientMessage(self) -> None:
        pass

    @abstractmethod
    @pyqtSlot()
    def onClientConnected(self) -> None:
        pass

    @abstractmethod
    @pyqtSlot()
    def onClientDisconnected(self) -> None:
        pass


class Handler(BaseRequestHandler):

    actual_server = None

    def __init__(self, actual_server, *args, **kwargs):
        self.actual_server = actual_server
        super().__init__(*args, **kwargs)

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.actual_server.clientMessageReceived.emit(self.data.decode('utf-8'))

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

class TCPSocketServer(QObject):

    port: Optional[int] = None
    server: Optional[TCPServer] = None
    server_thread: Optional[Thread] = None
    client: bool = False
    # connection: Optional[ServerConnection] = None

    serverListening = pyqtSignal(str)
    serverStopped = pyqtSignal()

    clientConnected = pyqtSignal()
    clientDisconnected = pyqtSignal()
    clientMessageReceived = pyqtSignal(str)

    action = pyqtSignal(str)
    press = pyqtSignal(str)
    release = pyqtSignal(str)
    tool = pyqtSignal(str)
    blend = pyqtSignal(str)
    script = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.clientMessageReceived.connect(self.onMessage)

    @pyqtSlot(str)
    def onMessage(self, msg: str):
        if (msg.startswith("action:tool:")):
            action_name = msg.split(":")[2]
            self.tool.emit(action_name)
        elif (msg.startswith("action:blend")):
            action_name = msg.split(":")[2]
            self.blend.emit(action_name)
        elif (msg.startswith("action:")):
            action_name = msg.split(":")[1]
            self.action.emit(action_name)
        elif (msg.startswith("press:")):
            press = msg.split(":")[1]
            self.press.emit(press)
        elif (msg.startswith("release:")):
            release = msg.split(":")[1]
            self.release.emit(release)
        elif (msg.startswith("script:")):
            script = msg.split(":")[1]
            self.script.emit(script)

    @pyqtSlot()
    def startListening(self):
        ip: QHostAddress = QHostAddress(gethostbyname(gethostname()))
        port = self.port or randint(9999,pow(2,16))
        self.port = port

        # https://stackoverflow.com/questions/21631799/how-can-i-pass-parameters-to-a-requesthandler
        handler = partial(Handler, self)

        self.server = ThreadedTCPServer(("0.0.0.0", self.port), handler)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        if (self.server_thread.is_alive()):
            self.serverListening.emit("tcp://{}:{}".format(ip.toString(),str(port)))
        else:
            self.serverStopped.emit()

    @pyqtSlot()
    def stopListening(self):
        if (self.server_thread and self.server_thread.is_alive()):
            assert self.server
            self.server.shutdown()
            self.serverStopped.emit()
            self.server = None

    @pyqtProperty(str)
    def address(self) -> str | None:
        if (self.server_thread and self.server_thread.is_alive()):
            return "tcp://{}:{}/".format(gethostbyname(gethostname()), self.port)
        else:
            return None

    def connectClientSignals(self, listener: ClientListener) -> None:
        self.clientMessageReceived.connect(listener.onClientMessage)
        # self.clientConnected.connect(listener.onClientConnected)
        # self.clientDisconnected.connect(listener.onClientDisconnected)

    def connectServerSignals(self, listener: ServerListener) -> None:
        self.serverListening.connect(listener.onServerListening)
        self.serverStopped.connect(listener.onServerStopped)
