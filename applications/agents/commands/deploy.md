---
description: Deploy the project and verify migrations via MCP
agent: devops-engineer
---
# Deploy Workflow

You are deploying the Django Customizer project.

1. **Run pre‑deploy checks**:
   - `python manage.py check --deploy`
   - `python manage.py validate_templates`
2. **Apply migrations**: `python manage.py migrate`
3. **Collect static files**: `python manage.py collectstatic --noinput`
4. **Restart the server** (Docker or systemd).
5. **Wait 5 seconds** for the server to come up.
6. **Verify MCP health**: `curl -f http://localhost:8001/health`
7. **Check migration status**: `curl http://localhost:8001/migrations/status`
8. **If both pass**, report "Deployment successful".
9. **If either fails**, rollback by reverting to the previous Docker image or git commit.

Always ask the user for confirmation before running `migrate` in production.