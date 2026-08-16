import http.server
import socketserver
import os
import threading
import time
import urllib.request

PORT = 4173
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='dist', **kwargs)
    def do_GET(self):
        if self.path == '/' or not os.path.exists('dist' + self.path.split('#')[0].split('?')[0]):
            self.path = '/index.html'
        return super().do_GET()

socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer(('127.0.0.1', PORT), Handler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()
print('SERVER_STARTED_IN_THREAD')

time.sleep(0.5)
try:
    print('Self-test fetch:', len(urllib.request.urlopen('http://127.0.0.1:4173').read()))
except Exception as e:
    print('Self-test error:', e)

# Keep alive for browser interaction
while True:
    time.sleep(1)
