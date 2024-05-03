from PyQt5.QtWidgets import QDialog, QBoxLayout, QFrame, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
import urllib.request
import urllib.parse

def generate_qr(client_url: str, ws_url: str)-> QPixmap:
        url_param = urllib.parse.urlencode({
            "data" : "{}/#{}".format(client_url, ws_url),
            "size" : 200,
            "margin" : 0,
            "qzone": "2",
            "ecc": "L",
            "format": "png",
            "color" : "000000",
            "bgcolor": "ffffff"
            })
        url = "https://api.qrserver.com/v1/create-qr-code/?{}".format(url_param)
        with urllib.request.urlopen(url, timeout=10) as response:
            assert response.status == 200
            image = QPixmap()
            image.loadFromData(response.read())
        return image

class QRDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        frame = QFrame(self)
        layout = QBoxLayout(QBoxLayout.Direction.Down, frame)
        self.label = QLabel(frame)
        warning = QLabel(frame)
        
        self.setWindowFlags(self.windowFlags())
        self.setMinimumSize(QSize(300,500))
        self.setWindowTitle("Scan the QR code on your phone")
        self.setLayout(layout)
        
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50,50,50,50)
        
        warning.setText("Remote connection is NOT SECURE as TLS is unsupported.\nDO NOT SCAN QR CODE WHILE CONNECTED TO UNTRUSTED WIFI!!!")
        
        self.url = QLabel(frame)

        layout.addWidget(warning)
        layout.addWidget(self.label)
        layout.addWidget(self.url)

    def set_pixmap(self, http_url, ws_url):
        url = "{}/#{}".format(http_url, ws_url)
        self.url.setText("<a href=\"{}\">{}</a>".format(url, url))
        self.url.setTextFormat(Qt.RichText)
        self.url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.url.setOpenExternalLinks(True)

        self.label.setPixmap(generate_qr(http_url,ws_url))
