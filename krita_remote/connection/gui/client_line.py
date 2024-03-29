from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLineEdit
from ..connection import Connection
from PyQt5.QtCore import pyqtProperty

class ClientLine(QLineEdit):
  
    _connected: bool = False
    
    def __init__(self, c: Connection, parent):
        super().__init__(parent)
        self.connected = c.connected
    
    @pyqtProperty(bool)
    def connected(self) -> bool:
        return self._connected
        
    @connected.setter
    def connected(self, connected: bool):
        if connected:
            self.setText("Connected")
        else:
            self.setText("Disconnected")
        self._connected = connected

    @pyqtSlot()
    def onClientConnected(self):
        self.connected = True
            
    @pyqtSlot()
    def onClientDisconnected(self):
        self.connected = False