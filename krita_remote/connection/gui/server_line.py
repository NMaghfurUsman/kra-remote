from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtProperty
from ..connection import Connection

class ServerLine(QLineEdit):
    
    _address: str = ""
    _listening: bool = False
    
    def __init__(self, c: Connection, parent = None):
        super().__init__(parent)
        self.listening = c.listening
    
    @pyqtProperty(bool)
    def listening(self) -> bool:
        return self._listening
        
    @listening.setter
    def listening(self, listening: bool):
        if listening:
            self.setText("Server listening on " + self._address)
        else:
            self.setText("Server stopped")
        self._connected = listening

    @pyqtSlot(str)
    def onServerListening(self, address: str):
        self._address = address
        self.listening = True
            
    @pyqtSlot()
    def onServerStopped(self):
        self._address = ""
        self.listening = False
