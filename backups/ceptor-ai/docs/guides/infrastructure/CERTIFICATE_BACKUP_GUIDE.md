# Certificate Backup & Recovery Guide

**Last Updated**: June 2, 2026
**Environment**: Production
**Location**: `/root/site/websites/compose/traefik/`

---

## 📋 Table of Contents

1. [Backup Locations](#backup-locations)
2. [Backup Types](#backup-types)
3. [Backup Scripts](#backup-scripts)
4. [Recovery Procedures](#recovery-procedures)
5. [Automated Backup Strategy](#automated-backup-strategy)
6. [Disaster Recovery](#disaster-recovery)

---

## Backup Locations

### Primary Backup Directory

**Path**: `/root/site/websites/compose/traefik/certs/`

### Certificate Source Files

**Traefik ACME JSON**:
```
/root/site/websites/compose/traefik/acme/acme.json
- Size: ~13KB
- Format: JSON with embedded base64-encoded certificates
- Permissions: 600 (read-only for Traefik)
```

**Individual Certificate Files**:
```
/root/site/websites/compose/traefik/certs/
├── ctc-research.crt          (1.3K) - Certificate
├── ctc-research.key          (1.7K) - Private key
├── ctc-research.pem          (3.0K) - Combined cert+key
├── ctc-research-chain.pem    (1.3K) - Certificate chain
├── structa-cloud.crt         (1.3K)
├── structa-cloud.key         (1.7K)
├── structa-cloud.pem         (3.0K)
├── structa-cloud-chain.pem   (1.3K)
├── vresume.crt               (1.3K)
├── vresume.key               (1.7K)
├── vresume.pem               (3.0K)
└── vresume-chain.pem         (1.3K)
```

---

## Backup Types

### Type 1: ACME JSON Backup (Timestamped)

**Location**: `certs/YYYYMMDD_HHMMSS_certs/`

**Contents**:
- `acme.json` - Complete Traefik ACME configuration
- `backup-metadata.txt` - Backup information and certificate details

**Size**: ~24KB per backup

**Use Case**:
- Regular point-in-time backups
- Easy restoration to Traefik
- Metadata tracking

**Example**:
```
certs/20260602_180649_certs/
├── acme.json
└── backup-metadata.txt
```

### Type 2: Compressed Archive Backup

**Location**: `certs/production-certs-YYYYMMDD-HHMMSS.tar.gz`

**Contents**:
- Complete `certs/` directory (all certificate, key, and chain files)
- Complete `acme/` directory (acme.json)
- Excludes CSR files to save space

**Size**: ~16KB per backup

**Use Case**:
- Long-term archival storage
- Offline/off-site backups
- Version control friendly
- Easy manual restoration

**Example**:
```
certs/production-certs-20260602-180702.tar.gz
certs/production-certs-20260602-180715.tar.gz
```

---

## Backup Scripts

### Certificate Backup Script

**Location**: `/root/site/websites/compose/traefik/cert-backup.sh`

**Commands**:

#### Backup Current Certificates
```bash
bash cert-backup.sh backup
```

**Output**:
- Creates timestamped backup directory
- Copies `acme.json`
- Generates `backup-metadata.txt` with certificate details
- Verifies backup integrity
- Displays summary

#### List Available Backups
```bash
bash cert-backup.sh list
```

**Output**:
- Lists all available backups
- Shows backup dates
- Displays backup sizes
- Shows certificate information

#### Restore from Backup
```bash
bash cert-backup.sh restore /path/to/backup/directory
```

**Process**:
1. Creates safety backup of current certificates
2. Copies backup files to acme directory
3. Sets correct permissions (600)
4. Prompts to restart Traefik

#### Cleanup Old Backups
```bash
bash cert-backup.sh cleanup [keep_count]
```

**Example** (keep last 10):
```bash
bash cert-backup.sh cleanup 10
```

#### Check Status
```bash
bash cert-backup.sh status
```

**Output**:
- Current certificate status
- ACME file information
- Available backups count
- Total backup size

---

## Recovery Procedures

### Quick Recovery (Traefik)

**Scenario**: Traefik lost its certificates or corrupt acme.json

**Steps**:

1. **List available backups**:
   ```bash
   cd /root/site/websites/compose/traefik
   bash cert-backup.sh list
   ```

2. **Restore from most recent backup**:
   ```bash
   bash cert-backup.sh restore certs/20260602_180649_certs
   ```

3. **Restart Traefik**:
   ```bash
   docker compose restart traefik
   ```

4. **Verify restoration**:
   ```bash
   docker compose logs traefik | grep -i "certificate"
   ```

**Time to Recovery**: ~1 minute

---

### Full System Recovery (Archive)

**Scenario**: Complete server failure, need to restore from archive backup

**Steps**:

1. **Extract archive**:
   ```bash
   cd /root/site/websites/compose/traefik
   tar -xzf certs/production-certs-20260602-180702.tar.gz
   ```

2. **Restore permissions**:
   ```bash
   chmod 600 acme/acme.json
   ```

3. **Verify restoration**:
   ```bash
   ls -la acme/acme.json
   ls -la certs/
   ```

4. **Restart Traefik**:
   ```bash
   docker compose restart traefik
   ```

**Time to Recovery**: ~2 minutes

---

### Certificate Regeneration (If Backups Lost)

**Scenario**: All backups lost, need to regenerate certificates

**Steps**:

1. **Regenerate new certificates**:
   ```bash
   cd /root/site/websites
   bash compose/traefik/generate-certs.sh
   ```

2. **Restart Traefik**:
   ```bash
   docker compose restart traefik
   ```

3. **Create backup of new certificates**:
   ```bash
   cd /root/site/websites/compose/traefik
   bash cert-backup.sh backup
   ```

4. **Archive the backup**:
   ```bash
   tar -czf certs/production-certs-regenerated.tar.gz certs/ acme/
   ```

**Time to Recovery**: ~3 minutes

---

## Automated Backup Strategy

### Daily Backup with Cron

**Setup automated daily backups**:

```bash
# Edit crontab
crontab -e

# Add this line (backup daily at 2 AM)
0 2 * * * cd /root/site/websites/compose/traefik && bash cert-backup.sh backup >> /var/log/traefik-backup.log 2>&1

# Add this line (cleanup old backups every Sunday at 3 AM, keep last 30)
0 3 * * 0 cd /root/site/websites/compose/traefik && bash cert-backup.sh cleanup 30 >> /var/log/traefik-backup.log 2>&1
```

### Weekly Off-Site Backup

**Copy archive backups to remote storage**:

```bash
#!/bin/bash
# backup-to-remote.sh

BACKUP_DIR="/root/site/websites/compose/traefik/certs"
REMOTE_HOST="backup-server.example.com"
REMOTE_PATH="/backups/traefik-certs"

# Copy latest archive backup
LATEST=$(ls -t ${BACKUP_DIR}/production-certs-*.tar.gz | head -1)

scp "${LATEST}" "${REMOTE_HOST}:${REMOTE_PATH}/"

echo "Backup copied to remote: $(basename ${LATEST})"
```

**Add to crontab** (every Monday at 3 AM):
```
0 3 * * 1 /root/site/websites/backup-to-remote.sh
```

---

## Disaster Recovery

### Complete Disaster Recovery Plan

**RTO** (Recovery Time Objective): < 15 minutes
**RPO** (Recovery Point Objective): < 24 hours

### Recovery Runbook

#### Step 1: Assess Damage
```bash
# Check if backups exist
ls -la /root/site/websites/compose/traefik/certs/

# Check if off-site backups exist
ls -la /backups/traefik-certs/ (if remote backup configured)

# Verify DNS records still point to server
dig @8.8.8.8 ctc-research.com
```

#### Step 2: Restore Certificates
```bash
# If local backups exist:
cd /root/site/websites/compose/traefik
bash cert-backup.sh restore certs/[LATEST_BACKUP]

# If using archive backup:
cd /root/site/websites/compose/traefik
tar -xzf certs/production-certs-*.tar.gz
chmod 600 acme/acme.json
```

#### Step 3: Verify Restoration
```bash
# Check certificate files
ls -la compose/traefik/certs/

# Check ACME JSON
ls -la compose/traefik/acme/acme.json

# Verify certificate validity
openssl x509 -in compose/traefik/certs/ctc-research.crt -text -noout | grep -E "Issuer|Subject|Expires"
```

#### Step 4: Restart Services
```bash
# Restart Traefik
docker compose restart traefik

# Verify Traefik started correctly
sleep 5
docker compose logs traefik | tail -20

# Verify HTTPS is working
curl -k https://ctc-research.com/ (if DNS updated)
# or
curl -k --resolve ctc-research.com:443:127.0.0.1 https://ctc-research.com/
```

#### Step 5: Verify All Services
```bash
# Check all services
docker compose ps

# Verify health checks
docker compose exec -T postgres pg_isready
docker compose exec -T redis redis-cli ping
curl http://localhost:8080/ping
```

---

## Certificate Maintenance

### Monthly Certificate Review

**First Monday of each month**:

1. Check certificate expiry dates:
   ```bash
   for cert in compose/traefik/certs/*.crt; do
     echo "=== $(basename $cert) ==="
     openssl x509 -in "$cert" -noout -dates
   done
   ```

2. List all backups:
   ```bash
   bash compose/traefik/cert-backup.sh list
   ```

3. Verify backup integrity:
   ```bash
   for backup in compose/traefik/certs/*.tar.gz; do
     tar -tzf "$backup" > /dev/null && echo "✓ $(basename $backup)" || echo "✗ $(basename $backup)"
   done
   ```

### Quarterly Restore Test

**Every 3 months (test recovery procedure)**:

1. Extract test backup:
   ```bash
   mkdir -p /tmp/cert-test
   tar -xzf compose/traefik/certs/production-certs-*.tar.gz -C /tmp/cert-test
   ```

2. Verify certificate files:
   ```bash
   ls -la /tmp/cert-test/
   ```

3. Check certificate details:
   ```bash
   openssl x509 -in /tmp/cert-test/certs/ctc-research.crt -text -noout
   ```

4. Clean up test files:
   ```bash
   rm -rf /tmp/cert-test
   ```

---

## Backup Checklist

### Daily
- [ ] Verify ACME JSON exists: `ls -la acme/acme.json`
- [ ] Check Traefik logs for certificate errors: `docker compose logs traefik`

### Weekly
- [ ] Run manual backup: `bash cert-backup.sh backup`
- [ ] Verify backup created: `bash cert-backup.sh list`
- [ ] Copy to off-site storage (if configured)

### Monthly
- [ ] Review certificate expiry dates
- [ ] Run cleanup to remove old backups: `bash cert-backup.sh cleanup 30`
- [ ] Check backup directory size: `du -sh certs/`

### Quarterly
- [ ] Perform restore test
- [ ] Verify off-site backups

### Annually
- [ ] Document backup procedure
- [ ] Update disaster recovery runbook
- [ ] Review backup retention policy

---

## Storage Recommendations

### Local Backup Storage

**Location**: `/root/site/websites/compose/traefik/certs/`
**Retention**: 30 days
**Size**: ~500KB total (20 backups)

### Off-Site Backup Storage

**Services** (choose one):
- AWS S3 (recommended) - `$3-5/month`
- Google Cloud Storage - `$5-8/month`
- Backblaze B2 - `$1-2/month`
- Manual SCP to backup server

**Script for AWS S3**:
```bash
#!/bin/bash
aws s3 sync /root/site/websites/compose/traefik/certs/ \
  s3://my-backup-bucket/traefik-certs/ \
  --sse AES256 \
  --delete
```

### Database Backup Integration

**Coordinate with database backups**:
- Schedule certificates 1 hour before database backups
- Keep certificates and database backups in sync
- Tag backups with matching timestamps

---

## Emergency Contact

**In case of certificate emergency**:

1. Check backup status: `bash cert-backup.sh status`
2. Contact system administrator
3. Follow Recovery Procedures section above
4. Document what happened in logs

---

## Appendix: Certificate File Descriptions

### `.crt` - Certificate File
- Format: PEM (base64-encoded X.509)
- Contains: Public certificate only
- Use: HTTPS servers, public distribution
- Readable: Yes (base64)

### `.key` - Private Key File
- Format: PEM (base64-encoded RSA)
- Contains: Private key material
- Use: Traefik, internal use only
- Security: Keep secret, permissions 600
- Readable: Partially (structure visible, not usable without password)

### `.pem` - Combined Bundle
- Format: PEM (concatenated .crt + .key)
- Contains: Certificate + Private key
- Use: When single file needed
- Security: Must be restricted to 600
- Readable: Partially (mixed content)

### `.csr` - Certificate Signing Request
- Format: PEM (base64-encoded request)
- Contains: Public key + subject information
- Use: Certificate renewal requests
- Note: Not needed for operation, can be deleted

### `acme.json` - Traefik ACME Configuration
- Format: JSON with base64-encoded certificates
- Contains: All certificate data for Traefik
- Use: Traefik certificate storage
- Security: Must be restricted to 600
- Backup: Essential for disaster recovery

---

**Last Updated**: June 2, 2026
**Next Review**: September 2, 2026

