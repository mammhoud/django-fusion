# Shared-media Nginx — static/media server + reverse proxy for Docus and
# the FileGator container. Workspace IDE/AppFlowy services are internal Coder
# apps and intentionally have no public subdomain.
#
# Build context is the repository root (see docker-compose.nginx.yml). Docus
# is intentionally a separate Nuxt service so its SSR, search, LLM, and
# language routes remain fully functional instead of being reduced to a
# fragile static export.
FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY applications/proxy/nginx/default.conf /etc/nginx/conf.d/nginx.conf
