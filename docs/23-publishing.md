# Building and Publishing to PyPI — DF-023

The complete runbook for cutting a `django-fusion` release: bump the version,
build the distributions, validate them, rehearse on TestPyPI, publish to PyPI,
and tag the repository.

Read the whole page once before your first release. The short version is:

```bash
make version        # 1. confirm the version
make dist           # 2. build sdist + wheel
make check-dist     # 3. twine check
make publish-test   # 4. rehearse on TestPyPI
make publish        # 5. publish to PyPI
```

## 1. One version, three places

A release version lives in exactly three coordinated places. They must agree or
the release is wrong in a way that cannot be undone.

| Place | What to change |
|---|---|
| `pyproject.toml` | `version = "X.Y.Z"` |
| `src/django_fusion/__init__.py` | `__version__ = "X.Y.Z"` |
| `CHANGELOG.md` | a dated `## [X.Y.Z]` section with a compare link |

```bash
make version   # prints the pyproject version
```

`make publish` refuses to run unless the working tree is clean **and** `HEAD` is
exactly the `vX.Y.Z` tag for that version, so a mismatched triple cannot be
published by accident.

### Choosing the number

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR** — a public import path, setting name, template contract, or response
  shape changes incompatibly.
- **MINOR** — new public API, or a documented behavior change that existing
  code survives.
- **PATCH** — fixes only.

Removing a symbol is a MAJOR change even when the symbol looked unused. Search
the whole repository for importers before deciding.

## 2. Before you build

- [ ] `pyproject.toml`, `__init__.py`, and `CHANGELOG.md` agree on the version.
- [ ] The changelog has a dated section for this version, and the
      `[Unreleased]` block above it is empty.
- [ ] `uv run --extra test pytest -q` is green.
- [ ] `uv run --with ruff ruff check src tests` is clean.
- [ ] `tests/test_documented_import_paths.py` passes — it pins the import paths
      the docs promise.
- [ ] Public docs that changed are updated, and `docs/INDEX.md` still reflects
      real files.
- [ ] Any new public symbol is listed in the README or the relevant `DF-0NN` doc.

## 3. Build

```bash
make dist
# equivalent to:
rm -rf dist build src/*.egg-info
uv build
```

This writes two artifacts:

```
dist/django_fusion-X.Y.Z.tar.gz              # sdist
dist/django_fusion-X.Y.Z-py3-none-any.whl    # wheel
```

`uv build` (like `python -m build`) uses an isolated build environment, so the
artifacts do not depend on your local venv. Do not publish with
`pip install .`-style builds — they can pick up stray local files.

## 4. Validate

```bash
make check-dist
# equivalent to:
uv run --with twine twine check dist/*
```

`twine check` validates the rendered long description, metadata, and the
README. It must print `PASSED` for **both** the wheel and the sdist. A failure
here means the PyPI page would be broken or the upload would be rejected.

### Confirm the wheel actually carries the package data

A wheel can be importable and still be useless, because Django only fails at
render time when templates are missing. Check the contents:

```bash
python -c "
import zipfile
z = zipfile.ZipFile('dist/django_fusion-X.Y.Z-py3-none-any.whl')
names = z.namelist()
print('templates:', sum(n.endswith('.html') for n in names))
print('scss     :', sum(n.endswith('.scss') for n in names))
print('py.typed :', any(n.endswith('py.typed') for n in names))
"
```

Expect roughly 50+ templates, 15+ SCSS partials, and `py.typed`. If templates
are missing, `[tool.setuptools.package-data]` or `MANIFEST.in` lost an entry.

### Smoke-test the wheel in a clean environment

Install the built wheel somewhere that is *not* this repository and confirm the
templates resolve:

```bash
uv venv /tmp/df-smoke --python 3.11
uv pip install --python /tmp/df-smoke/bin/python dist/django_fusion-X.Y.Z-py3-none-any.whl
/tmp/df-smoke/bin/python -c "
import django_fusion
from pathlib import Path
pkg = Path(django_fusion.__file__).parent
assert 'site-packages' in str(pkg), pkg
assert (pkg / 'templates' / 'components' / 'form' / 'form_block.html').is_file()
assert (pkg / 'py.typed').is_file()
print('wheel smoke test OK:', django_fusion.__version__)
"
```

## 5. Credentials

PyPI no longer accepts plain username/password for uploads. Use an **API token**
scoped to the project (`pypi-django-fusion-...`) or trusted publishing (step 8).

Create the token at <https://pypi.org/manage/account/token/>.

### Option A — `~/.pypirc`

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-...            # token value, never committed

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-...            # a separate token from test.pypi.org
```

### Option B — environment variables (preferred in CI)

`twine` and `uv publish` both read these; nothing touches disk.

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
# or, for uv publish:
export UV_PUBLISH_TOKEN=pypi-...
```

Never commit a token, never paste one into a doc, an issue, or a chat log. If a
token is exposed, revoke it immediately on the PyPI account page.

## 6. Rehearse on TestPyPI

Always publish to TestPyPI first. It is a separate index with separate accounts
and separate tokens, and it catches metadata problems that `twine check` cannot.

```bash
make publish-test
# equivalent to:
uv run --with twine twine upload --repository testpypi dist/*
```

Verify the rehearsal installs:

```bash
uv venv /tmp/df-test --python 3.11
uv pip install --python /tmp/df-test/bin/python \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  django-fusion==X.Y.Z
/tmp/df-test/bin/python -c "import django_fusion; print(django_fusion.__version__)"
```

The `--extra-index-url` is required because TestPyPI does not mirror the real
dependencies (`Django`, `Wagtail`, and the rest come from PyPI).

> **TestPyPI versions are also permanent.** If the rehearsal reveals a problem,
> fix it and bump to the next patch number; you cannot reuse `X.Y.Z` on
> TestPyPI either.

## 7. Publish to PyPI

```bash
make publish
# equivalent to (after the clean-tree and tag guard):
uv run --with twine twine upload dist/*
```

With `uv`, `uv publish --token "$UV_PUBLISH_TOKEN"` is an equivalent path.

Confirm:

```bash
uv pip install --python /tmp/df-check/bin/python --no-cache-dir django-fusion==X.Y.Z
```

Then check the project page renders: <https://pypi.org/project/django-fusion/>.

## 8. Trusted publishing (no long-lived tokens)

Preferred for CI. PyPI mints a short-lived credential for a specific workflow
via OIDC, so there is no token to leak or rotate.

1. On PyPI: **Your projects → django-fusion → Publishing → Add a new pending
   publisher → GitHub**.
2. Fill in:
   - Owner: `mammhoud`
   - Repository: `django-fusion`
   - Workflow: `release.yml`
   - Environment: `pypi`
3. Add `release.yml` that triggers on a published GitHub release or a `v*` tag,
   runs `uv build`, and uploads with `pypa/gh-action-pypi-publish`:

```yaml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write        # required for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

Because `pypa/gh-action-pypi-publish` needs `id-token: write` and its own
action reference, adding `release.yml` requires a GitHub token with the
**`workflow`** scope. A token without it is rejected with:

```
remote: Refusing to allow a Personal Access Token to create or update workflow
`.github/workflows/release.yml` without `workflow` scope.
```

If your token lacks that scope, publish locally with `make publish` (step 7)
and add the workflow once a workflow-scoped token is available.

## 9. Tag the release

The tag is what makes the release reproducible for consumers who install from
git, and `make publish` verifies it.

```bash
git tag -a vX.Y.Z -m "django-fusion X.Y.Z"
git push origin generic
git push origin vX.Y.Z
```

Then create the GitHub release from that tag and paste the matching
`CHANGELOG.md` section as the notes.

If `django-fusion` is checked out as a submodule of another repository, the
parent's gitlink now points at the previous commit. Update the parent in its own
commit — the library and the parent are two review surfaces.

## 10. If something goes wrong

| Situation | What to do |
|---|---|
| Bad metadata, upload rejected | Nothing was published. Fix and re-run from step 3. |
| Published, but the release is broken | **Delete the release file** for that version (PyPI → Manage → Releases → Options → Delete) within 72 hours — PyPI will not let you re-upload the same filename, and deletion is the only way back. Otherwise yank it and ship the next patch. |
| Published and installable, but you want it hidden | **Yank** the release (Manage → Releases → Options → Yank). It stops satisfying new `pip install` resolutions while existing pins keep working. |
| Wrong version number on PyPI | You cannot edit it. Yank or delete, then publish the correct number. |
| Token leaked | Revoke it on PyPI immediately and re-issue. |
| Forgot to include a file in the wheel | Fix `MANIFEST.in` / `package-data`, bump the patch version, and publish again. |

**Rule of thumb:** a version number that reached PyPI is spent. Fixing a release
means shipping the next number, not editing the old one.

## 11. Reference

- [PyPI API tokens](https://pypi.org/help/#apitoken)
- [Trusted publishing](https://docs.pypi.org/trusted-publishers/)
- [Twine documentation](https://twine.readthedocs.io/)
- [uv build / uv publish](https://docs.astral.sh/uv/guides/package/)
- [PEP 639 — license metadata](https://peps.python.org/pep-0639/)
- Repository `Makefile` — the `version`, `dist`, `check-dist`, `publish-test`,
  and `publish` targets used above.

## Related

- [DF-000 Documentation index](./INDEX.md)
- [DF-002 Architecture](./02-architecture.md)
- [DF-017 Integration modes and project boundaries](./17-integration-modes.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md) — day-to-day workflow and commit conventions
