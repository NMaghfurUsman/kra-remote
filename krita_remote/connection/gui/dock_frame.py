from ..socket_server import SocketServer
from ..web_server import WebServer
from .event_log import EventLog
from .qr_window import QRDialog
from PyQt5.QtWidgets import QBoxLayout, QFrame, QPushButton
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot

class DockFrame(QFrame):
    
    def __init__(self, socket: SocketServer, server: WebServer, parent: QObject):
        super().__init__(parent)
        
        # initialize GUI elements
        self._client_log = EventLog(socket, server, parent)
        self._connect_button = ConnectButton(socket, server, self)
        self._disconnect_button = DisconnectButton(socket, server, self)

        # initialize layouts
        main_layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.Down, self)
        btn_row: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        
        # place GUI elements

        btn_row.addWidget(self._connect_button)
        btn_row.addWidget(self._disconnect_button)
        main_layout.addLayout(btn_row)
        main_layout.addWidget(self._client_log)
        
        socket.connectClientSignals(self)
        
        self._clear_button = ClearButton(self, target=self._client_log)
        main_layout.addWidget(self._clear_button)

    @pyqtSlot()
    def showQRDialog(self):
        self._qr_dialog = QRDialog(self.parentWidget()._extension.server.address, self.parentWidget()._extension.socket.address)
        self._qr_dialog.show()
        
    def onClientConnected(self):
        if (self._qr_dialog.isVisible()):
            self._qr_dialog.close()
            
    def onClientDisconnected(self):
        pass

    def onClientMessage(self):
        pass
    
class ConnectButton(QPushButton):
        
    def __init__(self, s: SocketServer, w: WebServer, parent: DockFrame):
        super().__init__(parent)
        self.setText("Connect")
        if (s.address):
            self.setEnabled(False)
        else:
            self.setEnabled(True)
        s.connectClientSignals(self)
        self.clicked.connect(s.startListening)
        self.clicked.connect(w.startServer)
        self.clicked.connect(parent.showQRDialog)
        
    def onClientConnected(self):
        self.setEnabled(False)
            
    def onClientDisconnected(self):
        self.setEnabled(True)

    def onClientMessage(self):
        pass
        
class DisconnectButton(QPushButton):
    def __init__(self, s: SocketServer, w: WebServer, parent: DockFrame):
        super().__init__(parent)
        self.setText("Disconnect")
        if (s.address):
            self.setEnabled(True)
        else:
            self.setEnabled(False)
        s.connectClientSignals(self)
        self.clicked.connect(s.stopListening)
        self.clicked.connect(w.stopServer)
        
    def onClientConnected(self):
        self.setEnabled(True)
            
    def onClientDisconnected(self):
        self.setEnabled(False)

    def onClientMessage(self):
        pass

class ClearButton(QPushButton):
    def __init__(self, parent, target):
        super().__init__(parent)
        self.setText("Clear")
        self.clicked.connect(target.clear)