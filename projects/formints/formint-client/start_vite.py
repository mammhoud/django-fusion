import subprocess, time
p = subprocess.Popen(["/Users/mammhoud/.nvm/versions/node/v22.18.0/bin/node", "./node_modules/vite/bin/vite.js", "--host", "127.0.0.1", "--port", "1420"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
with open("server_pid.txt", "w") as f:
    f.write(str(p.pid))
for line in p.stdout:
    print(line, end="")
