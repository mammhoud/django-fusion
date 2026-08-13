terraform {
  required_providers {
    coder  = { source = "coder/coder" }
    docker = { source = "kreuzwerker/docker" }
  }
}

# ============================================================
# Variables
# ============================================================
variable "project_path" {
  type        = string
  default     = "/home/structa.cloud"
  description = "Host path to the monorepo root"
}
variable "container_mount" {
  type        = string
  default     = "/app"
  description = "Container mount point for the monorepo"
}
variable "django_port" {
  type        = number
  default     = 8075
  description = "Django dev server port (8074 used by standalone landing-fusion)"
}
variable "postgres_host" {
  type        = string
  default     = "postgres"
  description = "PostgreSQL host"
}
variable "postgres_port" {
  type        = number
  default     = 5432
  description = "PostgreSQL port"
}
variable "postgres_user" {
  type        = string
  default     = "structa"
  description = "PostgreSQL user"
}
variable "postgres_password" {
  type        = string
  default     = "CTCreSearch0x@"
  sensitive   = true
  description = "PostgreSQL password"
}
variable "redis_host" {
  type        = string
  default     = "default-redis"
  description = "Redis host"
}
variable "redis_port" {
  type        = number
  default     = 6379
  description = "Redis port"
}
variable "docker_network" {
  type        = string
  default     = "common"
  description = "Docker network to attach to"
}
variable "code_server_url" {
  type        = string
  default     = "https://code.structa.cloud"
  description = "External code-server URL for the IDE button"
}

data "coder_workspace" "me" {}

# ============================================================
# Coder Agent
# ============================================================
resource "coder_agent" "main" {
  arch = "amd64"
  os   = "linux"

  metadata {
    key          = "django"
    display_name = "Django URL"
    script       = "echo http://localhost:${var.django_port}"
    interval     = 10
    timeout      = 3
  }
  metadata {
    key          = "database"
    display_name = "Database"
    script       = "echo postgres://${var.postgres_user}@${var.postgres_host}:${var.postgres_port}/${lower(data.coder_workspace.me.name)}"
    interval     = 30
    timeout      = 3
  }
}

# ============================================================
# Coder Apps
# ============================================================
resource "coder_app" "code-server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "code-server IDE"
  url          = "${var.code_server_url}?folder=${var.container_mount}"
  icon         = "/icon/code.svg"
  external     = true
}

resource "coder_app" "django" {
  agent_id     = coder_agent.main.id
  slug         = "django"
  display_name = "Django (${var.django_port})"
  url          = "http://localhost:${var.django_port}"
  icon         = "/icon/database.svg"
  share        = "authenticated"
}

# ============================================================
# Docker Image – built from the landing-fusion Dockerfile
# ============================================================
resource "docker_image" "django_wagtail" {
  name = "coder-website:${lower(data.coder_workspace.me.name)}"
  build {
    context    = var.project_path
    dockerfile = "projects/landing-fusion/backend/Dockerfile"
    tag        = ["coder-website:latest"]
  }
  triggers = {
    build_id = data.coder_workspace.me.id
  }
}

# ============================================================
# Main container – Django + Docker CLI + Coder agent
# ============================================================
resource "docker_container" "workspace" {
  image    = docker_image.django_wagtail.name
  name     = "coder-${lower(data.coder_workspace.me.name)}"
  hostname = lower(data.coder_workspace.me.name)

  # Mount the full monorepo so all projects/libs are available
  volumes {
    host_path      = var.project_path
    container_path = var.container_mount
  }
  # Docker socket for container management
  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  env = [
    "CODER_AGENT_TOKEN=${coder_agent.main.token}",
    "CODER_AGENT_URL=http://172.18.0.11:7080",
    "DATABASE_URL=postgresql://${var.postgres_user}:${replace(var.postgres_password, "@", "%40")}@${var.postgres_host}:${var.postgres_port}/${lower(data.coder_workspace.me.name)}",
    "REDIS_URL=redis://${var.redis_host}:${var.redis_port}/0",
    "DJANGO_SETTINGS_MODULE=settings",
    "DJANGO_DEBUG=1",
    "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*,0.0.0.0",
    "WAGTAIL_SITE_NAME=${lower(data.coder_workspace.me.name)}-dev",
    "WAGTAILADMIN_BASE_URL=http://localhost:${var.django_port}",
  ]

  ports {
    internal = var.django_port
    external = var.django_port
  }

  networks_advanced {
    name = var.docker_network
  }

  # Coder DNS resolution
  host {
    host = "coder.structa.cloud"
    ip   = "172.18.0.11"
  }

  # Run as root so docker.io install + migrations work
  entrypoint = [""]

  command = [
    "/bin/sh", "-c",
    <<-EOT
    set -e
    # Install Docker CLI
    apt-get update -qq && apt-get install -y -qq docker.io 2>/dev/null || true

    # Download & start Coder agent
    curl -fsSL http://172.18.0.11:7080/bin/coder-linux-amd64 -o /tmp/coder-agent
    chmod +x /tmp/coder-agent
    /tmp/coder-agent agent &

    # Wait for PostgreSQL
    echo "Waiting for PostgreSQL..."
    until pg_isready -h ${var.postgres_host} -p ${var.postgres_port} -U ${var.postgres_user} 2>/dev/null; do
      sleep 2
    done

    # Create database if not exists
    PGPASSWORD=${var.postgres_password} psql \
      -h ${var.postgres_host} -p ${var.postgres_port} \
      -U ${var.postgres_user} -d postgres \
      -c "CREATE DATABASE ${lower(data.coder_workspace.me.name)} OWNER ${var.postgres_user};" 2>/dev/null || true

    # Run Django migrations
    cd ${var.container_mount}/landing-fusion/backend
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput 2>/dev/null || true

    echo "Django ready at http://localhost:${var.django_port}"
    exec python manage.py runserver 0.0.0.0:${var.django_port}
    EOT
  ]

  healthcheck {
    test         = ["CMD-SHELL", "curl -f http://localhost:${var.django_port}/ || exit 1"]
    interval     = "10s"
    timeout      = "5s"
    retries      = 5
    start_period = "90s"
  }

  must_run              = true
  destroy_grace_seconds = 15
}
