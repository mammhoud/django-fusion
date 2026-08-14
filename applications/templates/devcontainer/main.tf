# =============================================================================
# devcontainer — Coder Template
# =============================================================================
# Modeled on the official docker-devcontainer template
# (https://registry.coder.com/templates/coder/docker-devcontainer): a single
# privileged workspace container runs Docker-in-Docker so any repository with
# a devcontainer.json can be opened as a Coder workspace — the devcontainers-cli
# module builds/starts the devcontainer and the IDE attaches to it.
#
# Differences from the official template:
#   * The Coder access URL (https://coder.structa.cloud) serves a broken TLS
#     cert, so the agent binary is fetched over plain HTTP from the host
#     gateway (host.docker.internal:7080) instead of coder_agent.main.init_script
#     (same workaround as the `workspace` template).
#   * CODER_AGENT_URL is pinned to http://host.docker.internal:7080 so the
#     init-docker-in-docker script takes its host.docker.internal branch and
#     devcontainers can reach the agent through the dnsmasq/NAT forwarding.
# =============================================================================

terraform {
  required_providers {
    coder  = { source = "coder/coder" }
    docker = { source = "kreuzwerker/docker" }
  }
}

locals {
  username = data.coder_workspace_owner.me.name

  # Workspace image with Docker (Docker-in-Docker) and Node.js preinstalled,
  # required by the @devcontainers/cli tool.
  workspace_image = "codercom/enterprise-node:ubuntu"
}

variable "docker_socket" {
  default     = ""
  description = "(Optional) Docker socket URI"
  type        = string
}

data "coder_parameter" "repo_url" {
  type         = "string"
  name         = "repo_url"
  display_name = "Git Repository"
  description  = "URL of the Git repository to clone into the workspace. The repository must contain a devcontainer.json to configure the development environment."
  default      = "https://github.com/mammhoud/structa.cloud"
  mutable      = true
}

provider "docker" {
  # Defaulting to null when the variable is empty lets us have an optional
  # variable without setting our own default.
  host = var.docker_socket != "" ? var.docker_socket : null
}

data "coder_provisioner" "me" {}
data "coder_workspace" "me" {}
data "coder_workspace_owner" "me" {}

resource "coder_agent" "main" {
  arch = data.coder_provisioner.me.arch
  os   = "linux"

  startup_script = <<-EOT
    set -e

    # Prepare user home with default files on first start.
    if [ ! -f ~/.init_done ]; then
      cp -rT /etc/skel ~
      touch ~/.init_done
    fi
  EOT

  shutdown_script = <<-EOT
    set -e

    # Clean up the Docker volume from unused resources to keep storage usage low.
    # WARNING! This removes all stopped containers, unused networks, images
    # without an associated container, and build cache.
    docker system prune -a -f

    # Stop the Docker service.
    sudo service docker stop
  EOT

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
    display_name = "CPU Usage"
    key          = "0_cpu_usage"
    script       = "coder stat cpu"
    interval     = 10
    timeout      = 1
  }

  metadata {
    display_name = "RAM Usage"
    key          = "1_ram_usage"
    script       = "coder stat mem"
    interval     = 10
    timeout      = 1
  }

  metadata {
    display_name = "Home Disk"
    key          = "3_home_disk"
    script       = "coder stat disk --path $${HOME}"
    interval     = 60
    timeout      = 1
  }

  metadata {
    display_name = "CPU Usage (Host)"
    key          = "4_cpu_usage_host"
    script       = "coder stat cpu --host"
    interval     = 10
    timeout      = 1
  }

  metadata {
    display_name = "Memory Usage (Host)"
    key          = "5_mem_usage_host"
    script       = "coder stat mem --host"
    interval     = 10
    timeout      = 1
  }
}

resource "coder_script" "init_docker_in_docker" {
  count        = data.coder_workspace.me.start_count
  agent_id     = coder_agent.main.id
  display_name = "Initialize Docker-in-Docker"
  run_on_start = true
  icon         = "/icon/docker.svg"
  script       = file("${path.module}/scripts/init-docker-in-docker.sh")
}

# See https://registry.coder.com/modules/coder/devcontainers-cli
module "devcontainers-cli" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/devcontainers-cli/coder"
  agent_id = coder_agent.main.id
  version  = "~> 1.0"
}

# See https://registry.coder.com/modules/coder/git-clone
module "git-clone" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/git-clone/coder"
  agent_id = coder_agent.main.id
  url      = data.coder_parameter.repo_url.value
  base_dir = "~"
  version  = "~> 2.0"
}

# Browser editor ("VS Code Web"): code-server runs in the workspace container
# and opens the same cloned repo folder that the devcontainer bind-mounts, so
# both editors see the same files.
module "code-server" {
  count        = data.coder_workspace.me.start_count
  source       = "registry.coder.com/coder/code-server/coder"
  version      = "~> 1.5"
  agent_id     = coder_agent.main.id
  folder       = "~/${module.git-clone[0].folder_name}"
  display_name = "VS Code Web"
  slug         = "code-server"
}

# Automatically start the devcontainer for the workspace.
resource "coder_devcontainer" "repo" {
  count            = data.coder_workspace.me.start_count
  agent_id         = coder_agent.main.id
  workspace_folder = "~/${module.git-clone[0].folder_name}"
}

resource "docker_volume" "home_volume" {
  name = "coder-${data.coder_workspace.me.id}-home"
  # Protect the volume from being deleted due to changes in attributes.
  lifecycle {
    ignore_changes = all
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
    label = "coder.workspace_name_at_creation"
    value = data.coder_workspace.me.name
  }
}

resource "docker_volume" "docker_volume" {
  name = "coder-${data.coder_workspace.me.id}-docker"
  # Protect the volume from being deleted due to changes in attributes.
  lifecycle {
    ignore_changes = all
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
    label = "coder.workspace_name_at_creation"
    value = data.coder_workspace.me.name
  }
}

resource "docker_container" "workspace" {
  count = data.coder_workspace.me.start_count
  image = local.workspace_image

  # Privileged mode is required for Docker-in-Docker, which the devcontainer
  # depends on. Mounting the host Docker socket instead is discouraged because
  # workspaces would then compete for control of the devcontainers.
  privileged = true

  # Uses lower() to avoid Docker restriction on container names.
  name = "coder-${data.coder_workspace_owner.me.name}-${lower(data.coder_workspace.me.name)}"
  # Hostname makes the shell more user friendly: coder@my-workspace:~$
  hostname = data.coder_workspace.me.name

  # The access URL serves a broken TLS cert, so the agent binary is fetched
  # over plain HTTP from the host gateway (the server listens on host:7080)
  # instead of coder_agent.main.init_script. CODER_AGENT_URL is pinned to
  # host.docker.internal so the init-docker-in-docker script sets up the
  # dnsmasq/NAT forwarding devcontainers need to reach the agent.
  command = [
    "/bin/sh", "-c",
    <<-EOT
    set -e
    for i in 1 2 3 4 5; do
        curl -fsSL http://host.docker.internal:7080/bin/coder-linux-amd64 -o /tmp/coder-agent && break
        sleep 5
    done
    if [ -s /tmp/coder-agent ]; then
        chmod +x /tmp/coder-agent
        # Expose the `coder` CLI (same binary) on PATH so agent metadata
        # scripts (`coder stat cpu/mem/disk`) resolve it; the agent inherits
        # this PATH and passes it to the scripts it executes.
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
    "CODER_AGENT_URL=http://host.docker.internal:7080",
  ]

  host {
    host = "host.docker.internal"
    ip   = "host-gateway"
  }

  # Workspace home volume persists user data across workspace restarts.
  volumes {
    container_path = "/home/coder"
    volume_name    = docker_volume.home_volume.name
    read_only      = false
  }

  # Workspace docker volume persists Docker data across workspace restarts,
  # allowing the devcontainer cache to be reused.
  volumes {
    container_path = "/var/lib/docker"
    volume_name    = docker_volume.docker_volume.name
    read_only      = false
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
}
