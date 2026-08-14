#!/bin/bash
# Waits for the coder/space/docs.structa.cloud AAAA records to be repointed to
# this host's IPv6 (2a02:4780:28:4cb8::1), then restarts Traefik so ACME
# re-issues certs, and tails the logs for issuance success/failure.
LOG=/tmp/tls-fix.log
OLD="2a02:4780:41:3f58::1"
NEW="2a02:4780:28:4cb8::1"
: > "$LOG"
echo "[$(date -u +%H:%M:%S)] watcher started; waiting for AAAA repoint (old=$OLD new=$NEW)" >> "$LOG"

repointed() {
  local ip
  ip=$(timeout 8 dig +short AAAA coder.structa.cloud @1.1.1.1 2>/dev/null)
  case "$ip" in
    *"$NEW"*) return 0 ;;
    *"$OLD"*) return 1 ;;
    *) return 1 ;;
  esac
}

waited=0
while [ "$waited" -lt 3600 ]; do
  if repointed; then
    echo "[$(date -u +%H:%M:%S)] AAAA repointed -> $NEW (after ${waited}s). Restarting Traefik..." >> "$LOG"
    docker restart default-proxy >> "$LOG" 2>&1
    echo "[$(date -u +%H:%M:%S)] waiting for issuance..." >> "$LOG"
    sleep 60
    docker logs default-proxy --since 5m 2>&1 | grep -iE "Obtaining bundled SAN certificate|Unable to obtain ACME|error" \
      | grep -iE "coder|space|docs|blinko|Unable" | tail -12 >> "$LOG"
    echo "[$(date -u +%H:%M:%S)] done. cert check:" >> "$LOG"
    for h in coder space docs; do
      echo "--- $h: $(timeout 10 bash -c "echo | openssl s_client -connect localhost:443 -servername $h.structa.cloud 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null" | tr '\n' ' ')" >> "$LOG"
    done
    exit 0
  fi
  sleep 20
  waited=$((waited + 20))
done
echo "[$(date -u +%H:%M:%S)] timeout after 1h: AAAA still not repointed" >> "$LOG"
exit 1
