from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from socket import gethostname, gethostbyname
from random import randint
from ..api_krita import Krita

INDEX_DIR = Krita.instance.getAppDataLocation() + "/pykrita/krita_remote/client"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=INDEX_DIR, **kwargs)

class HTTPServer(ThreadingHTTPServer):
    address: str
    def __init__(self):
        ip = gethostbyname(gethostname())
        port = randint(9999,pow(2,16))
        super().__init__((ip, port), Handler)
        self.address = "http://{}:{}".format(ip, port)
        
    