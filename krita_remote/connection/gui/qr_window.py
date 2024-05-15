from PyQt5.QtWidgets import QDialog, QBoxLayout, QFrame, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize

import sys
from os.path import dirname, join
sys.path.append(join(dirname(dirname(dirname(__file__))),"qrcode")) # 😬
from qrcode import make
from qrcode.image import svg
from base64 import b64encode

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
        self.qr_code_url = QLabel(frame)

        layout.addWidget(warning)
        layout.addWidget(self.label)
        layout.addWidget(self.qr_code_url)
        layout.addWidget(self.url)

    def set_pixmap(self, http_url, ws_url):
        url = "{}/#{}".format(http_url, ws_url)

        self.url.setText("<a href=\"{}\">{}</a>".format(url, url))
        self.url.setTextFormat(Qt.RichText)
        self.url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.url.setOpenExternalLinks(True)

        svg_bytes = make(url,image_factory=svg.SvgPathFillImage, box_size=16).to_string()
        data_url = "data:image/svg+xml;base64,{}".format(b64encode(svg_bytes).decode())
        self.qr_code_url.setText("<a href=\"{}\">Display QR code in web browser</a>".format(data_url))
        self.qr_code_url.setTextFormat(Qt.RichText)
        self.qr_code_url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.qr_code_url.setOpenExternalLinks(True)

        self.label.setPixmap(QPixmap.fromImage(QImage.fromData(svg_bytes,"image/svg+xml")))
