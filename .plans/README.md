Overview

This directory contains operational plans, specs, and scripts to validate and
deploy both websites. Files are grouped into categories — see `PLAN_INDEX.md` for
an index and instructions.

- `DEPLOY_CHECKLIST.md`: the deployment and validation checklist for both websites.

Additional notes
- `.js.plans/`: design-time JS modules (notifications, SSE handlers). These are reference sources; move or copy into `websites/www/static_src/js/notifications/` when integrating into the production webpack build.
- `docker/copies/`: aggregated copies of repo `docker-compose` files for reference and reproducible compose fragments. See `docker/README.md` for usage.
Quick actions

```bash
cd /root/site/websites/.plans
./check_all_plans.sh   # generate UNDONE_TASKS.md with all pending tasks
```

Follow `PLAN_INDEX.md` for categories and next steps.

If you'd like, I can move `.js.plans` into the site's `static_src` and add a `notifications` webpack entry.
