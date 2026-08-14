# =============================================================================
# dev-workspace — Coder Template
# =============================================================================
# Multi-service development workspace with:
#   • code-server  (IDE)            → internal 8086 / Coder app only
#   • FileGator    (file manager)   → internal 8080 / proxy only
#   • AppFlowy     (workspace)      → internal web/API services / Coder app only
#
# The workspace services no longer publish fixed host ports or use public
# code-server/Blinko subdomains. This prevents collisions such as the old
# 0.0.0.0:1111 bind failure; Coder app proxying and the existing FileGator
# route are the supported access paths.
#
# ⚠️  WORKSPACE NAME CONSTRAINT:
# The shared FileGator proxy still targets coder-dev-filegator. This template
# MUST be used with a Coder workspace named exactly "dev", otherwise that
# external FileGator route will not resolve.
# =============================================================================
# Docker images used:
#   codercom/code-server:4.132.0       — Web-based VS Code IDE
#   filegator/filegator:latest         — Self-hosted file manager
#   appflowyinc/appflowy_cloud:latest  — AppFlowy Cloud API
#   appflowyinc/appflowy_web:latest    — AppFlowy web client
#   appflowyinc/gotrue:latest          — AppFlowy authentication service
#   minio/minio:latest                 — Internal AppFlowy object storage (S3)
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
variable "appflowy_cloud_version" {
  type        = string
  default     = "latest"
  description = "AppFlowy Cloud API image version"
}
variable "appflowy_web_version" {
  type        = string
  default     = "latest"
  description = "AppFlowy web client image version"
}
variable "appflowy_gotrue_version" {
  type        = string
  default     = "latest"
  description = "AppFlowy GoTrue authentication image version"
}
variable "appflowy_database_url" {
  type        = string
  sensitive   = true
  default     = "postgres://appflowy:appflowy@postgres:5432/appflowy"
  description = "AppFlowy Cloud PostgreSQL URL; override with the deployment secret"
}
variable "appflowy_gotrue_database_url" {
  type        = string
  sensitive   = true
  default     = "postgres://appflowy:appflowy@postgres:5432/appflowy"
  description = "AppFlowy GoTrue PostgreSQL URL; override with the deployment secret"
}
variable "appflowy_jwt_secret" {
  type        = string
  sensitive   = true
  default     = "change-me-in-coder"
  description = "AppFlowy JWT signing secret; override before production use"
}
variable "appflowy_redis_uri" {
  type        = string
  sensitive   = true
  default     = "redis://:redis_password@default-redis:6379/3"
  description = "Authenticated Redis URI for AppFlowy Cloud"
}
variable "appflowy_admin_email" {
  type        = string
  default     = "admin@structa.cloud"
  description = "Initial AppFlowy administrator email"
}
variable "appflowy_admin_password" {
  type        = string
  sensitive   = true
  default     = "change-me-in-coder"
  description = "Initial AppFlowy administrator password"
}
variable "appflowy_s3_access_key" {
  type        = string
  sensitive   = true
  default     = "appflowy"
  description = "Internal MinIO access key for AppFlowy"
}
variable "appflowy_s3_secret_key" {
  type        = string
  sensitive   = true
  default     = "change-me-in-coder"
  description = "Internal MinIO secret key for AppFlowy"
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
  description = "Shared Docker network for proxy and workspace services"
}
variable "database_network" {
  type        = string
  default     = "warehouse-net"
  description = "External Docker network attached to the shared PostgreSQL service"
}
variable "coder_host_ip" {
  type        = string
  default     = "172.18.0.16"
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

resource "coder_app" "appflowy" {
  agent_id     = coder_agent.main.id
  slug         = "appflowy"
  display_name = "AppFlowy Workspace"
  url          = "http://coder-${lower(data.coder_workspace.me.name)}-appflowy-web:80"
  icon         = "/icon/desktop.svg"
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

resource "docker_image" "appflowy_cloud_image" {
  name = "appflowyinc/appflowy_cloud:${var.appflowy_cloud_version}"
}

resource "docker_image" "appflowy_web_image" {
  name = "appflowyinc/appflowy_web:${var.appflowy_web_version}"
}

resource "docker_image" "appflowy_gotrue_image" {
  name = "appflowyinc/gotrue:${var.appflowy_gotrue_version}"
}

resource "docker_image" "appflowy_minio_image" {
  name = "minio/minio:latest"
}

# ============================================================
# code-server container  (hosts the Coder agent + IDE)
# ============================================================
resource "docker_container" "code_server" {
  image = docker_image.code_server.name
  # The name remains stable for Coder diagnostics; it is not a public proxy
  # target anymore.
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

  # Do not publish the IDE port. The authenticated Coder app is the only
  # supported access path, which avoids host-port collisions and removes the
  # old code-server public subdomain dependency.

  networks_advanced {
    name = var.docker_network
  }

  # Force IPv4 for sibling containers — Go proxy prefers IPv6. These aliases
  # are internal workspace conveniences only; no public code-server/AppFlowy
  # subdomain is configured.
  host {
    host = "filegator.local"
    ip   = docker_container.filegator.network_data[0].ip_address
  }
  host {
    host = "appflowy.local"
    ip   = docker_container.appflowy_web.network_data[0].ip_address
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
    test     = ["CMD-SHELL", "wget -q --spider http://localhost:${var.code_server_port}/ || exit 1"]
    interval = "15s"
    timeout  = "5s"
    retries  = 3
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
      # fails because the FileGator proxy cannot route to its container.
      condition     = contains(["dev", "default"], lower(data.coder_workspace.me.name))
      error_message = <<-EOT
        This template requires the Coder workspace to be named "dev".
        The FileGator proxy targets coder-dev-filegator. A workspace named
        "${data.coder_workspace.me.name}" would produce a container that the
        proxy cannot route to.

        Action: delete this workspace and recreate it with the name "dev".
      EOT
    }
  }

  must_run              = true
  destroy_grace_seconds = 10
}

# ============================================================
# FileGator — self-hosted file manager (alongside AppFlowy)
# ============================================================
# Workspace-scoped file manager served at https://filegator.structa.cloud
# (Traefik → shared-media nginx → coder-dev-filegator:8080). Uploads land in
# a per-workspace repository dir under the host monorepo, so the data is
# scoped per-workspace like the AppFlowy data. Auth + hardened config are
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

  # Do not publish 8080. The shared-media proxy reaches FileGator over the
  # common network, and Coder port forwarding handles workspace access. A
  # published host port caused the previous 0.0.0.0:1111 collision.

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

# ============================================================
# AppFlowy Cloud — internal workspace stack
# ============================================================
# The former Blinko resource is intentionally retired. AppFlowy Cloud is a
# multi-service application. The official deployment uses
# GoTrue, the Rust API, the web client, Redis, PostgreSQL, and S3-compatible
# storage. This template reuses the shared PostgreSQL/Redis networks and keeps
# every AppFlowy service internal: there are no host ports and no public
# AppFlowy or Blinko subdomain. The authenticated Coder app is the access path.
resource "docker_container" "appflowy_minio" {
  image = docker_image.appflowy_minio_image.name
  name  = "coder-${lower(data.coder_workspace.me.name)}-appflowy-minio"

  env = [
    "MINIO_ROOT_USER=${var.appflowy_s3_access_key}",
    "MINIO_ROOT_PASSWORD=${var.appflowy_s3_secret_key}",
  ]

  command = ["server", "/data", "--console-address", ":9001"]

  volumes {
    host_path      = "${var.workspace_mount}/.appflowy-data-${lower(data.coder_workspace.me.name)}/minio"
    container_path = "/data"
  }

  networks_advanced {
    name = var.docker_network
  }

  healthcheck {
    test         = ["CMD-SHELL", "curl -fsS http://127.0.0.1:9000/minio/health/live || exit 1"]
    interval     = "15s"
    timeout      = "5s"
    retries      = 5
    start_period = "20s"
  }

  must_run              = true
  destroy_grace_seconds = 10
}

resource "docker_container" "appflowy_gotrue" {
  image = docker_image.appflowy_gotrue_image.name
  name  = "coder-${lower(data.coder_workspace.me.name)}-appflowy-gotrue"

  env = [
    "GOTRUE_ADMIN_EMAIL=${var.appflowy_admin_email}",
    "GOTRUE_ADMIN_PASSWORD=${var.appflowy_admin_password}",
    "GOTRUE_DISABLE_SIGNUP=false",
    "GOTRUE_SITE_URL=appflowy://",
    "GOTRUE_URI_ALLOW_LIST=**",
    "GOTRUE_JWT_SECRET=${var.appflowy_jwt_secret}",
    "GOTRUE_JWT_EXP=3600",
    "GOTRUE_JWT_ADMIN_GROUP_NAME=supabase_admin",
    "GOTRUE_DB_DRIVER=postgres",
    "DATABASE_URL=${var.appflowy_gotrue_database_url}",
    "GOTRUE_DB_DATABASE_URL=${var.appflowy_gotrue_database_url}",
    "API_EXTERNAL_URL=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-gotrue:9999",
    "PORT=9999",
    "GOTRUE_MAILER_AUTOCONFIRM=true",
  ]

  networks_advanced {
    name = var.docker_network
  }
  networks_advanced {
    name = var.database_network
  }

  healthcheck {
    test         = ["CMD", "curl", "--fail", "http://127.0.0.1:9999/health"]
    interval     = "15s"
    timeout      = "5s"
    retries      = 8
    start_period = "40s"
  }

  must_run              = true
  destroy_grace_seconds = 10
}

resource "docker_container" "appflowy_cloud" {
  image = docker_image.appflowy_cloud_image.name
  name  = "coder-${lower(data.coder_workspace.me.name)}-appflowy-cloud"

  env = [
    "RUST_LOG=info",
    "APPFLOWY_ENVIRONMENT=production",
    "APPFLOWY_DATABASE_URL=${var.appflowy_database_url}",
    "APPFLOWY_REDIS_URI=${var.appflowy_redis_uri}",
    "APPFLOWY_GOTRUE_JWT_SECRET=${var.appflowy_jwt_secret}",
    "APPFLOWY_GOTRUE_BASE_URL=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-gotrue:9999",
    "APPFLOWY_S3_CREATE_BUCKET=true",
    "APPFLOWY_S3_USE_MINIO=true",
    "APPFLOWY_S3_MINIO_URL=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-minio:9000",
    "APPFLOWY_S3_ACCESS_KEY=${var.appflowy_s3_access_key}",
    "APPFLOWY_S3_SECRET_KEY=${var.appflowy_s3_secret_key}",
    "APPFLOWY_S3_BUCKET=appflowy",
    "APPFLOWY_S3_REGION=us-east-1",
    "APPFLOWY_S3_PRESIGNED_URL_ENDPOINT=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-minio:9000",
    "APPFLOWY_WEB_URL=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-web:80",
    "APPFLOWY_BASE_URL=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-web:80",
    "APPFLOWY_ACCESS_CONTROL=private",
    "AI_ENABLED=false",
  ]

  networks_advanced {
    name = var.docker_network
  }
  networks_advanced {
    name = var.database_network
  }

  depends_on = [docker_container.appflowy_gotrue, docker_container.appflowy_minio]

  healthcheck {
    test         = ["CMD", "curl", "--fail", "http://127.0.0.1:8000/api/health"]
    interval     = "15s"
    timeout      = "5s"
    retries      = 8
    start_period = "45s"
  }

  must_run              = true
  destroy_grace_seconds = 10
}

resource "docker_container" "appflowy_web" {
  image = docker_image.appflowy_web_image.name
  name  = "coder-${lower(data.coder_workspace.me.name)}-appflowy-web"

  env = [
    "APPFLOWY_BASE_URL=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-web:80",
    "APPFLOWY_GOTRUE_BASE_URL=http://coder-${lower(data.coder_workspace.me.name)}-appflowy-gotrue:9999",
    "APPFLOWY_WS_BASE_URL=ws://coder-${lower(data.coder_workspace.me.name)}-appflowy-cloud:8000",
  ]

  networks_advanced {
    name = var.docker_network
  }

  depends_on = [docker_container.appflowy_cloud]

  healthcheck {
    test         = ["CMD-SHELL", "wget -q --spider http://127.0.0.1/ || exit 1"]
    interval     = "15s"
    timeout      = "5s"
    retries      = 8
    start_period = "45s"
  }

  must_run              = true
  destroy_grace_seconds = 10
}
