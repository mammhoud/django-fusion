FROM node:24-slim

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --ignore-scripts && pnpm rebuild esbuild sharp
COPY frontend/. .

ENV HOST=0.0.0.0 \
    PORT=3000

EXPOSE 3000

# Build at startup (needs backend API), then serve the generated directory.
# Do not use `serve --single`: that SPA fallback maps every backend-owned
# route (about, previews, prompts, blog posts) back to the homepage.
CMD ["sh", "-c", "npm run build && npx --yes serve dist --listen tcp://0.0.0.0:3000 --no-clipboard"]
