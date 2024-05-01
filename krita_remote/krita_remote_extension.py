from typing import Any
from krita import Extension # type: ignore
from PyQt5.QtCore import pyqtProperty, pyqtSlot, QEvent, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QKeyEvent
from .connection import SocketServer
from .api_krita import Krita
from .api_krita.enums import Tool
from .connection.web_server import WebServer

class KritaRemoteExtension(Extension):

    _socket: SocketServer
    _server: WebServer
    _canvas: Any

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        self._socket = SocketServer()
        self._socket.action.connect(self.action)
        self._socket.press.connect(self.press)
        self._socket.release.connect(self.release)
        self._socket.tool.connect(self.tool)

        self._server = WebServer()

    def createActions(self, window):
        pass

    @pyqtProperty(SocketServer)
    def socket(self) -> SocketServer:
        return self._socket

    @pyqtProperty(WebServer)
    def server(self) -> WebServer:
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
