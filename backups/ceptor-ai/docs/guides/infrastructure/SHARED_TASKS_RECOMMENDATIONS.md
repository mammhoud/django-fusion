# Shared Celery and Email Services Recommendations

To set up Celery and Emails as shared tasks across both `ctc-research.com` and `vresume` applications, we recommend creating a shared services layer within your `services/` directory.

## Architecture Recommendations

Instead of running separate Redis and Celery instances for each application, you can orchestrate a shared message broker (Redis/RabbitMQ) and centralized worker processes. 

### Files to Create for a Shared Task Setup

1. **`services/docker-compose.tasks.yml`**
   This file should define the shared Redis broker and the Celery workers.
   ```yaml
   networks:
     shared-net:
       name: shared-net

   services:
     shared-redis:
       image: redis:alpine
       container_name: shared-redis
       networks:
         - shared-net
       restart: unless-stopped

     shared-celery-worker:
       build:
         context: ..
         dockerfile: ./services/celery/Dockerfile
       container_name: shared-celery-worker
       depends_on:
         - shared-redis
       environment:
         - CELERY_BROKER_URL=redis://shared-redis:6379/0
       networks:
         - shared-net
       restart: unless-stopped
   ```

2. **`services/docker-compose.email.yml`**
   For shared email routing (e.g. MailHog for development or a shared postfix relay for production):
   ```yaml
   services:
     shared-mailhog:
       image: mailhog/mailhog
       container_name: shared-mailhog
       ports:
         - "8025:8025" # Web UI
       networks:
         - shared-net
   ```

3. **Application `.env` Configuration**
   In both `ctc-research.com` and `VResume`, update the `settings.py` or `.env` files to point to the shared services:
   ```env
   # Shared Redis Broker
   CELERY_BROKER_URL=redis://shared-redis:6379/0
   
   # Shared Email Server
   EMAIL_HOST=shared-mailhog
   EMAIL_PORT=1025
   ```

## Make Commands to Add

Update the `services/Makefile` to include deployment commands for these shared components:

```makefile
deploy-tasks:
	@docker compose -f docker-compose.tasks.yml up -d

deploy-email:
	@docker compose -f docker-compose.email.yml up -d
```

These changes ensure both platforms delegate heavy background operations to a unified service cluster rather than spawning their own.
