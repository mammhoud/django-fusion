FROM node:22-bookworm-slim

WORKDIR /app

COPY projects/structa.cloud/frontend/package.json projects/structa.cloud/frontend/pnpm-workspace.yaml /app/
COPY projects/structa.cloud/frontend/ /app/

RUN corepack enable pnpm && pnpm install

RUN pnpm build

EXPOSE 3001

CMD ["pnpm", "start"]
