# mcp_server.py
from fastapi import FastAPI
from django.core.management import call_command
from io import StringIO
import json

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/migrations/status")
async def migration_status():
    out = StringIO()
    call_command("showmigrations", stdout=out)
    output = out.getvalue()
    return {"raw": output}
