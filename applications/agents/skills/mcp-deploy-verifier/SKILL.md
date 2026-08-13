---
name: mcp-deploy-verifier
description: Verify that a deployment succeeded by checking MCP endpoints for health and migration status. Use this after any deployment or migration.
---
# MCP Deployment Verifier Skill

You verify deployments using the MCP server.

## MCP Endpoints
- **Health**: `http://localhost:8001/health` – returns `{"status": "ok"}` if the server is running.
- **Migrations Status**: `http://localhost:8001/migrations/status` – returns a list of applied and unapplied migrations.

## Verification Steps
1. **Check health**:
   ```bash
   curl -f http://localhost:8001/health
If this fails, the server is down – abort and notify the user.

Check migrations:
curl http://localhost:8001/migrations/status
Parse the JSON response.
If there are any unapplied migrations, report them and suggest running python manage.py migrate.
If both pass, output:
✅ Deployment verified.
- MCP server is healthy.
- All migrations are applied.
If migrations are pending, output:
⚠️ Deployment partially successful.
- MCP server is healthy.
- Pending migrations: [list]
Please run `python manage.py migrate` and re‑verify.
If the server is unreachable, output:
❌ Deployment failed.
- MCP server is not responding.
- Check logs with `docker logs mcp-server`.
