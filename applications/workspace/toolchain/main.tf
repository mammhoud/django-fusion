# =============================================================================
# toolchain — Coder Template (minimal, from scratch)
# =============================================================================
# A minimal workspace that provisions ONE agent-host container and installs a
# reproducible frontend/monorepo toolchain on start:
#
#   * git  — source control client
#   * make — build orchestration
#   * Nx   — workspace task runner (installed globally via `npm i -g nx`)
#
# The install script is a `coder_script` that runs on every workspace start
# (`run_on_start = true`), is idempotent, and reports the resolved versions.
#
# Unlike the sibling `workspace` template (which bind-mounts the host checkout
# and runs the repo's devcontainer), this template is intentionally standalone:
# no devcontainer, no repository bind mount, no AFFiNE. It is the "from scratch"
# base for an Nx/monorepo workspace that clones or initializes its own project.
# =============================================================================

terraform {
  required_providers {
    coder  = { source = "coder/coder" }
    docker = { source = "kreuzwerker/docker" }
  }
}

# ============================================================
# Variables
# ============================================================
variable "docker_network" {
  type        = string
  default     = "common"
  description = "Shared Docker network that hosts the Coder control plane and this agent-host container"
}
variable "coder_host_ip" {
  type        = string
  default     = "172.18.0.16"
  description = "Coder server host/IP reachable from the workspace container for the agent binary download (http://<host>:7080/bin/coder-linux-amd64)"
}
variable "workspace_name" {
  type        = string
  default     = "toolchain"
  description = "Optional lowercase hostname and workspace label suffix"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9_.-]*$", lower(var.workspace_name)))
    error_message = "workspace_name must be a valid Docker container name suffix (lowercase alphanumerics plus '.', '_', '-')."
  }
}

locals {
  ws_name = lower(var.workspace_name)
  home    = "/home/coder"
}

# ============================================================
# Coder data
# ============================================================
data "coder_workspace" "me" {}
data "coder_provisioner" "me" {}
data "coder_workspace_owner" "me" {}

# ============================================================
# Coder agent (runs inside the agent-host container)
# ============================================================
resource "coder_agent" "main" {
  arch = data.coder_provisioner.me.arch
  os   = "linux"

  env = {
    GIT_AUTHOR_NAME     = coalesce(data.coder_workspace_owner.me.full_name, data.coder_workspace_owner.me.name)
    GIT_AUTHOR_EMAIL    = data.coder_workspace_owner.me.email
    GIT_COMMITTER_NAME  = coalesce(data.coder_workspace_owner.me.full_name, data.coder_workspace_owner.me.name)
    GIT_COMMITTER_EMAIL = data.coder_workspace_owner.me.email
  }

  display_apps {
    vscode                 = false
    web_terminal           = true
    ssh_helper             = true
    port_forwarding_helper = true
  }

  metadata {
    key          = "toolchain"
    display_name = "Toolchain"
    script       = "sh -c 'git --version; make --version | head -1; node --version; nx --version '"
    interval     = 3600
    timeout      = 5
  }
  metadata {
    key          = "workspace"
    display_name = "Workspace"
    script       = "echo ${data.coder_workspace.me.name}"
    interval     = 3600
    timeout      = 3
  }
}

# ============================================================
# Toolchain install script (runs on every start)
# ============================================================
resource "coder_script" "toolchain" {
  agent_id     = coder_agent.main.id
  display_name = "Install toolchain (git + make + Node + Nx)"
  run_on_start = true

  script = <<-EOT
    set -eux

    export DEBIAN_FRONTEND=noninteractive

    # 1. Base toolchain: git client + make. The enterprise-node image already
    #    ships most of this; apt is idempotent so re-running is safe.
    if command -v apt-get >/dev/null 2>&1; then
      apt-get update -y
      apt-get install -y --no-install-recommends git make ca-certificates curl
    fi

    # 2. Node.js runtime for Nx (guarded for minimal images that omit it).
    if ! command -v node >/dev/null 2>&1; then
      apt-get install -y --no-install-recommends nodejs npm
    fi

    # 3. Nx CLI globally — the requested `npm i -g nx`.
    npm install -g nx freebuff

    # 4. Report the resolved toolchain versions.
    echo "toolchain: git $(git --version) | make $(make --version | head -1) | node $(node --version) | npm $(npm --version) | nx $(nx --version) | freebuff $(freebuff --version)"
  EOT
}

# ============================================================
# Agent-host container
# ============================================================
# Persist /home/coder (agent state) across restarts.
resource "docker_volume" "home_volume" {
  name = "coder-${data.coder_workspace.me.id}-toolchain-home"
  lifecycle {
    ignore_changes = all
  }
  labels {
    label = "coder.workspace_id"
    value = data.coder_workspace.me.id
  }
}

resource "docker_container" "workspace" {
  count = data.coder_workspace.me.start_count
  # Prebuilt agent-host image (docker CLI + compose plugin + git + curl + node);
  # no build step in the template.
  image    = "codercom/enterprise-node:ubuntu"
  name     = "coder-${data.coder_workspace.me.id}-toolchain"
  hostname = local.ws_name

  # Same plain-HTTP agent-binary download workaround as the `workspace`
  # template: the Coder access URL serves a broken TLS cert, so fetch the
  # binary from the stable internal coder_host_ip.
  command = [
    "/bin/sh", "-c",
    <<-EOT
    set -e
    for i in 1 2 3 4 5; do
        curl -fsSL http://${var.coder_host_ip}:7080/bin/coder-linux-amd64 -o /tmp/coder-agent && break
        sleep 5
    done
    if [ -s /tmp/coder-agent ]; then
        chmod +x /tmp/coder-agent
        mkdir -p "$HOME/.local/bin"
        ln -sf /tmp/coder-agent "$HOME/.local/bin/coder"
        export PATH="$HOME/.local/bin:$PATH"
        exec sudo -n -E /tmp/coder-agent agent
    else
        echo "coder-agent download failed after retries" >&2
        exit 1
    fi
    EOT
  ]

  env = [
    "CODER_AGENT_TOKEN=${coder_agent.main.token}",
    "CODER_AGENT_URL=http://${var.coder_host_ip}:7080",
  ]

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }
  volumes {
    volume_name    = docker_volume.home_volume.name
    container_path = local.home
  }

  networks_advanced {
    name = var.docker_network
  }

  labels {
    label = "coder.owner"
    value = data.coder_workspace_owner.me.name
  }
  labels {
    label = "coder.owner_id"
    value = data.coder_workspace_owner.me.id
  }
  labels {
    label = "coder.workspace_id"
    value = data.coder_workspace.me.id
  }
  labels {
    label = "coder.workspace_name"
    value = data.coder_workspace.me.name
  }

  destroy_grace_seconds = 10
}
