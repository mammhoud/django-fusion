# SSL Certificate Management Documentation

## Overview

This document describes the SSL/TLS certificate management setup for the multi-site Traefik deployment. It covers current certificate status, backup procedures, renewal options, and troubleshooting.

## Current Certificate Status

All three domains are currently protected with **self-signed certificates**:

| Domain | Certificate | Issued | Expires | Days Left | Status |
|--------|-------------|--------|---------|-----------|--------|
| ctc-research.com | ctc-research.crt | Jun 2, 2026 | Jun 2, 2027 | ~355 | ✓ Valid |
| structa.cloud | structa-cloud.crt | Jun 2, 2026 | Jun 2, 2027 | ~355 | ✓ Valid |
| vresume.structa.cloud | vresume.crt | Jun 2, 2026 | Jun 2, 2027 | ~355 | ✓ Valid |

**Certificate Storage**: `/root/site/websites/compose/traefik/certs/`

**Validation**: All certificates and key pairs have been validated and match correctly. ✓

## Certificate Files

Each domain has the following certificate files:

```
certs/
├── ctc-research.crt          # Certificate (X.509)
├── ctc-research.key          # Private key (RSA 2048)
├── ctc-research.pem          # Combined cert + key
├── ctc-research-chain.pem    # Certificate chain
├── ctc-research.csr          # Certificate signing request
├── structa-cloud.crt
├── structa-cloud.key
├── structa-cloud.pem
├── structa-cloud-chain.pem
├── structa-cloud.csr
├── vresume.crt
├── vresume.key
├── vresume.pem
├── vresume-chain.pem
└── vresume.csr
```

## Using the Certificate Management Script

The `manage-certs.sh` script provides utilities for SSL certificate operations:

### List Certificates

```bash
cd compose/traefik
./manage-certs.sh list
```

Shows all certificates with:
- Certificate name and domain
- File location
- Expiration date and days remaining
- Validity status

### Check Expiry Status

```bash
./manage-certs.sh check-expiry
```

Returns exit code 0 if all certificates are valid, 1 if any are expired/expiring soon.

### Validate Certificates

```bash
./manage-certs.sh validate
```

Ensures certificate and key pairs match (validates modulus):
- ✓ Valid: Certificate and private key match
- ✗ Invalid: Certificate and key are mismatched (corrupted)

### Backup Certificates

```bash
./manage-certs.sh backup
```

Creates a dated backup archive:
- Location: `certs/certs-backup-YYYYMMDD-HHMMSS.tar.gz`
- Contains: All certificates and keys
- Recommended: Before major Traefik changes

### Restore from Backup

```bash
./manage-certs.sh restore certs/certs-backup-20260611-120000.tar.gz
```

Restores certificates from a backup:
- Prompts for confirmation
- Automatically restarts Traefik after restore
- Validates file before attempting restore

### Generate New Self-Signed Certificates

```bash
./manage-certs.sh generate-self-signed
```

Generates new self-signed certificates for all three domains:
- Valid for 365 days
- RSA 2048-bit keys
- Overwrites existing certificates

## Traefik Configuration

### Static Certificates (Current Method)

Traefik is configured in `traefik.yml` to use static certificates as the **primary method**:

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: ${TRAEFIK_ACME_EMAIL:-admin@structa.cloud}
      storage: /etc/traefik/acme/acme.json
      caServer: ${TRAEFIK_ACME_CASERVER:-https://acme-v02.api.letsencrypt.org/directory}
      httpChallenge:
        entryPoint: web

tls:
  stores:
    default:
      defaultCertificate:
        certFile: /etc/traefik/certs/ctc-research.crt
        keyFile: /etc/traefik/certs/ctc-research.key

  certificates:
    - certFile: /etc/traefik/certs/ctc-research.crt
      keyFile: /etc/traefik/certs/ctc-research.key
    - certFile: /etc/traefik/certs/structa-cloud.crt
      keyFile: /etc/traefik/certs/structa-cloud.key
    - certFile: /etc/traefik/certs/vresume.crt
      keyFile: /etc/traefik/certs/vresume.key
```

### Environment Variables

Configure ACME email in `.env`:

```bash
# ACME Configuration
TRAEFIK_ACME_EMAIL=admin@structa.cloud
TRAEFIK_LOG_LEVEL=INFO

# Use production CA (valid certificates)
TRAEFIK_ACME_CASERVER=https://acme-v02.api.letsencrypt.org/directory

# OR use staging CA for testing (invalid certs, no rate limits)
# TRAEFIK_ACME_CASERVER=https://acme-staging-v02.api.letsencrypt.org/directory
```

## Certificate Renewal Options

### Option 1: Replace Self-Signed with Let's Encrypt (Recommended)

To enable automatic certificate generation and renewal via Let's Encrypt:

1. **Verify email configuration** (.env):
   ```bash
   grep TRAEFIK_ACME_EMAIL .env
   ```

2. **Verify domains are publicly accessible**:
   - Ensure port 80 (HTTP) is reachable from internet
   - Traefik uses HTTP-01 challenge by default

3. **Enable ACME in Traefik** (optional - already configured):
   - Edit `traefik.yml`
   - Uncomment ACME resolver or enable HTTP challenge

4. **Update dynamic router configs** to use ACME:
   - Edit `dynamic/ctc-research.yml`
   - Change `certResolver: ""` to `certResolver: "letsencrypt"`
   - Repeat for `structa-cloud.yml` and `vresume.yml`

5. **Restart Traefik**:
   ```bash
   docker compose restart structa-proxy
   ```

6. **Verify certificate generation**:
   ```bash
   docker logs structa-proxy | grep -i "acme\|certificate"
   docker exec structa-proxy cat /etc/traefik/acme/acme.json | jq '.certificates[0]'
   ```

### Option 2: Generate New Self-Signed Certificates

To replace current certificates with updated self-signed ones:

```bash
cd compose/traefik

# Backup current certificates
./manage-certs.sh backup

# Generate new self-signed certificates (valid 365 days)
./manage-certs.sh generate-self-signed

# Restart Traefik to apply
docker compose restart structa-proxy
```

### Option 3: Use Backup Certificates

If certificates are lost or corrupted:

```bash
cd compose/traefik

# List available backups
ls -lh certs/

# Restore specific backup
./manage-certs.sh restore certs/certs-backup-20260611-120000.tar.gz
```

## Monitoring and Alerts

### Check Certificate Expiry

```bash
cd compose/traefik
./manage-certs.sh check-expiry
```

Add to crontab for weekly checks:

```bash
0 9 * * 1 cd /root/site/websites/compose/traefik && ./manage-certs.sh check-expiry >> /var/log/cert-check.log 2>&1
```

### Inspect Certificate Details

Get full certificate information:

```bash
# View certificate details
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -noout -text

# View certificate dates
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -noout -dates

# View certificate issuer (self-signed shows issuer=subject)
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -noout -issuer -subject

# View certificate fingerprint
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -noout -fingerprint
```

### Verify Certificate and Key Match

```bash
# Extract modulus from certificate and key
openssl x509 -noout -modulus -in /root/site/websites/compose/traefik/certs/ctc-research.crt | openssl md5
openssl rsa -noout -modulus -in /root/site/websites/compose/traefik/certs/ctc-research.key | openssl md5

# Should produce identical MD5 hashes if they match
```

## Troubleshooting

### Certificate Issues

**Problem**: HTTPS requests fail with certificate errors

**Solutions**:
1. Verify certificate files exist:
   ```bash
   ls -la /root/site/websites/compose/traefik/certs/*.crt
   ```

2. Validate certificates:
   ```bash
   cd compose/traefik && ./manage-certs.sh validate
   ```

3. Check certificate expiration:
   ```bash
   cd compose/traefik && ./manage-certs.sh check-expiry
   ```

4. Verify Traefik can read certificate files:
   ```bash
   docker exec structa-proxy ls -la /etc/traefik/certs/
   ```

5. Check Traefik logs:
   ```bash
   docker logs structa-proxy | grep -i "certificate\|tls\|error"
   ```

### ACME Configuration Issues

**Problem**: Let's Encrypt certificate generation fails

**Error**: "unable to parse email address"

**Solutions**:
1. Verify email format:
   ```bash
   grep TRAEFIK_ACME_EMAIL .env
   ```
   - Must be valid email format (contains @)
   - Must be valid domain (has TLD)
   - Cannot be admin@localhost

2. Check Traefik logs:
   ```bash
   docker logs structa-proxy | grep -i "acme"
   ```

3. Verify ACME storage location:
   ```bash
   docker exec structa-proxy ls -la /etc/traefik/acme/
   ```

4. Test with staging CA (no rate limits):
   ```bash
   # Edit .env
   TRAEFIK_ACME_CASERVER=https://acme-staging-v02.api.letsencrypt.org/directory

   # Restart
   docker compose restart structa-proxy
   ```

### Certificate Renewal Issues

**Problem**: Certificates are expiring soon

**Solutions**:
1. Check current status:
   ```bash
   cd compose/traefik && ./manage-certs.sh check-expiry
   ```

2. If using Let's Encrypt, force renewal:
   ```bash
   # Delete ACME storage to force renewal
   docker exec structa-proxy rm -f /etc/traefik/acme/acme.json
   docker compose restart structa-proxy

   # Monitor logs
   docker logs -f structa-proxy
   ```

3. If using self-signed, generate new ones:
   ```bash
   cd compose/traefik
   ./manage-certs.sh backup
   ./manage-certs.sh generate-self-signed
   docker compose restart structa-proxy
   ```

## DNS Configuration

### Add DNS Records (If Using Let's Encrypt)

For automatic certificate renewal, ensure DNS is configured:

```bash
# Verify DNS resolution
nslookup ctc-research.com
nslookup structa.cloud
nslookup vresume.structa.cloud

# Should return Traefik's public IP
```

### Certificate Validation Records

Some ACME providers may require DNS validation. This is configured in `traefik.yml` under `dnsChallenge` (currently commented out).

## Security Considerations

### Self-Signed Certificates

**When to use**:
- Development and staging environments
- Internal testing
- Temporary deployments

**Limitations**:
- Browser warnings (certificate not trusted)
- No automatic renewal
- Requires manual management

### Let's Encrypt Certificates

**When to use**:
- Production environments
- Public-facing applications
- Automatic renewal needed

**Requirements**:
- Valid email address
- Publicly accessible domains
- Port 80/443 accessible from internet
- Rate limits apply (50 certs per domain per week)

### Certificate Pinning

To prevent man-in-the-middle attacks in API clients:

```bash
# Get certificate public key hash (for pinning)
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -noout -pubkey | \
  openssl pkey -pubin -outform DER | \
  openssl dgst -sha256 -binary | \
  base64
```

## Related Documentation

- [Traefik TLS Configuration](https://doc.traefik.io/traefik/https/tls/)
- [Traefik ACME / Let's Encrypt](https://doc.traefik.io/traefik/https/acme/)
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)
- [OpenSSL Command Reference](https://www.openssl.org/docs/man1.1.1/man1/)

## Quick Reference

```bash
# List certificates
cd /root/site/websites/compose/traefik && ./manage-certs.sh list

# Check expiry
./manage-certs.sh check-expiry

# Validate certificates
./manage-certs.sh validate

# Backup certificates
./manage-certs.sh backup

# Generate new self-signed (365 days)
./manage-certs.sh generate-self-signed

# Restore from backup
./manage-certs.sh restore certs/certs-backup-YYYYMMDD-HHMMSS.tar.gz

# View certificate details
openssl x509 -in certs/ctc-research.crt -noout -text

# Check certificate dates
openssl x509 -in certs/ctc-research.crt -noout -dates
```

## Support & Contact

For SSL certificate issues:
1. Run `./manage-certs.sh help` for usage
2. Check Traefik logs: `docker logs structa-proxy`
3. Review Traefik configuration: `compose/traefik/traefik.yml`
4. Check environment variables: `grep TRAEFIK .env`
