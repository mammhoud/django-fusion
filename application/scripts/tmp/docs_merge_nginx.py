import re

path = 'application/proxy/nginx/default.conf'
s = open(path, encoding='utf-8').read()
orig = s

# 1. Add text/markdown to the types block (after the text/xml line)
s, n = re.subn(r'(text/xml\s+xml;)', r'\1\n        text/markdown                         md;', s, count=1)
assert n == 1, f'markdown type insert matched {n} times'

# 2. Resolver probe target: docs container no longer exists -> filegator
s, n = re.subn(r'set \$resolver_probe docs:80;', 'set $resolver_probe filegator:8080;', s, count=1)
assert n == 1, f'resolver probe matched {n} times'

# 3. Replace the docs location block (comment header + location = /docs +
#    location /docs/ proxy + nested asset locations) with local serving.
start = s.index('    # Docs \u2014 Structa Cloud documentation (Docsify SPA)')
end = s.index('    # Media index')
new_block = '''    # Docs \u2014 Structa Cloud documentation (Docsify SPA, baked into this image)
    # Served from /var/www/docs; history-mode deep links fall through to the
    # SPA shell (@docs_spa), which injects <base href="/docs/"> so relative
    # assets resolve at any depth.
    # Redirect the bare path so the SPA always loads under the trailing slash.
    location = /docs {
        absolute_redirect off;
        return 301 /docs/;
    }

    location /docs/ {
        root /var/www;
        try_files $uri @docs_spa;
        add_header Cache-Control "public, max-age=0, must-revalidate";
    }

    location @docs_spa {
        root /var/www;
        rewrite ^ /docs/index.html break;
        sub_filter_once on;
        sub_filter_types text/html;
        sub_filter '</head>' '<head><base href="/docs/" />';
    }

'''
s = s[:start] + new_block + s[end:]

# 4. Append the docs.structa.cloud server block.
server_block = '''

# ------------------------------------------------------------
# Docs \u2014 docs.structa.cloud (Docsify SPA, baked into this image)
# ------------------------------------------------------------
# Served from the same /var/www/docs tree as media.structa.cloud/docs/.
# Traefik's strip-docs-prefix middleware removes the SPA's /docs/* basePath
# before proxying here, so this block serves the doc tree at the container
# root (see ../traefik/dynamic/docs.yml).
server {
    listen 80;
    server_name docs.structa.cloud docs.localhost;
    include /etc/nginx/mime.types;
    types {
        text/markdown md;
    }
    root /var/www/docs;
    index index.html;
    location / {
        try_files $uri @spa;
    }
    location @spa {
        rewrite ^ /index.html break;
        sub_filter_once on;
        sub_filter_types text/html;
        sub_filter '</head>' '<head><base href="/docs/" />';
    }
}
'''
s = s.rstrip('\n') + server_block

open(path, 'w', encoding='utf-8').write(s)
print('OK: default.conf updated')
