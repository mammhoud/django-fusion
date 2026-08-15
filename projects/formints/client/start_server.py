import http.server
import socketserver
import os

PORT = 4173
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='dist', **kwargs)
    def do_GET(self):
        if self.path == '/' or not os.path.exists('dist' + self.path.split('#')[0].split('?')[0]):
            self.path = '/index.html'
        return super().do_GET()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
    print('Persistent server running at http://127.0.0.1:4173')
    httpd.serve_forever()
