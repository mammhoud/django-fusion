# =============================================================================
# workspace — Coder Template (single merged template)
# =============================================================================
# The ONLY workspace template: ONE agent-host container that bind-mounts the
# host's local checkout (`/home/structa.cloud` -> `/home/coder/structa.cloud`)
# and runs the repository's compose devcontainer INSIDE it via
# coder_devcontainer on the host Docker socket. No git clone — the mounted
# folder IS the source, so edits made locally or in the workspace are the same
# files and git commit/push work from both sides.
#
#   .devcontainer/docker-compose.yml  (the repo's devcontainer source)
#     └─ devcontainer   — full monorepo toolchain (VS Code attaches here)
#
# AFFiNE and FileGator are permanent shared proxy services, not workspace
# resources. Their data and network identity survive Coder workspace changes.
#
# The agent runs as root (passwordless sudo in the image) so the root-owned
# host checkout stays writable from the workspace (commit/push from both
# sides); the container keeps the docker CLI/compose/node tooling.
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
  description = "Shared Docker network that hosts the proxy, the devcontainer services, and this agent-host container"
}
variable "coder_host_ip" {
  type        = string
  default     = "172.18.0.16"
  description = "Coder server host/IP reachable from the workspace container for the agent binary download (http://<host>:7080/bin/coder-linux-amd64)"
}
variable "workspace_name" {
  type        = string
  default     = "workspace"
  description = "Optional lowercase hostname and workspace label suffix; it does not control shared proxy service names."

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9_.-]*$", lower(var.workspace_name)))
    error_message = "workspace_name must be a valid Docker container name suffix (lowercase alphanumerics plus '.', '_', '-')."
  }
}
variable "host_repo_path" {
  type        = string
  default     = "/home/structa.cloud"
  description = "Host path of the local checkout to bind-mount as the workspace project folder (/home/coder/structa.cloud). Mounted read-write: no clone happens, so changes and git operations are shared between host and workspace."
}
locals {
  ws_name           = lower(var.workspace_name)
  devcontainer_home = "/home/coder"
  workspace_folder  = "${local.devcontainer_home}/structa.cloud"
}

# ============================================================
# Coder data
# ============================================================
data "coder_workspace" "me" {}
data "coder_provisioner" "me" {}
data "coder_workspace_owner" "me" {}

# ============================================================
# Coder agent  (runs inside the agent-host container)
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

  # No VS Code Desktop: the browser editor (code-server module, "VS Code Web")
  # and the web terminal are the workspace apps.
  display_apps {
    vscode                 = false
    web_terminal           = true
    ssh_helper             = true
    port_forwarding_helper = true
  }

  metadata {
    key          = "devcontainer"
    display_name = "Devcontainer"
    script       = "echo ${local.workspace_folder}"
    interval     = 30
    timeout      = 3
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
# Coder apps  (reached from the agent over the shared `common` network)
# ============================================================
# ============================================================
# Devcontainer modules  (docker-devcontainer pattern)
# ============================================================
# The devcontainer CLI runs inside the agent-host container against the
# mounted host Docker socket, so the devcontainer stack (and its service
# containers) are created on the shared host daemon where the proxy can
# reach them.
module "devcontainers-cli" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/devcontainers-cli/coder"
  agent_id = coder_agent.main.id
  version  = "~> 1.0"
}

# Browser editor ("VS Code Web"): code-server runs in the agent-host
# container and opens the mounted project folder that the devcontainer
# bind-mounts too, so both editors see the same files.
module "code-server" {
  count        = data.coder_workspace.me.start_count
  source       = "registry.coder.com/coder/code-server/coder"
  version      = "~> 1.5"
  agent_id     = coder_agent.main.id
  folder       = local.workspace_folder
  display_name = "VS Code Web"
  slug         = "code-server"
  order        = 2
}

resource "coder_app" "filegator" {
  agent_id     = coder_agent.main.id
  slug         = "filegator"
  display_name = "Files"
  url          = "http://proxy-filegator:8080"
  icon         = "/emojis/1f4c1.png"
  share        = "authenticated"
  order        = 3
}

resource "coder_devcontainer" "repo" {
  count            = data.coder_workspace.me.start_count
  agent_id         = coder_agent.main.id
  workspace_folder = local.workspace_folder
}

# ============================================================
# Agent-host container
# ============================================================
# Persist /home/coder (agent and devcontainer state) across restarts.
resource "docker_volume" "home_volume" {
  name = "coder-${data.coder_workspace.me.id}-home"
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
  # same image the devcontainer template uses, so no build step in the template.
  image = "codercom/enterprise-node:ubuntu"
  # Unique per workspace; a fixed name would conflict whenever a stale
  # container or a second workspace lingers.
  name     = "coder-${data.coder_workspace.me.id}-workspace"
  hostname = local.ws_name

  # The Coder access URL serves a broken TLS cert, so the agent binary is
  # fetched over plain HTTP from the stable internal coder_host_ip instead of
  # coder_agent.main.init_script (which would target the HTTPS access URL).
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
        # Expose the `coder` CLI (same binary) on PATH so agent scripts
        # (metadata, modules) can resolve it.
        mkdir -p "$HOME/.local/bin"
        ln -sf /tmp/coder-agent "$HOME/.local/bin/coder"
        export PATH="$HOME/.local/bin:$PATH"
        # Run the agent as root (passwordless sudo, -E keeps the agent env)
        # so the root-owned bind-mounted checkout is writable from the
        # workspace — git commit/push work from both host and container.
        exec sudo -n -E /tmp/coder-agent agent
    else
        echo "coder-agent download failed after retries" >&2
        exit 1
    fi
    EOT
  ]

  env = [
    "CODER_AGENT_TOKEN=${coder_agent.main.token}",
    # The agent requires the server URL (the container reaches the server
    # directly over the shared `common` network; same plain-HTTP workaround
    # as the binary download above).
    "CODER_AGENT_URL=http://${var.coder_host_ip}:7080",
    # Passed through to the devcontainer compose (.devcontainer/docker-compose.yml
    # interpolation): REPO_HOST_PATH so the compose mounts the REAL host
    # checkout (the daemon is the host daemon, so a relative `..` would bind
    # an empty host dir).
    "REPO_HOST_PATH=${var.host_repo_path}",
  ]

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }
  volumes {
    volume_name    = docker_volume.home_volume.name
    container_path = local.devcontainer_home
  }
  # The project source: bind-mount the host checkout (no clone).
  volumes {
    host_path      = var.host_repo_path
    container_path = local.workspace_folder
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
