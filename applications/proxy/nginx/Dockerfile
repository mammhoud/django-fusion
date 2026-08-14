# Shared-media Nginx — static/media server + reverse proxy for Docus and the
# workspace AFFiNE under space.structa.cloud (root; legacy blinko host
# 301-redirects there). No other workspace service has a public subdomain.
#
# The config is an envsubst template: `WORKSPACE_NAME` controls the container
# name prefix (coder-<WORKSPACE_NAME>-*) so the proxy tracks the Coder
# template's `workspace_name` variable without editing the config.
#
# Build context is the repository root (see docker-compose.nginx.yml). Docus
# is intentionally a separate Nuxt service so its SSR, search, LLM, and
# language routes remain fully functional instead of being reduced to a
# fragile static export.
FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY applications/proxy/nginx/default.conf.template /etc/nginx/templates/default.conf.template
