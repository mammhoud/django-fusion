# Docus Nuxt documentation server.
# The shared-proxy Nginx proxies the public docs routes to this service.
# The Docus app lives at the root of docs/ (flattened from docs/docus/):
# the app files (nuxt.config.ts, package.json, scripts/) sit next to the
# authored markdown tree that scripts/prepare-content.mjs walks to generate
# content/en/ at build time.
FROM node:22-bookworm-slim

WORKDIR /workspace/docs

COPY docs/package*.json ./
RUN npm install --no-audit --no-fund

# Copy the full docs tree: the Docus app and the authored markdown source
# (scripts/prepare-content.mjs resolves the docs root as its own parent).
COPY docs /workspace/docs
ENV NODE_ENV=production
ENV NUXT_APP_BASE_URL=/docs/
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

RUN npm run build

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]