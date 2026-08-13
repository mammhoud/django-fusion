#!/usr/bin/env bash
cd /home/structa.cloud/projects/landing-fusion
# Kill any stale dev servers from earlier sessions
for port in 8074 4321; do
  fuser -k "$port"/tcp 2>/dev/null || true
done
sleep 1

# Backend on 8074 (the frontend API_BASE default)
cd backend
nohup make dev > /tmp/landing-backend.log 2>&1 &
echo "backend pid: $!"

# Frontend on 4321
cd ../frontend
nohup npm run dev -- --port 4321 > /tmp/landing-frontend.log 2>&1 &
echo "frontend pid: $!"

sleep 15
echo '=== backend health ==='
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8074/apis/products/ || true
echo
echo '=== frontend up? ==='
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:4321/products/ || true
echo
