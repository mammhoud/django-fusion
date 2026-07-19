# Deployment Quick Start Guide

**TL;DR**: Run one command to deploy everything

---

## One-Command Deployment

```bash
cd /root/site/websites
./deploy-production.sh
```

Done! This will:
- Validate environment
- Build Docker images
- Start all services
- Run migrations
- Collect static files
- Backup certificates
- Verify deployment

---

## Website URLs

Once deployed, access at:

```
CTC-Research:  http://localhost:5070/
LMS Demo:      http://localhost:5071/
VResume:       http://localhost:5072/

Admin Panels:
  CTC:    http://localhost:5070/admin/
  LMS:    http://localhost:5071/admin/
  Resume: http://localhost:5072/admin/
```

---

## Create Admin Users

```bash
docker exec -it web-ctc-research python manage.py createsuperuser
docker exec -it web-lms-demo python manage.py createsuperuser
docker exec -it web-vresume python manage.py createsuperuser
```

---

## Common Commands

### View Status
```bash
docker compose ps                    # All containers
docker logs web-ctc-research         # View logs
docker compose logs -f               # Stream all logs
```

### Troubleshoot
```bash
docker compose logs web-ctc-research | tail -50
docker exec web-ctc-research python manage.py check --deploy
```

### Restart Services
```bash
docker compose restart               # Restart all
docker compose restart web-ctc-research  # Restart one
```

### Run Tests
```bash
bash run_full_test_suite.sh
```

### Database Access
```bash
docker exec -it postgres psql -U structa -d db_ctc
```

---

## Full Documentation

- **Detailed Guide**: `../deployment/DEPLOYMENT_GUIDE.md`
- **Status Report**: `FINAL_DEPLOYMENT_STATUS.md`
- **Test Plan**: `DEPLOYMENT_TEST_PLAN.md`
- **Certificate Backup**: `compose/traefik/CERT_BACKUP_README.md`

---

## Troubleshooting

**Container won't start?**
```bash
docker logs [container-name] | tail -20
```

**Assets not loading?**
```bash
docker exec web-ctc-research python manage.py collectstatic --noinput
```

**Database connection error?**
```bash
docker exec postgres psql -U structa -l
```

**Port already in use?**
Edit `docker-compose.yml` and change the port numbers.

---

## Next Steps After Deployment

1. ✅ Verify containers are running: `docker compose ps`
2. ✅ Test websites in browser
3. ✅ Create admin users (see above)
4. ✅ Load production data if available
5. ✅ Run test suite: `bash run_full_test_suite.sh`
6. ✅ Monitor logs: `docker compose logs -f`
7. ✅ Setup backup automation: See `compose/traefik/CERT_BACKUP_README.md`

---

## Success Criteria

✅ All containers show "healthy" status  
✅ Websites respond on ports 5070, 5071, 5072  
✅ Admin panels accessible  
✅ Assets loading correctly  
✅ No errors in logs  

---

**Status**: 🟢 Ready for deployment!

Run: `./deploy-production.sh`
