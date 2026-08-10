# =============================================================================
# dev-stack — Coder Template
# =============================================================================
# Multi-service development workspace with:
#   • code-server  (IDE)          → port 8086
#   • Blinko       (AI notes)     → port 1111
#
# ⚠️  WORKSPACE NAME CONSTRAINT:
# The Traefik dynamic configs (applications/proxy/traefik/dynamic/) hardcode
# container names "coder-dev-code-server" and "coder-dev-blinko". This template
# MUST be used with a Coder workspace named exactly "dev", otherwise external
# routing via code.structa.cloud and blinko.structa.cloud will break.
# =============================================================================
# Docker images used:
#   codercom/code-server:4.131.0    — Web-based VS Code IDE
#   blinkospace/blinko:latest       — AI-powered personal note-taking tool
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
  default     = "4.131.0"
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
variable "blinko_port" {
  type        = number
  default     = 1111
  description = "Blinko HTTP port"
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
variable "postgres_host" {
  type        = string
  default     = "postgres"
  description = "PostgreSQL host for Blinko database"
}
variable "postgres_port" {
  type        = number
  default     = 5432
  description = "PostgreSQL port"
}
variable "postgres_password" {
  type        = string
  default     = "CTCreSearch0x@"
  sensitive   = true
  description = "PostgreSQL password for Blinko database"
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
    key          = "blinko"
    display_name = "Blinko"
    script       = "echo http://localhost:${var.blinko_port}"
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

resource "coder_app" "blinko" {
  agent_id     = coder_agent.main.id
  slug         = "blinko"
  display_name = "Blinko (Notes)"
  url          = "http://blinko.local:${var.blinko_port}"
  icon         = "/icon/database.svg"
  share        = "authenticated"
}

# ============================================================
# Docker Images
# ============================================================
resource "docker_image" "code_server" {
  name = "codercom/code-server:${var.code_server_version}"
}

resource "docker_image" "blinko_image" {
  name = "blinkospace/blinko:latest"
}

# ============================================================
# code-server container  (hosts the Coder agent + IDE)
# ============================================================
resource "docker_container" "code_server" {
  image    = docker_image.code_server.name
  # Container name MUST resolve to "coder-dev-code-server" for Traefik routing.
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

  # Route coder.structa.cloud through Traefik (port 443) for health checks
  # Agent binary download still uses direct IP http://coder_host_ip:7080
  host {
    host = "coder.structa.cloud"
    ip   = "127.0.0.1"
  }
  # Force IPv4 for sibling containers — Go proxy prefers IPv6
  host {
    host = "blinko.local"
    ip   = docker_container.blinko.network_data[0].ip_address
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
    npm install -g npm@latest 2>/dev/null
    curl -fsSL http://${var.coder_host_ip}:7080/bin/coder-linux-amd64 -o /tmp/coder-agent
    chmod +x /tmp/coder-agent
    /tmp/coder-agent agent &
    exec /usr/bin/entrypoint.sh --bind-addr 0.0.0.0:${var.code_server_port} --auth password .
    EOT
  ]

  healthcheck {
    test     = ["CMD-SHELL", "wget -q --spider http://localhost:${var.code_server_port}/ || exit 1"]
    interval = "15s"
    timeout  = "5s"
    retries  = 3
    start_period = "60s"
  }

  lifecycle {
    precondition {
      condition     = lower(data.coder_workspace.me.name) == "dev"
      error_message = <<-EOT
        This template requires the Coder workspace to be named "dev".
        Traefik dynamic configs hardcode container names coder-dev-code-server
        and coder-dev-blinko. A workspace named "${data.coder_workspace.me.name}"
        would produce containers that Traefik cannot route to.

        Action: delete this workspace and recreate it with the name "dev".
      EOT
    }
  }

  must_run              = true
  destroy_grace_seconds = 10
}

# ============================================================
# Blinko — AI-powered personal note-taking
# ============================================================
resource "docker_container" "blinko" {
  image = docker_image.blinko_image.name
  # Container name MUST resolve to "coder-dev-blinko" for Traefik routing.
  # See workspace name constraint in the header block above.
  name  = "coder-${lower(data.coder_workspace.me.name)}-blinko"

  env = [
    "NODE_ENV=production",
    "NEXTAUTH_SECRET=CTCreSearch0x@",
    "NEXTAUTH_URL=https://blinko.structa.cloud",
    "NEXT_PUBLIC_BASE_URL=https://blinko.structa.cloud",
    "DATABASE_URL=postgresql://structa:${replace(var.postgres_password, "@", "%40")}@${var.postgres_host}:${var.postgres_port}/blinko",
  ]

  volumes {
    host_path      = "${var.workspace_mount}/.blinko-data-${lower(data.coder_workspace.me.name)}"
    container_path = "/app/.blinko"
  }

  ports {
    internal = var.blinko_port
    external = var.blinko_port
  }

  networks_advanced {
    name = var.docker_network
  }

  healthcheck {
    test     = ["CMD-SHELL", "wget -q --spider http://localhost:${var.blinko_port}/ || exit 1"]
    interval = "15s"
    timeout  = "5s"
    retries  = 3
    start_period = "30s"
  }

  must_run              = true
  destroy_grace_seconds = 5
}
