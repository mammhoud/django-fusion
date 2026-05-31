FROM docker.io/postgres:16-alpine

# Copy and set up maintenance scripts
COPY ./maintenance /usr/local/bin/maintenance

RUN chmod +x /usr/local/bin/maintenance/* && \
    mv /usr/local/bin/maintenance/* /usr/local/bin && \
    rmdir /usr/local/bin/maintenance

# Copy initialization scripts
COPY ./init.d/ /docker-entrypoint-initdb.d/

# Make shell scripts executable
RUN chmod +x /docker-entrypoint-initdb.d/*.sh 2>/dev/null || true
