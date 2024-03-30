from .api_krita import Krita
from .krita_remote_extension import KritaRemoteExtension
from .krita_remote_dock import KritaRemoteDockWidget

DOCKER_ID: str = "krita_remote"

Krita.add_extension(KritaRemoteExtension)
Krita.add_dock_widget(KritaRemoteDockWidget, DOCKER_ID)
