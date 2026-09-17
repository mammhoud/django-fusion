FROM node:20-alpine AS dependencies
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=dependencies /app/node_modules ./node_modules
COPY package.json server.mjs ./
COPY public ./public
EXPOSE 1111
CMD ["node", "server.mjs"]
