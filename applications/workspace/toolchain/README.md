# toolchain — Coder Template

A minimal, standalone Coder workspace that installs a reproducible monorepo
toolchain on start. Unlike the sibling [`workspace`](../workspace/README.md)
template (which bind-mounts the host checkout and runs the repo's devcontainer),
this template is "from scratch": no devcontainer, no repository bind mount, and
no shared AFFiNE coupling.

## What it installs

A `coder_script` runs on every workspace start (`run_on_start = true`) and
installs, idempotently:

| Tool | Purpose | Install command |
|---|---|---|
| git | source control client | `apt-get install -y git` |
| make | build orchestration | `apt-get install -y make` |
| Node.js + npm | Nx runtime (guarded if absent) | `apt-get install -y nodejs npm` |
| Nx | workspace task runner | `npm install -g nx` |

The script reports the resolved versions (`git`, `make`, `node`, `npm`, `nx`)
to the workspace logs at the end.

## Access model

The workspace exposes a web terminal and SSH/port-forwarding helpers through
Coder. No workspace service publishes a host port, and there is no VS Code
Desktop app (matching the `workspace` template).

## Prerequisites

- Coder control plane running (`applications/docker-compose.yml`).
- External Docker network `common`.
- `coder_host_ip` reachable from the agent host for the agent binary download
  (default `172.18.0.16`).

## Push and create

```bash
coder templates push \
  -d applications/workspaces/toolchain \
  -m "Minimal Nx + git + make toolchain workspace" \
  -y toolchain
```

Create a workspace from the pushed `toolchain` template, then open the web
terminal and run `git --version`, `make --version`, and `nx --version` to
confirm the install script completed.

## Validation

```bash
terraform fmt -check applications/workspaces/toolchain
```
