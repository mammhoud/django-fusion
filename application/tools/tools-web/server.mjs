/**
 * tools-web — vanilla Node.js server for tools.structa.cloud
 * ============================================================
 * Replaces the former Astro SSR app with a zero-framework HTTP server:
 *
 *   GET  /               → public/index.html (dashboard; auth enforced client-side
 *                          via a sign-in modal driven by Alpine + htmx)
 *   GET  /health/        → 200 "healthy\n" (Traefik / Docker healthcheck)
 *   GET  /api/session    → JSON { authenticated, user, unlocked }
 *   POST /api/login      → JSON { success, user } | { error }  (users.yml)
 *   POST /api/logout     → clears the session cookie
 *   POST /api/unlock     → JSON { success, redirect } | { error }
 *                          validates TOOLS_UNLOCK_PASSWORD from the environment
 *   *                    → static assets from public/ (styles, js, vendor, logo)
 *
 * Users come from users.yml (bcrypt hashes). Sessions are a signed HttpOnly
 * cookie; the unlock gate is a separate short-lived cookie so the dashboard
 * itself stays logged in while each tool still asks for the shared password.
 */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';
import bcrypt from 'bcryptjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const PORT = Number(process.env.PORT || 4321);
const HOST = process.env.HOST || '0.0.0.0';

const PUBLIC_DIR = path.join(__dirname, 'public');
const USERS_FILE = path.join(__dirname, 'users.yml');

const SESSION_COOKIE = 'tools_auth_session';
const UNLOCK_COOKIE = 'tools_unlocked';
const SESSION_MAX_AGE = 60 * 60 * 24 * 7; // 7 days
const UNLOCK_MAX_AGE = 60 * 60 * 12; // 12 hours

// Secret used to sign session cookies. Falls back to the unlock password so
// the container works without extra config, but prefers an explicit secret.
const SESSION_SECRET =
  process.env.TOOLS_SESSION_SECRET || process.env.TOOLS_UNLOCK_PASSWORD || 'tools-dev-secret';

// ── Users (users.yml) ────────────────────────────────────────────────────────

let usersCache = null;

function loadUsers() {
  if (usersCache) return usersCache;
  const raw = fs.readFileSync(USERS_FILE, 'utf8');
  const parsed = yaml.load(raw);
  if (!parsed || !Array.isArray(parsed.users)) {
    throw new Error(`Invalid users file at ${USERS_FILE}: expected { users: [] }`);
  }
  usersCache = parsed.users.filter((u) => u.enabled !== false);
  return usersCache;
}

function findUser(username) {
  return loadUsers().find((u) => u.username === username);
}

function authenticate(username, password) {
  const user = findUser(username);
  if (!user) return null;
  if (!bcrypt.compareSync(password || '', user.password_hash)) return null;
  return user;
}

// ── Sessions ─────────────────────────────────────────────────────────────────

function sign(value) {
  return crypto.createHmac('sha256', SESSION_SECRET).update(value).digest('hex').slice(0, 32);
}

function makeSessionCookie(user) {
  const payload = Buffer.from(
    JSON.stringify({
      username: user.username,
      role: user.role,
      name: user.name,
      email: user.email,
    })
  ).toString('base64url');
  const mac = sign(payload);
  return `${SESSION_COOKIE}=${payload}.${mac}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${SESSION_MAX_AGE}`;
}

function parseCookies(req) {
  const out = {};
  const header = req.headers.cookie;
  if (!header) return out;
  for (const part of header.split(';')) {
    const idx = part.indexOf('=');
    if (idx === -1) continue;
    const key = part.slice(0, idx).trim();
    const value = part.slice(idx + 1).trim();
    if (key) out[key] = value;
  }
  return out;
}

function readSession(req) {
  const cookies = parseCookies(req);
  const cookie = cookies[SESSION_COOKIE];
  if (!cookie) return null;
  const dot = cookie.lastIndexOf('.');
  if (dot === -1) return null;
  const payload = cookie.slice(0, dot);
  const mac = cookie.slice(dot + 1);
  if (sign(payload) !== mac) return null;
  try {
    const user = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));
    return user && user.username ? user : null;
  } catch {
    return null;
  }
}

function isUnlocked(req) {
  const cookies = parseCookies(req);
  const cookie = cookies[UNLOCK_COOKIE];
  if (!cookie) return false;
  const dot = cookie.lastIndexOf('.');
  if (dot === -1) return false;
  const payload = cookie.slice(0, dot);
  const mac = cookie.slice(dot + 1);
  if (sign(payload) !== mac) return false;
  return payload === 'ok';
}

function makeUnlockCookie() {
  const mac = sign('ok');
  return `${UNLOCK_COOKIE}=ok.${mac}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${UNLOCK_MAX_AGE}`;
}

function clearCookie(name) {
  return `${name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`;
}

// ── Request helpers ──────────────────────────────────────────────────────────

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => {
      data += chunk;
      if (data.length > 1e6) {
        reject(new Error('Body too large'));
        req.destroy();
      }
    });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

function parseForm(body) {
  const out = {};
  if (!body) return out;
  for (const part of body.split('&')) {
    const idx = part.indexOf('=');
    if (idx === -1) continue;
    const key = decodeURIComponent(part.slice(0, idx).replace(/\+/g, ' '));
    const value = decodeURIComponent(part.slice(idx + 1).replace(/\+/g, ' '));
    out[key] = value;
  }
  return out;
}

function sendJson(res, status, data, extraHeaders = {}) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    ...extraHeaders,
  });
  res.end(body);
}

function sendFile(res, filePath, contentType) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    const cacheable = contentType.startsWith('text/html') ? 'no-cache' : 'public, max-age=86400';
    res.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': cacheable,
    });
    res.end(data);
  });
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.json': 'application/json; charset=utf-8',
};

// ── Static tool registry (kept in sync with tools-proxy nginx routes) ───────

const TOOLS = [
  { category: 'notes', name: 'Blinko', description: 'Self-hosted AI note tool. Sign up on first visit — no defaults.', path: '/notes/', internal: true },
  { category: 'documentation', name: 'Docs · Docus', description: 'Product and infrastructure guides, English + Arabic, full sidebar navigation.', path: '/docs/', internal: true },
  { category: 'database', name: 'Adminer', description: 'Lightweight database administration UI for PostgreSQL and friends.', path: '/adminer/', internal: true },
  { category: 'email', name: 'Mailpit', description: 'Email catcher — inspect outbound mail from staging and dev.', path: '/mailpit/', internal: true },
  { category: 'observability', name: 'Grafana', description: 'Dashboards on top of Prometheus metrics for the shared stack.', path: '/grafana/', internal: true },
  { category: 'automation', name: 'xyOps', description: 'Job scheduling, workflows, server monitoring, alerts, and incident tickets.', host: 'https://ops.structa.cloud', external: true },
  { category: 'workspace', name: 'Space', description: 'Cloud development environment — VS Code, terminals, AI agents.', host: 'https://space.structa.cloud', external: true },
  { category: 'proxy', name: 'Proxy health', description: 'tools-proxy liveness endpoint — plain-text 200, used by Traefik.', path: '/health/', internal: true },
];

// ── Router ───────────────────────────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = url.pathname;

  // Health
  if (pathname === '/health/') {
    res.writeHead(200, { 'Content-Type': 'text/plain', 'Cache-Control': 'no-store' });
    res.end('healthy\n');
    return;
  }

  // API
  if (pathname === '/api/session' && req.method === 'GET') {
    const session = readSession(req);
    const unlocked = isUnlocked(req);
    sendJson(res, 200, {
      authenticated: Boolean(session),
      user: session,
      unlocked,
    });
    return;
  }

  if (pathname === '/api/login' && req.method === 'POST') {
    try {
      const form = parseForm(await readBody(req));
      const user = authenticate(form.username, form.password);
      if (!user) {
        sendJson(res, 401, { error: 'Invalid username or password' });
        return;
      }
      sendJson(res, 200, { success: true, user: { username: user.username, role: user.role, name: user.name, email: user.email } }, {
        'Set-Cookie': makeSessionCookie(user),
      });
    } catch (err) {
      sendJson(res, 400, { error: err.message || 'Bad request' });
    }
    return;
  }

  if (pathname === '/api/logout' && req.method === 'POST') {
    sendJson(res, 200, { success: true }, {
      'Set-Cookie': clearCookie(SESSION_COOKIE) + ', ' + clearCookie(UNLOCK_COOKIE),
    });
    return;
  }

  if (pathname === '/api/unlock' && req.method === 'POST') {
    const session = readSession(req);
    if (!session) {
      sendJson(res, 401, { error: 'Sign in first' });
      return;
    }
    try {
      const form = parseForm(await readBody(req));
      const expected = process.env.TOOLS_UNLOCK_PASSWORD || '';
      const tool = TOOLS.find((t) => (t.path || t.host) === form.tool);
      if (!expected) {
        sendJson(res, 500, { error: 'TOOLS_UNLOCK_PASSWORD is not configured' });
        return;
      }
      if (!form.password || form.password !== expected) {
        sendJson(res, 401, { error: 'Incorrect password for this tool' });
        return;
      }
      // Redirect to the requested tool if it is a known one, else back to /.
      const redirect = tool ? tool.path || tool.host : '/';
      sendJson(res, 200, { success: true, redirect }, {
        'Set-Cookie': makeUnlockCookie(),
      });
    } catch (err) {
      sendJson(res, 400, { error: err.message || 'Bad request' });
    }
    return;
  }

  // Static assets (public/)
  if (pathname === '/' || pathname === '/index.html') {
    sendFile(res, path.join(PUBLIC_DIR, 'index.html'), MIME['.html']);
    return;
  }
  if (pathname === '/login' || pathname === '/login/') {
    // Sign-in now lives in a modal on the dashboard — redirect.
    res.writeHead(302, { Location: '/' });
    res.end();
    return;
  }

  // Avoid path traversal
  const rel = pathname.replace(/^\/+/, '');
  const filePath = path.resolve(PUBLIC_DIR, rel);
  if (!filePath.startsWith(PUBLIC_DIR + path.sep) && filePath !== PUBLIC_DIR) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  if (MIME[ext] && fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    sendFile(res, filePath, MIME[ext]);
    return;
  }

  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('Not found');
});

server.listen(PORT, HOST, () => {
  console.log(`tools-web listening on http://${HOST}:${PORT}`);
});
