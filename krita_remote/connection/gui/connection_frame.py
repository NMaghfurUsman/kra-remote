from ..connection import Connection
from .server_line import ServerLine
from .client_line import ClientLine
from .server_button import ServerButton
from PyQt5.QtWidgets import QBoxLayout, QFrame
from PyQt5.QtCore import QObject

class ConnectionFrame(QFrame):
    
    def __init__(self, connection: Connection, parent: QObject):
        super().__init__(parent)
        
        # initialize GUI
        self._status_line = ClientLine(connection, parent)
        self._start_btn = ServerButton(connection, parent, True)
        self._stop_btn = ServerButton(connection, parent, False)
        self._connection_line = ServerLine(connection, parent)
        


        # Connect signals
        self._start_btn.clicked.connect(connection.startServer)
        self._stop_btn.clicked.connect(connection.stopServer)
        
        connection.connectServerSignals(self._start_btn)
        connection.connectServerSignals(self._stop_btn)
        connection.connectServerSignals(self._connection_line)
        connection.connectClientSignals(self._status_line)
        
        main_layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.Down, self)
        btn_row: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        
        main_layout.addWidget(self._status_line)
        main_layout.addWidget(self._connection_line)
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)
        main_layout.addLayout(btn_row)
        main_layout.addStretch()