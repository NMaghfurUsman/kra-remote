from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QPushButton
from ..connection import Connection

LISTENING: str = "Stop Server"
STOPPED: str = "Start Server"

class ServerButton(QPushButton):

    start: bool

    def __init__(self, c: Connection, parent=None, start: bool = True):
        self.start = start
        if start:
            super().__init__(STOPPED)
            self.clicked.connect(c.startServer)
        else:
            super().__init__(LISTENING)
            self.setEnabled(False)
            self.clicked.connect(c.stopServer)
        c.connectServerSignals(self)

    def onServerListening(self, str):
        self.setEnabled(not (False != self.start))

    def onServerStopped(self):
        self.setEnabled(not (True != self.start))