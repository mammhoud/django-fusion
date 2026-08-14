# Docus Nuxt documentation server.
# The shared-proxy Nginx proxies the public docs routes to this service.
FROM node:22-bookworm-slim

WORKDIR /workspace/docs/docus

COPY docus/package*.json ./
RUN npm install --no-audit --no-fund

COPY . /workspace/docs
ENV NODE_ENV=production
ENV NUXT_APP_BASE_URL=/docs/
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

RUN npm run build

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
