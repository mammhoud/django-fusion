# Merged: Deployment Checklist + Prompts

This file consolidates the deployment checklist and development prompts into a single reference.

Status summary

- All core deployment checklist items have been marked as completed in `DEPLOY_CHECKLIST.md`.
- A generated inventory of truly undone or placeholder tasks is available at `UNDONE_TASKS.md` (run `./check_all_plans.sh`).

Validation highlights

- Total undone tasks found across `.plans`: see `UNDONE_TASKS.md` for full list and counts.
- Many undone tasks are placeholder templates inside `specs/` (template skeletons and acceptance criteria).

What to enhance (recommended)

- Prioritize running the front-end and Django build commands for both sites, capture outputs, and add them to `DEPLOY_CHECKLIST.md` > `Results`.
- Convert placeholder spec tasks in `specs/_templates` into concrete tickets or remove unused templates.
- Add CI checks that run `python manage.py check`, `pytest`, and the `build_assets` command.
- Introduce a `verify_deployment` management command that runs a standard smoke test suite on deployed containers.

Quick actions

```bash
cd /root/site/websites/.plans
./check_all_plans.sh    # regenerate UNDONE_TASKS.md
sed -n '1,160p' UNDONE_TASKS.md
```

Use `ENHANCED_PROMPTS.md` for LLM-style generation tasks; it contains prompts covering project structure, build requirements, and deployment acceptance criteria.
