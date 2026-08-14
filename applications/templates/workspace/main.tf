# =============================================================================
# workspace — Coder Template
# =============================================================================
# Provisions ONE agent-host container (docker CLI + git + curl) that runs the
# repository's compose devcontainer INSIDE it via coder_devcontainer on the
# host Docker socket. All workspace services now live in the devcontainer:
#
#   .devcontainer/docker-compose.yml  (the repo's devcontainer source)
#     ├─ devcontainer   — full monorepo toolchain (VS Code attaches here)
#     └─ affine         — AFFiNE workspace   (space.structa.cloud root; shared
#                                             postgres + redis via common /
#                                             warehouse-net)
#
# Service container names are pinned to coder-${workspace_name}-* inside the
# devcontainer compose; the shared-media nginx resolves the same names from
# its WORKSPACE_NAME env var (envsubst template) — both default to "workspace".
#
# The devcontainer image/toolchain is NOT defined here — the Coder template
# only hosts the agent; the devcontainer CLI (devcontainers-cli module) builds
# and runs the repo devcontainer through the mounted host socket.
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
variable "database_network" {
  type        = string
  default     = "warehouse-net"
  description = "External Docker network attached to the shared PostgreSQL service (used by the devcontainer AFFiNE service)"
}
variable "coder_host_ip" {
  type        = string
  default     = "172.18.0.16"
  description = "Coder server host/IP reachable from the workspace container for the agent binary download (http://<host>:7080/bin/coder-linux-amd64)"
}
variable "workspace_name" {
  type        = string
  default     = "workspace"
  description = "Service namespace suffix for the devcontainer service containers (coder-<workspace_name>-affine). Must match the shared-media nginx WORKSPACE_NAME env var (see applications/proxy/nginx/default.conf.template)."

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9_.-]*$", lower(var.workspace_name)))
    error_message = "workspace_name must be a valid Docker container name suffix (lowercase alphanumerics plus '.', '_', '-')."
  }
}

locals {
  ws_name           = lower(var.workspace_name)
  devcontainer_home = "/home/coder"
  workspace_folder  = "${local.devcontainer_home}/${try(module.git-clone[0].folder_name, "structa.cloud")}"
}

# ============================================================
# Coder data
# ============================================================
data "coder_workspace" "me" {}
data "coder_provisioner" "me" {}
data "coder_workspace_owner" "me" {}

data "coder_parameter" "repo_url" {
  type         = "string"
  name         = "repo_url"
  display_name = "Git Repository"
  description  = "Repository to clone for the devcontainer. Must contain a devcontainer.json + docker-compose.yml (the Structa Cloud monorepo root has both)."
  default      = "https://github.com/mammhoud/structa.cloud"
  mutable      = true
}

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
    key          = "affine"
    display_name = "AFFiNE"
    script       = <<-EOT
      name="coder-${local.ws_name}-affine"
      docker inspect -f '{{.State.Health.Status}}' "$name" 2>/dev/null \
        || docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null \
        || echo "not running"
    EOT
    interval     = 30
    timeout      = 5
  }
}

# ============================================================
# Coder apps  (reached from the agent over the shared `common` network)
# ============================================================
resource "coder_app" "affine" {
  agent_id     = coder_agent.main.id
  slug         = "affine"
  display_name = "AFFiNE Workspace"
  url          = "http://coder-${local.ws_name}-affine:3010"
  icon         = "/icon/desktop.svg"
  share        = "authenticated"
}

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

module "git-clone" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/git-clone/coder"
  agent_id = coder_agent.main.id
  url      = data.coder_parameter.repo_url.value
  base_dir = local.devcontainer_home
  version  = "~> 2.0"
}

# Browser editor ("VS Code Web"): code-server runs in the agent-host
# container and opens the same cloned repo folder that the devcontainer
# bind-mounts, so both editors see the same files.
module "code-server" {
  count        = data.coder_workspace.me.start_count
  source       = "registry.coder.com/coder/code-server/coder"
  version      = "~> 1.5"
  agent_id     = coder_agent.main.id
  folder       = local.workspace_folder
  display_name = "VS Code Web"
  slug         = "code-server"
}

resource "coder_devcontainer" "repo" {
  count            = data.coder_workspace.me.start_count
  agent_id         = coder_agent.main.id
  workspace_folder = local.workspace_folder
}

# ============================================================
# Agent-host container
# ============================================================
# Persist /home/coder (the git clone + devcontainer state) across restarts.
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
  # Unique per workspace (unlike the devcontainer service containers, which are
  # pinned to coder-<workspace_name>-* for the proxy); a fixed name would
  # conflict whenever a stale container or a second workspace lingers.
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
        exec /tmp/coder-agent agent
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
  ]

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }
  volumes {
    volume_name    = docker_volume.home_volume.name
    container_path = local.devcontainer_home
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
