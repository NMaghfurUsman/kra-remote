from typing import Any
from krita import Extension
from .connection import Connection
from .api_krita import Krita
from .api_krita.enums import Tool
from PyQt5.QtCore import pyqtProperty, pyqtSlot, QEvent, Qt
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QCursor,QKeyEvent

def find_current_canvas():
    app = Krita.instance
    q_window = app.activeWindow().qwindow()
    q_stacked_widget = q_window.centralWidget()
    q_mdi_area = q_stacked_widget.currentWidget()
    q_mdi_sub_window = q_mdi_area.currentSubWindow()
    view = q_mdi_sub_window.widget()
    for c in view.children():
        if c.metaObject().className() == 'KisCanvasController':
            # first QWidget child of viewport should be canvas...
            viewport = c.viewport()
            canvas = viewport.findChild(QWidget)
            return canvas

class KritaRemoteExtension(Extension):
    
    _connection: Connection

    def __init__(self, parent):
        super().__init__(parent)
        
        self._connection = Connection()
        self._connection.action.connect(self.action)
        self._connection.press.connect(self.press)
        self._connection.release.connect(self.release)
        self._connection.tool.connect(self.tool)

    def setup(self):
        pass

    def createActions(self, window):
        pass
            
    @pyqtProperty(Connection)
    def connection(self) -> Connection:
        return self._connection
    
    @pyqtSlot(str)
    def press(self, key: str):
        print("press: {}".format(key))
        canvas: Any = find_current_canvas()
        press = QKeyEvent(QEvent.KeyPress, getattr(Qt, key), Qt.NoModifier)
        if not canvas.isActiveWindow():
            canvas.activateWindow()
        QApplication.sendEvent(canvas, press)
        
    @pyqtSlot(str)
    def release(self, key: str):
        print("release: {}".format(key))
        canvas: Any = find_current_canvas()
        release = QKeyEvent(QEvent.KeyRelease, getattr(Qt, key), Qt.NoModifier)
        if not canvas.isActiveWindow():
            canvas.activateWindow()
        QApplication.sendEvent(canvas, release)
        
    @pyqtSlot(str)
    def action(self, action_name: str):
        print("action: {}".format(action_name))
        Krita.trigger_action(action_name)

    @pyqtSlot(str)
    def tool(self, tool_name: str):
        print("tool: {}".format(tool_name))
        Krita.active_tool = Tool(tool_name)