from typing import overload, Any
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLineEdit, QTextBrowser
from ..connection import ClientListener, Connection
from PyQt5.QtCore import pyqtProperty

class ClientLog(QTextBrowser):
    def __init__(self, c: Connection, parent: Any):
        super().__init__(parent)
        c.connectClientSignals(self)
        c.connectServerSignals(self)

    def onClientMessage(self, msg: str):
        self.append(msg)

    def onClientConnected(self):
        self.append("Client connected")

    def onClientDisconnected(self):
        self.append("Client disconnected")

    def onClientRejected(self):
        self.append("Client rejected")

    def onServerListening(self, address: str):
        self.append("Server listening on:")
        self.append(address)

    def onServerStopped(self):
        self.append("Server stopped")
