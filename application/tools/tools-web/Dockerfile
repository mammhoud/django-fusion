# tools-web — vanilla Node.js server for tools.structa.cloud
# Serves the Alpine + htmx dashboard (public/) and the auth/unlock API.
# No build step: plain Node http server with bcryptjs + js-yaml.
#
# Build context: repository root (see docker-compose.yml)
# Runs on port 4321, proxied by tools-proxy Nginx.

FROM node:22-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=4321
ENV HOST=0.0.0.0

# Install dependencies (package.json only — no lockfile committed)
COPY application/tools/tools-web/package.json ./
RUN npm install --omit=dev --no-audit --no-fund

# Copy application
COPY application/tools/tools-web/server.mjs ./
COPY application/tools/tools-web/public ./public

# Users for the sign-in modal (bcrypt hashes)
COPY application/tools/tools-web/users.yml ./

EXPOSE 4321

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:4321/health/ || exit 1

CMD ["node", "server.mjs"]
