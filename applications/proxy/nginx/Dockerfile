# Shared-media Nginx — static/media server + reverse proxy for Docus,
# permanent AFFiNE, and FileGator. AFFiNE is served at the root of
# space.structa.cloud; FileGator is available under /files/ and files.structa.cloud.
#
# The config is an envsubst template rendered by the official Nginx entrypoint.
#
# Build context is the repository root (see docker-compose.nginx.yml). Docus
# is intentionally a separate Nuxt service so its SSR, search, LLM, and
# language routes remain fully functional instead of being reduced to a
# fragile static export.
FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY applications/proxy/nginx/default.conf.template /etc/nginx/templates/default.conf.template
