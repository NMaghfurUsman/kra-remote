from typing import overload, Any
from PyQt5.QtWidgets import QTextEdit, QWidget
from ..connection import ClientListener, Connection

class ClientLog(QTextEdit):

    _connection : Connection

    def __init__(self, c: Connection, parent: QWidget):
        super().__init__(parent)
        c.connectClientSignals(self)
        c.connectServerSignals(self)
        self._connection = c

    def onClientMessage(self, msg: str):
        self.append(msg)

    def onClientConnected(self):
        self.append("Client connected")

    def onClientDisconnected(self):
        self.append("Client disconnected")

    def onClientRejected(self):
        self.append("Client rejected")

    def onServerListening(self, address: str):
        self.append(self._connection.remoteLink(address))

    def onServerStopped(self):
        self.append("Server stopped")
