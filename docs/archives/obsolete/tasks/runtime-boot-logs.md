# Runtime boot and log isolation tasks

Priority: 1 — complete before template/library moves.

## Affected paths
- `Makefile`
- `core/Makefile`
- `compose/`
- `core/configs/`
- `core/ctc-research/`
- `core/lms-demo/`
- `core/VResume/`
- `logs/`
- `core/*/logs/`
- `../services` deployment Makefiles when present in the deployment checkout

## Intended behavior
- Docker Compose paths resolve from the `core/` dispatcher and use canonical project paths (`ctc-research`, `lms-demo`, `VResume`) consistently.
- Containers mount shared application directories such as `core/configs`, shared commands, and shared assets instead of copying divergent site-local copies.
- Environment variables and service passwords are linked consistently between web, database, cache, worker, and deployment commands.
- Runtime logs are isolated per website while shared logs remain under the top-level shared log directory.
- Make targets can clean build, deploy, test, and website-specific runtime logs without deleting unrelated site logs.

## Validation commands
- `make -C applications show-vars WEBSITE=ctc`
- `make -C applications show-vars WEBSITE=lms-demo`
- `make -C applications show-vars WEBSITE=VResume`
- `make -C applications validate-config WEBSITE=ctc`
- `make -C applications validate-config WEBSITE=lms-demo`
- `make -C applications validate-config WEBSITE=VResume`
- `make -C applications docker-logs WEBSITE=ctc`
- `make -C applications docker-logs WEBSITE=lms-demo`
- `make -C applications docker-logs WEBSITE=VResume`
