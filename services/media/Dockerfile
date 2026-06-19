FROM nginx:1.25-alpine

# Install openssl for cert generation (only needed if generating inside container)
RUN apk add --no-cache openssl

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config (from this directory)
COPY services/media/nginx.conf /etc/nginx/conf.d/nginx.conf

# Copy entrypoint script
COPY services/media/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
