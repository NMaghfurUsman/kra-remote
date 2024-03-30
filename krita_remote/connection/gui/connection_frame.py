from ..connection import Connection
from .client_log import ClientLog
from .server_line import ServerLine
from .client_line import ClientLine
from .server_button import ServerButton
from PyQt5.QtWidgets import QBoxLayout, QFrame
from PyQt5.QtCore import QObject

class ConnectionFrame(QFrame):
    
    def __init__(self, connection: Connection, parent: QObject):
        super().__init__(parent)
        
        # initialize GUI elements
        self._status_line = ClientLine(connection, parent)
        self._start_btn = ServerButton(connection, parent, True)
        self._stop_btn = ServerButton(connection, parent, False)
        self._connection_line = ServerLine(connection, parent)
        self._client_log = ClientLog(connection, parent)
        
        # initialize layouts
        main_layout: QBoxLayout = QBoxLayout(QBoxLayout.Direction.Down, self)
        btn_row: QBoxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        
        # place GUI elements
        main_layout.addWidget(self._status_line)
        main_layout.addWidget(self._connection_line)
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)
        main_layout.addLayout(btn_row)
        main_layout.addWidget(self._client_log)
        main_layout.addStretch()