from typing import Any
from krita import DockWidget
from .connection.gui.connection_frame import ConnectionFrame
from .krita_remote_extension import KritaRemoteExtension
from .api_krita import Krita
from PyQt5.QtWidgets import QWidget

DOCKER_TITLE: str = "Krita Remote"

class KritaRemoteDockWidget(DockWidget):
    
    _extension: KritaRemoteExtension
    _connection_frame: ConnectionFrame

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        
        self._extension: KritaRemoteExtension = [e for e in Krita.instance.extensions() if e.__class__.__name__=="KritaRemoteExtension"][0]
        self._connection_frame = ConnectionFrame(self._extension.connection, self)
        
        self.setWidget(self._connection_frame)

    def canvasChanged(self, canvas: Any):
        if canvas:
            if (canvas.view() and canvas.view().document()):
                print("Canvas changed. visible?: {}".format((canvas.view().visible)))
                self._extension.connection.send("canvas changed to {}".format(canvas.view().document().name()))
