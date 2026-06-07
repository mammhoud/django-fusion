# SSL/TLS Deployment Guide

**Quick Reference for Deploying with SSL Certificates**

---

## Quick Start

### 1. Verify Certificates Exist
```bash
ls -la /root/site/websites/compose/traefik/certs/
```

**Expected Output:**
- `ctc-research.crt`, `ctc-research.key`
- `structa-cloud.crt`, `structa-cloud.key`
- `vresume.crt`, `vresume.key`

### 2. Rebuild Traefik Container
```bash
cd /root/site/websites
docker compose build traefik
```

### 3. Restart Traefik Service
```bash
docker compose restart traefik
```

### 4. Verify SSL is Working
```bash
# Check Traefik logs for certificate loading
docker logs traefik | tail -20

# Test HTTPS for each domain
curl -v https://ctc-research.com 2>&1 | head -20
curl -v https://structa.cloud 2>&1 | head -20
curl -v https://vresume.structa.cloud 2>&1 | head -20
```

---

## Configuration Overview

### What Was Changed

1. **Traefik Static Config** (`compose/traefik/traefik.yml`)
   - Added TLS certificate store configuration
   - Registered all 3 domain certificates
   - Changed entry point TLS resolver to "local"

2. **Docker Compose** (`compose/docker-compose.traefik.yml`)
   - Added volume mount for certificates directory
   - Mounted as read-only (`/etc/traefik/certs:ro`)

3. **Domain Routing** (`compose/traefik/dynamic/*.yml`)
   - Updated all TLS cert resolvers from "letsencrypt" to "local"
   - Applied to all domain routers

### Certificate File Locations

```
Local Machine:    /root/site/websites/compose/traefik/certs/
Container:        /etc/traefik/certs/
```

---

## Domain to Certificate Mapping

| Domain | Certificate File |
|--------|------------------|
| ctc-research.com | ctc-research.crt / ctc-research.key |
| structa.cloud | structa-cloud.crt / structa-cloud.key |
| vresume.structa.cloud | vresume.crt / vresume.key |

### Subject Alternative Names (SANs)

Each certificate also covers related subdomains:

```
ctc-research.crt      → ctc-research.com, www.ctc-research.com, arch.ctc-research.com
structa-cloud.crt     → structa.cloud, core.structa.cloud, www.structa.cloud
vresume.crt           → vresume.structa.cloud, www.vresume.structa.cloud, resume.structa.cloud
```

---

## Troubleshooting

### Issue: Certificate not loading
```bash
# Check file permissions
ls -l /root/site/websites/compose/traefik/certs/

# Should see: -rw------- for .key files, -rw-r--r-- for .crt files

# Check Traefik logs
docker logs traefik | grep -i "certificate\|error\|tls"
```

### Issue: HTTPS connections failing
```bash
# Test with curl to see details
curl -v https://ctc-research.com

# Check Traefik port 443 is listening
netstat -tlnp | grep 443
# or
ss -tlnp | grep 443
```

### Issue: HTTP not redirecting to HTTPS
```bash
# Check entry point configuration
curl -I http://ctc-research.com

# Should get 301 redirect to https://
```

---

## Verification Checklist

Run after deployment:

```bash
#!/bin/bash

echo "=== Traefik Status ==="
docker ps | grep traefik

echo -e "\n=== Certificate Files ==="
ls -lh /root/site/websites/compose/traefik/certs/*.crt

echo -e "\n=== Testing HTTPS Connections ==="
for domain in ctc-research.com structa.cloud vresume.structa.cloud; do
  echo "Testing $domain..."
  curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://$domain
done

echo -e "\n=== Testing HTTP Redirect ==="
for domain in ctc-research.com structa.cloud vresume.structa.cloud; do
  echo "Testing $domain redirect..."
  curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://$domain
done

echo -e "\n=== Traefik Dashboard ==="
echo "Access at: http://localhost:8080"
```

---

## Advanced: Manual Certificate Update

If you need to update certificates manually:

```bash
# 1. Backup current certificates
cd /root/site/websites/compose/traefik/certs/
tar -czf ../cert-backups/certs-backup-$(date +%s).tar.gz *.crt *.key

# 2. Replace certificate files (copy your new .crt and .key files)
cp /path/to/new/certificate.crt ./domain.crt
cp /path/to/new/private.key ./domain.key

# 3. Fix permissions
chmod 600 ./domain.key

# 4. Restart Traefik
docker compose restart traefik

# 5. Verify
docker logs traefik | tail -20
```

---

## Backup & Recovery

### View Available Backups
```bash
ls -la /root/site/websites/compose/traefik/cert-backups/
```

### Restore from Backup
```bash
cd /root/site/websites/compose/traefik/cert-backups/
tar -xzf production-certs-20260602-180715.tar.gz -C ../
docker compose restart traefik
```

---

## Performance & Monitoring

### Monitor Traefik Logs
```bash
docker logs -f traefik
```

### Check Certificate Validity
```bash
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -text -noout
```

### Traefik Dashboard
```
http://localhost:8080
```

Shows:
- Configured routes
- Certificate status
- Service health
- Middleware status

---

## Security Notes

1. **Private Keys** - Keep .key files secure (600 permissions)
2. **Certificate Chain** - .pem files include full chain
3. **Read-Only Mount** - Certificates mounted as read-only in container
4. **Backup Location** - Backups stored in cert-backups/ directory

---

## Related Documentation

- See `docs/00_MASTER_INDEX.md` for all documentation
- See `docs/TASK_4_COMPLETION_REPORT.md` for detailed changes
- See `docs/DEPLOYMENT_READY_SUMMARY.md` for system status
