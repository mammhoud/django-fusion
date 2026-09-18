import http.server
import socketserver

PORT = 4322
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """<!DOCTYPE html>
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
</html>""".encode('utf-8')
        self.wfile.write(html)

with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
    print('serving at port', PORT)
    httpd.serve_forever()
