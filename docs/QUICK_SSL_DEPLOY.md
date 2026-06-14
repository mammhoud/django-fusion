# 🚀 Quick SSL Deployment Reference

**One-Page Quick Reference for Deploying SSL-Enabled Services**

---

## 📋 Pre-Deployment Checklist

```bash
# 1. Verify all components are ready
/root/site/websites/VERIFY_SSL_CONFIG.sh
```

Expected output: ✅ ALL CHECKS PASSED

---

## 🔧 Deployment Commands

### Step 1: Rebuild Traefik
```bash
cd /root/site/websites
docker compose build traefik
```

### Step 2: Restart Traefik
```bash
docker compose restart traefik
```

### Step 3: Verify Startup
```bash
docker logs traefik | tail -20
```

Look for: No errors, certificate loading messages

---

## 🧪 Quick Tests

### Test HTTPS Connectivity
```bash
# Test all three domains
curl -v https://ctc-research.com 2>&1 | head -30
curl -v https://structa.cloud 2>&1 | head -30
curl -v https://vresume.structa.cloud 2>&1 | head -30
```

Expected: HTTP 200-308 status codes (redirects are ok)

### Test HTTP Redirect
```bash
# Should redirect to HTTPS
curl -I http://ctc-research.com
curl -I http://structa.cloud
curl -I http://vresume.structa.cloud
```

Expected: 301 or 308 redirect to HTTPS

### Check Certificate Info
```bash
# View certificate details
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -text -noout
```

Expected: Certificate details with correct domain names

---

## 🔍 Troubleshooting

### Issue: Traefik won't start
```bash
# Check logs
docker logs traefik

# Look for: permission errors, missing files
# Solution: Verify certificate files exist and have correct permissions
ls -l /root/site/websites/compose/traefik/certs/*.key
# Should show: -rw------- (600 permissions)
```

### Issue: HTTPS certificate warning
```bash
# The certificates may be self-signed or have expired
# Check certificate validity
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -dates -noout

# Update certificates if expired
# Replace files in /root/site/websites/compose/traefik/certs/
# Then restart: docker compose restart traefik
```

### Issue: Connection refused on port 443
```bash
# Verify Traefik is listening on 443
netstat -tlnp | grep 443
# or
ss -tlnp | grep 443

# Check if Traefik container is running
docker ps | grep traefik
```

---

## 📊 Configuration Summary

| Component | Location | Status |
|-----------|----------|--------|
| SSL Certificates | `/compose/traefik/certs/` | ✅ Ready |
| Traefik Config | `/compose/traefik/traefik.yml` | ✅ Updated |
| Docker Compose | `/compose/docker-compose.traefik.yml` | ✅ Updated |
| Domain Routes | `/compose/traefik/dynamic/*.yml` | ✅ Updated |
| Documentation | `/docs/` | ✅ Complete |

---

## 🎯 Domain Mapping

```
ctc-research.com           → ctc-research.crt
structa.cloud              → structa-cloud.crt
vresume.structa.cloud      → vresume.crt
```

All domains configured for HTTPS with auto-redirect from HTTP

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [TASK_4_COMPLETION_REPORT.md](./docs/TASK_4_COMPLETION_REPORT.md) | Detailed changes |
| [DEPLOYMENT_GUIDE_SSL.md](./docs/DEPLOYMENT_GUIDE_SSL.md) | Full SSL guide |
| [00_MASTER_INDEX.md](./docs/00_MASTER_INDEX.md) | Documentation hub |

---

## ⏱️ Estimated Time

- Build Traefik: 2-3 minutes
- Restart Traefik: 30 seconds
- Verification: 2-3 minutes
- **Total: ~5-6 minutes**

---

## ✅ Success Criteria

After deployment:
- [ ] Traefik container running: `docker ps | grep traefik`
- [ ] HTTPS works: `curl -v https://ctc-research.com`
- [ ] HTTP redirects to HTTPS: `curl -I http://ctc-research.com`
- [ ] No certificate errors in logs: `docker logs traefik`
- [ ] All three domains responding: All curl tests return 2xx-3xx status

---

## 🆘 Emergency Restore

If issues occur:

```bash
# Restore from backup
cd /root/site/websites/compose/traefik/certs-backups/
tar -xzf production-certs-20260602-180715.tar.gz -C ../

# Restart
docker compose restart traefik

# Verify
docker logs traefik
```

---

## 📞 Support

For detailed troubleshooting, see:
- `/root/site/websites/docs/DEPLOYMENT_GUIDE_SSL.md` - Full guide
- `/root/site/websites/docs/TASK_4_COMPLETION_REPORT.md` - Technical details
- `/root/site/websites/VERIFY_SSL_CONFIG.sh` - Verification script

---

**Last Updated:** June 2, 2026  
**Status:** ✅ Ready for Deployment
