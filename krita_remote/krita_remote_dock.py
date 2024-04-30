from typing import Any
from krita import DockWidget # type: ignore
from .connection.gui.dock_frame import DockFrame
from .krita_remote_extension import KritaRemoteExtension
from .api_krita import Krita
from PyQt5.QtWidgets import QWidget

DOCKER_TITLE: str = "Krita Remote"

class KritaRemoteDockWidget(DockWidget):
    
    _extension: KritaRemoteExtension
    _dock_frame: DockFrame

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        
        self._extension: KritaRemoteExtension = [e for e in Krita.instance.extensions() if e.__class__.__name__=="KritaRemoteExtension"][0]
        self._dock_frame = DockFrame(self._extension.socket, self._extension.server, self)
        self.setWidget(self._dock_frame)

    def canvasChanged(self, canvas: Any):
        if canvas:
            if canvas.view() and canvas.view().document():
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
                        self._extension._canvas = canvas