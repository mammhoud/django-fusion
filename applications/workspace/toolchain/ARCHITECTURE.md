# toolchain — Architecture

The `toolchain` Coder template provisions one agent-host container and installs
the Nx/git/make toolchain via a startup script. It is intentionally minimal and
owns no shared application data.

## Provisioning flow

```text
coder templates push -d applications/workspaces/toolchain
  │
  ▼
Terraform (coder + docker providers)
  ├─ coder_agent.main        — agent, web terminal, SSH helper
  ├─ coder_script.toolchain  — idempotent install (git, make, node, nx)
  ├─ docker_volume.home_volume — persistent /home/coder
  └─ docker_container.workspace — agent host on the `common` network
```

The `docker_container.workspace` command downloads the `coder` agent binary over
plain HTTP from `coder_host_ip` (the Coder access URL serves a broken TLS cert),
then runs it as root. The `coder_script` installs the toolchain on
`run_on_start`, so every restart re-checks and re-installs missing tools.

## Ownership boundaries

| Component | Owner | Persistence |
|---|---|---|
| Agent host + toolchain | Coder template | Coder home volume (`coder-<id>-toolchain-home`) |
| Coder control plane | `applications/docker-compose.yml` | Coder's own volumes |
| PostgreSQL / Redis | `applications/databases/` | database volumes |

Deleting or rebuilding a `toolchain` workspace does not affect the Coder control
plane, shared databases, or the sibling `workspace` template.

## Idempotency

The install script is safe to re-run:

- `apt-get install` is a no-op for already-installed packages.
- Node.js is only installed when `node` is absent (the
  `codercom/enterprise-node:ubuntu` image already ships it).
- `npm install -g nx` upgrades/reinstalls the Nx CLI without leaving partial
  state.

If a tool is missing after start, open the workspace logs and confirm the
`coder_script` ran to completion; the final log line lists the resolved
versions.
