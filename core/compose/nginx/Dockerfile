FROM nginx:1.25-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config
COPY ./compose/nginx/nginx.conf /etc/nginx/conf.d/nginx.conf
