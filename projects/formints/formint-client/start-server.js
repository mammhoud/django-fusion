const fs = require("fs");
const http = require("http");
const path = require("path");

const distDir = path.join(process.cwd(), "dist");
const server = http.createServer((req, res) => {
  let reqPath = req.url.split("?")[0];
  if (reqPath === "/") {
    reqPath = "/index.html";
  }
  let filePath = path.join(distDir, reqPath);
  if (!fs.existsSync(filePath)) {
    filePath = path.join(distDir, "index.html");
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not found");
    } else {
      let ext = path.extname(filePath);
      let contentType = "text/html";
      if (ext === ".js") {
        contentType = "application/javascript";
      } else if (ext === ".css") {
        contentType = "text/css";
      } else if (ext === ".woff2") {
        contentType = "font/woff2";
      }
      res.writeHead(200, {"Content-Type": contentType});
      res.end(data);
    }
  });
});
server.listen(4173, "127.0.0.1", () => {
  console.log("SERVER RUNNING ON 4173");
});
