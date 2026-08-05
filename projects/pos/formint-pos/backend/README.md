# Formint Django sidecar

This directory is the application backend for the Formint Tauri shell.
Django owns domain rules, persistence, permissions, audit, and the first
`django-fusion` fragment render. Rust only supervises the process and exposes
native capabilities.

## Local development

```bash
cd projects/pos/formint-pos/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python sidecar.py runserver 127.0.0.1:8767
```

The Astro dev proxy and the Tauri shell use port `8767`. Browser requests to
`/htmx/` and `/fusion/` remain same-origin from the frontend through the dev
proxy.

## Tauri sidecar packaging

Build a platform-specific executable named `formint-backend` and place it in
`../src-tauri/binaries/` with Tauri's target-triple suffix, for example:

```bash
pyinstaller --onefile --name formint-backend sidecar.py
# rename/copy dist/formint-backend to
# ../src-tauri/binaries/formint-backend-<target-triple>
```

The binary is intentionally not committed. Release automation must build it
from the locked backend environment, checksum it, and attach the checksum to
the release manifest.

## Rendering boundary

- `formint/fusion_components.py` is the first django-fusion component.
- `formint/views.py` exposes the explicit `X-Fusion-Render-First: true` proof
  path and the lean HTMX data path.
- Astro owns page layout, skeletons, retry, and empty/error states.
- No Wagtail or backend-rendered full page is required by this sidecar.
