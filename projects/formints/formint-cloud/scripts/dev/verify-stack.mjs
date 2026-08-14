#!/usr/bin/env node
/**
 * Formint Cloud — Live end-to-end stack verification.
 *
 * Boots the two Django roads that replace the removed Robyn server and
 * sweeps the full HTTP surface the frontend consumes:
 *
 *   :8767  — API surface  (daphne, configs.asgi:application) — REST CRUD,
 *            /stats, /health, /fusion/* contract, /api/* bridges +
 *            sync dashboard, /ws/sync-events/ WebSocket.
 *   :8082  — Admin/bolt road (runserver) — Unfold admin + /apis/data/*
 *            bolt analytics dashboards.
 *
 * For every endpoint it asserts the *expected* status code (verified live
 * against a clean seed) and reports PASS/FAIL.  It then runs a full
 * WebSocket frame-exchange parity check on the sync-events protocol
 * (connect → identify → trigger a sync event → assert the frame shapes),
 * mirroring the unit parity contract in backend/apps/test_ws_parity_contract.py.
 * Exits non-zero on any failure so it can gate CI or a pre-push hook.
 *
 * Usage:
 *   node scripts/dev/verify-stack.mjs                 # boot both + sweep
 *   node scripts/dev/verify-stack.mjs --keep-alive    # leave servers running
 *   VERIFY_API_PORT=8767 VERIFY_ADMIN_PORT=8082 node scripts/dev/verify-stack.mjs
 *
 * Exit codes:
 *   0  — every expected endpoint responded correctly
 *   1  — one or more endpoints failed
 *   2  — a server failed to boot / port already in use by another process
 */

import { spawn, spawnSync } from 'node:child_process';
import { closeSync, mkdtempSync, openSync, rmSync, writeSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';
import http from 'node:http';
import { randomBytes } from 'node:crypto';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..'); // formint-cloud/
const BACKEND = join(ROOT, 'backend');
const VENV_PY = join(BACKEND, '.venv', 'bin', 'python');
const DAPHNE = join(BACKEND, '.venv', 'bin', 'daphne');

const API_PORT = Number(process.env.VERIFY_API_PORT || 8767);
const ADMIN_PORT = Number(process.env.VERIFY_ADMIN_PORT || 8082);
const KEEP_ALIVE = process.argv.includes('--keep-alive');

// ── Server orchestration ───────────────────────────────────────────────────

const children = new Set();
const logsDir = mkdtempSync(join(tmpdir(), 'formint-cloud-verify-'));

function boot(name, cmd, args) {
  const log = join(logsDir, `${name}.log`);
  const fd = openSync(log, 'w');
  // Child writes its stdout/stderr directly to the log fd (no parent-owned
  // pipes), so --keep-alive orphans survive the parent's exit without EPIPE.
  const child = spawn(cmd, args, {
    cwd: BACKEND,
    detached: true,
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
    stdio: ['ignore', fd, fd],
  });
  child._logFd = fd;
  children.add(child);
  child.on('error', (e) => {
    // e.g. missing .venv/bin/daphne on a clean clone — report, don't crash.
    try { writeSync(fd, `[spawn error] ${e.message}\n`); } catch { /* ignore */ }
    children.delete(child);
  });
  child.on('exit', () => children.delete(child));
  if (KEEP_ALIVE) child.unref();
  return child;
}

function waitForPort(port, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolvePort) => {
    let settled = false;
    const settle = (v) => { if (!settled) { settled = true; resolvePort(v); } };
    const tryOnce = () => {
      const sock = net.connect({ host: '127.0.0.1', port });
      sock.setTimeout(1500); // never hang on a dropped/backlogged connect
      sock.on('connect', () => { sock.destroy(); settle(true); });
      sock.on('timeout', () => {
        sock.destroy();
        if (Date.now() > deadline) settle(false); else setTimeout(tryOnce, 250);
      });
      sock.on('error', () => {
        sock.destroy();
        if (Date.now() > deadline) settle(false); else setTimeout(tryOnce, 250);
      });
    };
    tryOnce();
  });
}

async function stopServers() {
  for (const child of children) {
    try { child.kill('SIGTERM'); } catch { /* already gone */ }
  }
  const deadline = Date.now() + 5000;
  while (children.size > 0 && Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 100));
  }
  for (const child of children) {
    try { child.kill('SIGKILL'); } catch { /* ignore */ }
  }
  for (const child of children) {
    try { if (child._logFd) closeSync(child._logFd); } catch { /* ignore */ }
  }
  if (!KEEP_ALIVE) rmSync(logsDir, { recursive: true, force: true });
}

// ── HTTP helpers ────────────────────────────────────────────────────────────

function request({ port, method = 'GET', path, body }) {
  return new Promise((resolveReq) => {
    const req = http.request(
      { host: '127.0.0.1', port, path, method, timeout: 8000 },
      (res) => {
        let data = '';
        res.setEncoding('utf8');
        res.on('data', (c) => (data += c));
        res.on('end', () => resolveReq({ status: res.statusCode, body: data }));
      },
    );
    req.on('timeout', () => { req.destroy(); resolveReq({ status: 0, body: 'timeout' }); });
    req.on('error', (e) => resolveReq({ status: 0, body: String(e) }));
    if (body !== undefined) {
      req.setHeader('Content-Type', 'application/json');
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

function wsHandshake(port, path, timeoutMs = 8000) {
  return new Promise((resolveWs) => {
    // RFC 6455 requires a base64-encoded 16-byte nonce.
    const key = randomBytes(16).toString('base64');
  const req = http.request({
    host: '127.0.0.1', port, path,
    headers: {
      Connection: 'Upgrade',
      Upgrade: 'websocket',
      'Sec-WebSocket-Key': key,
      'Sec-WebSocket-Version': '13',
    },
  });
  let done = false;
  const finish = (status, note) => {
    if (done) return;
    done = true;
    resolveWs({ status, note });
  };
  req.on('upgrade', (_res, socket) => { socket.destroy(); finish(101, '101 upgrade'); });
  req.on('response', (res) => finish(res.statusCode, `HTTP ${res.statusCode}`));
  req.on('error', (e) => finish(0, String(e)));
  req.on('close', () => finish(0, 'connection closed'));
  setTimeout(() => { req.destroy(); finish(0, 'timeout'); }, timeoutMs);
  req.end();
});
}

// ── Full WebSocket client (RFC 6455, stdlib only) ───────────────────────────
// Needed for the sync-events parity check: real frame exchange (identify →
// sync_event → broker_message), not just the 101 handshake.

function buildFrame(payload) {
  const data = Buffer.from(payload, 'utf8');
  const mask = randomBytes(4);
  const masked = Buffer.alloc(data.length);
  for (let i = 0; i < data.length; i += 1) masked[i] = data[i] ^ mask[i % 4];
  let header;
  if (data.length < 126) {
    header = Buffer.from([0x81, 0x80 | data.length]);
  } else if (data.length < 65536) {
    header = Buffer.alloc(4);
    header[0] = 0x81;
    header[1] = 0x80 | 126;
    header.writeUInt16BE(data.length, 2);
  } else {
    header = Buffer.alloc(10);
    header[0] = 0x81;
    header[1] = 0x80 | 127;
    header.writeBigUInt64BE(BigInt(data.length), 2);
  }
  return Buffer.concat([header, mask, masked]);
}

class WsClient {
  constructor(port, path = '/ws/sync-events/') {
    this.port = port;
    this.path = path;
    this.socket = null;
    this.buffer = Buffer.alloc(0);
    this.frames = [];
    this.waiters = [];
    this.closed = false;
  }

  connect(timeoutMs = 8000) {
    return new Promise((resolveConnect, rejectConnect) => {
      const req = http.request({
        host: '127.0.0.1',
        port: this.port,
        path: this.path,
        headers: {
          Connection: 'Upgrade',
          Upgrade: 'websocket',
          'Sec-WebSocket-Key': randomBytes(16).toString('base64'),
          'Sec-WebSocket-Version': '13',
        },
      });
      let settled = false;
      const fail = (e) => { if (!settled) { settled = true; rejectConnect(e); } };
      req.on('upgrade', (_res, socket) => {
        this.socket = socket;
        socket.setNoDelay(true);
        socket.on('data', (chunk) => this._onData(chunk));
        socket.on('close', () => { this.closed = true; this._flush(new Error('socket closed')); });
        socket.on('error', (e) => { this.closed = true; this._flush(e); });
        settled = true;
        resolveConnect(this);
      });
      req.on('response', (res) => fail(new Error(`upgrade rejected: HTTP ${res.statusCode}`)));
      req.on('error', fail);
      setTimeout(() => fail(new Error('connect timeout')), timeoutMs);
      req.end();
    });
  }

  send(obj) {
    if (!this.socket || this.closed) throw new Error('socket not open');
    this.socket.write(buildFrame(JSON.stringify(obj)));
  }

  /** Resolve with the next frame matching `predicate` (drains queue first). */
  waitFor(predicate, timeoutMs = 6000, label = 'frame') {
    return new Promise((resolveWait, rejectWait) => {
      const idx = this.frames.findIndex(predicate);
      if (idx !== -1) {
        const [frame] = this.frames.splice(idx, 1);
        return resolveWait(frame);
      }
      const waiter = { predicate, resolve: resolveWait, reject: rejectWait, timer: null };
      waiter.timer = setTimeout(() => {
        const i = this.waiters.indexOf(waiter);
        if (i !== -1) this.waiters.splice(i, 1);
        rejectWait(new Error(`timeout waiting for ${label}`));
      }, timeoutMs);
      this.waiters.push(waiter);
    });
  }

  close() {
    if (this.socket && !this.closed) {
      try { this.socket.write(Buffer.from([0x88, 0x00])); } catch { /* ignore */ }
      try { this.socket.destroy(); } catch { /* ignore */ }
    }
  }

  _onData(chunk) {
    this.buffer = Buffer.concat([this.buffer, chunk]);
    let frame = this._parseFrame();
    while (frame) {
      this._handleFrame(frame);
      frame = this._parseFrame();
    }
  }

  _parseFrame() {
    const buf = this.buffer;
    if (buf.length < 2) return null;
    const b0 = buf[0];
    const b1 = buf[1];
    const fin = (b0 & 0x80) !== 0;
    const opcode = b0 & 0x0f;
    const masked = (b1 & 0x80) !== 0;
    let len = b1 & 0x7f;
    let offset = 2;
    if (len === 126) {
      if (buf.length < 4) return null;
      len = buf.readUInt16BE(2);
      offset = 4;
    } else if (len === 127) {
      if (buf.length < 10) return null;
      len = Number(buf.readBigUInt64BE(2));
      offset = 10;
    }
    let maskKey = null;
    if (masked) {
      if (buf.length < offset + 4) return null;
      maskKey = buf.subarray(offset, offset + 4);
      offset += 4;
    }
    if (buf.length < offset + len) return null;
    let payload = buf.subarray(offset, offset + len);
    if (maskKey) {
      const unmasked = Buffer.alloc(len);
      for (let i = 0; i < len; i += 1) unmasked[i] = payload[i] ^ maskKey[i % 4];
      payload = unmasked;
    }
    this.buffer = buf.subarray(offset + len);
    return { fin, opcode, payload };
  }

  _handleFrame(frame) {
    if (frame.opcode === 0x9) { // ping → pong
      try { this.socket.write(Buffer.concat([Buffer.from([0x8a, frame.payload.length]), frame.payload])); } catch { /* ignore */ }
      return;
    }
    if (frame.opcode === 0x8) { // close → echo + destroy
      this.closed = true;
      try { this.socket.write(Buffer.from([0x88, 0x00])); } catch { /* ignore */ }
      try { this.socket.destroy(); } catch { /* ignore */ }
      return;
    }
    if (frame.opcode === 0x1) { // text
      let msg;
      try { msg = JSON.parse(frame.payload.toString('utf8')); } catch { return; }
      this._flush(null, msg);
    }
    // Binary (0x2) and continuation frames are not produced by the consumer.
  }

  _flush(err, msg) {
    if (msg !== undefined) {
      this.frames.push(msg);
      for (let i = this.waiters.length - 1; i >= 0; i -= 1) {
        const w = this.waiters[i];
        if (w.predicate(msg)) {
          clearTimeout(w.timer);
          this.waiters.splice(i, 1);
          w.resolve(msg);
        }
      }
      return;
    }
    for (const w of this.waiters.splice(0)) {
      clearTimeout(w.timer);
      w.reject(err || new Error('socket closed'));
    }
  }
}

// ── Sync-events WS parity ────────────────────────────────────────────────────
// Live end-to-end pin of the documented sync-events protocol (mirrors the
// backend unit parity contract in backend/apps/test_ws_parity_contract.py):
//   1. connect two real clients (A + B)
//   2. B's connect broadcasts terminal_connected → A receives the sync_event
//   3. A identifies → identify_ack (exact shape)
//   4. POST /api/sync/push/products for a seeded branch → A receives a
//      sync_event with the documented {entity_type, synced, branch, node_id,
//      timestamp} shape, then a broker_message on the branch group.
// The branch is created via manage.py shell (deterministic on any DB state)
// and removed afterwards.

const SEED_BRANCH_CODE = 'VER-E2E';
const SEED_NODE_ID = 'verify-e2e-node';
const SEED_BRANCH_NAME = 'Verify E2E';
const SEED_ORG_SLUG = 'verify-e2e-org';

function manageShell(code) {
  return spawnSync(VENV_PY, ['manage.py', 'shell', '-c', code], {
    cwd: BACKEND, encoding: 'utf8', timeout: 60000,
  });
}

function seedParityBranch() {
  const r = manageShell(`
from apps.core.models import Organization, Branch
org = Organization.objects.filter(slug='${SEED_ORG_SLUG}').first()
if org is None:
    org = Organization.objects.create(name='Verify E2E Org', slug='${SEED_ORG_SLUG}', is_active=True)
Branch.objects.update_or_create(
    code='${SEED_BRANCH_CODE}',
    defaults={
        'organization': org,
        'name': '${SEED_BRANCH_NAME}',
        'node_id': '${SEED_NODE_ID}',
        'is_active': True,
        'sync_enabled': True,
    },
)
print('branch-ready')
`);
  return r.status === 0 && r.stdout.includes('branch-ready');
}

function cleanupParityBranch() {
  manageShell(`
from apps.core.models import Branch, Organization
Branch.objects.filter(code='${SEED_BRANCH_CODE}').delete()
Organization.objects.filter(slug='${SEED_ORG_SLUG}').delete()
print('branch-cleaned')
`);
}

async function runWsParity() {
  let failures = 0;
  const record = (name, ok, detail = '') => {
    if (!ok) failures += 1;
    console.log(`${(ok ? 'PASS' : 'FAIL').padEnd(4)}  ${name}${detail ? `  [${detail}]` : ''}`);
  };

  let a = null;
  let b = null;
  try {
    const seeded = seedParityBranch();
    record('seed verify branch (VER-E2E)', seeded, seeded ? 'branch-ready' : manageShell('print(1)').stderr?.slice(0, 80));

    a = new WsClient(API_PORT);
    b = new WsClient(API_PORT);
    await a.connect();
    await b.connect();
    record('ws connect A + B', true, '101 upgrade x2');

    // B's connect broadcasts terminal_connected to the sync_events group.
    const link = await a.waitFor((m) => m.entity_type === 'terminal_connected', 6000, 'terminal_connected');
    const linkKeys = Object.keys(link).sort().join(',');
    record('sync_event: terminal_connected shape',
      linkKeys === 'branch,entity_type,node_id,synced,timestamp'
        && link.synced === 1
        && typeof link.timestamp === 'string' && !Number.isNaN(Date.parse(link.timestamp)),
      linkKeys);

    // A identifies → exact identify_ack.
    a.send({ type: 'identify', payload: { branch_code: SEED_BRANCH_CODE, node_id: 'verify-node-a' } });
    const ack = await a.waitFor((m) => m.type === 'identify_ack', 6000, 'identify_ack');
    record('identify → identify_ack exact',
      Object.keys(ack).sort().join(',') === 'branch_code,node_id,status,type'
        && ack.type === 'identify_ack'
        && ack.branch_code === SEED_BRANCH_CODE
        && ack.node_id === 'verify-node-a'
        && ack.status === 'registered',
      JSON.stringify(ack));

    // B identifies on the same branch so both join branch_VER-E2E.
    b.send({ type: 'identify', payload: { branch_code: SEED_BRANCH_CODE, node_id: 'verify-node-b' } });
    await b.waitFor((m) => m.type === 'identify_ack', 6000, 'identify_ack (B)');

    // Trigger a real sync event via the receiver endpoint.
    const push = await request({
      port: API_PORT, method: 'POST', path: '/api/sync/push/products',
      body: { node_id: SEED_NODE_ID, products: [{ id: 'e2e-1', name: 'E2E Product', price: 9.99 }] },
    });
    record('POST /api/sync/push/products',
      push.status === 200 && push.body.includes('"synced": 1'),
      `${push.status} ${push.body.slice(0, 80)}`);

    const syncEvent = await a.waitFor((m) => m.entity_type === 'products', 6000, 'sync_event products');
    const evKeys = Object.keys(syncEvent).sort().join(',');
    record('sync_event: products shape',
      evKeys === 'branch,entity_type,node_id,synced,timestamp'
        && syncEvent.synced === 1
        && syncEvent.node_id === SEED_NODE_ID
        && syncEvent.branch === SEED_BRANCH_NAME
        && !Number.isNaN(Date.parse(syncEvent.timestamp)),
      evKeys);

    const bm = await a.waitFor((m) => m.type === 'broker_message', 6000, 'broker_message');
    const inner = bm.message || {};
    record('broker_message envelope (branch group)',
      inner.subtype === 'entity_event'
        && inner.payload && inner.payload.entity_type === 'products'
        && inner.payload.action === 'sync'
        && typeof inner.message_id === 'string'
        && typeof inner.timestamp === 'string',
      `${bm.type} / ${inner.subtype}`);
  } catch (e) {
    record('ws parity sequence', false, String((e && e.message) || e));
  } finally {
    if (a) a.close();
    if (b) b.close();
    cleanupParityBranch();
  }
  return failures;
}

// ── Check table ─────────────────────────────────────────────────────────────
// Each entry: { port, method, path, expect: status | array, body?, label? }

const checks = [
  // ── API surface :8767 — public health/contract ──
  { port: 'api', path: '/health', expect: 200 },
  { port: 'api', path: '/stats', expect: 200 },
  { port: 'api', path: '/fusion/health', expect: 200 },
  { port: 'api', path: '/fusion/render-mode', expect: 200 },
  { port: 'api', path: '/fusion/nav', expect: 200 },
  { port: 'api', path: '/fusion/session-mode', expect: 200 },
  { port: 'api', method: 'POST', path: '/fusion/session-mode', body: { mode: 'data-api' }, expect: 200 },
  { port: 'api', method: 'DELETE', path: '/fusion/session-mode', expect: 200 },
  { port: 'api', path: '/fusion/assets', expect: 200 },
  // ── API surface :8767 — auth-gated CRUD (anonymous ⇒ JSON 401) ──
  { port: 'api', path: '/organizations/', expect: 401 },
  { port: 'api', path: '/branches/', expect: 401 },
  { port: 'api', path: '/leads/', expect: 401 },
  { port: 'api', path: '/contacts/', expect: 401 },
  { port: 'api', path: '/deals/', expect: 401 },
  { port: 'api', path: '/inventory-reports/', expect: 401 },
  { port: 'api', path: '/branch-reports/', expect: 401 },
  { port: 'api', path: '/device-tokens/', expect: 401 },
  { port: 'api', path: '/conflicts/', expect: 401 },
  { port: 'api', path: '/queue/', expect: 401 },
  { port: 'api', path: '/sync/logs/', expect: 401 },
  { port: 'api', path: '/sync/products/', expect: 401 },
  { port: 'api', path: '/sync/sales/', expect: 401 },
  { port: 'api', path: '/sync/inventory/', expect: 401 },
  // ── API surface :8767 — /api/* viewset mount (anonymous ⇒ JSON 401,
  //    no 302 login redirect) ──
  { port: 'api', path: '/api/organizations/', expect: 401 },
  { port: 'api', path: '/api/branches/', expect: 401 },
  { port: 'api', path: '/api/leads/', expect: 401 },
  { port: 'api', path: '/api/contacts/', expect: 401 },
  { port: 'api', path: '/api/deals/', expect: 401 },
  { port: 'api', path: '/api/inventory-reports/', expect: 401 },
  { port: 'api', path: '/api/branch-reports/', expect: 401 },
  { port: 'api', path: '/api/device-tokens/', expect: 401 },
  { port: 'api', path: '/api/conflicts/', expect: 401 },
  { port: 'api', path: '/api/queue/', expect: 401 },
  { port: 'api', path: '/api/sync/logs/', expect: 401 },
  { port: 'api', path: '/api/sync/products/', expect: 401 },
  { port: 'api', path: '/api/sync/sales/', expect: 401 },
  { port: 'api', path: '/api/sync/inventory/', expect: 401 },
  // ── API surface :8767 — community bridges ──
  { port: 'api', path: '/api/health', expect: 200 },
  { port: 'api', path: '/api/sales', expect: 200 },
  { port: 'api', path: '/api/products', expect: 200 },
  { port: 'api', path: '/api/settings', expect: 200 },
  // ── API surface :8767 — sync dashboard (anonymous OK) ──
  { port: 'api', path: '/api/dashboard/branches/health', expect: 200 },
  { port: 'api', path: '/api/dashboard/queue/summary', expect: 200 },
  { port: 'api', path: '/api/dashboard/queue/by-branch', expect: 200 },
  { port: 'api', path: '/api/dashboard/queue/list/pending', expect: 200 },
  { port: 'api', path: '/api/dashboard/conflicts', expect: 200 },
  { port: 'api', path: '/api/dashboard/conflicts/stats', expect: 200 },
  { port: 'api', path: '/api/dashboard/activity', expect: 200 },
  // ── API surface :8767 — sync push receivers (csrf_exempt POST) ──
  // 200 = processed, 400 = invalid JSON, 404 = "no active branch" (empty seed).
  // bodyOn404 proves the 404 is the receiver's JSON business logic, not a
  // Django HTML routing miss.
  { port: 'api', method: 'POST', path: '/api/sync/push/heartbeat', body: {}, expect: [200, 400, 404], bodyOn404: 'No active branch' },
  // ── Admin/bolt road :8082 ──
  { port: 'admin', path: '/health', expect: 200 },
  { port: 'admin', path: '/admin/', expect: [200, 302] },
  { port: 'admin', path: '/admin/login/', expect: 200 },
  { port: 'admin', path: '/apis/data/', expect: 200 },
  { port: 'admin', path: '/apis/data/stats', expect: 200 },
  { port: 'admin', path: '/apis/data/products', expect: 200 },
  { port: 'admin', path: '/apis/data/sales', expect: 200 },
  { port: 'admin', path: '/apis/data/inventory', expect: 200 },
  { port: 'admin', path: '/apis/data/branches', expect: 200 },
  { port: 'admin', path: '/apis/data/sync-logs', expect: 200 },
  { port: 'admin', path: '/apis/data/sync-monitor', expect: 200 },
];

const PORT_FOR = { api: API_PORT, admin: ADMIN_PORT };

// ── Run ─────────────────────────────────────────────────────────────────────

function fmt(ok, expected, got) {
  const mark = ok ? 'PASS' : 'FAIL';
  return `${mark.padEnd(4)} ${String(expected).padEnd(22)} got ${String(got).padEnd(4)}`;
}

async function main() {
  console.log('── Formint Cloud live stack verification ────────────────');
  console.log(`api :8767  = ${API_PORT}   admin :8082 = ${ADMIN_PORT}   keep-alive=${KEEP_ALIVE}`);

  // Boot both roads.
  const api = boot('api', DAPHNE, ['-b', '127.0.0.1', '-p', String(API_PORT), 'configs.asgi:application']);
  const admin = boot('admin', VENV_PY, ['manage.py', 'runserver', `127.0.0.1:${ADMIN_PORT}`, '--noreload']);

  const apiUp = await waitForPort(API_PORT, 45000);
  const adminUp = await waitForPort(ADMIN_PORT, 45000);
  if (!apiUp || !adminUp) {
    console.log(`FATAL: api up=${apiUp} admin up=${adminUp} — see logs in ${logsDir}`);
    await stopServers();
    process.exit(2);
  }
  console.log(`servers up: api=${apiUp} admin=${adminUp}\n`);

  // Sweep.
  let failures = 0;
  for (const c of checks) {
    const res = await request({ port: PORT_FOR[c.port], method: c.method || 'GET', path: c.path, body: c.body });
    const expected = c.expect;
    let ok = Array.isArray(expected) ? expected.includes(res.status) : res.status === expected;
    if (ok && c.bodyOn404 && res.status === 404) ok = res.body.includes(c.bodyOn404);
    if (!ok) failures += 1;
    const label = c.label || `${c.method || 'GET'} ${c.path}`;
    console.log(fmt(ok, JSON.stringify(expected), res.status) + `  ${label}`);
  }

  // WebSocket handshake (both roads serve the ASGI app via daphne/runserver).
  console.log('\n── WebSocket /ws/sync-events/ ──');
  for (const [which, port] of Object.entries(PORT_FOR)) {
    const ws = await wsHandshake(port, '/ws/sync-events/');
    const ok = ws.status === 101; // strict — consumer accepts anonymous, so 101 expected
    if (!ok) failures += 1;
    console.log(fmt(ok, '101', ws.note) + `  ws ${which} :${port}`);
  }

  // Full frame-exchange parity: identify → trigger sync event → assert shape.
  console.log('\n── Sync-events WS parity (identify → push → frame shape) ──');
  failures += await runWsParity();

  console.log(`\n${failures === 0 ? '✅ ALL CHECKS PASSED' : `❌ ${failures} check(s) FAILED`}`);
  if (!KEEP_ALIVE) await stopServers();
  process.exit(failures === 0 ? 0 : 1);
}

main().catch(async (e) => {
  console.error('verify-stack crashed:', e);
  await stopServers();
  process.exit(2);
});
