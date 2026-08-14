---
display_name: Docker-in-Docker Dev Containers
description: Provision a privileged Docker container as a Coder workspace and auto-start any repository's devcontainer via Docker-in-Docker
icon: /icon/docker.svg
tags: [docker, container, devcontainer]
---

# Dev Containers

Provision a privileged Docker container as a [Coder workspace](https://coder.com/docs/user-guides/workspace-management)
running [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
via Docker-in-Docker — modeled on the official
[`coder/docker-devcontainer`](https://registry.coder.com/templates/coder/docker-devcontainer)
template. The workspace clones `repo_url` (default: the Structa Cloud monorepo)
and `coder_devcontainer` auto-starts its `.devcontainer/`, so the editor
attaches straight into the repo's devcontainer.

The editor is **VS Code Web** (browser): the `code-server` module installs
code-server in the workspace container and registers it as a Coder app
(`display_apps` disables the VS Code Desktop button — `vscode = false`). The
web terminal and SSH/port-forwarding helpers remain.

## Prerequisites

The host running Coder needs a working Docker socket. The workspace container
runs its own Docker daemon (privileged, Docker-in-Docker) and persists it on a
dedicated volume, so no host Docker group membership is required.

The Coder server must be reachable on the host gateway port `7080` (the agent
binary is fetched over plain HTTP from `host.docker.internal:7080`, matching
the `workspace` template's workaround for the broken public TLS cert).

## Architecture

The template provisions:

- A privileged Docker container (ephemeral) running the
  `codercom/enterprise-node:ubuntu` image (Docker + Node.js preinstalled)
- A Docker volume (persistent) at `/home/coder` — the git clone + user data
- A Docker volume (persistent) at `/var/lib/docker` — the inner Docker daemon
  data, so the devcontainer image/build cache survives restarts
- `init-docker-in-docker.sh` on start: configures `dnsmasq` + NAT so
  devcontainers can resolve `host.docker.internal` back to the workspace agent
- The `devcontainers-cli` and `git-clone` modules, plus `coder_devcontainer`
  to build and auto-start the repo's devcontainer

Only files under `/home/coder` (and the Docker volume) persist across
restarts; anything else in the workspace container is ephemeral. Persistence
inside the devcontainer itself is governed by each project's
`devcontainer.json`.

## Project source (cloned, not mounted)

The project directory is a **fresh `git clone`** performed by the `git-clone`
module at workspace start — **not** a bind mount of a local directory. The
clone lives in the workspace container's persistent home volume at
`~/<repo>` (from `repo_url`). The devcontainer CLI bind-mounts that same
cloned folder into the devcontainer, and the code-server editor opens it
directly, so all three see one copy of the source. Set `repo_url` to your fork
when the repo is private so the clone uses your authenticated GitHub identity.

## Usage

From the Coder UI, pick the **Dev Containers** template, choose the repository
(`repo_url` defaults to `https://github.com/mammhoud/structa.cloud`) and create
the workspace. The devcontainer starts automatically; open **VS Code Web**
from the workspace page (VS Code Desktop is disabled in `display_apps`).

Push the template from the repo root:

```bash
coder templates push devcontainer \
  --org coder \
  --directory applications/templates/devcontainer \
  --yes
```

> [!NOTE]
> Devcontainers run on the workspace's *inner* Docker daemon, so they start on
> an isolated bridge network. The Structa Cloud `.devcontainer/docker-compose.yml`
> attaches to host-level external networks (`common`, `warehouse-net`); when the
> devcontainer requires shared infrastructure, prefer the `workspace` template,
> which mounts the host Docker socket instead.
