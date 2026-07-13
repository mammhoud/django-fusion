# Configuration & Secrets Management

This directory contains configuration files for the Structa Cloud infrastructure and services.

## Structure

- `secrets.example.yml` - Template for sensitive credentials and database passwords
- `secrets.yml` - **ACTUAL SECRETS** (git-ignored, never committed)

## Setup Instructions

### 1. Create Your Secrets File

Copy the example file to create your actual secrets configuration:

```bash
cp applications/compose/config/secrets.example.yml applications/compose/config/secrets.yml
```

### 2. Edit `secrets.yml`

Fill in all the placeholder values with your actual credentials:

```yaml
passwords:
  postgres:
    password: "your-actual-postgres-password"
    admin_password: "your-actual-admin-password"
  
  django:
    secret_key: "your-django-secret-key-here"
    admin_password: "your-admin-password"
  
  # ... etc
```

### 3. Update Docker Compose

In your `docker-compose.yml` or docker-compose override files, reference the secrets:

```yaml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    secrets:
      - postgres_password
  
  django:
    environment:
      DJANGO_SECRET_KEY_FILE: /run/secrets/django_secret_key
    secrets:
      - django_secret_key

secrets:
  postgres_password:
    file: ./applications/compose/config/secrets.yml
  django_secret_key:
    file: ./applications/compose/config/secrets.yml
```

## Security Best Practices

### ✅ DO:
- Keep `secrets.yml` in `.gitignore` (already configured)
- Use unique, strong passwords (minimum 32 characters)
- Rotate secrets regularly in production
- Use environment-specific secrets files (dev, staging, prod)
- Store secrets in a secure vault in production (e.g., AWS Secrets Manager, HashiCorp Vault)
- Version control only the `.example.yml` template
- Audit secrets access and changes

### ❌ DON'T:
- Commit `secrets.yml` to version control
- Use weak passwords or placeholder values in production
- Share secrets in chat, email, or version control
- Hard-code secrets in Dockerfiles or application code
- Use the same password across environments
- Expose secrets in logs or error messages

## Environment-Specific Secrets

For different environments, create separate secrets files:

```
applications/compose/config/
├── secrets.example.yml          # Template
├── secrets.yml                  # Development (git-ignored)
├── secrets.staging.yml          # Staging (git-ignored)
└── secrets.production.yml       # Production (git-ignored, backup separately)
```

## Loading Secrets in Your Application

### Django (.env)

Store the path to your secrets file:

```bash
SECRETS_FILE=./applications/compose/config/secrets.yml
```

Then load in your Django settings:

```python
import yaml
import os

secrets_file = os.getenv('SECRETS_FILE', './applications/compose/config/secrets.yml')
if os.path.exists(secrets_file):
    with open(secrets_file) as f:
        secrets = yaml.safe_load(f)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': secrets['database']['postgres']['name'],
                'USER': secrets['database']['postgres']['user'],
                'PASSWORD': secrets['passwords']['postgres']['password'],
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
            }
        }
```

### Docker Secrets (Swarm/Kubernetes)

For production with Docker Secrets or Kubernetes Secrets:

```yaml
# In docker-compose.yml for Swarm
secrets:
  db_password:
    external: true

services:
  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
```

## Backup and Recovery

⚠️ **Critical**: Always backup your production secrets securely:

```bash
# Backup (encrypted)
gpg --symmetric applications/compose/config/secrets.production.yml

# Restore
gpg applications/compose/config/secrets.production.yml.gpg > applications/compose/config/secrets.production.yml
```

## Troubleshooting

**"secrets.yml not found"**
- Ensure you've created `secrets.yml` from the example
- Check file path and permissions

**"Invalid credentials"**
- Verify values match between `secrets.yml` and environment setup
- Check YAML formatting (indentation matters!)

**"Permission denied reading secrets"**
- Ensure file has correct permissions: `chmod 600 applications/compose/config/secrets.yml`

## Further Reading

- [Docker Secrets Management](https://docs.docker.com/engine/swarm/secrets/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
