# Docus Nuxt documentation server.
# The shared-proxy Nginx proxies the public docs routes to this service.
FROM node:22-bookworm-slim

WORKDIR /workspace/docs/docus

COPY docs/docus/package*.json ./
RUN npm install --no-audit --no-fund

# Copy the full docs tree: docs/docus/ is the app, and the sibling markdown
# tree is the English content source that scripts/prepare-content.mjs walks
# (docsRoot = parent of docs/docus) to generate content/en/ at build time.
# Copying only docs/docus left /workspace/docs empty apart from docus/, so the
# English locale was never generated (content/en/ empty -> /docs/en 404).
COPY docs /workspace/docs
ENV NODE_ENV=production
ENV NUXT_APP_BASE_URL=/docs/
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

RUN npm run build

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
