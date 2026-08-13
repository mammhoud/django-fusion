import http.server
import socketserver

PORT = 1420

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head><title>Formint POS</title></head>
<body>
  <div class="flex items-center justify-between p-4 bg-gray-900 text-white">
    <div class="flex items-center space-x-2">
      <span class="text-xl font-bold">Formint POS</span>
      <span class="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded-full">v1.0.0</span>
    </div>
    <div class="flex items-center space-x-4">
      <a href="#settings" id="nav-settings" onclick="showSettings()">Settings</a>
      <a href="#dashboard" onclick="showDashboard()">Dashboard</a>
    </div>
  </div>

  <div id="content" class="p-8">
    <h1>Welcome to POS</h1>
  </div>

  <script>
    function showSettings() {
      document.getElementById('content').innerHTML = `
        <h1 class="text-2xl font-bold mb-4">Settings</h1>
        <div class="p-4 border rounded shadow mb-4">
          <h2 class="font-bold text-lg">About</h2>
          <p>Client version v1.0.0</p>
          <p>Backend fusion version v9c5535d3</p>
        </div>
        <div class="p-4 border rounded shadow">
          <h2 class="font-bold text-lg">Fusion render mode</h2>
          <label class="flex items-center cursor-pointer mt-2">
            <span class="mr-3">Enable Fusion Render</span>
            <input type="checkbox" id="fusion-toggle" class="toggle-switch" checked />
          </label>
        </div>
      `;
    }
    function showDashboard() {
      document.getElementById('content').innerHTML = '<h1>Welcome to POS</h1>';
    }
  </script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print("Serving POS at port", PORT)
    httpd.serve_forever()
