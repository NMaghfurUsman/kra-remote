from abc import abstractmethod
from typing import Protocol
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWebSockets import QWebSocketServer, QWebSocket
from PyQt5.QtNetwork import QHostAddress
from socket import gethostbyname, gethostname
from random import randint
from PyQt5.QtCore import pyqtProperty

class ServerListener(Protocol):
    
    @abstractmethod
    def onServerStopped(self) -> None:
        pass

    @abstractmethod
    def onServerListening(self, address: str) -> None:
        pass
    
class ClientListener(Protocol):
    
    @abstractmethod
    def onClientConnected(self) -> None:
        pass

    @abstractmethod
    def onClientDisconnected(self) -> None:
        pass

class Socket(QObject):
    
    messageReceived = pyqtSignal(str)
    disconnected = pyqtSignal()
    connected = pyqtSignal()
    ws: QWebSocket

    def sendMessage(self, msg: str) -> None:
        self.ws.sendTextMessage(msg)
        pass

    @pyqtSlot(str)
    def onMessage(self, msg: str):
        self.messageReceived.emit(msg)
        
    @pyqtSlot()
    def onDisconnect(self):
        pass
    
    def __init__(self, ws: QWebSocket):
        super().__init__()
        ws.textMessageReceived.connect(self.onMessage)
        ws.connected.connect(self.connected.emit)
        ws.disconnected.connect(self.disconnected.emit)
        self.ws: QWebSocket = ws
        
    def disconnectClient(self):
        self.ws.close()
        
class SocketServer(QWebSocketServer):
    def __init__(self):
        super().__init__("krita_remote", QWebSocketServer.SslMode.NonSecureMode)

# Wrangles the websocket server and websocket connection
class Connection(QObject):
    
    server: SocketServer
    client: Socket = None
    
    serverListening = pyqtSignal(str)
    serverStopped = pyqtSignal()
    
    clientConnected = pyqtSignal()
    clientDisconnected = pyqtSignal()
    clientRejected = pyqtSignal()
    
    action = pyqtSignal(str)
    press = pyqtSignal(str)
    release = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.server = SocketServer()
        self.server.newConnection.connect(self.onNewConnection)
        self.server.closed.connect(self.serverStopped.emit)
        
        self.clientDisconnected.connect(self.onClientDisconnected)
        self.clientConnected.connect(self.onClientConnected)
        self.clientRejected.connect(self.onClientRejected)
        
        self.onMessage

    @pyqtSlot(bool)
    def onServerChange(self, listening: bool):
        print("Listening: {}".format(listening))

    @pyqtSlot()
    def onNewConnection(self):
        socket = Socket(self.server.nextPendingConnection())
        if (self.client != None): # reject new connections if we already have a client
            socket.disconnectClient()
            self.clientRejected.emit()
        else:
            self.client = socket
            self.clientConnected.emit()
            self.client.disconnected.connect(self.clientDisconnected)
            self.client.messageReceived.connect(self.onMessage)
            
    @pyqtSlot(str)
    def onMessage(self, msg: str):
        if (msg.startswith("action:")):
            action_name = msg.split(":")[1]
            self.action.emit(action_name)
        if (msg.startswith("press:")):
            press = msg.split(":")[1]
            self.press.emit(press)
        if (msg.startswith("release:")):
            release = msg.split(":")[1]
            self.release.emit(release)

    @pyqtSlot()
    def onClientDisconnected(self):
        print("Client disconnected")
        self.client = None
              
    @pyqtSlot()  
    def onClientConnected(self):
        print("Client connected")

    @pyqtSlot()  
    def onClientRejected(self):
        print("Client rejected")

    @pyqtSlot()
    def startServer(self):
        if (self.server): 
            if (self.server.isListening()): return
        if (not self.server): self.server = SocketServer()

        # initialize server
        # host IP on local network, qt5 doesn't have a way to retrieve this?
        ip: QHostAddress = QHostAddress(gethostbyname(gethostname()))
        # random port, later check for availability first
        port: int = randint(9999,pow(2,16))

        if (self.server.listen(ip, port)):
            self.serverListening.emit(ip.toString()+":"+str(port))
        else:
            self.serverStopped.emit()

        print("WebSockets server at ws://{}:{}".format(ip.toString(),port))

    @pyqtSlot()
    def stopServer(self):
        if (self.server.isListening()):
            self.server.close()
        if (self.client != None):
            self.client.disconnectClient()
            self.client = None
            
    @pyqtProperty(bool)
    def connected(self) -> bool:
        return self.client != None
    
    @pyqtProperty(bool)
    def listening(self) -> bool:
        return self.server.isListening()
    
    def connectClientSignals(self, cls: ClientListener) -> None:
        self.clientConnected.connect(cls.onClientConnected)
        self.clientDisconnected.connect(cls.onClientDisconnected)
        
    def connectServerSignals(self, cls: ServerListener) -> None:
        self.serverListening.connect(cls.onServerListening)
        self.serverStopped.connect(cls.onServerStopped)
        
    @pyqtSlot(str)
    def send(self, msg: str) -> bool:
        if self.client:
            self.client.sendMessage(msg)
            return True
        else:
            return False
        