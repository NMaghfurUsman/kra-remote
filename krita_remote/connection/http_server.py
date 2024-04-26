from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from socket import gethostname, gethostbyname
from random import randint
from ..api_krita import Krita
from typing import Optional

INDEX_DIR = Krita.instance.getAppDataLocation() + "/pykrita/krita_remote/client"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=INDEX_DIR, **kwargs)

class HTTPServer(ThreadingHTTPServer):
    address: str
    port: Optional[int] = None
    def __init__(self, port = None):
        ip = gethostbyname(gethostname().split(".")[-1])
        port = port or randint(9999,pow(2,16))
        self.port = port
        super().__init__((ip, port), Handler)
        self.address = "http://{}:{}".format(ip, port)
        
    