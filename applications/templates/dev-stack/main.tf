# =============================================================================
# dev-stack — Coder Template
# =============================================================================
# Multi-service development workspace with:
#   • code-server  (IDE)            → port 8086
#   • FileGator    (file manager)   → internal 8080 / published 1111
#
# ⚠️  WORKSPACE NAME CONSTRAINT:
# The proxy configs (applications/proxy/traefik/dynamic/ + nginx) hardcode
# container names "coder-dev-code-server" and "coder-dev-filegator". This
# template MUST be used with a Coder workspace named exactly "dev", otherwise
# external routing via code.structa.cloud and filegator.structa.cloud will
# break.
# =============================================================================
# Docker images used:
#   codercom/code-server:4.132.0   — Web-based VS Code IDE
#   filegator/filegator:latest     — Self-hosted file manager
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
variable "code_server_version" {
  type        = string
  default     = "4.132.0"
  description = "code-server image version"
}
variable "code_server_port" {
  type        = number
  default     = 8086
  description = "code-server HTTP port"
}
variable "code_server_password" {
  type        = string
  default     = "CTCreSearch0x@"
  sensitive   = true
  description = "code-server login password"
}
variable "filegator_port" {
  type        = number
  default     = 1111
  description = "FileGator published host port (the container listens on 8080 internally)"
}
variable "workspace_mount" {
  type        = string
  default     = "/home/structa.cloud"
  description = "Host monorepo path"
}
variable "container_mount" {
  type        = string
  default     = "/home/coder/project"
  description = "Container mount point"
}
variable "docker_network" {
  type        = string
  default     = "common"
  description = "Docker network name"
}
variable "coder_host_ip" {
  type        = string
  default     = "172.18.0.11"
  description = "Coder container IP on common network"
}

data "coder_workspace" "me" {}

# ============================================================
# Coder Agent  (runs inside code-server container)
# ============================================================
resource "coder_agent" "main" {
  arch = "amd64"
  os   = "linux"

  metadata {
    key          = "code-server"
    display_name = "code-server"
    script       = "echo http://localhost:${var.code_server_port}/?folder=${var.container_mount}"
    interval     = 10
    timeout      = 3
  }
  metadata {
    key          = "filegator"
    display_name = "FileGator"
    script       = "echo http://filegator.local:8080"
    interval     = 10
    timeout      = 3
  }
}

# ============================================================
# Coder Apps  (shown in workspace UI)
# ============================================================
resource "coder_app" "code-server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "code-server IDE"
  url          = "http://localhost:${var.code_server_port}/?folder=${var.container_mount}"
  icon         = "/icon/code.svg"
  share        = "authenticated"
}

resource "coder_app" "filegator" {
  agent_id     = coder_agent.main.id
  slug         = "filegator"
  display_name = "FileGator (Files)"
  url          = "http://filegator.local:8080"
  icon         = "/icon/folder.svg"
  share        = "authenticated"
}

# ============================================================
# Docker Images
# ============================================================
resource "docker_image" "code_server" {
  name = "codercom/code-server:${var.code_server_version}"
}

resource "docker_image" "filegator_image" {
  name = "filegator/filegator:latest"
}

# ============================================================
# code-server container  (hosts the Coder agent + IDE)
# ============================================================
resource "docker_container" "code_server" {
  image = docker_image.code_server.name
  # Container name MUST resolve to "coder-dev-code-server" for proxy routing.
  # See workspace name constraint in the header block above.
  name     = "coder-${lower(data.coder_workspace.me.name)}-code-server"
  hostname = lower(data.coder_workspace.me.name)

  volumes {
    host_path      = var.workspace_mount
    container_path = var.container_mount
  }
  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  env = [
    "CODER_AGENT_TOKEN=${coder_agent.main.token}",
    "CODER_AGENT_URL=http://${var.coder_host_ip}:7080",
    "PASSWORD=${var.code_server_password}",
  ]

  ports {
    internal = var.code_server_port
    external = var.code_server_port
  }

  networks_advanced {
    name = var.docker_network
  }

  # Route code.structa.cloud through Traefik → shared-media nginx (port 443)
  # for health checks. Agent binary download still uses direct IP
  # http://coder_host_ip:7080
  host {
    host = "code.structa.cloud"
    ip   = "127.0.0.1"
  }
  # Force IPv4 for sibling containers — Go proxy prefers IPv6
  host {
    host = "filegator.local"
    ip   = docker_container.filegator.network_data[0].ip_address
  }

  user       = "root"
  entrypoint = [""]

  command = [
    "/bin/sh", "-c",
    <<-EOT
    set -e
    apt-get update -qq && apt-get install -y -qq docker.io curl 2>/dev/null
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
    apt-get install -y -qq nodejs 2>/dev/null
    # npm CLIs below are non-fatal: a registry hiccup must not abort the
    # entrypoint before the Coder agent starts (set -e + 2>/dev/null would
    # otherwise kill the whole container on a failed install). Failures are
    # still logged via the || echo fallback.
    npm install -g npm@latest 2>/dev/null || echo "npm@latest install skipped"
    # pnpm — repo-standard package manager (landing-fusion frontend + all
    # formints editions use pnpm-lock.yaml); available as a shell CLI.
    npm install -g pnpm@latest 2>/dev/null || echo "pnpm install skipped"
    # Extra shell CLIs — node tooling for the Astro/TS projects and scripts:
    #   tsx     run TypeScript files directly (repo scripts are TS-heavy)
    #   yarn    classic yarn CLI for any yarn.lock projects
    #   astro   the Astro CLI for the landing-fusion / precis frontends
    #   nodemon auto-restart Node scripts on file changes
    #   bun     Bun runtime + package manager (bun.lock projects)
    npm install -g tsx yarn nodemon 2>/dev/null || echo "tsx/yarn/nodemon install skipped"
    npm install -g astro@latest 2>/dev/null || echo "astro install skipped"
    npm install -g bun 2>/dev/null || echo "bun install skipped"
    # Log which shell CLIs actually landed so a silenced failure is visible
    # in `docker logs coder-dev-code-server`.
    for cli in node npm pnpm tsx yarn astro nodemon bun docker curl; do
        command -v "$cli" >/dev/null 2>&1 && echo "$cli OK" || echo "$cli MISSING"
    done
    curl -fsSL http://${var.coder_host_ip}:7080/bin/coder-linux-amd64 -o /tmp/coder-agent
    chmod +x /tmp/coder-agent
    /tmp/coder-agent agent &
    exec /usr/bin/entrypoint.sh --bind-addr 0.0.0.0:${var.code_server_port} --auth password .
    EOT
  ]

  healthcheck {
    test         = ["CMD-SHELL", "wget -q --spider http://localhost:${var.code_server_port}/ || exit 1"]
    interval     = "15s"
    timeout      = "5s"
    retries      = 3
    # Generous grace for the node/npm global CLI installs (3 extra npm
    # invocations can add 30-60s on a cold registry pull).
    start_period = "120s"
  }

  lifecycle {
    precondition {
      # "default" is Coder's placeholder workspace name used by the template
      # import/plan dry-run (`coder templates push` validates the plan against
      # a synthetic workspace named default). Tolerate only that synthetic
      # name so template pushes keep working; any other non-dev name still
      # fails because the proxy cannot route to its containers.
      condition     = contains(["dev", "default"], lower(data.coder_workspace.me.name))
      error_message = <<-EOT
        This template requires the Coder workspace to be named "dev".
        Proxy configs hardcode container names coder-dev-code-server and
        coder-dev-filegator. A workspace named "${data.coder_workspace.me.name}"
        would produce containers that the proxy cannot route to.

        Action: delete this workspace and recreate it with the name "dev".
      EOT
    }
  }

  must_run              = true
  destroy_grace_seconds = 10
}

# ============================================================
# FileGator — self-hosted file manager (replaces Blinko)
# ============================================================
# Workspace-scoped file manager served at https://filegator.structa.cloud
# (Traefik → shared-media nginx → coder-dev-filegator:8080). Uploads land in
# a per-workspace repository dir under the host monorepo, so the data is
# scoped per-workspace like the old Blinko data. Auth + hardened config are
# the same version-controlled files the host-level FileGator uses
# (applications/proxy/filegator/), bind-mounted read-only.
resource "docker_container" "filegator" {
  image = docker_image.filegator_image.name
  # Container name MUST resolve to "coder-dev-filegator" for proxy routing.
  # See workspace name constraint in the header block above.
  name = "coder-${lower(data.coder_workspace.me.name)}-filegator"

  volumes {
    host_path      = "${var.workspace_mount}/.filegator-data-${lower(data.coder_workspace.me.name)}/repository"
    container_path = "/var/www/filegator/repository"
  }
  volumes {
    host_path      = "${var.workspace_mount}/applications/proxy/filegator/configuration.php"
    container_path = "/var/www/filegator/configuration.php"
    read_only      = true
  }
  volumes {
    host_path      = "${var.workspace_mount}/applications/proxy/filegator/users.json"
    container_path = "/var/www/filegator/private/users.json"
    read_only      = true
  }

  ports {
    internal = 8080
    external = var.filegator_port
  }

  networks_advanced {
    name = var.docker_network
  }

  healthcheck {
    test         = ["CMD-SHELL", "curl -fsS http://localhost:8080/ || exit 1"]
    interval     = "15s"
    timeout      = "5s"
    retries      = 3
    start_period = "20s"
  }

  must_run              = true
  destroy_grace_seconds = 5
}
