FROM node:24-slim

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Build context is the repository root (docker-compose.yml, context: ../..) so
# the local-library sources below are in scope — same pattern as the backend
# image, which COPYs libs /app/libs for django_fusion.
COPY projects/landing-fusion/frontend/package.json projects/landing-fusion/frontend/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --ignore-scripts && pnpm rebuild esbuild sharp

# fusion-js (the shared TS modules behind the `@fusion` alias in
# astro.config.mjs) lives in the django-fusion submodule at the repo base.
# The alias resolves to /libs/django-fusion/js/fusion-js/src relative to the
# Astro config, so place the package exactly there.
COPY libs/django-fusion/js/fusion-js /libs/django-fusion/js/fusion-js
COPY projects/landing-fusion/frontend/. .

ENV HOST=0.0.0.0 \
    PORT=3000

EXPOSE 3000

# Build at startup (needs backend API), then serve the generated directory.
# Do not use `serve --single`: that SPA fallback maps every backend-owned
# route (about, previews, prompts, blog posts) back to the homepage.
CMD ["sh", "-c", "npm run build && npx --yes serve dist --listen tcp://0.0.0.0:3000 --no-clipboard"]
