# Enhanced Prompts (actionable)

Use these prompts with an LLM or automation tool to generate code, documentation, or step-by-step actions for the project.

1) Full project audit and remediation plan

Prompt:
```
You are an engineering assistant with access to a Django monorepo at /root/site/websites.
Perform a full deployment audit for two sites (ctc-research.com and structa.cloud):
- Validate `websites/configs` settings, ENV YAMLs, and secret handling.
- Ensure `libs/` packages (`django_osoul`, `django_rseal`) are imported from the workspace, not duplicated.
- Run frontend builds (`npm ci`, `npm run build:ctc`, `npm run build:structa`) and verify bundles exist.
- Run `manage.py build_assets` for each site and check `collectstatic` outputs.
- Run Django checks and unit tests.
- Produce a prioritized remediation list (fixes, risks, and quick wins).
Return results as JSON with `done`, `pending`, `errors`, and `recommendations` fields.
```

2) Generate deploy-ready Dockerfiles and compose

Prompt:
```
Generate a `Dockerfile.web` and `docker-compose.websites.yml` for building per-site images.
Requirements:
- Parameterize build with `PROJECT_PATH` and `BUNDLES_DIR` to avoid bundle collisions.
- Mount `websites/configs` read-only and an external `media` volume for uploads.
- Include setup for MinIO as S3-compatible media server or an Nginx static server option.
- Include a `verify_deployment` command that runs smoke checks on startup.
Return the files and brief instructions to build and run locally.
```

3) Produce CI config that runs build and tests

Prompt:
```
Create a CI workflow (e.g., GitHub Actions or GitLab CI) that:
- Installs Python and Node.
- Runs `npm ci` and `npm run build:ctc`/`build:structa`.
- Runs `pip install -r requirements.txt` and `pytest`.
- Runs `python manage.py build_assets` and `python manage.py collectstatic --no-input`.
- Fails the build if any step errors and reports artifacts (bundles.json, coverage).
Return a YAML CI file and guidance for secrets.
```

4) Documentation and acceptance criteria prompt

Prompt:
```
Create an actionable `Results` report for the deployment checklist including:
- What was verified and how (commands and outputs).
- What remains undone (link to `UNDONE_TASKS.md`).
- A prioritized list of enhancements with owners and time estimates.
Return as Markdown suitable for inclusion in `DEPLOY_CHECKLIST.md` under `## Results`.
```

Use these prompts iteratively; copy and adapt them to the specific step you want the model to perform.
