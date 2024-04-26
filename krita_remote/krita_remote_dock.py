from typing import Any
from krita import DockWidget # type: ignore
from .connection.gui.dock_frame import DockFrame
from .krita_remote_extension import KritaRemoteExtension
from .api_krita import Krita

DOCKER_TITLE: str = "Krita Remote"

class KritaRemoteDockWidget(DockWidget):
    
    _extension: KritaRemoteExtension
    _dock_frame: DockFrame

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        
        self._extension: KritaRemoteExtension = [e for e in Krita.instance.extensions() if e.__class__.__name__=="KritaRemoteExtension"][0]
        self._dock_frame = DockFrame(self._extension.connection, self) # type: ignore
        self.setWidget(self._dock_frame)

    def canvasChanged(self, canvas: Any):
        if canvas:
            if (canvas.view() and canvas.view().document()):
