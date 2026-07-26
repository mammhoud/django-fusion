# www/ci — CI/CD Preflight Utilities

The `ci/` package provides shared helper functions used by the deploy-preflight GitHub Action and local `make deploy-preflight` commands.

---

## 📁 Directory Structure

```
ci/
├── __init__.py    # Package marker
├── utils.py       # Shared CI helper functions
└── README.md      # This file
```

---

## 🎯 Use Cases

### Preflight Validation
- Validate compose files before deployment
- Check Docker daemon availability
- Verify network configurations

### CI Pipeline Integration
- Used by `.github/workflows/deploy-ci.yml` for PR gating
- Used by `make deploy-preflight` for local validation

---

## 📄 File Documentation

### `utils.py` — CI Helper Functions

Provides reusable functions for CI/CD pipelines:

```python
def validate_compose_file(path: str) -> bool:
    """Run `docker compose config -q` on a compose file.
    
    Returns True if valid, False if parse errors found.
    """

def check_daemon_health() -> bool:
    """Probe the Docker daemon and return health status."""

def validate_network_name(name: str) -> bool:
    """Check a Docker network name against Docker's identifier rules.
    
    Validates: length ≤ 64, matches ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$
    """
```

---

## 🔗 Related
- `.github/workflows/deploy-ci.yml` — CI workflow
- `Makefile` — `deploy-preflight` target
- `docs/infrastructure/deployment.md` — Deployment documentation
