# Docsify static documentation server
FROM nginx:1.27-alpine


RUN rm -rf /usr/share/nginx/html/*

COPY . /usr/share/nginx/html/

# Quoted heredoc ('EOF') so $uri and quotes stay literal — no shell escaping.
RUN cat > /etc/nginx/conf.d/default.conf <<'EOF'
server {
  listen 80;
  # Re-include the base mime map before adding types: a server-level
  # `types` block REPLACES the inherited http-level map (html/css/js would
  # collapse to application/octet-stream), so the markdown mapping must be
  # appended at the same level. The shared-media nginx gzips /docs/* only
  # for types in its gzip_types list — text/markdown enables gzip for the
  # .md documentation pages.
  include /etc/nginx/mime.types;
  types {
    text/markdown md;
  }
  root /usr/share/nginx/html;
  index index.html;
  location / {
    # Docsify uses history-mode routing: serve real files (markdown,
    # css, assets) directly, but fall back to the SPA shell for every
    # other path — including deep links that happen to match real
    # directory names (try_files $uri $uri/ would 403 on those).
    try_files $uri @spa;
  }
  location @spa {
    rewrite ^ /index.html break;
    # Deep links (e.g. /docs/plans/overview) hit this fallback, and
    # index.html loads theme.css RELATIVELY, so the browser would
    # resolve it one level too deep (/docs/plans/theme.css) and get
    # this same fallback instead of the stylesheet. Inject a
    # <base href="/docs/"> so relative assets always resolve against
    # the docs root at any depth (media.structa.cloud/docs/* and
    # docs.structa.cloud/* both mount this same /docs/ path). Root
    # and directory requests (/docs/, /docs/plans/) also pass through
    # @spa; there the base is a no-op (resolves to the same URL).
    sub_filter_once on;
    sub_filter_types text/html;
    sub_filter '</head>' '<head><base href="/docs/" />';
  }
}
EOF

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ || exit 1
