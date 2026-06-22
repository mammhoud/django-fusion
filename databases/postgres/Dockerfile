FROM docker.io/postgres:15-alpine

# Copy and set up maintenance scripts
COPY ./maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/* && \
    mv /usr/local/bin/maintenance/* /usr/local/bin && \
    rmdir /usr/local/bin/maintenance

# Copy initialization scripts (used by our custom entrypoint)
COPY ./init/ /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/*.sh 2>/dev/null || true

# Copy custom entrypoint and make it executable
COPY ./entrypoint /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint

# Use our custom entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint"]
CMD ["postgres"]