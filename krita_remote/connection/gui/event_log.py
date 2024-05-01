from PyQt5.QtWidgets import QTextEdit, QWidget
from ..socket_server import SocketServer
from ..web_server import WebServer

class EventLog(QTextEdit):

    def __init__(self, c: SocketServer, h: WebServer, parent: QWidget):
        super().__init__(parent)
        self.setReadOnly(True)
        c.connectClientSignals(self)
        c.connectServerSignals(self)
        h.serverStarted.connect(self.onServerStarted)

    def onClientMessage(self, msg: str):
        self.append(msg)

    def onClientConnected(self):
        self.append("Client connected")

    def onClientDisconnected(self):
        self.append("Client disconnected")

    def onClientRejected(self):
        self.append("Client rejected")

    def onServerListening(self, address: str):
        self.append("Socket server: {}".format(address))

    def onServerStarted(self, address: str):
        self.append("Web server: {}".format(address))

    def onServerStopped(self):
        self.append("Server stopped")