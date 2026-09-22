import json
import subprocess

TOKEN = open("/tmp/coder_token").read().strip()
BASE = "http://localhost:7080"

def api(path):
    out = subprocess.run(
        ["docker", "exec", "coder", "curl", "-s", "-H", f"Coder-Session-Token: {TOKEN}",
         f"{BASE}{path}"],
        capture_output=True, text=True,
    )
    return out.stdout

orgs = json.loads(api("/api/v2/organizations"))
org = orgs[0]["id"]
print("org:", orgs[0]["name"])

raw = json.loads(api(f"/api/v2/organizations/{org}/templates/dev-stack/versions"))
print("RAW keys:", list(raw.keys()) if isinstance(raw, dict) else type(raw).__name__)
vs = raw if isinstance(raw, list) else raw.get("versions", [])
print("count in payload:", len(vs))
for v in vs[:8]:
    print("VERSION:", v["name"], "| created:", v["created_at"], "| archived:", v.get("archived", False))

# Inspect the newest version's files for filegator / blinko markers
latest = vs[0]
files = json.loads(api(f"/api/v2/organizations/{org}/templates/dev-stack/versions/{latest['name']}/files"))
for f in files:
    if f.get("path") == "main.tf":
        content = f.get("content", "")
        print(f"--- main.tf in {latest['name']}: filegator={content.count('filegator')} blinko={content.count('blinko')} resolver={content.count('resolver 127.0.0.11')} node CLIs={content.count('pnpm')}")
