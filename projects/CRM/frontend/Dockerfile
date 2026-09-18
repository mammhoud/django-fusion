FROM node:22-alpine AS build

WORKDIR /app

COPY projects/loop-crm/frontend/package.json projects/loop-crm/frontend/package-lock.json ./
RUN npm ci

# The Astro alias references the shared Fusion frontend modules at build time.
COPY libs/django-fusion/js/fusion-js /libs/django-fusion/js/fusion-js
COPY projects/loop-crm/frontend/astro.config.mjs ./astro.config.mjs
COPY projects/loop-crm/frontend/tsconfig.json ./tsconfig.json
COPY projects/loop-crm/frontend/src ./src
COPY projects/loop-crm/frontend/public ./public

ARG PUBLIC_SITE_URL=https://crm.structa.cloud
ENV PUBLIC_SITE_URL=${PUBLIC_SITE_URL}

RUN npm run build

FROM nginx:1.27-alpine

RUN apk add --no-cache curl
COPY projects/loop-crm/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
