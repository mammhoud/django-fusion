# =============================================================================
# Structa Cloud — full monorepo devcontainer image
# =============================================================================
# Pre-bakes every toolchain the monorepo needs so the devcontainer is complete
# on first boot (no feature installs or long postCreateCommand):
#
#   Node 22 LTS + npm 11 (root package.json packageManager)
#   pnpm, tsx, astro, bun, yarn, nodemon (global CLIs used across projects)
#   Python 3.11 + uv (root + projects pyproject.toml, Django/Wagtail/django-fusion)
#   Rust stable + Tauri v2 system libraries (formints Tauri editions)
#   Docker CLI + compose plugin (the daemon comes from the docker-in-docker
#   feature in devcontainer.json)
#
# Base: official VS Code devcontainer TypeScript/Node image (Debian bookworm).
# =============================================================================

ARG NODE_VARIANT=22-bookworm
FROM mcr.microsoft.com/devcontainers/typescript-node:1-${NODE_VARIANT}

# Shared homes so both root (build) and the vscode user (runtime) can use them.
ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH="/usr/local/cargo/bin:/usr/local/bin:$PATH"

USER root

# ---------------------------------------------------------------------------
# System packages
# ---------------------------------------------------------------------------
# Tauri v2 (formint-* editions) needs webkit2gtk-4.1 + GTK3 toolchain; the
# Django/Wagtail workspace (uv) builds native wheels, so we also install
# python dev headers, libpq (psycopg), libxml2/libxslt (lxml), and libffi.
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends \
        build-essential pkg-config file curl wget git ca-certificates gnupg \
        libwebkit2gtk-4.1-dev libgtk-3-dev libayatana-appindicator3-dev \
        librsvg2-dev libsoup-3.0-dev libjavascriptcoregtk-4.1-dev \
        libssl-dev libpq-dev libffi-dev libxml2-dev libxslt1-dev \
        python3 python3-pip python3-venv make \
        zsh fonts-powerline \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Oh My Zsh (installed for root; the non-root `node` user gets it below)
# ---------------------------------------------------------------------------
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
    && sed -i 's/^ZSH_THEME=.*/ZSH_THEME="af-magic"/' /root/.zshrc \
    && echo 'plugins=(git python pip docker docker-compose)' >> /root/.zshrc

# ---------------------------------------------------------------------------
# Docker CLI + compose plugin (static binaries; daemon via docker-in-docker)
# ---------------------------------------------------------------------------
# Keeps the Dockerfile self-contained (works with a bare `docker build` too).
# The docker-in-docker feature in devcontainer.json adds the daemon + socket.
# NOTE: the Docker static channel moved from `amd64` to `x86_64` for recent
# releases, and Compose is at v5.x — versions below (verified live) 404 on the
# old paths. TARGETARCH (amd64/arm64) maps to the channel layout (x86_64/aarch64).
ARG TARGETARCH
ARG DOCKER_VERSION=29.6.1
ARG DOCKER_COMPOSE_VERSION=5.4.0
RUN set -eux; \
    case "${TARGETARCH}" in \
        amd64) static_arch="x86_64" ;; \
        arm64) static_arch="aarch64" ;; \
        *) static_arch="${TARGETARCH}" ;; \
    esac; \
    curl -fsSL "https://download.docker.com/linux/static/stable/${static_arch}/docker-${DOCKER_VERSION}.tgz" \
        | tar -xz -C /usr/local/bin --strip-components=1 docker/docker; \
    mkdir -p /usr/local/lib/docker/cli-plugins; \
    curl -fsSL "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-linux-${static_arch}" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose; \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose; \
    docker --version && docker compose version

# ---------------------------------------------------------------------------
# Node toolchain — global CLIs used across the monorepo
# ---------------------------------------------------------------------------
# npm 11 matches the root package.json packageManager. pnpm/tsx/astro/bun/
# yarn/nodemon are the CLIs referenced by precis-landing, precis, formints,
# and repo scripts.
RUN npm install -g npm@11 pnpm@latest tsx astro@latest bun yarn nodemon \
    && npm cache clean --force

# ---------------------------------------------------------------------------
# Python 3.11 + uv  (root pyproject.toml + projects/pyproject.toml)
# ---------------------------------------------------------------------------
# .python-version pins 3.11. uv is installed via its official installer so
# `uv sync` / `uv run` work for the Django/Wagtail/django-fusion workspace.
ARG UV_VERSION=latest
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh \
    && uv --version

# ---------------------------------------------------------------------------
# Rust stable + Tauri v2 (formints desktop editions)
# ---------------------------------------------------------------------------
# The Tauri editions (formint-community/standard/pro/client) build Linux
# bundles with webkit2gtk; rustup default profile is enough for cargo build.
ARG RUST_TOOLCHAIN=stable
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- \
        -y --profile default --default-toolchain ${RUST_TOOLCHAIN} \
    && rustc --version && cargo --version

# ---------------------------------------------------------------------------
# Finalize — hand shared homes + workspace dir to the non-root user
# ---------------------------------------------------------------------------
# The typescript-node base image's non-root user is `node` (UID 1000), not
# `vscode`. The devcontainer attaches as root so the root-owned host bind mount
# remains writable; the image still verifies its non-root toolchain at build.
RUN chown -R node:node /usr/local/cargo /usr/local/rustup /usr/local/lib/docker \
    && mkdir -p /workspaces && chown -R node:node /workspaces

# ---------------------------------------------------------------------------
# Oh My Zsh for the non-root `node` user
# ---------------------------------------------------------------------------
USER node
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
    && sed -i 's/^ZSH_THEME=.*/ZSH_THEME="af-magic"/' ~/.zshrc \
    && echo 'plugins=(git python pip docker docker-compose node)' >> ~/.zshrc

WORKDIR /workspaces/structa.cloud

# Verify the full toolchain is present (fails the build if anything is missing).
RUN set -eux; \
    for cli in node npm pnpm tsx astro bun yarn nodemon uv docker python3 cargo rustc; do \
        command -v "$cli" >/dev/null 2>&1 || { echo "MISSING: $cli"; exit 1; }; \
    done; \
    echo "devcontainer toolchain OK"
