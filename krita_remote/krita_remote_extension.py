from random import randint
from typing import Any
from krita import Extension # type: ignore
from .connection import WSConnection
from .api_krita import Krita
from .api_krita.enums import Tool
from PyQt5.QtCore import pyqtProperty, pyqtSlot, QEvent, Qt, QObject
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QCursor,QKeyEvent
from .connection.http_server import HTTPServer
from threading import Thread
from .connection.gui.qr_window import QRDialog

class KritaRemoteExtension(Extension):

    _connection: WSConnection
    _server_thread: Thread
    _server: HTTPServer
    _canvas: Any

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        self._connection = WSConnection()
        self._connection.action.connect(self.action)
        self._connection.press.connect(self.press)
        self._connection.release.connect(self.release)
        self._connection.tool.connect(self.tool)

        self._server = HTTPServer()
        self._server_thread = Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()

    def createActions(self, window):
        pass

    @pyqtProperty(WSConnection)
    def connection(self) -> WSConnection:
        return self._connection

    @pyqtProperty(HTTPServer)
    def server(self) -> HTTPServer:
        return self._server

    @pyqtSlot(str)
    def press(self, key: str):
        if self._canvas:
            press = QKeyEvent(QEvent.KeyPress, getattr(Qt, key), Qt.NoModifier)
            if not self._canvas.isActiveWindow():
                self._canvas.activateWindow()
            QApplication.sendEvent(self._canvas, press)

    @pyqtSlot(str)
    def release(self, key: str):
        if self._canvas:
            release = QKeyEvent(QEvent.KeyRelease, getattr(Qt, key), Qt.NoModifier)
            if not self._canvas.isActiveWindow():
                self._canvas.activateWindow()
            QApplication.sendEvent(self._canvas, release)

    @pyqtSlot(str)
    def action(self, action_name: str):
        Krita.trigger_action(action_name)

    @pyqtSlot(str)
    def tool(self, tool_name: str):
        Krita.active_tool = Tool(tool_name)
