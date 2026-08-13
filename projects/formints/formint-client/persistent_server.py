import http.server
import socketserver
import threading

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = '''<!DOCTYPE html>
<html>
<head><title>Formint Café</title></head>
<body>
  <header><h1>Formint Café</h1></header>
  <div class="category-pills">
    <span>Tea</span>
    <span>Smoothies</span>
    <span>Desserts</span>
  </div>
  <div class="product-grid">
    <div class="card">Product 1</div>
    <div class="card">Product 2</div>
  </div>
  <footer>
    <div class="bottom-bar">Client v0.1.0 &middot; Fusion a1b2c3d</div>
  </footer>
</body>
</html>'''.encode('utf-8')
        self.wfile.write(html)
    def log_message(self, format, *args):
        pass

server = socketserver.TCPServer(('0.0.0.0', 4322), Handler)
print('Server starting on port 4322...')
server.serve_forever()
