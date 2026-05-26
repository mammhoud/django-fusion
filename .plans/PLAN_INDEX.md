# Plans Index

Purpose: categorize the `.plans` documents and provide a single entrypoint to run checks and surface undone tasks.

Categories

- **Deployment**
  - DEPLOY_CHECKLIST.md
  - PLANS_VERIFICATION.md

- **Specifications & Tasks**
  - SPECIFICATION.md
  - specs/ (detailed spec directories)

- **Prompts & Guidance**
  - PROMPTS.md

- **Scripts & Automation**
  - check_plans.sh
  - check_all_plans.sh
  - manage-specs.sh

- **Steering / Governance**
  - steering/ (notes and governance files)

How to use

1. Run the aggregated scan to collect undone tasks across all plan files:

```bash
cd /root/site/websites/.plans
./check_all_plans.sh
# opens/creates UNDONE_TASKS.md with grouped results
```

2. Review `UNDONE_TASKS.md`, then open each referenced plan file to address tasks.

3. Once tasks are completed, re-run the script to validate the list is empty.

Tips

- Keep each plan file focused: a single top-level header and task list for traceability.
- Use `- [ ]` for pending tasks and `- [x]` for completed tasks; the script scans for `- [ ]` only.
- Place long-running or high-risk todos into `specs/` with clear owner and ETA in the item text.
