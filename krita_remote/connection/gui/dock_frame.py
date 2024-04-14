from ..ws_connection import WSConnection
from .event_log import EventLog
from PyQt5.QtWidgets import QBoxLayout, QFrame, QPushButton
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from krita_remote.connection.gui.qr_window import QRDialog

class DockFrame(QFrame):
    
    def __init__(self, connection: WSConnection, parent: QObject):
        super().__init__(parent)
        
        # initialize GUI elements
        self._client_log = EventLog(connection, parent)
        self._connect_button = ConnectButton(connection, self)
        self._disconnect_button = DisconnectButton(connection, self)

        # initialize layouts
        main_layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.Down, self)
        btn_row: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        
        # place GUI elements

        btn_row.addWidget(self._connect_button)
        btn_row.addWidget(self._disconnect_button)
        main_layout.addLayout(btn_row)
        main_layout.addWidget(self._client_log)
        
        connection.connectClientSignals(self)
        
    @pyqtSlot()
    def showQRDialog(self):
        self._qr_dialog = QRDialog(self.parentWidget()._extension.server.address, self.parentWidget()._extension.connection.address)
        self._qr_dialog.show()
        
    def onClientConnected(self):
        if (self._qr_dialog.isVisible()):
            self._qr_dialog.close()
            
    def onClientDisconnected(self):
        pass

    def onClientMessage(self):
        pass
    
class ConnectButton(QPushButton):
        
    def __init__(self, c: WSConnection, parent: DockFrame):
        super().__init__(parent)
        self.setText("Connect")
        if (c.address):
            self.setEnabled(False)
        else:
            self.setEnabled(True)
        c.connectClientSignals(self)
        self.clicked.connect(c.startServer)
        self.clicked.connect(parent.showQRDialog)
        
    def onClientConnected(self):
        self.setEnabled(False)
            
    def onClientDisconnected(self):
        self.setEnabled(True)

    def onClientMessage(self):
        pass
        
class DisconnectButton(QPushButton):
    def __init__(self, c: WSConnection, parent: DockFrame):
        super().__init__(parent)
        self.setText("Disconnect")
        if (c.address):
            self.setEnabled(True)
        else:
            self.setEnabled(False)
        c.connectClientSignals(self)
        self.clicked.connect(c.stopServer)
        
    def onClientConnected(self):
        self.setEnabled(True)
            
    def onClientDisconnected(self):
        self.setEnabled(False)

    def onClientMessage(self):
        pass
