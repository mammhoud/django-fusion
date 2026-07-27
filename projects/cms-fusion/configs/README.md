# 📁 Shared Configuration (`projects/configs/`)

## What's Here

Shared Django settings and environment configuration used across all sites (ctc-research, lms, VResume).

```
configs/
├── base/                    # 🔴 Core settings modules (do NOT edit directly)
│   ├── __init__.py          #    Orchestrates all sub-modules
│   ├── database.py          #    PostgreSQL connection config
│   ├── cache.py             #    Redis cache backend
│   ├── email.py             #    SMTP backend config
│   └── auth.py              #    Allauth configuration
└── settings/                # ⚪ Environment-specific YAML settings
    └── ENV/
        ├── _production.yml  #    Production defaults
        └── sites.yml        # 🟢 Site registry — add new sites here
```

## Customization Tags

| Module | Tag | How to customize |
|--------|-----|-----------------|
| `base/` | 🔴 `not-customizable` | Override in site `settings.py`, not here |
| `ENV/sites.yml` | 🟢 `customizable` | Add/remove site entries freely |
| `ENV/_production.yml` | ⚪ `config-only` | Edit env var values, not structure |

## How to Add a Site

1. Add entry in `ENV/sites.yml`:
```yaml
sites:
  my-site:
    domain: mysite.com
    db_name: db_mysite
    port: 5100
```

2. The site auto-registers — no code changes needed.

## Quick Reference

- Settings are layered: `configs/base/` → `ENV/` → site `settings.py`
- [Full docs →](../../docs/back-env/README.md)
