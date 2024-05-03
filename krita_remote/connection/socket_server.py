from abc import abstractmethod
from threading import Thread
from typing import Protocol, Optional
from random import randint
from socket import gethostbyname, gethostname
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtCore import pyqtProperty
from ..websockets.src.websockets.sync.server import serve, ServerConnection, WebSocketServer

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

class SocketServer(QObject):
    
    port: Optional[int] = None
    server: Optional[WebSocketServer] = None
    server_thread: Optional[Thread] = None
    client: bool = False
    connection: Optional[ServerConnection] = None
    
    serverListening = pyqtSignal(str)
    serverStopped = pyqtSignal()
    
    clientConnected = pyqtSignal()
    clientDisconnected = pyqtSignal()
    clientMessageReceived = pyqtSignal(str)

    action = pyqtSignal(str)
    press = pyqtSignal(str)
    release = pyqtSignal(str)
    tool = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.clientMessageReceived.connect(self.onMessage)

    @pyqtSlot(str)
    def onMessage(self, msg: str):
        if (msg.startswith("action:tool:")):
            action_name = msg.split(":")[2]
            self.tool.emit(action_name)
        elif (msg.startswith("action:")):
            action_name = msg.split(":")[1]
            self.action.emit(action_name)
        elif (msg.startswith("press:")):
            press = msg.split(":")[1]
            self.press.emit(press)
        elif (msg.startswith("release:")):
            release = msg.split(":")[1]
            self.release.emit(release)

    @pyqtSlot()
    def startListening(self):
        ip: QHostAddress = QHostAddress(gethostbyname(gethostname()))
        port = self.port or randint(9999,pow(2,16))
        self.port = port

        def handler(ws: ServerConnection) -> None:
            self.client = True
            self.connection = ws
            self.clientConnected.emit()
            for msg in ws:
                self.clientMessageReceived.emit(msg)
            self.client = False

        self.server = serve(handler, ip.toString(), self.port)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()

        if (self.server_thread.is_alive()):
            self.serverListening.emit(ip.toString()+":"+str(port))
        else:
            self.serverStopped.emit()

    @pyqtSlot()
    def stopListening(self):
        if (self.server_thread and self.server_thread.is_alive()):
            assert self.server
            assert self.client
            assert self.connection
            self.server.shutdown()
            self.connection.close()
            self.serverStopped.emit()
            self.server = None

    @pyqtProperty(str)
    def address(self) -> str | None:
        if (self.server_thread and self.server_thread.is_alive()):
            return "ws://{}:{}/".format(gethostbyname(gethostname()), self.port)
        else:
            return None

    def connectClientSignals(self, listener: ClientListener) -> None:
        self.clientMessageReceived.connect(listener.onClientMessage)
        self.clientConnected.connect(listener.onClientConnected)
        self.clientDisconnected.connect(listener.onClientDisconnected)
        
    def connectServerSignals(self, listener: ServerListener) -> None:
        self.serverListening.connect(listener.onServerListening)
        self.serverStopped.connect(listener.onServerStopped)
        