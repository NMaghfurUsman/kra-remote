from typing import overload, Any
from PyQt5.QtWidgets import QTextEdit, QWidget
from ..ws_connection import ClientListener, WSConnection

class EventLog(QTextEdit):

    _connection : WSConnection

    def __init__(self, c: WSConnection, parent: QWidget):
        super().__init__(parent)
        self.setReadOnly(True)
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
        self.append("Server listening on {}".format(self._connection.address))

    def onServerStopped(self):
        self.append("Server stopped")
