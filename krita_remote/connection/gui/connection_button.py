from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QPushButton
from ..connection import Connection

LISTENING: str = "Stop Server"
STOPPED: str = "Start Server"

class ConnectionButton(QPushButton):
    
    start: bool
    
    def __init__(self, _c: Connection, parent=None, start: bool = True):
        self.start = start
        if start:
            super().__init__(STOPPED)
        else:
            super().__init__(LISTENING)
            self.setEnabled(False)
        
    @pyqtSlot(str)
    def onServerListening(self, str):
        self.setEnabled(not (False != self.start))
        
    @pyqtSlot()
    def onServerStopped(self):
        self.setEnabled(not (True != self.start))