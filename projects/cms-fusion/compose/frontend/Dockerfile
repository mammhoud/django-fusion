# =============================================================================
# cms-fusion — Next.js frontend container
# Build context: project root (projects/cms-fusion)
# =============================================================================
FROM node:24-slim AS builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/. .
RUN npm run build

FROM node:24-slim AS runner
WORKDIR /app/frontend

COPY --from=builder /app/frontend/package*.json ./
COPY --from=builder /app/frontend/.next ./.next
COPY --from=builder /app/frontend/public ./public
COPY --from=builder /app/frontend/node_modules ./node_modules
COPY compose/frontend/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["npm", "run", "start"]
