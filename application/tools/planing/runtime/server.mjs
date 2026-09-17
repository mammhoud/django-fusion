import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import express from 'express';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { Surreal, RecordId, StringRecordId } from 'surrealdb';
import { renderMarkdown as renderSharedMarkdown } from './public/markdown.mjs';
import { sampleContent } from './public/sample-content.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const port = Number(process.env.PLANING_PORT || 1111);
const surrealUrl = (process.env.SURREALDB_URL || 'http://surrealdb:8000/rpc').replace(/\/rpc\/?$/, '');
const surrealUser = process.env.SURREALDB_USER || 'root';
const surrealPass = process.env.SURREALDB_PASS || 'planing';
const surrealNs = process.env.SURREALDB_NS || 'planing';
const surrealDb = process.env.SURREALDB_DB || 'planing';
const jwtSecret = process.env.NEXTAUTH_SECRET || 'planing-secret-change-me';
const uploadDir = process.env.UPLOAD_DIR || path.join(__dirname, 'data', 'uploads');
const maxUploadBytes = Number(process.env.MAX_UPLOAD_BYTES || 26214400);

// Chat context roots: the directories a chat is allowed to read from. The
// `project` root is mounted read-only (the repository the notes are about),
// `documents` and `notes` live in the persisted volume so members can drop
// files in and let the AI work on them. Roots are resolved from configuration
// only — a request can never introduce a new path, only pick one already
// listed here. PLANING_CONTEXT_ROOTS overrides the defaults as a comma-separated
// `id=path` list; `id:label=path` adds a display label.
const contextIgnoredDirs = new Set(['node_modules', '.git', '.venv', 'venv', '__pycache__', 'dist', 'build', '.next', '.nuxt', '.svelte-kit', '.cache', '.turbo', '.parcel-cache', 'target', 'coverage', 'test-results', 'playwright-report', '.mypy_cache', '.ruff_cache', '.pytest_cache', '.idea', '.vscode']);
const contextTextExtensions = new Set(['.md', '.markdown', '.mdx', '.txt', '.json', '.jsonc', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.env', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.py', '.rb', '.go', '.rs', '.java', '.kt', '.cs', '.php', '.sql', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.css', '.scss', '.sass', '.less', '.html', '.htm', '.xml', '.svg', '.csv', '.tsv', '.log', '.lua', '.ex', '.exs', '.vue', '.svelte', '.astro', '.prisma', '.graphql', '.gql', '.tf', '.hcl', '.c', '.h', '.cc', '.cpp', '.hpp', '.swift', '.dart', '.r', '.jl', '.pl', '.diff', '.patch', '.just', '.mk']);
const contextTextNames = new Set(['dockerfile', 'makefile', 'readme', 'readme.md', 'license', 'changelog', 'procfile', 'justfile', 'agents.md', '.editorconfig', '.gitignore', '.dockerignore', '.npmrc', '.nvmrc', '.env.example']);
// PDFs contribute extracted text; images are sent to the model as data URLs, so
// they carry their own (smaller) cap and count against a separate limit.
const contextPdfExtensions = new Set(['.pdf']);
const contextImageExtensions = new Map([['.png', 'image/png'], ['.jpg', 'image/jpeg'], ['.jpeg', 'image/jpeg'], ['.webp', 'image/webp'], ['.gif', 'image/gif']]);
const maxContextBytes = Number(process.env.PLANING_CONTEXT_MAX_BYTES || 262144);
const maxContextImageBytes = Number(process.env.PLANING_CONTEXT_MAX_IMAGE_BYTES || 2097152);
const maxContextFiles = 12;
const maxContextImages = 4;
const maxContextBlockChars = 96000;

function defaultContextRoots() {
  const override = String(process.env.PLANING_CONTEXT_ROOTS || '').trim();
  if (override) {
    return override.split(',').map((entry) => {
      const [head, dir] = entry.split('=').map((part) => (part || '').trim());
      if (!head || !dir) return null;
      const [id, label] = head.split(':').map((part) => part.trim());
      if (!id) return null;
      return {
        id: id.replace(/[^a-z0-9-]+/gi, '-').toLowerCase().slice(0, 24),
        label: label || id,
        dir: path.resolve(dir),
        kind: id === 'project' ? 'project' : 'documents',
        writable: id !== 'project',
      };
    }).filter(Boolean);
  }
  return [
    { id: 'project', label: 'Project directory', dir: process.env.PLANING_CONTEXT_PROJECT_DIR || path.join(__dirname, 'context'), kind: 'project', writable: false },
    { id: 'documents', label: 'Documents', dir: process.env.PLANING_CONTEXT_DOCUMENTS_DIR || path.join(uploadDir, '..', 'documents'), kind: 'documents', writable: true },
    { id: 'notes', label: 'Notes folder', dir: process.env.PLANING_CONTEXT_NOTES_DIR || path.join(uploadDir, '..', 'notes'), kind: 'notes', writable: true },
  ];
}

const contextRoots = defaultContextRoots();
for (const root of contextRoots) {
  try { fs.mkdirSync(root.dir, { recursive: true }); } catch { /* read-only mount or missing volume */ }
}

if (process.env.DATABASE_URL || process.env.POSTGRES_HOST || process.env.PGHOST) {
  throw new Error('PostgreSQL configuration is forbidden in the SurrealDB-only Planing runtime');
}

// Edge writes on this stack: `RELATE` cannot take bound or function-valued
// endpoints through the HTTP driver (v1.5.6 parses `type::thing(...)` in a
// RELATE path as a syntax error and binding a RecordId yields `in = NONE`), and
// `CREATE`/`INSERT` on a RELATION table are rejected. What does work is
// upserting the edge by a deterministic id with explicit `in`/`out` fields,
// which produces exactly the record shape RELATE would have.
const recordLiteral = (table, id) => {
  const value = String(id);
  return /^[A-Za-z0-9_]+$/.test(value) ? `${table}:${value}` : `${table}:⟨${value}⟩`;
};

// Nested objects and arrays inside a *bound* parameter are silently dropped on
// this driver/engine pair (only scalars survive), so structured values are
// embedded as SurrealQL literals instead. Bound parameters stay for scalars.
function inlineValue(value) {
  if (value === null || value === undefined) return 'NONE';
  if (value instanceof Date) return `d${JSON.stringify(value.toISOString())}`;
  if (Array.isArray(value)) {
    const items = value.filter((entry) => entry !== null && entry !== undefined).map(inlineValue);
    return `[${items.join(', ')}]`;
  }
  if (typeof value === 'object') {
    if ('tb' in value && 'id' in value) return recordLiteral(value.tb, value.id);
    const entries = Object.entries(value)
      .filter(([, entry]) => entry !== null && entry !== undefined)
      .map(([key, entry]) => `${/^[A-Za-z_][A-Za-z0-9_]*$/.test(key) ? key : JSON.stringify(key)}: ${inlineValue(entry)}`);
    return `{ ${entries.join(', ')} }`;
  }
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : 'NONE';
  return JSON.stringify(String(value));
}

const literalAssignments = (data) => Object.entries(data)
  .filter(([, value]) => value !== null && value !== undefined)
  .map(([key, value]) => `${key} = ${inlineValue(value)}`);

async function createRecord(table, data, suffix = '') {
  return q(`CREATE ${table}${suffix} SET ${literalAssignments(data).join(', ')};`);
}

async function updateRecord(table, id, data) {
  const assignments = literalAssignments(data);
  if (!assignments.length) return [];
  return q(`UPDATE ${table}:⟨${String(id).replace(/[^A-Za-z0-9_-]+/g, '_')}⟩ SET ${assignments.join(', ')};`);
}

const edgeId = (...parts) => parts
  .map((part) => String(part).replace(/[^A-Za-z0-9_]+/g, '_'))
  .join('__')
  .slice(0, 150);

async function upsertEdge(edgeTable, fromTable, fromId, toTable, toId, data = {}, extraKey = '') {
  const id = edgeId(fromTable, fromId, toTable, toId, extraKey);
  const assignments = [`in = ${recordLiteral(fromTable, fromId)}`, `out = ${recordLiteral(toTable, toId)}`];
  const vars = {};
  Object.entries(data).forEach(([key, value], index) => {
    // option<...> fields reject explicit nulls in schemafull mode.
    if (value === null || value === undefined || !/^[a-z_][a-z0-9_]*$/i.test(key)) return;
    vars[`v${index}`] = value;
    assignments.push(`${key} = $v${index}`);
  });
  return q(`UPDATE ${edgeTable}:⟨${id}⟩ SET ${assignments.join(', ')};`, vars);
}

// Consolidated schema version. The incremental "workspace-vN" steps (v1..v13)
// have been folded into one canonical base. The bootstrap below is idempotent:
// every DEFINE and backfill UPDATE can run against an existing database, so a
// deployment that predates the consolidation converges on this version without
// a destructive migration. Bump the string only when a change is not backwards
// compatible.
const schemaVersion = 'workspace-v1';
// Workspace roles, most powerful first. `superadmin` is the bootstrap account
// (instance-wide); `owner` holds the workspace and is the only role that can
// hand out ownership or archive the workspace; `commenter` is the read-and-reply
// role for reviewers. The earlier `admin`/`editor`/`viewer` roles stay valid so
// existing memberships keep working.
const roles = ['superadmin', 'owner', 'admin', 'editor', 'commenter', 'viewer'];
const ownerRoles = ['superadmin', 'owner'];
const rolePermissions = {
  superadmin: ['notes:read', 'notes:write', 'categories:write', 'members:write', 'settings:write', 'comments:write', 'workspace:manage'],
  owner: ['notes:read', 'notes:write', 'categories:write', 'members:write', 'settings:write', 'comments:write', 'workspace:manage'],
  admin: ['notes:read', 'notes:write', 'categories:write', 'members:write', 'settings:write', 'comments:write'],
  editor: ['notes:read', 'notes:write', 'categories:write', 'comments:write'],
  commenter: ['notes:read', 'comments:write'],
  viewer: ['notes:read'],
};
const roleRank = { viewer: 1, commenter: 2, editor: 3, admin: 4, owner: 5, superadmin: 6 };
// Roles that can be handed out through the People tab. `superadmin` is never
// grantable here: it is instance-wide, not a workspace membership.
const grantableRoles = ['owner', 'admin', 'editor', 'commenter', 'viewer'];
const isOwnerRole = (role) => ownerRoles.includes(role);
const inviteTtlDays = 14;

// Who may hand out which role: a member can grant roles at or below their own
// rank, so only an owner (or the bootstrap superadmin) can create another owner.
function canGrantRole(actorRole, targetRole) {
  if (!grantableRoles.includes(targetRole)) return false;
  return (roleRank[actorRole] || 0) >= (roleRank[targetRole] || 0);
}
const themes = ['light', 'dark', 'system'];
// Theme variants ported from the Formints editions (ThemeContext.tsx): each
// variant is a surface-palette personality with light and dark counterparts.
// Accent and mode stay independent axes on top of the variant.
const themeVariants = ['default', 'corporate', 'luxury', 'pastel', 'perplexity'];
const accents = ['violet', 'blue', 'green', 'orange', 'red'];
const fontScales = ['compact', 'default', 'large'];
const styleVariants = ['sharp', 'rounded', 'compact', 'wide'];
const radiusScales = ['none', 'subtle', 'default', 'soft', 'full'];
const edgeStrengths = ['soft', 'default', 'strong'];
const shadowDepths = ['flat', 'default', 'floating'];
const densities = ['compact', 'cozy', 'comfortable'];
// Element-tier styles (component tokens): shape personality of small controls.
const buttonStyles = ['default', 'outline', 'solid', 'ghost'];
const badgeStyles = ['default', 'tinted', 'outline', 'solid'];

const defaultWorkspace = {
  name: 'Planing workspace',
  description: 'A shared stream for people and agents.',
  default_category: 'notes',
  ai_context: 'Keep answers concise, cite the relevant note, and ask before changing shared context.',
  theme: 'system',
  accent: 'violet',
  font_scale: 'default',
};

const defaultCategories = [
  { name: 'Notes', slug: 'notes', color: '#2563eb', icon: 'N', is_system: true },
  { name: 'Agent', slug: 'agent', color: '#7c3aed', icon: 'A', is_system: true },
];

// The legacy 'planing' system lane was removed from defaults; existing
// deployments keep their data (never auto-delete user content).

const defaultPrompts = [
  { id: 'concise-answer', title: 'Concise answer', body: 'Answer the user in at most five sentences. Cite note titles when you rely on workspace context.' },
  { id: 'meeting-notes', title: 'Meeting notes cleanup', body: 'Turn the following raw transcript into clean meeting notes with decisions, owners, and open questions.' },
  { id: 'explain-code', title: 'Explain this code', body: 'Explain what the attached code does step by step, then list edge cases and possible improvements.' },
  { id: 'summarize-thread', title: 'Summarize a thread', body: 'Summarize the conversation so far into bullet points and end with the three most important next actions.' },
  // Study flows (from the book-study / exam-coach skill patterns): compile,
  // test recall, and schedule review rather than only answering questions.
  { id: 'study-notes', title: 'Study notes from source', body: 'Turn the material below into study notes: a one-line summary, a key-terms table, three worked examples, and an open-questions list. Keep headings short and link related concepts with [[double brackets]].' },
  { id: 'flashcards', title: 'Flashcards (Q/A)', body: 'Produce 10 flashcards from the material as a two-column markdown table of Question and Answer. Questions must be answerable without the original text.' },
  { id: 'quiz-me', title: 'Quiz me (5 questions)', body: 'Write five increasingly difficult questions about the material, one at a time, and wait for my answer before revealing the correct response with a short explanation.' },
  { id: 'revision-summary', title: 'Revision summary', body: 'Compress the material into a revision sheet: definition, why it matters, common mistakes, and a 3-item recall checklist.' },
  { id: 'explain-tutor', title: 'Explain like a tutor', body: 'Explain the concept as a patient tutor: intuition first, then formal definition, then one counterexample, then how to recognise it in an exam question.' },
];

let db;
let reauthInFlight = null;

// The bundled SurrealDB driver can hand back either a flat result or a
// per-statement array; normalise to the first statement's rows.
function unwrapResult(result) {
  return Array.isArray(result) && Array.isArray(result[0]) ? result[0] : result;
}

const AUTH_ERROR = /authentication|unauthorized|invalid token|not authenticated/i;

// The HTTP transport signs in once at boot and then reuses that token. If the
// engine restarts or rotates its signing key the token goes stale and every
// query fails until the process restarts. Re-sign in (once, shared across
// concurrent failures) so a long-running deployment heals itself.
async function reauthenticate() {
  if (!reauthInFlight) {
    reauthInFlight = (async () => {
      // Rebuild the client instead of only signing in again on the existing
      // socket. SurrealDB can rotate a token or close an HTTP session while
      // the process remains alive; reusing that client caused every health
      // probe and worker retry to emit the same authentication error forever.
      const next = new Surreal();
      await next.connect(surrealUrl);
      await next.signin({ username: surrealUser, password: surrealPass });
      await next.use({ namespace: surrealNs, database: surrealDb });
      const previous = db;
      db = next;
      try { await previous?.close(); } catch { /* stale client is disposable */ }
    })().finally(() => { reauthInFlight = null; });
  }
  await reauthInFlight;
}

async function q(sql, vars = {}) {
  try {
    return unwrapResult(await db.query(sql, vars));
  } catch (error) {
    if (!AUTH_ERROR.test(String(error?.message || ''))) throw error;
    await reauthenticate();
    return unwrapResult(await db.query(sql, vars));
  }
}

async function connectSurreal() {
  db = new Surreal();
  // The engine may still be starting when we boot (compose ordering, test
  // harnesses), so retry the handshake briefly instead of dying on first try.
  const maxAttempts = 30;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      await db.connect(surrealUrl);
      await db.signin({ username: surrealUser, password: surrealPass });
      break;
    } catch (error) {
      if (attempt === maxAttempts) throw error;
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }
  await db.use({ namespace: surrealNs, database: surrealDb });
  await q('RETURN 1;');
  await dedupeCategories();
  await q(`
    DEFINE TABLE workspace SCHEMAFULL;
    DEFINE FIELD name ON workspace TYPE option<string> DEFAULT 'Planing workspace';
    DEFINE FIELD description ON workspace TYPE option<string> DEFAULT 'A shared stream for people and agents.';
    DEFINE FIELD default_category ON workspace TYPE option<string> DEFAULT 'notes';
    DEFINE FIELD ai_context ON workspace TYPE option<string> DEFAULT '';
    DEFINE FIELD theme ON workspace TYPE option<string> DEFAULT 'system';
    DEFINE FIELD theme_variant ON workspace TYPE option<string> DEFAULT 'default';
    DEFINE FIELD button_style ON workspace TYPE option<string> DEFAULT 'default';
    DEFINE FIELD badge_style ON workspace TYPE option<string> DEFAULT 'default';
    DEFINE FIELD accent ON workspace TYPE option<string> DEFAULT 'violet';
    DEFINE FIELD font_scale ON workspace TYPE option<string> DEFAULT 'default';
    DEFINE FIELD style_variant ON workspace TYPE option<string> DEFAULT 'sharp';
    DEFINE FIELD radius_scale ON workspace TYPE option<string> DEFAULT 'default';
    DEFINE FIELD edge_strength ON workspace TYPE option<string> DEFAULT 'default';
    DEFINE FIELD shadow_depth ON workspace TYPE option<string> DEFAULT 'default';
    DEFINE FIELD density ON workspace TYPE option<string> DEFAULT 'cozy';
    DEFINE FIELD slug ON workspace TYPE option<string>;
    // The configured context roots this workspace may read. An empty list means
    // every configured root; a populated list is the allow-list for chats here.
    DEFINE FIELD context_roots ON workspace TYPE option<array> DEFAULT [];
    DEFINE FIELD created_by ON workspace TYPE option<record<account>>;
    DEFINE FIELD created_at ON workspace TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON workspace TYPE option<datetime> DEFAULT time::now();

    DEFINE TABLE category SCHEMAFULL;
    DEFINE FIELD name ON category TYPE string;
    DEFINE FIELD slug ON category TYPE string;
    DEFINE FIELD color ON category TYPE option<string> DEFAULT '#64748b';
    DEFINE FIELD icon ON category TYPE option<string> DEFAULT 'C';
    DEFINE FIELD is_system ON category TYPE option<bool> DEFAULT false;
    DEFINE FIELD created_at ON category TYPE option<datetime> DEFAULT time::now();
    // Lane slugs are unique per workspace, not globally: every workspace has its
    // own "notes" lane, and a slug only has to be stable inside one workspace.
    REMOVE INDEX IF EXISTS category_slug ON category;
    DEFINE INDEX category_ws_slug ON category FIELDS workspace, slug UNIQUE;

    DEFINE TABLE account SCHEMAFULL;
    DEFINE FIELD name ON account TYPE string;
    DEFINE FIELD password_hash ON account TYPE string;
    DEFINE FIELD role ON account TYPE string;
    DEFINE FIELD workspace ON account TYPE option<record<workspace>> DEFAULT workspace:default;
    // The workspace this account is currently looking at. Membership is still
    // the authority: switching validates the edge before the field is written.
    DEFINE FIELD active_workspace ON account TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_at ON account TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX account_name ON account FIELDS name UNIQUE;

    DEFINE TABLE tag SCHEMAFULL;
    DEFINE FIELD name ON tag TYPE string;
    DEFINE FIELD created_at ON tag TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX tag_name ON tag FIELDS name UNIQUE;

    DEFINE TABLE notes SCHEMAFULL;
    DEFINE FIELD content ON notes TYPE string;
    DEFINE FIELD category ON notes TYPE record<category>;
    DEFINE FIELD account ON notes TYPE record<account>;
    DEFINE FIELD tags ON notes TYPE option<array> DEFAULT [];
    DEFINE FIELD tags.* ON notes TYPE option<record<tag>>;
    DEFINE FIELD is_archived ON notes TYPE option<bool> DEFAULT false;
    DEFINE FIELD is_recycle ON notes TYPE option<bool> DEFAULT false;
    DEFINE FIELD is_top ON notes TYPE option<bool> DEFAULT false;
    DEFINE FIELD is_share ON notes TYPE option<bool> DEFAULT false;
    // FLEXIBLE is load-bearing on v1.5.6: a plain object field type strips
    // every key from the value, so metadata/flags/mapping would read back empty.
    DEFINE FIELD metadata ON notes FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD created_at ON notes TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON notes TYPE option<datetime> DEFAULT time::now();
    // ---- planning model (kanban + calendar) ----
    // A note doubles as a plan item: status is its kanban column, position
    // is its manual order inside that column, and the three dates drive the
    // calendar. Keeping these as first-class fields (not flags) lets the kanban
    // and calendar queries use real indexes instead of scanning the JSON bag.
    DEFINE FIELD status ON notes TYPE option<string> DEFAULT 'todo';
    DEFINE FIELD priority ON notes TYPE option<string> DEFAULT 'medium';
    DEFINE FIELD due_date ON notes TYPE option<datetime>;
    DEFINE FIELD start_date ON notes TYPE option<datetime>;
    DEFINE FIELD end_date ON notes TYPE option<datetime>;
    DEFINE FIELD position ON notes TYPE option<number> DEFAULT 0;
    DEFINE FIELD event_color ON notes TYPE option<string>;
    DEFINE FIELD assignee ON notes TYPE option<record<account>>;
    DEFINE INDEX notes_status ON notes FIELDS workspace, status;
    DEFINE INDEX notes_position ON notes FIELDS workspace, status, position;
    DEFINE INDEX notes_due ON notes FIELDS workspace, due_date;
    DEFINE INDEX notes_start ON notes FIELDS workspace, start_date;

    DEFINE TABLE attachments SCHEMAFULL;
    DEFINE FIELD name ON attachments TYPE string;
    DEFINE FIELD path ON attachments TYPE string;
    DEFINE FIELD size ON attachments TYPE number;
    DEFINE FIELD type ON attachments TYPE string;
    DEFINE FIELD note ON attachments TYPE option<record<notes>>;
    DEFINE FIELD account ON attachments TYPE option<record<account>>;
    DEFINE FIELD sort_order ON attachments TYPE number DEFAULT 0;
    DEFINE FIELD created_at ON attachments TYPE datetime DEFAULT time::now();

    // Phase 2 tenancy: notes and categories carry a workspace link so every
    // read/mutation can be bounded by membership; the edge table is the single
    // source of the account→workspace role. Enforced per-query in SurrealQL.
    DEFINE FIELD workspace ON notes TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD workspace ON category TYPE option<record<workspace>> DEFAULT workspace:default;

    DEFINE TABLE workspace_member TYPE RELATION IN account OUT workspace SCHEMAFULL;
    DEFINE FIELD role ON workspace_member TYPE string;
    DEFINE FIELD created_by ON workspace_member TYPE option<record<account>>;
    DEFINE FIELD created_at ON workspace_member TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX member_unique ON workspace_member FIELDS in, out UNIQUE;

    DEFINE TABLE workspace_invitation SCHEMAFULL;
    DEFINE FIELD code ON workspace_invitation TYPE string;
    DEFINE FIELD role ON workspace_invitation TYPE string;
    DEFINE FIELD workspace ON workspace_invitation TYPE record<workspace>;
    DEFINE FIELD created_by ON workspace_invitation TYPE record<account>;
    DEFINE FIELD accepted_at ON workspace_invitation TYPE option<datetime>;
    DEFINE FIELD revoked_at ON workspace_invitation TYPE option<datetime>;
    // Per-workspace codes are time-boxed: an unclaimed code stops working after
    // inviteTtlDays instead of standing open forever.
    DEFINE FIELD expires_at ON workspace_invitation TYPE option<datetime>;
    DEFINE FIELD created_at ON workspace_invitation TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX invitation_code ON workspace_invitation FIELDS code UNIQUE;

    // Phase 2 comments: a thread hangs off one note and repeats that note's
    // workspace, so a comment is unreadable from any other workspace even by id.
    // Deletion is a soft flag so a thread keeps its shape and its audit trail.
    DEFINE TABLE note_comment SCHEMAFULL;
    DEFINE FIELD note ON note_comment TYPE record<notes>;
    DEFINE FIELD workspace ON note_comment TYPE record<workspace>;
    DEFINE FIELD author ON note_comment TYPE option<record<account>>;
    DEFINE FIELD body ON note_comment TYPE string;
    DEFINE FIELD is_deleted ON note_comment TYPE option<bool> DEFAULT false;
    DEFINE FIELD edited_at ON note_comment TYPE option<datetime>;
    DEFINE FIELD metadata ON note_comment FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD created_at ON note_comment TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON note_comment TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX comment_thread ON note_comment FIELDS note, created_at;

    DEFINE TABLE audit_event SCHEMAFULL;
    DEFINE FIELD action ON audit_event TYPE string;
    DEFINE FIELD actor ON audit_event TYPE option<record<account>>;
    DEFINE FIELD workspace ON audit_event TYPE option<record<workspace>>;
    DEFINE FIELD target ON audit_event TYPE option<string>;
    DEFINE FIELD detail ON audit_event FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD created_at ON audit_event TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX audit_created ON audit_event FIELDS created_at;

    // Phase 3: per-note activity history. Every meaningful note mutation lands
    // here (note.created/updated/...), so a note card can show its own timeline
    // without the workspace audit stream having to be filtered by target.
    DEFINE TABLE note_activity SCHEMAFULL;
    DEFINE FIELD note ON note_activity TYPE record<notes>;
    DEFINE FIELD workspace ON note_activity TYPE record<workspace>;
    DEFINE FIELD action ON note_activity TYPE string;
    DEFINE FIELD actor ON note_activity TYPE option<record<account>>;
    DEFINE FIELD detail ON note_activity FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD created_at ON note_activity TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX note_activity_note ON note_activity FIELDS note, created_at;
    DEFINE INDEX note_activity_created ON note_activity FIELDS created_at;

    // Phase 3: rate limiting + security events. Buckets are keyed by
    // "scope:identity" (e.g. "login:ip:10.0.0.1"); a hit is recorded, then
    // the count inside the window decides whether the request passes.
    DEFINE TABLE rate_limit_hit SCHEMAFULL;
    DEFINE FIELD bucket ON rate_limit_hit TYPE string;
    DEFINE FIELD created_at ON rate_limit_hit TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX rate_bucket_time ON rate_limit_hit FIELDS bucket, created_at;

    DEFINE TABLE security_event SCHEMAFULL;
    DEFINE FIELD kind ON security_event TYPE string;
    DEFINE FIELD workspace ON security_event TYPE option<record<workspace>>;
    DEFINE FIELD name ON security_event TYPE option<string>;
    DEFINE FIELD ip ON security_event TYPE option<string>;
    DEFINE FIELD user_agent ON security_event TYPE option<string>;
    DEFINE FIELD detail ON security_event FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD created_at ON security_event TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX security_created ON security_event FIELDS created_at;

    // Phase 4 query-budget telemetry: one row per tracked query shape with
    // latency, scanned/returned counts, and failure details. Statement text is
    // never stored — only the caller-declared shape name — and error detail is
    // bounded so exceptions (which can embed bound values) cannot leak secrets.
    DEFINE TABLE query_metric SCHEMAFULL;
    DEFINE FIELD shape ON query_metric TYPE string;
    DEFINE FIELD workspace ON query_metric TYPE option<record<workspace>>;
    DEFINE FIELD ok ON query_metric TYPE bool DEFAULT true;
    DEFINE FIELD duration_ms ON query_metric TYPE number;
    DEFINE FIELD scanned ON query_metric TYPE option<number>;
    DEFINE FIELD returned ON query_metric TYPE option<number>;
    DEFINE FIELD error_kind ON query_metric TYPE option<string>;
    DEFINE FIELD created_at ON query_metric TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX query_metric_shape ON query_metric FIELDS shape, created_at;
    DEFINE INDEX query_metric_created ON query_metric FIELDS created_at;

    // Phase 2 closeout: retention. 'retention_days' (NONE = keep forever)
    // bounds recycle-bin age; 'purge_after_days' bounds soft-deleted row age.
    // The purge sweep is part of the boot sequence and runs hourly after that.
    DEFINE FIELD retention_days ON workspace TYPE option<number>;
    DEFINE FIELD purge_after_days ON workspace TYPE option<number>;

    // Phase 3 foundations: AI provider/model operations, chat sessions, and
    // reusable prompt templates. Provider secrets are write-only through the
    // API (masked on read) and stored in SurrealDB alongside the workspace.
    DEFINE TABLE ai_provider SCHEMAFULL;
    DEFINE FIELD name ON ai_provider TYPE string;
    DEFINE FIELD kind ON ai_provider TYPE string;
    DEFINE FIELD base_url ON ai_provider TYPE string;
    DEFINE FIELD api_key ON ai_provider TYPE string;
    DEFINE FIELD model ON ai_provider TYPE string;
    DEFINE FIELD is_active ON ai_provider TYPE bool DEFAULT false;
    DEFINE FIELD workspace ON ai_provider TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_at ON ai_provider TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX provider_name ON ai_provider FIELDS name UNIQUE;

    // Per-workspace AI policy (schema v11): which providers/models a workspace
    // may use, which one chats default to, and an optional cap on AI runs. An
    // empty allow-list means every active provider is allowed.
    DEFINE FIELD ai_allowed_providers ON workspace TYPE option<array> DEFAULT [];
    DEFINE FIELD ai_default_provider ON workspace TYPE option<string>;
    DEFINE FIELD ai_run_cap ON workspace TYPE option<number>;
    // Monthly spend ceiling in currency micros (1e6 = one unit, same unit the
    // ledger prices runs in). NONE means unlimited.
    DEFINE FIELD ai_monthly_budget_micros ON workspace TYPE option<number>;

    // Per-workspace AI run ledger (schema v11): one row per provider call, so
    // usage, latency, and failures are visible per workspace and per feature.
    DEFINE TABLE ai_run SCHEMAFULL;
    DEFINE FIELD workspace ON ai_run TYPE record<workspace>;
    DEFINE FIELD provider ON ai_run TYPE option<record<ai_provider>>;
    DEFINE FIELD model ON ai_run TYPE option<string>;
    DEFINE FIELD feature ON ai_run TYPE string;
    DEFINE FIELD status ON ai_run TYPE string;
    DEFINE FIELD prompt_chars ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD response_chars ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD duration_ms ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD error_message ON ai_run TYPE option<string>;
    DEFINE FIELD account ON ai_run TYPE option<record<account>>;
    DEFINE FIELD session ON ai_run TYPE option<record<chat_session>>;
    DEFINE FIELD note ON ai_run TYPE option<record<notes>>;
    DEFINE FIELD created_at ON ai_run TYPE option<datetime> DEFAULT time::now();
    // Token/cost accounting (schema v12): usage comes from the provider
    // response when it reports it; cost is estimated from per-model pricing in
    // micros of the currency (1e6 = 1 unit) so rows are comparable.
    DEFINE FIELD prompt_tokens ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD completion_tokens ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD total_tokens ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD cost_micros ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD cost_currency ON ai_run TYPE option<string>;

    DEFINE INDEX ai_run_created ON ai_run FIELDS created_at;
    DEFINE INDEX ai_run_ws_feature ON ai_run FIELDS workspace, feature, created_at;

    // Idempotency (schema v13): a run row is created BEFORE the provider call
    // (the spend reservation), then updated with the outcome — so a crash
    // mid-call still counts the spend exactly once. Jobs link the run they
    // consumed, and a caller-supplied idempotency key makes a retried enqueue
    // return the original job instead of spending twice.
    DEFINE FIELD job ON ai_run TYPE option<record<ai_job>>;
    DEFINE FIELD attempt ON ai_run TYPE option<number> DEFAULT 0;
    DEFINE FIELD ledger_status ON ai_run TYPE option<string> DEFAULT 'pending';
    DEFINE INDEX ai_run_ws_hour ON ai_run FIELDS workspace, created_at;

    // Queued AI runs (schema v12): a job is a deferred provider call whose
    // whole lifecycle (queued → running → succeeded/failed/cancelled) lives in
    // SurrealDB. Retries back off exponentially up to max_attempts.
    DEFINE TABLE ai_job SCHEMAFULL;
    DEFINE FIELD workspace ON ai_job TYPE record<workspace>;
    DEFINE FIELD kind ON ai_job TYPE string;
    DEFINE FIELD status ON ai_job TYPE string DEFAULT 'queued';
    DEFINE FIELD payload ON ai_job FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD run ON ai_job TYPE option<record<ai_run>>;
    DEFINE FIELD attempts ON ai_job TYPE option<number> DEFAULT 0;
    DEFINE FIELD max_attempts ON ai_job TYPE option<number> DEFAULT 3;
    DEFINE FIELD next_attempt_at ON ai_job TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD last_error ON ai_job TYPE option<string>;
    DEFINE FIELD requested_by ON ai_job TYPE option<record<account>>;
    DEFINE FIELD created_at ON ai_job TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON ai_job TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD started_at ON ai_job TYPE option<datetime>;
    DEFINE FIELD finished_at ON ai_job TYPE option<datetime>;
    // Caller-supplied idempotency key. Unique per workspace, so a retried
    // enqueue resolves to the original job instead of creating a second one.
    DEFINE FIELD idempotency_key ON ai_job TYPE option<string>;
    DEFINE FIELD identity ON ai_job TYPE option<string>;
    DEFINE INDEX ai_job_due ON ai_job FIELDS status, next_attempt_at;
    DEFINE INDEX ai_job_ws_created ON ai_job FIELDS workspace, created_at;
    DEFINE INDEX ai_job_ws_key ON ai_job FIELDS workspace, idempotency_key UNIQUE;

    DEFINE TABLE chat_session SCHEMAFULL;
    DEFINE FIELD title ON chat_session TYPE string;
    DEFINE FIELD provider ON chat_session TYPE option<record<ai_provider>>;
    DEFINE FIELD prompt_id ON chat_session TYPE option<string>;
    // Files from the configured context roots that this chat may read. Stored
    // as root:relative/path refs so the AI sees project/document files without
    // the browser ever holding a filesystem handle.
    DEFINE FIELD context_files ON chat_session TYPE option<array> DEFAULT [];
    DEFINE FIELD created_by ON chat_session TYPE record<account>;
    DEFINE FIELD workspace ON chat_session TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_at ON chat_session TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX session_created ON chat_session FIELDS created_at;

    DEFINE TABLE chat_message SCHEMAFULL;
    DEFINE FIELD session ON chat_message TYPE record<chat_session>;
    DEFINE FIELD role ON chat_message TYPE string;
    DEFINE FIELD content ON chat_message TYPE string;
    DEFINE FIELD prompt_id ON chat_message TYPE option<string>;
    DEFINE FIELD model ON chat_message TYPE option<string>;
    DEFINE FIELD error ON chat_message TYPE option<bool> DEFAULT false;
    DEFINE FIELD created_at ON chat_message TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX message_session ON chat_message FIELDS session, created_at;

    DEFINE TABLE prompt_template SCHEMAFULL;
    DEFINE FIELD title ON prompt_template TYPE string;
    DEFINE FIELD body ON prompt_template TYPE string;
    DEFINE FIELD is_system ON prompt_template TYPE bool DEFAULT false;
    DEFINE FIELD workspace ON prompt_template TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_at ON prompt_template TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX prompt_id ON prompt_template FIELDS id UNIQUE;

    // Phase 5: spaced-recall study items derived from notes. The box number is
    // the Leitner box; due_at is the single scheduling source of truth so the
    // review queue is one indexed range query.
    DEFINE TABLE study_item SCHEMAFULL;
    DEFINE FIELD note ON study_item TYPE option<record<notes>>;
    DEFINE FIELD workspace ON study_item TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD question ON study_item TYPE string;
    DEFINE FIELD answer ON study_item TYPE string;
    DEFINE FIELD box ON study_item TYPE option<number> DEFAULT 0;
    DEFINE FIELD due_at ON study_item TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD reviewed_at ON study_item TYPE option<datetime>;
    DEFINE FIELD review_count ON study_item TYPE option<number> DEFAULT 0;
    DEFINE FIELD lapses ON study_item TYPE option<number> DEFAULT 0;
    DEFINE FIELD source ON study_item TYPE option<string> DEFAULT 'manual';
    DEFINE FIELD created_by ON study_item TYPE option<record<account>>;
    DEFINE FIELD created_at ON study_item TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON study_item TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX study_due ON study_item FIELDS due_at;
    DEFINE INDEX study_note ON study_item FIELDS note;

    // One row per grading. Retention, activity, and lapse hotspots are derived
    // from this log instead of only from the counters on the card, so history
    // stays queryable after a card is rescheduled many times.
    DEFINE TABLE study_review SCHEMAFULL;
    DEFINE FIELD item ON study_review TYPE record<study_item>;
    DEFINE FIELD workspace ON study_review TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD note ON study_review TYPE option<record<notes>>;
    DEFINE FIELD grade ON study_review TYPE string;
    DEFINE FIELD box_before ON study_review TYPE option<number> DEFAULT 0;
    DEFINE FIELD box_after ON study_review TYPE option<number> DEFAULT 0;
    DEFINE FIELD interval_days ON study_review TYPE option<number> DEFAULT 0;
    DEFINE FIELD account ON study_review TYPE option<record<account>>;
    DEFINE FIELD created_at ON study_review TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX review_item ON study_review FIELDS item, created_at;
    DEFINE INDEX review_created ON study_review FIELDS created_at;

    // Extracted text for uploaded files, so markdown/PDF material can be
    // turned into notes without retyping it. text_status is 'none' when no
    // extractor applied, 'ready' when text_content holds usable text.
    DEFINE FIELD text_content ON attachments TYPE option<string>;
    DEFINE FIELD text_status ON attachments TYPE option<string> DEFAULT 'none';

    // ---- schema v5: mapping, flags, ownership, relations, integrations ----
    // Every domain record carries the same shape so imports, syncs, and
    // integrations can round-trip without a bespoke mapping per table:
    //   flags     — boolean bag for soft workflow state
    //   metadata  — free-form bag for tool-specific extras
    //   external_id / external_source — the mapping key back to the origin
    //   created_by / created_at / updated_at — ownership + audit
    DEFINE FIELD parent ON category TYPE option<record<category>>;
    DEFINE FIELD description ON category TYPE option<string>;
    DEFINE FIELD sort_order ON category TYPE option<number> DEFAULT 0;
    DEFINE FIELD is_archived ON category TYPE option<bool> DEFAULT false;
    DEFINE FIELD is_default ON category TYPE option<bool> DEFAULT false;
    DEFINE FIELD flags ON category FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD metadata ON category FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD external_id ON category TYPE option<string>;
    DEFINE FIELD external_source ON category TYPE option<string>;
    DEFINE FIELD created_by ON category TYPE option<record<account>>;
    DEFINE FIELD updated_at ON category TYPE option<datetime> DEFAULT time::now();

    DEFINE FIELD created_by ON notes TYPE option<record<account>>;
    DEFINE FIELD updated_by ON notes TYPE option<record<account>>;
    DEFINE FIELD flags ON notes FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD external_id ON notes TYPE option<string>;
    DEFINE FIELD external_source ON notes TYPE option<string>;
    DEFINE FIELD word_count ON notes TYPE option<number> DEFAULT 0;
    DEFINE FIELD link_count ON notes TYPE option<number> DEFAULT 0;

    DEFINE FIELD color ON tag TYPE option<string>;
    DEFINE FIELD description ON tag TYPE option<string>;
    DEFINE FIELD is_system ON tag TYPE option<bool> DEFAULT false;
    DEFINE FIELD workspace ON tag TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_by ON tag TYPE option<record<account>>;
    DEFINE FIELD updated_at ON tag TYPE option<datetime> DEFAULT time::now();

    DEFINE FIELD created_by ON attachments TYPE option<record<account>>;
    DEFINE FIELD room ON attachments TYPE option<record<chat_room>>;
    DEFINE FIELD metadata ON attachments FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD updated_at ON attachments TYPE option<datetime> DEFAULT time::now();

    DEFINE FIELD slug ON workspace TYPE option<string>;
    DEFINE FIELD owner ON workspace TYPE option<record<account>>;
    DEFINE FIELD is_archived ON workspace TYPE option<bool> DEFAULT false;
    DEFINE FIELD metadata ON workspace FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD created_by ON workspace TYPE option<record<account>>;

    DEFINE FIELD last_grade ON study_item TYPE option<string>;
    DEFINE FIELD interval_days ON study_item TYPE option<number> DEFAULT 0;
    DEFINE FIELD metadata ON study_item FLEXIBLE TYPE option<object> DEFAULT {};

    // Explicit wiki-link edges, written when a note is saved. The graph view
    // reads these (falling back to parsing when a note predates the table) and
    // the UNIQUE index keeps saves idempotent.
    DEFINE TABLE note_link TYPE RELATION IN notes OUT notes SCHEMAFULL;
    DEFINE FIELD label ON note_link TYPE string;
    DEFINE FIELD resolved ON note_link TYPE option<bool> DEFAULT false;
    DEFINE FIELD workspace ON note_link TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_by ON note_link TYPE option<record<account>>;
    DEFINE FIELD created_at ON note_link TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX note_link_unique ON note_link FIELDS in, out, label UNIQUE;

    // Outbound/inbound integration definitions. Secrets are write-only through
    // the API (masked on read) exactly like provider keys.
    DEFINE TABLE integration SCHEMAFULL;
    DEFINE FIELD name ON integration TYPE string;
    DEFINE FIELD kind ON integration TYPE string;
    DEFINE FIELD direction ON integration TYPE option<string> DEFAULT 'outbound';
    DEFINE FIELD endpoint ON integration TYPE option<string>;
    DEFINE FIELD secret ON integration TYPE option<string>;
    DEFINE FIELD mapping ON integration FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD flags ON integration FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD is_enabled ON integration TYPE option<bool> DEFAULT false;
    DEFINE FIELD last_status ON integration TYPE option<string>;
    DEFINE FIELD last_run_at ON integration TYPE option<datetime>;
    DEFINE FIELD workspace ON integration TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_by ON integration TYPE option<record<account>>;
    DEFINE FIELD created_at ON integration TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON integration TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX integration_name ON integration FIELDS name UNIQUE;

    // Team chat: temporary rooms that workspace members can be invited into,
    // with room-scoped messages and file attachments.
    DEFINE TABLE chat_room SCHEMAFULL;
    DEFINE FIELD name ON chat_room TYPE string;
    DEFINE FIELD topic ON chat_room TYPE option<string>;
    DEFINE FIELD is_temporary ON chat_room TYPE option<bool> DEFAULT true;
    DEFINE FIELD expires_at ON chat_room TYPE option<datetime>;
    DEFINE FIELD workspace ON chat_room TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_by ON chat_room TYPE option<record<account>>;
    DEFINE FIELD created_at ON chat_room TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON chat_room TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX room_created ON chat_room FIELDS created_at;

    DEFINE TABLE chat_room_member TYPE RELATION IN account OUT chat_room SCHEMAFULL;
    DEFINE FIELD role ON chat_room_member TYPE option<string> DEFAULT 'member';
    DEFINE FIELD created_by ON chat_room_member TYPE option<record<account>>;
    DEFINE FIELD created_at ON chat_room_member TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX room_member_unique ON chat_room_member FIELDS in, out UNIQUE;

    DEFINE TABLE chat_room_message SCHEMAFULL;
    DEFINE FIELD room ON chat_room_message TYPE record<chat_room>;
    DEFINE FIELD author ON chat_room_message TYPE option<record<account>>;
    DEFINE FIELD content ON chat_room_message TYPE string;
    DEFINE FIELD attachments ON chat_room_message TYPE option<array> DEFAULT [];
    DEFINE FIELD attachments.* ON chat_room_message TYPE option<record<attachments>>;
    DEFINE FIELD is_system ON chat_room_message TYPE option<bool> DEFAULT false;
    DEFINE FIELD created_at ON chat_room_message TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX room_message ON chat_room_message FIELDS room, created_at;

    // Support tickets. Custom field definitions are workspace-scoped rows; the
    // values live on the ticket as an object keyed by field id so deleting a
    // definition never orphans or rewrites stored data.
    DEFINE TABLE ticket_field SCHEMAFULL;
    DEFINE FIELD label ON ticket_field TYPE string;
    DEFINE FIELD type ON ticket_field TYPE string;
    DEFINE FIELD options ON ticket_field TYPE option<array> DEFAULT [];
    DEFINE FIELD required ON ticket_field TYPE option<bool> DEFAULT false;
    DEFINE FIELD sort_order ON ticket_field TYPE option<number> DEFAULT 0;
    DEFINE FIELD workspace ON ticket_field TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_at ON ticket_field TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX ticket_field_ws ON ticket_field FIELDS workspace;

    DEFINE TABLE ticket SCHEMAFULL;
    DEFINE FIELD subject ON ticket TYPE string;
    DEFINE FIELD description ON ticket TYPE option<string> DEFAULT '';
    DEFINE FIELD status ON ticket TYPE option<string> DEFAULT 'new';
    DEFINE FIELD priority ON ticket TYPE option<string> DEFAULT 'medium';
    DEFINE FIELD requester ON ticket TYPE option<record<account>>;
    DEFINE FIELD assignee ON ticket TYPE option<record<account>>;
    // FLEXIBLE like notes.metadata: SCHEMAFULL otherwise strips inner keys of
    // an option<object> because their names/types are undeclared.
    DEFINE FIELD custom_fields ON ticket FLEXIBLE TYPE option<object> DEFAULT {};
    DEFINE FIELD reply_count ON ticket TYPE option<number> DEFAULT 0;
    DEFINE FIELD workspace ON ticket TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_at ON ticket TYPE option<datetime> DEFAULT time::now();
    DEFINE FIELD updated_at ON ticket TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX ticket_ws_status ON ticket FIELDS workspace, status;

    DEFINE TABLE ticket_reply SCHEMAFULL;
    DEFINE FIELD ticket ON ticket_reply TYPE record<ticket>;
    DEFINE FIELD author ON ticket_reply TYPE option<record<account>>;
    DEFINE FIELD body ON ticket_reply TYPE string;
    DEFINE FIELD workspace ON ticket_reply TYPE option<record<workspace>> DEFAULT workspace:default;
    DEFINE FIELD created_at ON ticket_reply TYPE option<datetime> DEFAULT time::now();
    DEFINE INDEX ticket_reply_ticket ON ticket_reply FIELDS ticket, created_at;
  `);
  const workspaceRows = await q('SELECT * FROM workspace:default LIMIT 1;');
  if (!workspaceRows[0]) await q('CREATE workspace:default CONTENT $workspace;', { workspace: defaultWorkspace });
  for (const prompt of defaultPrompts) {
    const existing = await q('SELECT id FROM type::thing("prompt_template", $id) LIMIT 1;', { id: prompt.id });
    if (!existing[0]) {
      const { id: _omit, ...data } = prompt; // id comes from type::thing, not CONTENT
      await q('CREATE type::thing("prompt_template", $id) CONTENT $data;', { id: prompt.id, data: { ...data, is_system: true } });
    }
  }
  await q(`
    UPDATE category SET color = color ?? '#64748b', icon = icon ?? 'C', is_system = is_system ?? false, created_at = created_at ?? time::now();
    UPDATE notes SET tags = tags ?? [], metadata = metadata ?? {}, is_archived = is_archived ?? false, is_recycle = is_recycle ?? false, is_top = is_top ?? false, is_share = is_share ?? false, created_at = created_at ?? time::now(), updated_at = updated_at ?? time::now();
    UPDATE account SET workspace = workspace ?? workspace:default, created_at = created_at ?? time::now();
    UPDATE tag SET created_at = created_at ?? time::now();
    UPDATE workspace:default SET theme = theme ?? 'system', theme_variant = theme_variant ?? 'default', button_style = button_style ?? 'default', badge_style = badge_style ?? 'default', accent = accent ?? 'violet', font_scale = font_scale ?? 'default', style_variant = style_variant ?? 'sharp', radius_scale = radius_scale ?? 'default', edge_strength = edge_strength ?? 'default', shadow_depth = shadow_depth ?? 'default', density = density ?? 'cozy', updated_at = updated_at ?? time::now();
    UPDATE workspace SET theme_variant = theme_variant ?? 'default', button_style = button_style ?? 'default', badge_style = badge_style ?? 'default' WHERE theme_variant IS NONE OR button_style IS NONE OR badge_style IS NONE;
    UPDATE category SET workspace = workspace ?? workspace:default WHERE workspace IS NONE;
    UPDATE notes SET workspace = workspace ?? workspace:default WHERE workspace IS NONE;
    UPDATE attachments SET text_status = text_status ?? 'none' WHERE text_status IS NONE;
    UPDATE notes SET flags = flags ?? {}, word_count = word_count ?? 0, link_count = link_count ?? 0, created_by = created_by ?? account, updated_at = updated_at ?? time::now();
    // Planning backfill: existing notes become 'todo' cards at position 0, and
    // any due/start dates that live inside flags are lifted to real fields so
    // the calendar index picks them up.
    UPDATE notes SET status = status ?? 'todo' WHERE status IS NONE;
    UPDATE notes SET priority = priority ?? 'medium' WHERE priority IS NONE;
    UPDATE notes SET position = position ?? 0 WHERE position IS NONE;
    UPDATE notes SET due_date = <datetime> flags.due_date WHERE due_date IS NONE AND flags.due_date IS NOT NONE;
    UPDATE notes SET start_date = <datetime> flags.start_date WHERE start_date IS NONE AND flags.start_date IS NOT NONE;
    UPDATE category SET flags = flags ?? {}, metadata = metadata ?? {}, sort_order = sort_order ?? 0, is_archived = is_archived ?? false, is_default = is_default ?? false, updated_at = updated_at ?? time::now();
    UPDATE tag SET is_system = is_system ?? false, workspace = workspace ?? workspace:default, updated_at = updated_at ?? time::now();
    UPDATE attachments SET created_by = created_by ?? account, metadata = metadata ?? {}, updated_at = updated_at ?? time::now();
    UPDATE workspace:default SET is_archived = is_archived ?? false, metadata = metadata ?? {};
    UPDATE account SET active_workspace = active_workspace ?? workspace:default WHERE active_workspace IS NONE;
    UPDATE workspace SET context_roots = context_roots ?? [] WHERE context_roots IS NONE;
    // Tickets backfill: tables are new, so every existing row just gets defaults.
    UPDATE ticket_field SET required = required ?? false, sort_order = sort_order ?? 0, workspace = workspace ?? workspace:default, created_at = created_at ?? time::now();
    UPDATE ticket SET status = status ?? 'new', priority = priority ?? 'medium', custom_fields = custom_fields ?? {}, reply_count = reply_count ?? 0, workspace = workspace ?? workspace:default, created_at = created_at ?? time::now(), updated_at = updated_at ?? time::now();
    UPDATE ticket_reply SET workspace = workspace ?? workspace:default, created_at = created_at ?? time::now();
    UPDATE workspace_invitation SET expires_at = expires_at ?? ((created_at ?? time::now()) + 14d) WHERE expires_at IS NONE;
    UPDATE chat_session SET context_files = context_files ?? [];
    UPDATE study_item SET metadata = metadata ?? {}, interval_days = interval_days ?? 0;
    UPDATE study_item SET box = box ?? 0, due_at = due_at ?? time::now(), review_count = review_count ?? 0, lapses = lapses ?? 0, source = source ?? 'manual', created_at = created_at ?? time::now(), updated_at = updated_at ?? time::now();
    // Repair study rows that were filed under the default workspace before the
    // creator passed its workspace through: the card's note knows where it lives.
    UPDATE study_item SET workspace = note.workspace WHERE workspace = workspace:default AND note != NONE AND note.workspace != NONE AND note.workspace != workspace:default;
    UPDATE study_review SET workspace = item.workspace WHERE workspace = workspace:default AND item != NONE AND item.workspace != NONE AND item.workspace != workspace:default;
    UPDATE study_review SET workspace = note.workspace WHERE workspace = workspace:default AND note != NONE AND note.workspace != NONE AND note.workspace != workspace:default;
    UPDATE workspace SET ai_allowed_providers = ai_allowed_providers ?? [], ai_run_cap = ai_run_cap ?? NONE WHERE ai_allowed_providers IS NONE;
    UPDATE workspace SET ai_monthly_budget_micros = ai_monthly_budget_micros ?? NONE WHERE ai_monthly_budget_micros IS NONE;
    UPDATE ai_run SET prompt_tokens = prompt_tokens ?? 0, completion_tokens = completion_tokens ?? 0, total_tokens = total_tokens ?? 0, cost_micros = cost_micros ?? 0, ledger_status = 'recorded' WHERE ledger_status IS NONE;
    UPDATE ai_run SET attempt = attempt ?? 0 WHERE attempt IS NONE;
    UPDATE ai_job SET attempts = attempts ?? 0, max_attempts = max_attempts ?? 3, next_attempt_at = next_attempt_at ?? time::now(), payload = payload ?? {}, updated_at = updated_at ?? time::now();
    UPDATE ai_job SET identity = idempotency_key WHERE identity IS NONE;
    // SurrealDB v1 unique indexes index NONE values too, so a terminal job
    // cannot simply NULL its key — every terminal row would collide on the
    // same [workspace, NONE] entry. Terminal rows instead take a per-row
    // 'released:' marker, which frees the real key and keeps the index clean.
    UPDATE ai_job SET idempotency_key = string::concat('released:', <string>id) WHERE status IN ['succeeded', 'failed', 'cancelled'] AND idempotency_key IS NOT NONE AND string::startsWith(idempotency_key, 'released:') == false;
    // A server restart must never orphan in-flight jobs: anything still
    // 'running' when the process died goes back to the queue.
    UPDATE ai_job SET status = 'queued', updated_at = time::now() WHERE status = 'running';
  `);
  await q('DEFINE INDEX notes_updated ON notes FIELDS updated_at;');
  // Full-text search: the ngram analyzer indexes existing rows on DEFINE INDEX,
  // matches substrings and multi-word queries, and re-definition is idempotent.
  await q(`
    DEFINE ANALYZER note_search_an TOKENIZERS blank FILTERS lowercase, ngram(1,32);
    DEFINE INDEX note_search ON notes FIELDS content SEARCH ANALYZER note_search_an BM25;
  `);
  for (const category of defaultCategories) {
    const existing = await q('SELECT * FROM type::thing("category", $slug) LIMIT 1;', { slug: category.slug });
    if (existing[0]) await q('UPDATE type::thing("category", $slug) MERGE $category;', { slug: category.slug, category });
    else await q('CREATE type::thing("category", $slug) CONTENT $category;', { slug: category.slug, category });
  }
  // Bootstrap the workspace edge for existing accounts so the membership
  // source of truth is populated for every pre-Phase-2 user.
  for (const account of await q('SELECT id, role FROM account;')) {
    const accountId = recordId(account.id);
    const edge = await q('SELECT id FROM workspace_member WHERE in = type::thing("account", $id) AND out = workspace:default LIMIT 1;', { id: accountId });
    if (edge[0]) continue;
    try {
      await upsertEdge('workspace_member', 'account', accountId, 'workspace', 'default', {
        role: account.role, created_at: new Date(),
      });
    } catch { /* unique index race — edge already exists */ }
  }
}

// Legacy v2-era categories used random record ids, so duplicate slugs can
// coexist with the canonical category:<slug> records from later schemas.
// The unique slug index cannot be rebuilt while duplicates exist, so reconcile
// before defining schema: keep the canonical record (or the oldest), reassign
// its notes, and remove the duplicates.
async function dedupeCategories() {
  const categoryRows = await q('SELECT id, slug, created_at FROM category;');
  if (!Array.isArray(categoryRows) || categoryRows.length < 2) return;
  const bySlug = new Map();
  for (const row of categoryRows) {
    const slug = recordId(row.slug);
    if (!slug) continue;
    if (!bySlug.has(slug)) bySlug.set(slug, []);
    bySlug.get(slug).push(row);
  }
  for (const [slug, group] of bySlug) {
    if (group.length < 2) continue;
    group.sort((a, b) => String(recordId(a.id)).localeCompare(String(recordId(b.id))));
    const keeper = group.find((row) => recordId(row.id) === slug) || group[0];
    const keeperId = recordId(keeper.id);
    for (const row of group) {
      const rowId = recordId(row.id);
      if (rowId === keeperId) continue;
      await q('UPDATE notes SET category = $keeper WHERE category = $duplicate;', {
        keeper: new RecordId('category', keeperId),
        duplicate: new RecordId('category', rowId),
      });
      await q('DELETE type::thing("category", $id);', { id: rowId });
    }
  }
}

function recordId(value) {
  if (value && typeof value === 'object') {
    if (typeof value.tb === 'string' && value.id !== undefined) return recordId(value.id);
    if (value instanceof RecordId || value instanceof StringRecordId) {
      const asString = String(value).replace(/⟨|⟩/g, '');
      return asString.includes(':') ? asString.split(':').slice(1).join(':') : asString;
    }
    if (value.id !== undefined) return recordId(value.id);
  }
  if (typeof value === 'string') {
    const cleaned = value.replace(/⟨|⟩/g, '');
    return cleaned.includes(':') ? cleaned.split(':').slice(1).join(':') : cleaned;
  }
  return value;
}

function isRecordLink(value) {
  return value instanceof RecordId || value instanceof StringRecordId
    || (typeof value === 'string' && value.includes(':'))
    || (value && typeof value === 'object' && typeof value.tb === 'string' && value.id !== undefined);
}

function publicCategory(row) {
  return { id: recordId(row.id), name: row.name, slug: row.slug, color: row.color, icon: row.icon, isSystem: Boolean(row.is_system) };
}

function publicTag(row) {
  if (isRecordLink(row)) return { id: recordId(row), name: recordId(row) };
  return { id: recordId(row.id), name: row.name };
}

function publicAttachment(row) {
  const text = String(row.text_content || '');
  return {
    id: recordId(row.id),
    name: row.name,
    path: row.path,
    size: Number(row.size || 0),
    type: row.type || 'application/octet-stream',
    note: row.note ? recordId(row.note) : null,
    textStatus: row.text_status || 'none',
    textLength: text.length,
    hasText: text.length > 0,
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
  };
}

function publicNote(row, attachments = []) {
  const category = row.category_record || row.category;
  // Tolerate being passed straight to Array.map (where the second argument is
  // the index) and rows fetched without an attachment join.
  const files = Array.isArray(attachments) ? attachments : [];
  return {
    id: recordId(row.id),
    content: row.content,
    category: category ? publicCategory(category) : null,
    tags: Array.isArray(row.tags) ? row.tags.map(publicTag) : [],
    attachments: files.map(publicAttachment),
    isTop: Boolean(row.is_top),
    isArchived: Boolean(row.is_archived),
    isRecycle: Boolean(row.is_recycle),
    isShare: Boolean(row.is_share),
    flags: row.flags || {},
    status: row.status || 'todo',
    priority: row.priority || 'medium',
    dueDate: isoOrNull(row.due_date),
    startDate: isoOrNull(row.start_date),
    endDate: isoOrNull(row.end_date),
    position: Number(row.position || 0),
    eventColor: row.event_color || null,
    assignee: row.assignee ? recordId(row.assignee) : null,
    wordCount: Number(row.word_count || 0),
    linkCount: Number(row.link_count || 0),
    metadata: row.metadata || {},
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
    updatedAt: row.updated_at instanceof Date ? row.updated_at.toISOString() : row.updated_at,
  };
}

async function currentAccount(req) {
  const rows = await q('SELECT * FROM type::thing("account", $id) LIMIT 1;', { id: recordId(req.account.sub) });
  return rows[0];
}

function can(account, permission) {
  return Boolean(account && (rolePermissions[account.role] || []).includes(permission));
}

// The membership edge for one account in one workspace — the single place a
// workspace role is read or written.
async function membershipEdge(accountId, workspaceId) {
  const rows = await q('SELECT * FROM workspace_member WHERE in = type::thing("account", $id) AND out = $ws LIMIT 1;', { id: recordId(accountId), ws: new RecordId('workspace', workspaceId) });
  return rows[0] || null;
}

// How many members of a workspace can own it. A workspace must always keep one,
// so the last owner can never be demoted or removed.
async function countWorkspaceOwners(workspaceId) {
  const rows = await q('SELECT role FROM workspace_member WHERE out = $ws;', { ws: new RecordId('workspace', workspaceId) });
  return rows.filter((row) => isOwnerRole(row.role)).length;
}

async function addWorkspaceMember(accountId, workspaceId, role, actorId = null) {
  await upsertEdge('workspace_member', 'account', recordId(accountId), 'workspace', workspaceId, {
    role,
    created_by: actorId ? new RecordId('account', recordId(actorId)) : undefined,
    created_at: new Date(),
  });
}

async function setWorkspaceMemberRole(accountId, workspaceId, role) {
  await upsertEdge('workspace_member', 'account', recordId(accountId), 'workspace', workspaceId, { role });
}

// Every membership of an account, so the switcher can list workspaces and the
// request scope can be validated against them.
async function workspaceMemberships(accountId) {
  const rows = await q('SELECT out AS workspace, role FROM workspace_member WHERE in = type::thing("account", $id);', { id: recordId(accountId) });
  return rows.map((row) => ({ id: recordId(row.workspace), role: row.role })).filter((row) => row.id);
}

// The workspace a request operates in: the account's active workspace when the
// account is still a member, else its first membership, else the default
// workspace. This is the single place tenancy is decided for a request.
async function resolveWorkspaceScope(accountId) {
  const [memberships, rows] = await Promise.all([
    workspaceMemberships(accountId),
    q('SELECT active_workspace, workspace, role FROM type::thing("account", $id) LIMIT 1;', { id: recordId(accountId) }),
  ]);
  const active = rows[0]?.active_workspace ? recordId(rows[0].active_workspace) : null;
  // Legacy accounts created before membership edges existed still resolve to the
  // workspace recorded on the account row, so nothing is invisible mid-migration.
  const legacyId = rows[0]?.workspace ? recordId(rows[0].workspace) : 'default';
  const scoped = memberships.length ? memberships : [{ id: legacyId, role: rows[0]?.role || 'admin' }];
  const member = scoped.find((entry) => entry.id === active) || scoped[0];
  return { workspaceId: member.id, role: member.role, memberships: scoped };
}

// Names for a set of accounts, in one query, so a thread does not run a lookup
// per comment.
async function accountNames(ids) {
  const unique = [...new Set((ids || []).filter(Boolean))];
  if (!unique.length) return new Map();
  const rows = await q(`SELECT id, name FROM account WHERE id IN [${unique.map((id) => recordLiteral('account', id)).join(', ')}];`);
  return new Map(rows.map((row) => [recordId(row.id), row.name]));
}

async function recordAudit(action, actorId, detail = {}, target = null, workspaceId = 'default') {
  try {
    // SurrealDB v1.5 schemafull rejects explicit `null` for option<string>
    // fields, so unset fields are omitted; the nested detail map is written as
    // a literal because bound parameters drop nested objects.
    const event = { action, detail: detail && typeof detail === 'object' ? detail : {}, created_at: new Date() };
    if (actorId) event.actor = new RecordId('account', recordId(actorId));
    event.workspace = new RecordId('workspace', workspaceId);
    if (target) event.target = String(target).slice(0, 120);
    await q(`CREATE audit_event SET ${literalAssignments(event).join(', ')};`);
  } catch (error) { console.error('[audit-fail]', action, error && error.message); /* auditing must never break the mutation it observes */ }
}

/* ---------- Phase 3: note activity, rate limits, security events ---------- */

/* ---------- Phase 4: query telemetry, transactions, retention ---------- */

// Wrap a SurrealDB query with budget telemetry. 'shape' is a stable caller-
// declared name (never the SQL text); latency is measured around the round
// trip; failures record only an error kind so bound values never leak into the
// ledger. Telemetry must never break the query it observes.
// Phase 4 query-budget telemetry, used on the hot paths: list loads, search,
// graph, settings reads. `shape` is a stable caller-declared name (never SQL
// text); latency wraps the round trip; failures record only an error kind so
// bound values never leak into the ledger.
const queryMetricBuffer = [];
let telemetryEnabled = false;

async function tq(shape, sql, vars = {}, workspaceId = 'default') {
  const started = Date.now();
  try {
    const result = await q(sql, vars);
    if (telemetryEnabled) {
      queryMetricBuffer.push({
        shape,
        workspace: workspaceId,
        ok: true,
        duration_ms: Date.now() - started,
        returned: Array.isArray(result) ? result.length : null,
      });
      // Self-regulating flush: steady traffic persists its own ledger without
      // waiting for the hourly sweep.
      if (queryMetricBuffer.length >= 200) await flushQueryMetrics();
    }
    return result;
  } catch (error) {
    if (telemetryEnabled) {
      const kind = String(error?.message || 'error').split(':')[0].slice(0, 80);
      queryMetricBuffer.push({ shape, workspace: workspaceId, ok: false, duration_ms: Date.now() - started, error_kind: kind });
    }
    throw error;
  }
}

// Flush the in-memory telemetry buffer to SurrealDB. Bounded per flush; the
// buffer is drained in place so concurrent flushes never double-write.
let telemetryFlushing = false;
async function flushQueryMetrics() {
  if (!telemetryEnabled || telemetryFlushing || !queryMetricBuffer.length) return;
  telemetryFlushing = true;
  const batch = queryMetricBuffer.splice(0, queryMetricBuffer.length).slice(0, 500);
  telemetryFlushing = false;
  try {
    const rows = batch.map((m) => {
      const parts = [
        `shape = ${JSON.stringify(m.shape)}`,
        `ok = ${Boolean(m.ok)}`,
        `duration_ms = ${Number(m.duration_ms) || 0}`,
        `created_at = time::now()`,
      ];
      if (m.workspace) parts.push(`workspace = ${recordLiteral('workspace', m.workspace)}`);
      if (m.returned != null) parts.push(`returned = ${Number(m.returned)}`);
      if (m.error_kind) parts.push(`error_kind = ${JSON.stringify(m.error_kind)}`);
      return `CREATE query_metric SET ${parts.join(', ')};`;
    });
    await q(`BEGIN TRANSACTION; ${rows.join('\n')} COMMIT TRANSACTION;`);
  } catch (error) { console.error('[telemetry-fail]', error && error.message); /* telemetry must never break the app */ }
}

// Run mutations inside a single SurrealDB transaction so a mid-sequence
// failure cannot leave half-applied state (a lane deleted but notes not
// reassigned, an invite claimed but no membership edge). SurrealDB v1.5
// supports BEGIN/COMMIT through the query endpoint; a failure between BEGIN
// and COMMIT rolls the whole batch back.
async function transaction(statements, vars = {}) {
  const batch = statements.filter(Boolean).join('\n');
  return q(`BEGIN TRANSACTION;\n${batch}\nCOMMIT TRANSACTION;`, vars);
}

// Phase 2 closeout: retention. Purge soft-deleted content older than the
// workspace's window. Notes in the recycle bin past `retention_days` are hard-
// deleted with their attachments (rows then files); recycle-bin rows never
// count as "live" content so a full bin cannot wedge the sweep.
async function purgeExpiredContent() {
  const workspaces = await q('SELECT * FROM workspace;');
  let purgedNotes = 0, purgedComments = 0, purgedMetrics = 0;
  for (const workspace of workspaces) {
    const workspaceId = recordId(workspace.id);
    const retentionDays = Number(workspace.retention_days) || null;
    if (!retentionDays) continue;
    const cutoff = new Date(Date.now() - retentionDays * 24 * 60 * 60 * 1000).toISOString();
    // NOTE: the SDK serializes an ISO *string* as a SurrealDB string, which
    // never compares true against a datetime field — the bound param must be a
    // Date object so CBOR encodes it as a datetime.
    const expired = await q(
      `SELECT * FROM notes WHERE workspace = ${recordLiteral('workspace', workspaceId)} AND is_recycle = true AND updated_at < $cutoff;`,
      { cutoff: new Date(cutoff) },
    );
    for (const note of expired) {
      const noteId = recordId(note.id);
      const attachmentRows = await q('SELECT * FROM attachments WHERE note = type::thing("notes", $id);', { id: noteId });
      for (const attachment of attachmentRows) {
        fs.rm(path.join(uploadDir, path.basename(attachment.path)), { force: true }, () => {});
      }
      await transaction([
        `DELETE attachments WHERE note = type::thing("notes", ${JSON.stringify(noteId)});`,
        `DELETE note_comment WHERE note = type::thing("notes", ${JSON.stringify(noteId)});`,
        `DELETE note_link WHERE in = type::thing("notes", ${JSON.stringify(noteId)}) OR out = type::thing("notes", ${JSON.stringify(noteId)});`,
        `DELETE type::thing("notes", ${JSON.stringify(noteId)});`,
      ]);
      purgedNotes += 1;
    }
  }
  // Soft-deleted comments (is_deleted flag) older than 30 days everywhere.
  const commentCutoff = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
  const purged = await q('DELETE note_comment WHERE is_deleted = true AND updated_at < $cutoff RETURN count;', { cutoff: new Date(commentCutoff) });
  purgedComments = Number(purged?.[0]?.count || 0);
  // The telemetry ledger writes one row per instrumented query, so it needs its
  // own horizon or a busy workspace grows it forever. The read API only ever
  // looks back 168 h, so dropping rows past 30 days is invisible to callers and
  // is enough history to compare a shape week over week.
  const metricCutoff = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const prunedMetrics = await q('DELETE query_metric WHERE created_at < $cutoff RETURN count;', { cutoff: metricCutoff });
  purgedMetrics = Number(prunedMetrics?.[0]?.count || 0);
  return { purgedNotes, purgedComments, purgedMetrics };
}

let telemetryTimer = null;
let sweepTimer = null;
function startRetentionSweeps() {
  if (sweepTimer) return;
  // Telemetry flush every 30s: with the 200-row auto-flush threshold this is
  // the floor for low-traffic deployments, so a quiet workspace still persists
  // its ledger and a restart loses at most 30s of shapes.
  telemetryTimer = setInterval(async () => {
    try {
      await flushQueryMetrics();
    } catch { /* flushed again next tick */ }
  }, 30 * 1000).unref();
  sweepTimer = setInterval(async () => {
    try {
      const result = await purgeExpiredContent();
      if (result.purgedNotes || result.purgedComments || result.purgedMetrics) console.log('[retention]', JSON.stringify(result));
    } catch (error) { console.error('[retention-fail]', error && error.message); }
    await flushQueryMetrics();
  }, 60 * 60 * 1000).unref();
}

// Per-note timeline rows. Auditing stays workspace-wide; this is the same
// story filtered to one note so the card can show what happened to it.
async function recordNoteActivity(noteId, workspaceId, action, actorId = null, detail = {}) {
  try {
    const event = {
      note: new RecordId('notes', recordId(noteId)),
      workspace: new RecordId('workspace', workspaceId),
      action,
      detail: detail && typeof detail === 'object' ? detail : {},
      created_at: new Date(),
    };
    if (actorId) event.actor = new RecordId('account', recordId(actorId));
    await q(`CREATE note_activity SET ${literalAssignments(event).join(', ')};`);
  } catch (error) { console.error('[note-activity-fail]', action, error && error.message); }
}

const securityKinds = ['login.failed', 'login.success', 'register.rejected', 'register.success', 'invite.rejected', 'token.invalid', 'rate.blocked'];

async function recordSecurityEvent(kind, { name = null, ip = null, userAgent = null, detail = {}, workspaceId = null } = {}) {
  if (!securityKinds.includes(kind)) return;
  try {
    const event = {
      kind,
      detail: detail && typeof detail === 'object' ? detail : {},
      created_at: new Date(),
    };
    if (workspaceId) event.workspace = new RecordId('workspace', workspaceId);
    if (name) event.name = String(name).slice(0, 80);
    if (ip) event.ip = String(ip).slice(0, 64);
    if (userAgent) event.user_agent = String(userAgent).slice(0, 200);
    await q(`CREATE security_event SET ${literalAssignments(event).join(', ')};`);
  } catch (error) { console.error('[security-event-fail]', kind, error && error.message); }
}

const clientIp = (req) => (String(req.headers['x-forwarded-for'] || '').split(',')[0].trim())
  || req.socket?.remoteAddress
  || 'unknown';

// Fixed-window counter backed by SurrealDB. A hit is written first, then the
// rows inside the window are counted, so parallel requests can only ever be
// counted once each and the limit is enforced across server restarts too.
const rateLimits = {
  'login': { windowMs: 15 * 60 * 1000, max: 30 },
  'register': { windowMs: 60 * 60 * 1000, max: 20 },
  'redeem': { windowMs: 60 * 60 * 1000, max: 30 },
  'token': { windowMs: 15 * 60 * 1000, max: 60 },
};

async function checkRateLimit(scope, identity) {
  const rule = rateLimits[scope];
  if (!rule) return { allowed: true };
  const bucket = `${scope}:${identity}`.slice(0, 180);
  try {
    await q('CREATE rate_limit_hit SET bucket = $bucket, created_at = time::now();', { bucket });
    const rows = await q(
      `SELECT count() AS count FROM rate_limit_hit
       WHERE bucket = $bucket AND created_at > time::now() - ${Math.round(rule.windowMs / 1000)}s
       GROUP ALL;`,
      { bucket },
    );
    const hits = Number(rows[0]?.count || 0);
    if (hits > rule.max) return { allowed: false, bucket, hits, max: rule.max, windowMs: rule.windowMs };
    return { allowed: true, hits, max: rule.max };
  } catch (error) {
    // The limiter must never lock everyone out because the database hiccuped:
    // fail open and let the normal handler answer.
    console.error('[rate-limit-fail]', scope, error && error.message);
    return { allowed: true };
  }
}

async function pruneRateLimits() {
  try { await q('DELETE rate_limit_hit WHERE created_at < time::now() - 25h;'); } catch { /* best effort */ }
}
setInterval(pruneRateLimits, 60 * 60 * 1000).unref();

function aiPolicyFor(workspace) {
  return {
    allowedProviders: Array.isArray(workspace?.ai_allowed_providers) ? workspace.ai_allowed_providers.map(String) : [],
    defaultProvider: workspace?.ai_default_provider ? String(workspace.ai_default_provider) : null,
    runCap: Number.isFinite(Number(workspace?.ai_run_cap)) && workspace?.ai_run_cap !== null && workspace?.ai_run_cap !== undefined ? Number(workspace.ai_run_cap) : null,
    monthlyBudgetMicros: Number.isFinite(Number(workspace?.ai_monthly_budget_micros)) && workspace?.ai_monthly_budget_micros !== null && workspace?.ai_monthly_budget_micros !== undefined ? Number(workspace.ai_monthly_budget_micros) : null,
  };
}

// First instant of the current UTC calendar month — the budget window.
function monthStartIso() {
  const now = new Date();
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1)).toISOString();
}

// { budget: null | micros, spend: micros, remaining, limited }
async function aiBudgetForWorkspace(workspaceId) {
  const workspace = await findWorkspace(workspaceId);
  const budget = aiPolicyFor(workspace).monthlyBudgetMicros;
  let spend = 0;
  if (budget !== null) {
    const rows = await q(
      `SELECT math::sum(cost_micros ?? 0) AS spend FROM ai_run
       WHERE workspace = ${recordLiteral('workspace', workspaceId)}
         AND created_at >= d${JSON.stringify(monthStartIso())}
       GROUP ALL;`,
    );
    spend = Number(rows[0]?.spend || 0);
  }
  const limited = budget !== null && spend >= budget;
  return { budget, spend, remaining: budget === null ? null : Math.max(0, budget - spend), limited };
}

const budgetRefusal = (budgetInfo) => `This workspace reached its monthly AI budget (${(budgetInfo.spend / 1e6).toFixed(2)} of ${(budgetInfo.budget / 1e6).toFixed(2)} ${costCurrency} this month). Raise or remove the budget in Settings → AI, or wait for next month.`;

// Run-first ledger: the run row is created BEFORE the provider call (status
// 'pending') and updated with the outcome afterwards. A crash between the two
// leaves a pending row that still counted toward caps/budgets — the spend was
// attempted, which is exactly what the budgets protect — and the boot
// migration finalizes stale pending rows as 'recorded' so nothing is lost.
// Token counts come from the provider (or the length estimate); cost is
// derived at write time so the ledger is comparable across providers.
async function beginAiRun({ workspaceId, provider = null, model = null, feature, accountId = null, sessionId = null, noteId = null, jobId = null, attempt = 0, promptChars = 0 }) {
  try {
    const row = {
      workspace: new RecordId('workspace', workspaceId),
      feature: String(feature).slice(0, 40),
      status: 'error',
      ledger_status: 'pending',
      prompt_chars: Math.max(0, Math.round(Number(promptChars) || 0)),
      response_chars: 0,
      duration_ms: 0,
      prompt_tokens: 0,
      completion_tokens: 0,
      total_tokens: 0,
      cost_micros: 0,
      attempt: Math.max(0, Math.round(Number(attempt) || 0)),
      created_at: new Date(),
    };
    if (provider) row.provider = new RecordId('ai_provider', recordId(provider));
    if (model) row.model = String(model).slice(0, 120);
    if (accountId) row.account = new RecordId('account', recordId(accountId));
    if (sessionId) row.session = new RecordId('chat_session', recordId(sessionId));
    if (noteId) row.note = new RecordId('notes', recordId(noteId));
    if (jobId) row.job = new RecordId('ai_job', recordId(jobId));
    const rows = await q(`CREATE ai_run SET ${literalAssignments(row).join(', ')} RETURN AFTER;`);
    return rows[0] || null;
  } catch (error) {
    // Ledger failures must never break the feature; the run just isn't counted.
    console.error('[ai-run-begin-fail]', feature, error && error.message);
    return null;
  }
}

async function completeAiRun(runRow, { reply = '', usage = null, error = null, startedAt = Date.now() }) {
  if (!runRow) return;
  try {
    const durationMs = Math.max(0, Date.now() - startedAt);
    const promptTokens = Math.max(0, Math.round(Number(usage?.promptTokens) || 0));
    const completionTokens = Math.max(0, Math.round(Number(usage?.completionTokens) || 0));
    const totalTokens = Math.max(0, Math.round(Number(usage?.totalTokens) || 0)) || promptTokens + completionTokens;
    const assignments = [
      `status = ${inlineValue(error ? 'error' : 'ok')}`,
      'ledger_status = "recorded"',
      `response_chars = ${Math.round(String(reply).length)}`,
      `duration_ms = ${durationMs}`,
      `prompt_tokens = ${promptTokens}`,
      `completion_tokens = ${completionTokens}`,
      `total_tokens = ${totalTokens}`,
      `cost_micros = ${estimateCostMicros(runRow.model, promptTokens, completionTokens)}`,
      `cost_currency = ${inlineValue(costCurrency)}`,
    ];
    if (error) assignments.push(`error_message = ${inlineValue(String(error).slice(0, 400))}`);
    await q(`UPDATE type::thing("ai_run", $id) SET ${assignments.join(', ')};`, { id: recordId(runRow.id) });
  } catch (error) { console.error('[ai-run-complete-fail]', error && error.message); }
}

/* ---------- Phase 3: cap enforcement, token/cost accounting, job queue ---------- */

const capWindowSeconds = 3600;

// Runs that count against the cap: completed provider round-trips in the last
// hour. The cap is therefore "provider calls per hour", matching the Settings
// copy, and it is enforced before a call is made.
async function aiRunsThisHour(workspaceId) {
  const rows = await q(
    `SELECT count() AS count FROM ai_run
     WHERE workspace = ${recordLiteral('workspace', workspaceId)}
       AND created_at > time::now() - ${capWindowSeconds}s
     GROUP ALL;`,
  );
  return Number(rows[0]?.count || 0);
}

// { cap: null | number, used: number, remaining: null | number, limited: bool }
async function aiCapForWorkspace(workspaceId) {
  const workspace = await findWorkspace(workspaceId);
  const cap = aiPolicyFor(workspace).runCap;
  const used = await aiRunsThisHour(workspaceId);
  const limited = cap !== null && used >= cap;
  return { cap, used, remaining: cap === null ? null : Math.max(0, cap - used), limited };
}

// Refuse with 429 before a provider call when the hourly budget is spent.
// Failed calls count toward the cap on purpose: each one burned a real attempt
// against the provider, which is exactly what the budget protects.
const capRefusal = (capInfo) => `This workspace reached its AI run cap (${capInfo.used}/${capInfo.cap} runs this hour). Raise or remove the cap in Settings → AI, or wait for the window to reset.`;

// One guard for every provider entry point (chat, study, job enqueue): both
// limits are checked and the first refusal wins. The job worker reuses the
// same helpers through its fail-fast path.
async function aiGuardForWorkspace(workspaceId) {
  const [capInfo, budgetInfo] = await Promise.all([
    aiCapForWorkspace(workspaceId),
    aiBudgetForWorkspace(workspaceId),
  ]);
  if (capInfo.limited) return { blocked: true, status: 429, body: { error: capRefusal(capInfo), cap: capInfo } };
  if (budgetInfo.limited) return { blocked: true, status: 429, body: { error: budgetRefusal(budgetInfo), budget: budgetInfo } };
  return { blocked: false, capInfo, budgetInfo };
}

// Estimate cost in micros (1e6 = one currency unit) from per-model pricing.// Unknown models price at zero so rows stay comparable without inventing cost.
const AI_PRICING = {
  // USD per 1M tokens: [input, output]. Extending this table is all it takes
  // to price a new model; anything absent estimates as free.
  'gpt-4o': [2.5, 10],
  'gpt-4o-mini': [0.15, 0.6],
  'gpt-4.1': [2, 8],
  'gpt-4.1-mini': [0.4, 1.6],
  'o3': [2, 8],
  'o4-mini': [1.1, 4.4],
};
const costCurrency = 'USD';

function estimateCostMicros(model, promptTokens, completionTokens) {
  const price = AI_PRICING[String(model || '').toLowerCase()];
  if (!price) return 0;
  const usd = (promptTokens * price[0] + completionTokens * price[1]) / 1_000_000;
  return Math.round(usd * 1_000_000); // micros
}

// Per-provider usage totals for the last hour (and all time for the ledger
// summary): tokens, cost, and call counts, grouped by provider name.
async function aiUsageSummary(workspaceId) {
  const rows = await q(
    `SELECT provider, model, count() AS calls,
            math::sum(total_tokens ?? 0) AS tokens,
            math::sum(cost_micros ?? 0) AS cost
     FROM ai_run
     WHERE workspace = ${recordLiteral('workspace', workspaceId)}
     GROUP BY provider, model;`,
  );
  const groups = rows.map((row) => ({
    provider: row.provider ? recordId(row.provider) : null,
    model: row.model || '(unknown)',
    calls: Number(row.calls || 0),
    tokens: Number(row.tokens || 0),
    costMicros: Number(row.cost || 0),
  }));
  const monthRows = await q(
    `SELECT math::sum(cost_micros ?? 0) AS spend, count() AS calls FROM ai_run
     WHERE workspace = ${recordLiteral('workspace', workspaceId)}
       AND created_at >= d${JSON.stringify(monthStartIso())}
     GROUP ALL;`,
  );
  return {
    currency: costCurrency,
    totalCalls: groups.reduce((sum, group) => sum + group.calls, 0),
    totalTokens: groups.reduce((sum, group) => sum + group.tokens, 0),
    totalCostMicros: groups.reduce((sum, group) => sum + group.costMicros, 0),
    monthCalls: Number(monthRows[0]?.calls || 0),
    monthCostMicros: Number(monthRows[0]?.spend || 0),
    byProvider: groups.sort((a, b) => b.costMicros - a.costMicros || b.tokens - a.tokens),
  };
}

// ---- AI job queue -------------------------------------------------------
// A job is a deferred provider call whose state machine lives in SurrealDB:
// queued → running → succeeded | failed | cancelled. Failed attempts get a new
// next_attempt_at with exponential backoff until max_attempts, then the job is
// terminally failed. The worker claims with a single conditional UPDATE, so
// two workers can never run the same job.
const jobRetryBaseMs = 5_000;

function jobBackoffMs(attempt) {
  return jobRetryBaseMs * 2 ** Math.max(0, attempt - 1);
}

// Deterministic idempotency key from the job's identity: the same logical
// operation (kind + payload + requester) always maps to the same key within a
// workspace, so a retried enqueue returns the original job. Callers may pass
// their own key to tie several operations to one job deliberately.
function deriveJobKey(workspaceId, kind, payload, accountId) {
  const material = JSON.stringify({ kind, payload, by: accountId ? recordId(accountId) : null });
  return crypto.createHash('sha256').update(`${workspaceId}:${material}`).digest('hex').slice(0, 32);
}

// An idempotent enqueue: with a key, an existing job that is still queued or
// running wins and is returned with created=false, so a client retry (or a
// double-click) can never queue the same provider work twice. Once a job is
// terminal the key is free again — re-running the operation is then a new,
// deliberate spend.
async function createAiJob({ workspaceId, kind, payload = {}, accountId = null, maxAttempts = 3, idempotencyKey = null, runAt = null }) {
  const identity = deriveJobKey(workspaceId, kind, payload, accountId);
  const key = idempotencyKey || identity;
  const wsClause = recordLiteral('workspace', workspaceId);
  const existing = await q(
    `SELECT * FROM ai_job WHERE workspace = ${wsClause} AND idempotency_key = $key
       AND status IN ['queued', 'running'] LIMIT 1;`,
    { key },
  );
  // A keyless (derived) enqueue also dedupes against an active job of the same
  // operation identity even when that job's key was caller-chosen, so a
  // double-click can never fork one queued operation into two spends.
  // Explicitly distinct keys are deliberate and stay distinct.
  let match = existing[0];
  if (!match && !idempotencyKey) {
    const byIdentity = await q(
      `SELECT * FROM ai_job WHERE workspace = ${wsClause} AND identity = $identity
         AND status IN ['queued', 'running'] LIMIT 1;`,
      { identity },
    );
    match = byIdentity[0];
  }
  if (match) return { job: match, created: false };
  const row = {
    workspace: new RecordId('workspace', workspaceId),
    kind: String(kind).slice(0, 40),
    status: 'queued',
    payload: payload && typeof payload === 'object' ? payload : {},
    attempts: 0,
    max_attempts: Math.max(1, Math.round(Number(maxAttempts) || 3)),
    next_attempt_at: runAt || new Date(),
    idempotency_key: key,
    identity,
    created_at: new Date(),
    updated_at: new Date(),
  };
  if (accountId) row.requested_by = new RecordId('account', recordId(accountId));
  try {
    const rows = await q(`CREATE ai_job SET ${literalAssignments(row).join(', ')} RETURN AFTER;`);
    return { job: rows[0], created: true };
  } catch (error) {
    // The (workspace, key) unique index also guards a race between two
    // concurrent enqueues: the loser reads the winner's job instead of failing.
    // The status filter keeps a just-terminal job from being mistaken for the
    // winner (terminal rows have already released the key, so this is purely
    // defensive against a mid-transition read).
    if (!/unique/i.test(String(error?.message))) throw error;
    const raced = await q(
      `SELECT * FROM ai_job WHERE workspace = ${recordLiteral('workspace', workspaceId)} AND idempotency_key = $key
         AND status IN ['queued', 'running'] LIMIT 1;`,
      { key },
    );
    if (!raced[0]) throw error;
    return { job: raced[0], created: false };
  }
}

async function claimDueJobs(limit = 3) {
  const due = await q(
    `SELECT * FROM ai_job WHERE status = 'queued' AND next_attempt_at <= time::now() ORDER BY created_at ASC LIMIT ${Math.max(1, Math.round(limit) || 1)};`,
  );
  const claimed = [];
  for (const job of due) {
    // The conditional UPDATE is the claim: only one worker's UPDATE matches,
    // so a job picked by two workers is executed once. SurrealDB field
    // defaults apply at write time but `CREATE ... SET` rows can still read
    // attempts as NONE, so the increment is null-safe.
    const rows = await q(
      `UPDATE type::thing("ai_job", $id) MERGE { status: 'running', attempts: (attempts ?? 0) + 1, started_at: time::now(), updated_at: time::now() }
       WHERE status = 'queued' AND next_attempt_at <= time::now() RETURN AFTER;`,
      { id: recordId(job.id) },
    );
    if (rows[0]) claimed.push(rows[0]);
  }
  return claimed;
}

async function finishJob(jobId, { status, runId = null, error = null, retry = false, nextAttemptAt = null }) {
  const assignments = [
    `status = ${inlineValue(status)}`,
    'updated_at = time::now()',
  ];
  if (runId) assignments.push(`run = ${recordLiteral('ai_run', runId)}`);
  if (error) assignments.push(`last_error = ${inlineValue(String(error).slice(0, 400))}`);
  if (retry) {
    // A retry is not a finish: the job goes back to 'queued' with a fresh
    // scheduled attempt, and finished_at stays unset.
    assignments.push(`next_attempt_at = ${nextAttemptAt ? inlineValue(nextAttemptAt) : 'time::now()'}`);
  } else {
    // Terminal: finished_at is set and the idempotency key is released so the
    // same key can enqueue a fresh job. The key must not linger in the
    // (workspace, key) unique index under its real value, and it cannot be
    // set to NONE either (SurrealDB v1 indexes NONE, which would collide
    // across terminal rows) — so it takes a per-row 'released:' marker.
    // identity stays for history and dedupe joins.
    assignments.push('finished_at = time::now()', `idempotency_key = string::concat('released:', ${recordLiteral('ai_job', jobId)})`);
  }
  await q(`UPDATE type::thing("ai_job", $id) SET ${assignments.join(', ')};`, { id: jobId });
}

// The worker tick: claim due jobs, execute each by kind, and honour retries.
// One tick runs jobs sequentially; the interval keeps throughput modest and
// the engine load predictable.
// Fail fast before any provider work when the workspace has hit a limit —
// the job goes back to the queue with a delayed retry instead of burning a
// doomed attempt.
async function jobGuardOrDefer(job) {
  const guard = await aiGuardForWorkspace(recordId(job.workspace));
  if (!guard.blocked) return null;
  const attempts = Number(job.attempts || 1);
  if (attempts < Number(job.max_attempts || 3)) {
    const nextAttemptAt = new Date(Date.now() + Math.max(jobBackoffMs(attempts), 60_000));
    await finishJob(recordId(job.id), { status: 'queued', error: guard.body.error, retry: true, nextAttemptAt });
  } else {
    await finishJob(recordId(job.id), { status: 'failed', error: guard.body.error });
    await recordAudit('ai_job.failed', job.requested_by ? recordId(job.requested_by) : null, { kind: job.kind, error: guard.body.error }, recordId(job.id), recordId(job.workspace));
  }
  return guard.body;
}

// Material for a summarization run: the note content, or the extracted text of
// an attachment. Attachments are the common case for long documents.
async function summarizationSource(workspaceId, payload) {
  if (payload.attachmentId) {
    const rows = await q(
      `SELECT * FROM attachments WHERE id = type::thing("attachments", $id) LIMIT 1;`,
      { id: payload.attachmentId },
    );
    const attachment = rows[0];
    const text = String(attachment?.text_content || '').trim();
    if (!attachment || !text) return null;
    return { title: attachment.name, content: text.slice(0, 60_000), kind: 'attachment' };
  }
  if (payload.noteId) {
    const rows = await q(
      `SELECT * FROM type::thing("notes", $id) WHERE workspace = ${recordLiteral('workspace', workspaceId)} LIMIT 1;`,
      { id: payload.noteId },
    );
    const note = rows[0];
    if (!note) return null;
    return { title: noteTitle(note.content) || 'Note', content: String(note.content).slice(0, 60_000), kind: 'note' };
  }
  return null;
}

async function executeAiJob(job) {
  const jobId = recordId(job.id);
  const workspaceId = recordId(job.workspace);
  const payload = job.payload || {};
  try {
    if (job.kind === 'study.generate') {
      const deferred = await jobGuardOrDefer(job);
      if (deferred) return;
      const noteRows = await q(`SELECT * FROM type::thing("notes", $id) WHERE workspace = ${recordLiteral('workspace', workspaceId)} LIMIT 1;`, { id: payload.noteId });
      const note = noteRows[0];
      if (!note) throw new Error('Note not found for job');
      const promptRows = payload.promptId ? await q('SELECT * FROM type::thing("prompt_template", $id) LIMIT 1;', { id: String(payload.promptId) }) : [];
      const candidates = await generateStudyCandidatesWithProvider(note, promptRows[0], workspaceId, job.requested_by ? recordId(job.requested_by) : null, { jobId, attempt: Number(job.attempts || 1) });
      if (!candidates) throw new Error('Provider returned no usable flashcards');
      const created = await createStudyItems({ candidates, noteId: recordId(note.id), source: 'provider', accountSub: job.requested_by ? recordId(job.requested_by) : null, workspaceId });
      await finishJob(jobId, { status: 'succeeded', error: null });
      await recordAudit('ai_job.succeeded', job.requested_by ? recordId(job.requested_by) : null, { kind: job.kind, created: created.length }, jobId, workspaceId);
    } else if (job.kind === 'summarize.note') {
      const deferred = await jobGuardOrDefer(job);
      if (deferred) return;
      const source = await summarizationSource(workspaceId, payload);
      if (!source) throw new Error('Summarization source not found or has no readable text');
      const { provider } = await resolveProviderForWorkspace(workspaceId);
      if (!provider) throw new Error('No active AI provider is configured');
      const systemContent = 'You summarize study material. Reply with markdown: a one-paragraph overview, then "## Key points" with 3-7 bullets, then "## Review questions" with up to 3 questions.';
      const userContent = `Summarize this material titled "${source.title}".\n\n---\n${source.content}`;
      const started = Date.now();
      const runRow = await beginAiRun({
        workspaceId,
        provider: recordId(provider.id),
        model: provider.model,
        feature: 'summarize.note',
        accountId: job.requested_by ? recordId(job.requested_by) : null,
        noteId: payload.noteId || null,
        jobId,
        attempt: Number(job.attempts || 1),
        promptChars: systemContent.length + userContent.length,
      });
      let reply;
      let usage = null;
      try {
        ({ content: reply, usage } = await callProvider(provider, [
          { role: 'system', content: systemContent },
          { role: 'user', content: userContent },
        ]));
        await completeAiRun(runRow, { reply, usage, startedAt: started });
      } catch (error) {
        await completeAiRun(runRow, { error: error.message, startedAt: started });
        throw error;
      }
      // The summary lands as a linked note in the workspace, tagged so it is
      // findable; the run ledger row carries the source note id.
      const lane = await findCategory((await findWorkspace(workspaceId))?.default_category || 'notes', workspaceId) || await findCategory('notes', workspaceId);
      if (!lane) throw new Error('No lane available for the summary note');
      const heading = `Summary: ${source.title}`.slice(0, 120);
      const content = `# ${heading}\n\n${reply}\n\n---\n*Generated by an AI run from ${source.kind === 'attachment' ? `attachment ${payload.attachmentId}` : `[[${source.title}]]`}.*`;
      const accountSub = job.requested_by ? recordId(job.requested_by) : null;
      const tagIds = await ensureTags(['ai-summary'], workspaceId);
      const rows = await q(`CREATE notes CONTENT {
        content: $content,
        category: ${recordLiteral('category', recordId(lane.id))},
        account: ${accountSub ? `type::thing('account', $account)` : 'NONE'},
        created_by: ${accountSub ? `type::thing('account', $account)` : 'NONE'},
        workspace: ${recordLiteral('workspace', workspaceId)},
        tags: ${inlineValue(tagIds)},
        is_archived: false,
        is_recycle: false,
        is_top: false,
        is_share: false,
        flags: { ai_summary: true },
        metadata: { job: ${inlineValue(jobId)}, source_kind: ${inlineValue(source.kind)} },
        word_count: ${countWords(content)},
        created_at: time::now(),
        updated_at: time::now()
      } RETURN AFTER;`, accountSub ? { content, account: accountSub } : { content });
      if (rows[0]) {
        const summaryId = recordId(rows[0].id);
        if (payload.noteId) {
          try { await syncNoteLinks(summaryId, content, accountSub, workspaceId); } catch { /* links are best-effort */ }
        }
        await recordNoteActivity(summaryId, workspaceId, 'note.created', accountSub, { category: recordId(lane.id), via: 'ai_job', job: jobId });
      }
      await finishJob(jobId, { status: 'succeeded', error: null });
      await recordAudit('ai_job.succeeded', accountSub, { kind: job.kind, summary: rows[0] ? recordId(rows[0].id) : null }, jobId, workspaceId);
    } else {
      throw new Error(`Unknown job kind: ${job.kind}`);
    }
  } catch (error) {
    const attempts = Number(job.attempts || 1);
    if (attempts < Number(job.max_attempts || 3)) {
      const nextAttemptAt = new Date(Date.now() + jobBackoffMs(attempts));
      await finishJob(jobId, { status: 'queued', error: error.message, retry: true, nextAttemptAt });
      console.warn('[ai-job-retry]', job.kind, jobId, attempts, error.message);
    } else {
      await finishJob(jobId, { status: 'failed', error: error.message });
      await recordAudit('ai_job.failed', job.requested_by ? recordId(job.requested_by) : null, { kind: job.kind, error: error.message }, jobId, workspaceId);
    }
  }
}

async function runJobWorker() {
  try {
    const jobs = await claimDueJobs(3);
    for (const job of jobs) await executeAiJob(job);
  } catch (error) { console.error('[ai-job-worker]', error && error.message); }
}
setInterval(runJobWorker, 5_000).unref();

function publicAiJob(row) {
  return {
    id: recordId(row.id),
    kind: row.kind,
    status: row.status,
    attempts: Number(row.attempts || 0),
    maxAttempts: Number(row.max_attempts || 3),
    lastError: row.last_error || null,
    run: row.run ? recordId(row.run) : null,
    idempotencyKey: row.idempotency_key && !String(row.idempotency_key).startsWith('released:') ? row.idempotency_key : null,
    nextAttemptAt: isoOrNull(row.next_attempt_at),
    createdAt: isoOrNull(row.created_at),
    startedAt: isoOrNull(row.started_at),
    finishedAt: isoOrNull(row.finished_at),
    updatedAt: isoOrNull(row.updated_at),
  };
}

// Permissions follow the workspace role, not the account's global role: a
// member is only as powerful as their membership in the workspace they are in.
function requirePermission(permission) {
  return async (req, res, next) => {
    try {
      req.accountRecord = await currentAccount(req);
      if (!req.accountRecord) return res.status(401).json({ error: 'User not found' });
      // The workspace edge is the source of truth for the effective role; the
      // account.role field remains as a legacy fallback for pre-Phase-2 rows.
      // auth() already resolved the active workspace and its membership, so the
      // effective role here is the role in *that* workspace.
      req.membershipRole = req.workspaceRole || req.accountRecord.role;
      const effective = { ...req.accountRecord, role: req.membershipRole };
      if (!can(effective, permission)) return res.status(403).json({ error: 'This role cannot perform that action' });
      next();
    } catch (error) {
      res.status(503).json({ error: error.message });
    }
  };
}

// `roleOverride` carries the effective role in the request's workspace: the
// membership edge, not the legacy account.role column, decides what a member
// can do. `accountRole` stays visible for migrations and diagnostics.
function publicUser(row, roleOverride = null) {
  const role = roleOverride || row.role;
  return { id: recordId(row.id), name: row.name, role, accountRole: row.role, permissions: rolePermissions[role] || [] };
}

// A row in the People tab: the role here is the membership role in the
// workspace being looked at, and `canManage` tells the client whether the
// signed-in member may edit or remove this row.
function publicMember(row, { role, callerRole, isSelf = false, owners = 0 } = {}) {
  const effective = role || row.role;
  return {
    ...publicUser(row, effective),
    isSelf,
    canManage: !isSelf
      && (roleRank[callerRole] || 0) >= (roleRank[effective] || 0)
      && !(isOwnerRole(effective) && owners <= 1),
  };
}

function publicWorkspaceSummary(row, { role, isActive, notes } = {}) {
  return {
    id: recordId(row.id),
    name: row.name,
    slug: row.slug || recordId(row.id),
    description: row.description || '',
    role: role || null,
    isActive: Boolean(isActive),
    isArchived: Boolean(row.is_archived),
    notes: notes ?? null,
    contextRoots: Array.isArray(row.context_roots) ? row.context_roots.map(String) : [],
  };
}

// The context roots a workspace may use. An empty list means every configured
// root, which is what pre-existing workspaces keep.
function contextRootsForWorkspace(workspace) {
  const allowed = Array.isArray(workspace?.context_roots) ? workspace.context_roots.map(String) : [];
  if (!allowed.length) return contextRoots;
  return contextRoots.filter((root) => allowed.includes(root.id));
}

// Public shape for AI providers: never leak the stored API key.
function publicProvider(row) {
  return {
    id: recordId(row.id),
    name: row.name,
    kind: row.kind,
    baseUrl: row.base_url,
    model: row.model,
    isActive: Boolean(row.is_active),
    hasKey: Boolean(row.api_key),
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
  };
}

function publicPrompt(row) {
  return {
    id: recordId(row.id),
    title: row.title,
    body: row.body,
    isSystem: Boolean(row.is_system),
  };
}

const contextRoot = (id) => contextRoots.find((root) => root.id === id) || null;

// What a file contributes to a chat: readable text, a PDF whose text stream is
// extracted, or an image handed to the model as a data URL.
function contextFileKind(name) {
  const lower = String(name).toLowerCase();
  const extension = path.extname(lower);
  if (contextTextNames.has(lower) || contextTextExtensions.has(extension)) return 'text';
  if (contextPdfExtensions.has(extension)) return 'pdf';
  if (contextImageExtensions.has(extension)) return 'image';
  return null;
}

const isAttachableFile = (name) => Boolean(contextFileKind(name));

// Resolve a request-supplied relative path inside one configured root. Both the
// lexical path and the real path (symlinks followed) must stay inside the root,
// so parent traversal and symlink escapes are rejected before any filesystem
// call, and a request can never reach a path that configuration did not expose.
function resolveContextPath(root, relative) {
  const raw = String(relative || '').replace(/\\/g, '/').replace(/^\/+/, '').replace(/\/+$/, '');
  if (raw.includes('\0')) return null;
  const base = path.resolve(root.dir);
  const abs = path.resolve(base, raw);
  if (abs !== base && !abs.startsWith(base + path.sep)) return null;
  try {
    const real = fs.realpathSync(abs);
    const realBase = fs.realpathSync(base);
    if (real !== realBase && !real.startsWith(realBase + path.sep)) return null;
  } catch { /* not created yet: writes validate the parent instead */ }
  return { abs, relative: raw, base };
}

function publicContextRoot(root) {
  let exists = false;
  let entries = 0;
  try { exists = fs.statSync(root.dir).isDirectory(); } catch { /* not mounted */ }
  if (exists) {
    try { entries = fs.readdirSync(root.dir).filter((name) => !contextIgnoredDirs.has(name)).length; } catch { /* unreadable */ }
  }
  return { id: root.id, label: root.label, kind: root.kind, writable: root.writable, exists, entries };
}

function listContextDir(root, resolved) {
  const entries = [];
  for (const entry of fs.readdirSync(resolved.abs, { withFileTypes: true })) {
    if (entry.name.startsWith('.') && entry.name !== '.env.example') continue;
    if (contextIgnoredDirs.has(entry.name)) continue;
    if (entry.isSymbolicLink()) continue;
    const child = resolved.relative ? `${resolved.relative}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      entries.push({ name: entry.name, path: child, type: 'dir', size: 0, attachable: false });
    } else if (entry.isFile() && contextFileKind(entry.name)) {
      let size = 0;
      try { size = fs.statSync(path.join(resolved.abs, entry.name)).size; } catch { /* raced away */ }
      const entryKind = contextFileKind(entry.name);
      const limit = entryKind === 'image' ? maxContextImageBytes : maxContextBytes;
      entries.push({ name: entry.name, path: child, type: 'file', kind: entryKind, size, attachable: size <= limit, ref: `${root.id}:${child}` });
    }
    if (entries.length >= 400) break;
  }
  entries.sort((a, b) => (a.type === b.type ? a.name.localeCompare(b.name) : a.type === 'dir' ? -1 : 1));
  return entries;
}

// Read one `root:path` ref as chat context. Returns null for anything that is
// not a supported file inside a configured root; text and PDF files come back
// as `content`, images as a `dataUrl` for the multimodal message.
function readContextFile(ref) {
  const separator = String(ref || '').indexOf(':');
  if (separator < 1) return null;
  const root = contextRoot(String(ref).slice(0, separator));
  if (!root) return null;
  const resolved = resolveContextPath(root, String(ref).slice(separator + 1));
  if (!resolved) return null;
  let stat;
  try { stat = fs.statSync(resolved.abs); } catch { return null; }
  if (!stat.isFile()) return null;
  const name = path.basename(resolved.abs);
  const kind = contextFileKind(name);
  if (!kind) return null;
  const refId = `${root.id}:${resolved.relative}`;
  const base = { ref: refId, name, path: resolved.relative, size: stat.size, kind };

  if (kind === 'image') {
    if (stat.size > maxContextImageBytes) return { ...base, truncated: false, content: '', dataUrl: null, status: 'too-large' };
    const mime = contextImageExtensions.get(path.extname(name).toLowerCase()) || 'application/octet-stream';
    return { ...base, truncated: false, content: '', status: 'ready', dataUrl: `data:${mime};base64,${fs.readFileSync(resolved.abs).toString('base64')}` };
  }

  if (kind === 'pdf') {
    const text = extractPdfText(fs.readFileSync(resolved.abs)).trim().slice(0, MAX_EXTRACTED_CHARS);
    return { ...base, truncated: stat.size > MAX_EXTRACTED_CHARS, content: text, dataUrl: null, status: text ? 'ready' : 'unsupported' };
  }

  const buffer = fs.readFileSync(resolved.abs).subarray(0, maxContextBytes);
  return { ...base, truncated: stat.size > buffer.length, content: buffer.toString('utf8'), dataUrl: null, status: 'ready' };
}

// `allowedRoots` is the workspace's context-root allow-list; a ref to a root the
// workspace cannot use is rejected here, not merely hidden in the UI.
function sanitizeContextRefs(input, allowedRoots = null) {
  if (!Array.isArray(input)) return [];
  const allowed = allowedRoots ? new Set(allowedRoots.map(String)) : null;
  const seen = new Set();
  const refs = [];
  for (const entry of input) {
    const ref = String(entry || '').trim();
    if (!ref || ref.length > 400 || seen.has(ref)) continue;
    if (allowed && !allowed.has(ref.slice(0, ref.indexOf(':')))) continue;
    const file = readContextFile(ref);
    if (!file || file.status === 'too-large') continue;
    seen.add(ref);
    refs.push(ref);
    if (refs.length >= maxContextFiles) break;
  }
  return refs;
}

// Assemble the read-only context handed to the model: one text block bounded so
// a message can never grow past the provider window on its own, plus the image
// files that travel as multimodal parts on the current turn.
function buildContextBlock(refs) {
  const parts = [];
  const images = [];
  const skipped = [];
  let used = 0;
  for (const ref of refs) {
    const file = readContextFile(ref);
    if (!file) { skipped.push(ref); continue; }
    if (file.kind === 'image') {
      if (file.dataUrl && images.length < maxContextImages) images.push({ ref: file.ref, name: file.name, dataUrl: file.dataUrl });
      else skipped.push(ref);
      continue;
    }
    const remaining = maxContextBlockChars - used;
    if (remaining < 400) { skipped.push(ref); continue; }
    if (file.kind === 'pdf' && !file.content) {
      parts.push(`--- ${file.ref} (pdf, no extractable text) ---\nThis PDF has no text layer (scanned or image-only). Ask about the image instead.`);
      continue;
    }
    const body = file.content.slice(0, remaining);
    used += body.length;
    const note = file.truncated || body.length < file.content.length ? 'truncated' : 'complete';
    parts.push(`--- ${file.ref} (${file.kind === 'pdf' ? 'pdf text, ' : ''}${note}) ---\n${body}`);
  }
  const text = parts.length ? `WORKSPACE FILES (read-only, attached by the member for this task):\n\n${parts.join('\n\n')}` : '';
  return { text, images, skipped };
}

function publicSession(row) {
  return {
    id: recordId(row.id),
    title: row.title,
    provider: row.provider ? recordId(row.provider) : null,
    promptId: row.prompt_id || null,
    contextFiles: Array.isArray(row.context_files) ? row.context_files.map(String) : [],
    createdBy: row.created_by ? recordId(row.created_by) : null,
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
  };
}

function publicMessage(row) {
  return {
    id: recordId(row.id),
    session: recordId(row.session),
    role: row.role,
    content: row.content,
    promptId: row.prompt_id || null,
    model: row.model || null,
    error: Boolean(row.error),
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
  };
}

function publicWorkspace(row) {
  return {
    id: recordId(row.id),
    name: row.name,
    description: row.description,
    defaultCategory: row.default_category,
    aiContext: row.ai_context,
    theme: themes.includes(row.theme) ? row.theme : 'system',
    themeVariant: themeVariants.includes(row.theme_variant) ? row.theme_variant : 'default',
    buttonStyle: buttonStyles.includes(row.button_style) ? row.button_style : 'default',
    badgeStyle: badgeStyles.includes(row.badge_style) ? row.badge_style : 'default',
    accent: accents.includes(row.accent) ? row.accent : 'violet',
    fontScale: fontScales.includes(row.font_scale) ? row.font_scale : 'default',
    styleVariant: styleVariants.includes(row.style_variant) ? row.style_variant : 'sharp',
    radiusScale: radiusScales.includes(row.radius_scale) ? row.radius_scale : 'default',
    edgeStrength: edgeStrengths.includes(row.edge_strength) ? row.edge_strength : 'default',
    shadowDepth: shadowDepths.includes(row.shadow_depth) ? row.shadow_depth : 'default',
    density: densities.includes(row.density) ? row.density : 'cozy',
    retentionDays: row.retention_days != null ? Number(row.retention_days) : null,
    purgeAfterDays: row.purge_after_days != null ? Number(row.purge_after_days) : null,
    updatedAt: row.updated_at instanceof Date ? row.updated_at.toISOString() : row.updated_at,
  };
}

async function findWorkspace(workspaceId = 'default') {
  const rows = await q(`SELECT * FROM ${recordLiteral('workspace', workspaceId)} LIMIT 1;`);
  return rows[0];
}

// SurrealQL literal for the request's active workspace, used inside query
// templates so every read and write is bounded by the same scope.
const wsLiteral = (req) => recordLiteral('workspace', req?.workspaceId || 'default');

async function auth(req, res, next) {
  const header = req.headers.authorization || '';
  if (!header.startsWith('Bearer ')) return res.status(401).json({ error: 'Not authenticated' });
  try {
    req.account = jwt.verify(header.slice(7), jwtSecret);
    const scope = await resolveWorkspaceScope(req.account.sub);
    req.workspaceId = scope.workspaceId;
    req.workspaceRole = scope.role;
    req.memberships = scope.memberships;
    next();
  } catch (error) {
    if (error?.name === 'JsonWebTokenError' || error?.name === 'TokenExpiredError') {
      // Token abuse is throttled per IP like the other auth surfaces, so a
      // forged-token flood cannot hammer the workspace scope resolver.
      const limit = await checkRateLimit('token', clientIp(req));
      if (!limit.allowed) {
        await recordSecurityEvent('rate.blocked', { ip: clientIp(req), userAgent: String(req.headers['user-agent'] || '').slice(0, 200), detail: { scope: 'token' } });
        return res.status(429).json({ error: 'Too many attempts. Try again later.' });
      }
      await recordSecurityEvent('token.invalid', { ip: clientIp(req), userAgent: String(req.headers['user-agent'] || '').slice(0, 200), detail: { reason: error?.name } });
      return res.status(401).json({ error: 'Invalid token' });
    }
    res.status(500).json({ error: 'Unable to resolve workspace' });
  }
}

function authQueryToken(req, res, next) {
  try {
    req.account = jwt.verify(String(req.query.token || ''), jwtSecret);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

async function countRecords(table) {
  const rows = await q(`SELECT count() AS count FROM ${table} GROUP ALL;`);
  return Number(rows[0]?.count || 0);
}

// Lanes are addressed by slug inside a workspace, never by a global id, so two
// workspaces can both have a `notes` lane without colliding.
async function findCategory(slug, workspaceId = 'default') {
  const rows = await q(`SELECT * FROM category WHERE slug = $slug AND workspace = ${recordLiteral('workspace', workspaceId)} LIMIT 1;`, { slug });
  return rows[0];
}

async function requireCategory(slug, workspaceId = 'default') {
  const category = await findCategory(slug, workspaceId);
  if (!category) {
    const error = new Error('Category not found');
    error.statusCode = 400;
    throw error;
  }
  return category;
}

async function findAccount(name) {
  const rows = await q('SELECT * FROM account WHERE name = $name LIMIT 1;', { name });
  return rows[0];
}

// `workspaceId` is the workspace the account is being created in, so the legacy
// account.workspace pointer and the membership edge agree from the first write.
async function ensureAccount(name, password, role = 'superadmin', workspaceId = 'default') {
  const existing = await findAccount(name);
  if (existing) return existing;
  const rows = await q('CREATE type::thing("account", $name) CONTENT $data RETURN AFTER;', {
    name,
    data: { name, password_hash: await bcrypt.hash(password, 12), role, workspace: new RecordId('workspace', workspaceId), active_workspace: new RecordId('workspace', workspaceId), created_at: new Date() },
  });
  return rows[0];
}

// Tags stay one shared vocabulary across workspaces (a tag is a label, and the
// same `#study` means the same thing everywhere), but each tag records the
// workspace that introduced it and a workspace only lists tags it can see.
async function ensureTags(names = [], workspaceId = 'default') {
  const ids = [];
  for (const raw of names) {
    const name = String(raw).trim().replace(/^#/, '').slice(0, 40);
    if (!name) continue;
    const existing = await q('SELECT * FROM type::thing("tag", $id) LIMIT 1;', { id: name });
    if (existing[0]) { ids.push(new RecordId('tag', name)); continue; }
    try {
      await q(`CREATE ${recordLiteral('tag', name)} SET name = $name, workspace = ${recordLiteral('workspace', workspaceId)}, created_at = time::now();`, { name });
      ids.push(new RecordId('tag', name));
    } catch {
      const retry = await q('SELECT * FROM type::thing("tag", $id) LIMIT 1;', { id: name });
      if (retry[0]) ids.push(new RecordId('tag', name));
    }
  }
  return ids;
}

function issueToken(account) {
  return jwt.sign({ sub: recordId(account.id), name: account.name, role: account.role }, jwtSecret, { expiresIn: '30d' });
}

fs.mkdirSync(uploadDir, { recursive: true });
// Never let browsers or proxies cache API responses: Express's default ETag made
// conditional GETs on /api/* answer 304 and the client replayed stale bodies after
// mutations, so fresh notes/tags never appeared until a hard reload.
app.set('etag', false);
app.use(express.json({ limit: '2mb' }));
app.use('/api', (req, res, next) => { res.set('Cache-Control', 'no-store'); next(); });
app.use(express.static(path.join(__dirname, 'public'), { etag: false, setHeaders: (res) => res.set('Cache-Control', 'no-cache') }));

app.get('/health', async (_req, res) => {
  try {
    await q('RETURN 1;');
    const [categories, accounts, notes] = await Promise.all([countRecords('category'), countRecords('account'), countRecords('notes')]);
    res.json({ status: 'ok', database: 'surrealdb', schemaVersion, sdk: 'surrealdb@1', storage: { connected: true, categories, accounts, notes } });
  } catch (error) {
    res.status(503).json({ status: 'degraded', database: 'surrealdb', error: error.message });
  }
});

app.get('/api/health/storage', auth, async (_req, res) => {
  try {
    const [categories, accounts, notes, tags, attachments] = await Promise.all([
      countRecords('category'), countRecords('account'), countRecords('notes'), countRecords('tag'), countRecords('attachments'),
    ]);
    res.json({ status: 'ok', database: 'surrealdb', schemaVersion, categories, accounts, notes, tags, attachments });
  } catch (error) {
    res.status(503).json({ status: 'degraded', database: 'surrealdb', error: error.message });
  }
});

app.get('/api/settings', auth, async (req, res) => {
  res.json({
    workspace: publicWorkspace(await findWorkspace(req.workspaceId)),
    workspaceRole: req.workspaceRole,
    roles: roles.map((role) => ({ name: role, permissions: rolePermissions[role] })),
    // Only the roles this member may actually hand out, so the People tab never
    // offers an option the server would refuse.
    grantableRoles: grantableRoles.filter((role) => canGrantRole(req.workspaceRole, role)),
    inviteTtlDays,
    appearance: { themes, themeVariants, accents, fontScales, styleVariants, radiusScales, edgeStrengths, shadowDepths, densities, buttonStyles, badgeStyles },
  });
});

app.patch('/api/settings', auth, requirePermission('settings:write'), async (req, res) => {
  const updates = {};
  for (const [key, field] of [['name', 'name'], ['description', 'description'], ['defaultCategory', 'default_category'], ['aiContext', 'ai_context']]) {
    if (req.body[key] !== undefined) updates[field] = String(req.body[key]).trim();
  }
  if (req.body.theme !== undefined) {
    if (!themes.includes(req.body.theme)) return res.status(400).json({ error: 'Unknown theme' });
    updates.theme = req.body.theme;
  }
  if (req.body.themeVariant !== undefined) {
    if (!themeVariants.includes(req.body.themeVariant)) return res.status(400).json({ error: 'Unknown theme variant' });
    updates.theme_variant = req.body.themeVariant;
  }
  if (req.body.buttonStyle !== undefined) {
    if (!buttonStyles.includes(req.body.buttonStyle)) return res.status(400).json({ error: 'Unknown button style' });
    updates.button_style = req.body.buttonStyle;
  }
  if (req.body.badgeStyle !== undefined) {
    if (!badgeStyles.includes(req.body.badgeStyle)) return res.status(400).json({ error: 'Unknown badge style' });
    updates.badge_style = req.body.badgeStyle;
  }
  if (req.body.accent !== undefined) {
    if (!accents.includes(req.body.accent)) return res.status(400).json({ error: 'Unknown accent' });
    updates.accent = req.body.accent;
  }
  if (req.body.fontScale !== undefined) {
    if (!fontScales.includes(req.body.fontScale)) return res.status(400).json({ error: 'Unknown font scale' });
    updates.font_scale = req.body.fontScale;
  }
  if (req.body.styleVariant !== undefined) {
    if (!styleVariants.includes(req.body.styleVariant)) return res.status(400).json({ error: 'Unknown style variant' });
    updates.style_variant = req.body.styleVariant;
  }
  if (req.body.radiusScale !== undefined) {
    if (!radiusScales.includes(req.body.radiusScale)) return res.status(400).json({ error: 'Unknown radius scale' });
    updates.radius_scale = req.body.radiusScale;
  }
  if (req.body.edgeStrength !== undefined) {
    if (!edgeStrengths.includes(req.body.edgeStrength)) return res.status(400).json({ error: 'Unknown edge strength' });
    updates.edge_strength = req.body.edgeStrength;
  }
  if (req.body.shadowDepth !== undefined) {
    if (!shadowDepths.includes(req.body.shadowDepth)) return res.status(400).json({ error: 'Unknown shadow depth' });
    updates.shadow_depth = req.body.shadowDepth;
  }
  if (req.body.density !== undefined) {
    if (!densities.includes(req.body.density)) return res.status(400).json({ error: 'Unknown density' });
    updates.density = req.body.density;
  }
  // Phase 2 closeout: retention controls. Values are whole days; null disables
  // the window entirely (keep forever). Lower bound rejects zero so "purge
  // everything immediately" cannot be set by accident. Clearing cannot ride in
  // $updates: the SDK encodes JS null as SurrealDB NULL, and a SCHEMAFULL
  // option<number> rejects NULL — the column has to be assigned NONE, so these
  // two fields build an explicit SET clause instead of a MERGE payload.
  const clears = [];
  for (const [key, field] of [['retentionDays', 'retention_days'], ['purgeAfterDays', 'purge_after_days']]) {
    if (req.body[key] === undefined) continue;
    if (req.body[key] === null) { clears.push(field); continue; }
    const days = Math.floor(Number(req.body[key]));
    if (!Number.isFinite(days) || days < 1 || days > 3650) return res.status(400).json({ error: 'Retention must be 1-3650 days or null' });
    updates[field] = days;
  }
  if (updates.name !== undefined && (updates.name.length < 2 || updates.name.length > 80)) return res.status(400).json({ error: 'Workspace name must be 2-80 characters' });
  updates.updated_at = new Date();
  // Field names come from the fixed lists above, never from the request body.
  const assignments = [...Object.keys(updates).map((field) => `${field} = $${field}`), ...clears.map((field) => `${field} = NONE`)];
  const rows = await q(`UPDATE ${wsLiteral(req)} SET ${assignments.join(', ')} RETURN AFTER;`, updates);
  if (!rows[0]) return res.status(404).json({ error: 'Workspace not found' });
  res.json({ workspace: publicWorkspace(rows[0]) });
});

/* ---------- workspaces: list, create, rename, switch, archive ---------- */

const workspaceLanes = ['planing', 'notes', 'agent'];

// Seed a workspace's system lanes. The default workspace keeps the original
// `category:<slug>` ids; every other workspace gets its own records, which the
// composite (workspace, slug) index allows.
async function seedWorkspaceLanes(workspaceId, ownerId) {
  for (const lane of defaultCategories) {
    const existing = await findCategory(lane.slug, workspaceId);
    if (existing) continue;
    const data = {
      name: lane.name,
      slug: lane.slug,
      color: lane.color,
      icon: lane.icon,
      is_system: true,
      is_default: lane.slug === 'notes',
      workspace: new RecordId('workspace', workspaceId),
      created_by: ownerId ? new RecordId('account', recordId(ownerId)) : undefined,
      created_at: new Date(),
      updated_at: new Date(),
    };
    if (workspaceId === 'default') await q(`CREATE ${recordLiteral('category', lane.slug)} SET ${literalAssignments(data).join(', ')};`);
    else await q(`CREATE category SET ${literalAssignments(data).join(', ')};`);
  }
}

app.get('/api/workspaces', auth, async (req, res) => {
  const memberships = req.memberships || [];
  const rows = memberships.length
    ? await q(`SELECT * FROM workspace WHERE id IN [${memberships.map((entry) => recordLiteral('workspace', entry.id)).join(', ')}];`)
    : [];
  const counts = await q('SELECT count() AS count, workspace FROM notes GROUP BY workspace;');
  const countByWorkspace = new Map(counts.map((row) => [recordId(row.workspace), Number(row.count || 0)]));
  const byId = new Map(rows.map((row) => [recordId(row.id), row]));
  // Memberships without a surviving workspace row are skipped rather than
  // rendered as a broken entry in the switcher.
  const workspaces = memberships
    .map((membership) => {
      const row = byId.get(membership.id);
      if (!row) return null;
      return publicWorkspaceSummary(row, {
        role: membership.role,
        isActive: membership.id === req.workspaceId,
        notes: countByWorkspace.get(membership.id) || 0,
      });
    })
    .filter(Boolean);
  res.json({ workspaces, activeId: req.workspaceId });
});

app.post('/api/workspaces', auth, requirePermission('settings:write'), async (req, res) => {
  const name = String(req.body?.name || '').trim().slice(0, 80);
  if (name.length < 2) return res.status(400).json({ error: 'Workspace name must be at least 2 characters' });
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40) || 'workspace';
  const rows = await q(`CREATE workspace SET ${literalAssignments({
    name,
    slug,
    description: String(req.body?.description || '').trim().slice(0, 200),
    default_category: 'notes',
    ai_context: defaultWorkspace.ai_context,
    theme: 'system',
    accent: 'violet',
    font_scale: 'default',
    is_archived: false,
    context_roots: [],
    metadata: {},
    created_by: { tb: 'account', id: req.account.sub },
    created_at: new Date(),
    updated_at: new Date(),
  }).join(', ')} RETURN AFTER;`);
  const workspace = rows[0];
  const workspaceId = recordId(workspace.id);
  // The creator owns what they just made: ownership is what carries the right
  // to invite another owner or archive the workspace.
  await upsertEdge('workspace_member', 'account', req.account.sub, 'workspace', workspaceId, {
    role: 'owner',
    created_by: new RecordId('account', recordId(req.account.sub)),
    created_at: new Date(),
  });
  await seedWorkspaceLanes(workspaceId, req.account.sub);
  // Creating a workspace is also a switch: the member lands where they just
  // created something, instead of staring at the old workspace.
  await q(`UPDATE type::thing("account", $id) SET active_workspace = ${recordLiteral('workspace', workspaceId)};`, { id: req.account.sub });
  await recordAudit('workspace.create', req.account.sub, { name }, workspaceId, workspaceId);
  res.status(201).json(publicWorkspaceSummary(workspace, { role: 'owner', isActive: true, notes: 0 }));
});

app.patch('/api/workspaces/:id', auth, requirePermission('settings:write'), async (req, res) => {
  const membership = (req.memberships || []).find((entry) => entry.id === req.params.id);
  if (!membership) return res.status(403).json({ error: 'You are not a member of that workspace' });
  const updates = {};
  if (req.body?.name !== undefined) {
    const name = String(req.body.name).trim().slice(0, 80);
    if (name.length < 2) return res.status(400).json({ error: 'Workspace name must be at least 2 characters' });
    updates.name = name;
  }
  if (req.body?.description !== undefined) updates.description = String(req.body.description).trim().slice(0, 200);
  if (!Object.keys(updates).length) return res.status(400).json({ error: 'No changes provided' });
  updates.updated_at = new Date();
  const rows = await q(`UPDATE ${recordLiteral('workspace', req.params.id)} MERGE $updates RETURN AFTER;`, { updates });
  if (!rows[0]) return res.status(404).json({ error: 'Workspace not found' });
  await recordAudit('workspace.update', req.account.sub, { name: updates.name || null }, req.params.id, req.params.id);
  res.json(publicWorkspaceSummary(rows[0], { role: membership.role, isActive: req.params.id === req.workspaceId }));
});

app.post('/api/workspaces/:id/active', auth, async (req, res) => {
  const membership = (req.memberships || []).find((entry) => entry.id === req.params.id);
  if (!membership) return res.status(403).json({ error: 'You are not a member of that workspace' });
  const rows = await q(`SELECT * FROM ${recordLiteral('workspace', req.params.id)} LIMIT 1;`);
  if (!rows[0]) return res.status(404).json({ error: 'Workspace not found' });
  if (rows[0].is_archived) return res.status(400).json({ error: 'That workspace is archived' });
  await q(`UPDATE type::thing("account", $id) SET active_workspace = ${recordLiteral('workspace', req.params.id)};`, { id: req.account.sub });
  await recordAudit('workspace.switch', req.account.sub, { to: req.params.id }, req.params.id, req.params.id);
  res.json({ activeId: req.params.id, workspace: publicWorkspaceSummary(rows[0], { role: membership.role, isActive: true }) });
});

app.post('/api/workspaces/:id/archive', auth, requirePermission('workspace:manage'), async (req, res) => {
  const membership = (req.memberships || []).find((entry) => entry.id === req.params.id);
  if (!membership) return res.status(403).json({ error: 'You are not a member of that workspace' });
  const others = (req.memberships || []).filter((entry) => entry.id !== req.params.id);
  if (!others.length) return res.status(400).json({ error: 'The last workspace cannot be archived' });
  await q(`UPDATE ${recordLiteral('workspace', req.params.id)} SET is_archived = true, updated_at = time::now();`);
  // Archiving the workspace you are in moves the session to a surviving one, so
  // the next request never lands in an archived scope.
  if (req.params.id === req.workspaceId) {
    await q(`UPDATE type::thing("account", $id) SET active_workspace = ${recordLiteral('workspace', others[0].id)};`, { id: req.account.sub });
  }
  await recordAudit('workspace.archive', req.account.sub, { workspace: req.params.id }, req.params.id, others[0].id);
  res.json({ archived: req.params.id, activeId: req.params.id === req.workspaceId ? others[0].id : req.workspaceId });
});

// Per-workspace context roots: which configured directories chats here may use.
app.get('/api/workspaces/:id/context-roots', auth, async (req, res) => {
  const membership = (req.memberships || []).find((entry) => entry.id === req.params.id);
  if (!membership) return res.status(403).json({ error: 'You are not a member of that workspace' });
  const row = await findWorkspace(req.params.id);
  if (!row) return res.status(404).json({ error: 'Workspace not found' });
  const enabled = contextRootsForWorkspace(row).map((root) => root.id);
  res.json({ workspaceId: req.params.id, enabled, roots: contextRoots.map((root) => ({ ...publicContextRoot(root), enabled: enabled.includes(root.id) })) });
});

app.patch('/api/workspaces/:id/context-roots', auth, requirePermission('settings:write'), async (req, res) => {
  const membership = (req.memberships || []).find((entry) => entry.id === req.params.id);
  if (!membership) return res.status(403).json({ error: 'You are not a member of that workspace' });
  const requested = Array.isArray(req.body?.roots) ? req.body.roots.map(String) : null;
  if (!requested) return res.status(400).json({ error: 'roots must be an array of root ids' });
  const unknown = requested.filter((id) => !contextRoot(id));
  if (unknown.length) return res.status(400).json({ error: `Unknown context root: ${unknown.join(', ')}` });
  // An empty selection means "all configured roots", never "none": a workspace
  // with no roots at all could not be given files, which is never the intent.
  const roots = [...new Set(requested)];
  const rows = await q(`UPDATE ${recordLiteral('workspace', req.params.id)} SET context_roots = ${inlineValue(roots.length === contextRoots.length ? [] : roots)}, updated_at = time::now() RETURN AFTER;`);
  if (!rows[0]) return res.status(404).json({ error: 'Workspace not found' });
  await recordAudit('workspace.context_roots', req.account.sub, { roots: roots.length }, req.params.id, req.params.id);
  const enabled = contextRootsForWorkspace(rows[0]).map((root) => root.id);
  res.json({ workspaceId: req.params.id, enabled, roots: contextRoots.map((root) => ({ ...publicContextRoot(root), enabled: enabled.includes(root.id) })) });
});

app.get('/api/members', auth, requirePermission('members:write'), async (req, res) => {
  // People are listed per workspace: an account only appears when it holds a
  // membership here, and the role is that membership's role.
  const [rows, edges] = await Promise.all([
    q(`SELECT * FROM account WHERE id IN (SELECT VALUE in FROM workspace_member WHERE out = ${wsLiteral(req)}) ORDER BY name ASC;`),
    q(`SELECT in AS account, role FROM workspace_member WHERE out = ${wsLiteral(req)};`),
  ]);
  const roleByAccount = new Map(edges.map((row) => [recordId(row.account), row.role]));
  const owners = [...roleByAccount.values()].filter(isOwnerRole).length;
  res.json(rows.map((row) => publicMember(row, {
    role: roleByAccount.get(recordId(row.id)) || row.role,
    callerRole: req.workspaceRole,
    isSelf: recordId(row.id) === recordId(req.account.sub),
    owners,
  })));
});

// Adds a brand-new account to the workspace you are in. Existing accounts are
// deliberately not renamed or re-passworded here: they join with an invitation
// code from the same tab, which is the consent record for the membership.
app.post('/api/members', auth, requirePermission('members:write'), async (req, res) => {
  const name = String(req.body.name || '').trim();
  const password = String(req.body.password || '');
  const role = String(req.body.role || 'viewer');
  if (name.length < 3 || password.length < 8 || !roles.includes(role)) return res.status(400).json({ error: 'Provide a valid name, password, and role' });
  if (!canGrantRole(req.workspaceRole, role)) return res.status(403).json({ error: 'Your role cannot grant that role' });
  if (await findAccount(name)) return res.status(409).json({ error: 'That username is taken — invite the existing account with a code instead' });
  const account = await ensureAccount(name, password, role, req.workspaceId);
  const accountId = recordId(account.id);
  await addWorkspaceMember(accountId, req.workspaceId, role, req.account.sub);
  await recordAudit('member.add', req.account.sub, { role }, accountId, req.workspaceId);
  res.status(201).json({ member: publicMember(account, { role, callerRole: req.workspaceRole }) });
});

app.patch('/api/members/:id', auth, requirePermission('members:write'), async (req, res) => {
  const role = String(req.body.role || '');
  if (!roles.includes(role) || role === 'superadmin') return res.status(400).json({ error: 'Unknown role' });
  if (!canGrantRole(req.workspaceRole, role)) return res.status(403).json({ error: 'Your role cannot grant that role' });
  const targetId = recordId(req.params.id);
  if (targetId === recordId(req.account.sub)) return res.status(400).json({ error: 'You cannot change your own role' });
  const target = (await q('SELECT * FROM type::thing("account", $id) LIMIT 1;', { id: targetId }))[0];
  if (!target) return res.status(404).json({ error: 'Member not found' });
  const current = await membershipEdge(targetId, req.workspaceId);
  if (!current) return res.status(404).json({ error: 'That account is not a member of this workspace' });
  // The role lives on the membership edge, so demoting someone in one workspace
  // never changes what they are in another.
  if (isOwnerRole(current.role) && !isOwnerRole(role) && (await countWorkspaceOwners(req.workspaceId)) <= 1) {
    return res.status(400).json({ error: 'A workspace must keep at least one owner' });
  }
  await setWorkspaceMemberRole(targetId, req.workspaceId, role);
  await recordAudit('member.role', req.account.sub, { role, from: current.role }, targetId, req.workspaceId);
  res.json({ member: publicMember(target, { role, callerRole: req.workspaceRole }) });
});

app.delete('/api/members/:id', auth, requirePermission('members:write'), async (req, res) => {
  const targetId = recordId(req.params.id);
  if (targetId === recordId(req.account.sub)) return res.status(400).json({ error: 'You cannot remove yourself' });
  const target = (await q('SELECT * FROM type::thing("account", $id) LIMIT 1;', { id: targetId }))[0];
  if (!target) return res.status(404).json({ error: 'Member not found' });
  const current = await membershipEdge(targetId, req.workspaceId);
  if (!current) return res.status(404).json({ error: 'That account is not a member of this workspace' });
  if ((roleRank[req.workspaceRole] || 0) < (roleRank[current.role] || 0)) return res.status(403).json({ error: 'Your role cannot remove that member' });
  if (isOwnerRole(current.role) && (await countWorkspaceOwners(req.workspaceId)) <= 1) {
    return res.status(400).json({ error: 'A workspace must keep at least one owner' });
  }
  // Removing someone takes them out of this workspace only; the account itself
  // is deleted when it no longer belongs anywhere.
  await q('DELETE workspace_member WHERE in = type::thing("account", $id) AND out = $ws;', { id: targetId, ws: new RecordId('workspace', req.workspaceId) });
  const remaining = await q('SELECT id FROM workspace_member WHERE in = type::thing("account", $id) LIMIT 1;', { id: targetId });
  if (!remaining.length) await q('DELETE type::thing("account", $id);', { id: targetId });
  await recordAudit('member.remove', req.account.sub, { role: current.role }, targetId, req.workspaceId);
  res.status(204).end();
});

/* ---------- support tickets: custom-field defs, tickets, replies ---------- */

const ticketStatuses = ['new', 'open', 'pending', 'resolved', 'closed'];
const ticketPriorities = ['low', 'medium', 'high', 'urgent'];
const ticketFieldTypes = ['text', 'textarea', 'number', 'date', 'select', 'checkbox'];

// A field definition. `options` only applies to select fields; `required` is
// enforced on ticket create/update; `sort_order` keeps the form stable.
function publicTicketField(row) {
  return {
    id: recordId(row.id),
    label: row.label,
    type: ticketFieldTypes.includes(row.type) ? row.type : 'text',
    options: Array.isArray(row.options) ? row.options : [],
    required: Boolean(row.required),
    sortOrder: Number(row.sort_order) || 0,
  };
}

function publicTicket(row, { names, fields }) {
  // Unknown field ids are dropped, values pass through as strings — custom
  // fields are display/metadata data, never query interpolations.
  const byId = new Map((fields || []).map((field) => [field.id, field]));
  const custom = {};
  for (const [key, value] of Object.entries(row.custom_fields || {})) {
    if (byId.has(key)) custom[key] = String(value ?? '');
  }
  return {
    id: recordId(row.id),
    subject: row.subject,
    description: row.description,
    status: ticketStatuses.includes(row.status) ? row.status : 'new',
    priority: ticketPriorities.includes(row.priority) ? row.priority : 'medium',
    requester: row.requester ? (names?.get(recordId(row.requester)) || recordId(row.requester)) : null,
    assignee: row.assignee ? (names?.get(recordId(row.assignee)) || recordId(row.assignee)) : null,
    customFields: custom,
    replyCount: Number(row.reply_count) || 0,
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
    updatedAt: row.updated_at instanceof Date ? row.updated_at.toISOString() : row.updated_at,
  };
}

function publicTicketReply(row, names) {
  return {
    id: recordId(row.id),
    ticket: recordId(row.ticket),
    author: row.author ? (names?.get(recordId(row.author)) || recordId(row.author)) : null,
    body: row.body,
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
  };
}

async function ticketNames(rows) {
  const ids = [...new Set(rows.flatMap((row) => [row.requester, row.assignee].filter(Boolean).map(recordId)))];
  return await accountNames(ids);
}

app.get('/api/tickets/fields', auth, async (req, res) => {
  const rows = await q(`SELECT * FROM ticket_field WHERE workspace = ${wsLiteral(req)} ORDER BY sort_order ASC, label ASC;`);
  res.json(rows.map(publicTicketField));
});

app.post('/api/tickets/fields', auth, requirePermission('settings:write'), async (req, res) => {
  const label = String(req.body.label || '').trim().slice(0, 60);
  const type = String(req.body.type || 'text');
  if (!label) return res.status(400).json({ error: 'Field label is required' });
  if (!ticketFieldTypes.includes(type)) return res.status(400).json({ error: 'Unknown field type' });
  let options = [];
  if (type === 'select') {
    options = [...new Set((Array.isArray(req.body.options) ? req.body.options : String(req.body.options || '').split(','))
      .map((option) => String(option).trim()).filter(Boolean).map((option) => option.slice(0, 40)))];
    if (options.length < 1) return res.status(400).json({ error: 'Select fields need at least one option' });
  }
  const existing = await q('SELECT * FROM ticket_field WHERE workspace = $ws AND label = $label LIMIT 1;', { ws: new RecordId('workspace', req.workspaceId), label });
  if (existing[0]) return res.status(409).json({ error: 'A field with that label already exists' });
  const rows = await createRecord('ticket_field', {
    label,
    type,
    options,
    required: Boolean(req.body.required),
    sort_order: Number(req.body.sortOrder) || 0,
    workspace: new RecordId('workspace', req.workspaceId),
    created_at: new Date(),
  });
  res.status(201).json(publicTicketField(rows[0]));
});

app.patch('/api/tickets/fields/:id', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ticket_field", $id) WHERE workspace = $ws LIMIT 1;', { id: req.params.id, ws: new RecordId('workspace', req.workspaceId) });
  if (!rows[0]) return res.status(404).json({ error: 'Field not found' });
  const field = rows[0];
  const updates = {};
  if (req.body.label !== undefined) {
    const label = String(req.body.label).trim().slice(0, 60);
    if (!label) return res.status(400).json({ error: 'Field label is required' });
    updates.label = label;
  }
  if (req.body.type !== undefined) {
    if (!ticketFieldTypes.includes(req.body.type)) return res.status(400).json({ error: 'Unknown field type' });
    updates.type = req.body.type;
  }
  if (req.body.options !== undefined && (updates.type || field.type) === 'select') {
    const options = [...new Set((Array.isArray(req.body.options) ? req.body.options : String(req.body.options).split(','))
      .map((option) => String(option).trim()).filter(Boolean).map((option) => option.slice(0, 40)))];
    if (!options.length) return res.status(400).json({ error: 'Select fields need at least one option' });
    updates.options = options;
  }
  if (req.body.required !== undefined) updates.required = Boolean(req.body.required);
  if (req.body.sortOrder !== undefined) updates.sort_order = Number(req.body.sortOrder) || 0;
  if (Object.keys(updates).length) {
    await q('UPDATE type::thing("ticket_field", $id) SET ' + literalAssignments(updates).join(', ') + ';', { id: req.params.id });
  }
  const fresh = await q('SELECT * FROM type::thing("ticket_field", $id) LIMIT 1;', { id: req.params.id });
  res.json(publicTicketField(fresh[0]));
});

app.delete('/api/tickets/fields/:id', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ticket_field", $id) WHERE workspace = $ws LIMIT 1;', { id: req.params.id, ws: new RecordId('workspace', req.workspaceId) });
  if (!rows[0]) return res.status(404).json({ error: 'Field not found' });
  await q('DELETE type::thing("ticket_field", $id);', { id: req.params.id });
  res.status(204).end();
});

app.get('/api/tickets', auth, async (req, res) => {
  const filters = [`workspace = ${wsLiteral(req)}`];
  if (req.query.status && ticketStatuses.includes(String(req.query.status))) filters.push(`status = ${JSON.stringify(String(req.query.status))}`);
  if (req.query.priority && ticketPriorities.includes(String(req.query.priority))) filters.push(`priority = ${JSON.stringify(String(req.query.priority))}`);
  if (req.query.q) {
    const needle = String(req.query.q).slice(0, 100);
    filters.push(`(subject ~ ${JSON.stringify(needle)} OR description ~ ${JSON.stringify(needle)})`);
  }
  const rows = await q(`SELECT * FROM ticket WHERE ${filters.join(' AND ')} ORDER BY created_at DESC LIMIT 200;`);
  const names = await ticketNames(rows);
  const fieldRows = await q(`SELECT id FROM ticket_field WHERE workspace = ${wsLiteral(req)};`);
  const fields = fieldRows.map(publicTicketField);
  res.json(rows.map((row) => publicTicket(row, { names, fields })));
});

app.get('/api/tickets/:id', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ticket", $id) WHERE workspace = $ws LIMIT 1;', { id: req.params.id, ws: new RecordId('workspace', req.workspaceId) });
  if (!rows[0]) return res.status(404).json({ error: 'Ticket not found' });
  const [replies, fieldRows, names] = await Promise.all([
    q(`SELECT * FROM ticket_reply WHERE ticket = ${recordLiteral('ticket', req.params.id)} ORDER BY created_at ASC;`),
    q(`SELECT * FROM ticket_field WHERE workspace = ${wsLiteral(req)} ORDER BY sort_order ASC, label ASC;`),
    accountNames([rows[0].requester, rows[0].assignee].filter(Boolean).map(recordId)),
  ]);
  const replyNames = await ticketNames(replies.map((row) => ({ ...row, requester: row.author })));
  res.json({
    ...publicTicket(rows[0], { names, fields: fieldRows.map(publicTicketField) }),
    replies: replies.map((row) => publicTicketReply(row, replyNames)),
    fieldDefs: fieldRows.map(publicTicketField),
  });
});

function validateTicketInput(body, fieldDefs) {
  const subject = String(body.subject || '').trim().slice(0, 160);
  if (!subject) return { error: 'Subject is required' };
  const errors = {};
  const custom = {};
  const byId = new Map(fieldDefs.map((field) => [field.id, field]));
  const raw = body.customFields && typeof body.customFields === 'object' && !Array.isArray(body.customFields) ? body.customFields : {};
  for (const field of fieldDefs) {
    const value = raw[field.id];
    if (value === undefined || value === null || String(value).trim() === '') {
      if (field.required) errors[field.id] = 'required';
      continue;
    }
    const text = String(value).trim();
    if (field.type === 'number' && Number.isNaN(Number(text))) { errors[field.id] = 'number'; continue; }
    if (field.type === 'date' && Number.isNaN(new Date(text).getTime())) { errors[field.id] = 'date'; continue; }
    if (field.type === 'checkbox') { custom[field.id] = ['true', '1', 'yes'].includes(text.toLowerCase()) ? 'true' : 'false'; continue; }
    if (field.type === 'select' && !field.options.includes(text)) { errors[field.id] = 'option'; continue; }
    custom[field.id] = text.slice(0, 500);
  }
  if (Object.keys(errors).length) return { error: 'Validation failed', fields: errors };
  return { subject, custom };
}

async function loadFieldDefs(workspaceId) {
  const rows = await q(`SELECT * FROM ticket_field WHERE workspace = ${recordLiteral('workspace', workspaceId)} ORDER BY sort_order ASC, label ASC;`);
  return rows.map(publicTicketField);
}

app.post('/api/tickets', auth, async (req, res) => {
  const fieldDefs = await loadFieldDefs(req.workspaceId);
  const parsed = validateTicketInput(req.body, fieldDefs);
  if (parsed.error) return res.status(400).json({ error: parsed.error, fields: parsed.fields });
  const priority = ticketPriorities.includes(String(req.body.priority)) ? String(req.body.priority) : 'medium';
  let assignee = null;
  if (req.body.assignee) {
    const targetId = recordId(String(req.body.assignee));
    const edge = await q('SELECT role FROM workspace_member WHERE in = type::thing("account", $id) AND out = $ws LIMIT 1;', { id: targetId, ws: new RecordId('workspace', req.workspaceId) });
    if (!edge[0]) return res.status(400).json({ error: 'Assignee must be a member of this workspace' });
    assignee = targetId;
  }
  const rows = await createRecord('ticket', {
    subject: parsed.subject,
    description: String(req.body.description || '').trim().slice(0, 5000),
    status: 'new',
    priority,
    requester: new RecordId('account', recordId(req.account.sub)),
    assignee,
    custom_fields: parsed.custom,
    reply_count: 0,
    workspace: new RecordId('workspace', req.workspaceId),
    created_at: new Date(),
    updated_at: new Date(),
  });
  const names = await ticketNames(rows);
  res.status(201).json(publicTicket(rows[0], { names, fields: fieldDefs }));
});

app.patch('/api/tickets/:id', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ticket", $id) WHERE workspace = $ws LIMIT 1;', { id: req.params.id, ws: new RecordId('workspace', req.workspaceId) });
  if (!rows[0]) return res.status(404).json({ error: 'Ticket not found' });
  const updates = { updated_at: new Date() };
  if (req.body.status !== undefined) {
    if (!ticketStatuses.includes(req.body.status)) return res.status(400).json({ error: 'Unknown status' });
    updates.status = req.body.status;
  }
  if (req.body.priority !== undefined) {
    if (!ticketPriorities.includes(req.body.priority)) return res.status(400).json({ error: 'Unknown priority' });
    updates.priority = req.body.priority;
  }
  if (req.body.subject !== undefined) {
    const subject = String(req.body.subject).trim().slice(0, 160);
    if (!subject) return res.status(400).json({ error: 'Subject is required' });
    updates.subject = subject;
  }
  if (req.body.description !== undefined) updates.description = String(req.body.description).trim().slice(0, 5000);
  if (req.body.assignee !== undefined) {
    let assignee = null;
    if (req.body.assignee) {
      const targetId = recordId(String(req.body.assignee));
      const edge = await q('SELECT role FROM workspace_member WHERE in = type::thing("account", $id) AND out = $ws LIMIT 1;', { id: targetId, ws: new RecordId('workspace', req.workspaceId) });
      if (!edge[0]) return res.status(400).json({ error: 'Assignee must be a member of this workspace' });
      assignee = targetId;
    }
    updates.assignee = assignee;
  }
  if (req.body.customFields !== undefined) {
    const fieldDefs = await loadFieldDefs(req.workspaceId);
    const parsed = validateTicketInput({ subject: updates.subject || rows[0].subject, customFields: req.body.customFields }, fieldDefs);
    if (parsed.error) return res.status(400).json({ error: parsed.error, fields: parsed.fields });
    updates.custom_fields = parsed.custom;
  }
  await q('UPDATE type::thing("ticket", $id) SET ' + literalAssignments(updates).join(', ') + ';', { id: req.params.id });
  const fresh = await q('SELECT * FROM type::thing("ticket", $id) LIMIT 1;', { id: req.params.id });
  const names = await ticketNames([fresh[0]]);
  res.json(publicTicket(fresh[0], { names, fields: await loadFieldDefs(req.workspaceId) }));
});

app.delete('/api/tickets/:id', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ticket", $id) WHERE workspace = $ws LIMIT 1;', { id: req.params.id, ws: new RecordId('workspace', req.workspaceId) });
  if (!rows[0]) return res.status(404).json({ error: 'Ticket not found' });
  await q('DELETE type::thing("ticket", $id);', { id: req.params.id });
  res.status(204).end();
});

app.post('/api/tickets/:id/replies', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ticket", $id) WHERE workspace = $ws LIMIT 1;', { id: req.params.id, ws: new RecordId('workspace', req.workspaceId) });
  if (!rows[0]) return res.status(404).json({ error: 'Ticket not found' });
  const body = String(req.body.body || '').trim().slice(0, 5000);
  if (!body) return res.status(400).json({ error: 'Reply body is required' });
  const replies = await createRecord('ticket_reply', {
    ticket: new RecordId('ticket', recordId(rows[0].id)),
    author: new RecordId('account', recordId(req.account.sub)),
    body,
    workspace: new RecordId('workspace', req.workspaceId),
    created_at: new Date(),
  });
  // The count subquery yields an array; SELECT VALUE flattens it to a scalar so
  // the option<number> field accepts it (bound [1] would be rejected).
  await q('UPDATE type::thing("ticket", $id) SET reply_count = (SELECT VALUE count FROM (SELECT count() AS count FROM ticket_reply WHERE ticket = type::thing("ticket", $id) GROUP ALL))[0] ?? 0, updated_at = time::now();', { id: req.params.id });
  const replyNames = await ticketNames(replies.map((row) => ({ ...row, requester: row.author })));
  res.status(201).json(publicTicketReply(replies[0], replyNames));
});

app.get('/api/categories', auth, async (req, res) => {
  const rows = await q(`SELECT * FROM category WHERE workspace = ${wsLiteral(req)} ORDER BY is_system DESC, name ASC;`);
  res.json(rows.map(publicCategory));
});

app.post('/api/categories', auth, requirePermission('categories:write'), async (req, res) => {
  const name = String(req.body.name || '').trim();
  if (!name || name.length > 40) return res.status(400).json({ error: 'Category name must be 1-40 characters' });
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  if (!slug) return res.status(400).json({ error: 'Category name must contain letters or numbers' });
  if (await findCategory(slug, req.workspaceId)) return res.status(409).json({ error: 'Category already exists' });
  // The default workspace keeps the readable `category:<slug>` ids; every other
  // workspace gets a generated id so two workspaces never share a record.
  const data = {
    name,
    slug,
    color: req.body.color || '#64748b',
    icon: req.body.icon || name.slice(0, 1).toUpperCase(),
    is_system: false,
    is_default: false,
    workspace: { tb: 'workspace', id: req.workspaceId },
    created_by: { tb: 'account', id: req.account.sub },
    created_at: new Date(),
    updated_at: new Date(),
  };
  try {
    const rows = req.workspaceId === 'default'
      ? await q(`CREATE ${recordLiteral('category', slug)} SET ${literalAssignments(data).join(', ')} RETURN AFTER;`)
      : await q(`CREATE category SET ${literalAssignments(data).join(', ')} RETURN AFTER;`);
    await recordAudit('category.create', req.account.sub, { name }, null, req.workspaceId);
    res.status(201).json(publicCategory(rows[0]));
  } catch {
    res.status(409).json({ error: 'Category already exists' });
  }
});

app.patch('/api/categories/:slug', auth, requirePermission('categories:write'), async (req, res) => {
  const slug = req.params.slug;
  const category = await findCategory(slug, req.workspaceId);
  if (!category) return res.status(404).json({ error: 'Category not found' });
  const updates = {};
  if (req.body.color !== undefined) {
    const color = String(req.body.color).trim();
    if (!/^#[0-9a-f]{6}$/i.test(color)) return res.status(400).json({ error: 'Color must be a #rrggbb hex value' });
    updates.color = color;
  }
  if (req.body.icon !== undefined) {
    const icon = String(req.body.icon).trim();
    if (!icon || icon.length > 2) return res.status(400).json({ error: 'Icon must be 1-2 characters' });
    updates.icon = icon;
  }
  if (req.body.name !== undefined) {
    if (category.is_system) return res.status(400).json({ error: 'System categories cannot be renamed' });
    const name = String(req.body.name).trim();
    if (!name || name.length > 40) return res.status(400).json({ error: 'Category name must be 1-40 characters' });
    updates.name = name;
  }
  if (!Object.keys(updates).length) return res.status(400).json({ error: 'No changes provided' });
  const rows = await q(`UPDATE ${recordLiteral('category', recordId(category.id))} MERGE $updates RETURN AFTER;`, { updates });
  res.json(publicCategory(rows[0]));
});

app.delete('/api/categories/:slug', auth, requirePermission('categories:write'), async (req, res) => {
  const slug = req.params.slug;
  if (defaultCategories.some((category) => category.slug === slug)) return res.status(400).json({ error: 'System categories cannot be deleted' });
  const category = await findCategory(slug, req.workspaceId);
  if (!category) return res.status(404).json({ error: 'Category not found' });
  const workspace = await findWorkspace(req.workspaceId);
  const fallbackSlug = workspace?.default_category || 'notes';
  const fallback = fallbackSlug === slug ? (defaultCategories.find((item) => item.slug !== slug) || {}).slug : fallbackSlug;
  const fallbackLane = await findCategory(fallback, req.workspaceId) || await requireCategory('notes', req.workspaceId);
  const categoryRef = recordLiteral('category', recordId(category.id));
  // Reassign notes and remove the lane inside one transaction so no failure
  // can leave notes pointing at a deleted lane (Phase 4 hardening).
  await transaction([
    `UPDATE notes SET category = ${recordLiteral('category', recordId(fallbackLane.id))} WHERE category = ${categoryRef};`,
    `DELETE ${categoryRef};`,
  ]);
  await recordAudit('category.delete', req.account.sub, { slug }, null, req.workspaceId);
  res.status(204).end();
});

app.get('/api/tags', auth, async (req, res) => {
  // Counts are workspace-local: a tag used only elsewhere shows up with 0 here
  // rather than advertising another workspace's note count.
  const rows = await q(`SELECT *, (SELECT count() FROM notes WHERE $parent.id IN tags AND workspace = ${wsLiteral(req)} GROUP ALL) AS count FROM tag ORDER BY name ASC;`);
  res.json(rows.map((row) => ({ ...publicTag(row), count: Number(row.count?.[0]?.count || row.count?.count || row.count || 0) })));
});

async function loadNoteList({ account, category, view, tag, search, workspaceId = 'default' }) {
  // Phase 2 scoping: notes are bounded by workspace membership, not by
  // ownership, so every member of a workspace shares one stream.
  const filters = [`workspace = ${recordLiteral('workspace', workspaceId)}`];
  if (view === 'archive') filters.push('is_archived = true', 'is_recycle = false');
  else if (view === 'recycle') filters.push('is_recycle = true');
  else filters.push('is_recycle = false', 'is_archived = false');
  // Lanes are per workspace, so a lane filter resolves to that workspace's
  // record rather than to a global slug id.
  if (category) {
    const lane = await findCategory(category, workspaceId);
    filters.push(`category = ${lane ? recordLiteral('category', recordId(lane.id)) : recordLiteral('category', '__missing__')}`);
  }
  if (tag) filters.push('type::thing("tag", $tag) IN tags');
  if (search) filters.push('content @@ $search');
  const rows = await tq('notes.list', `SELECT *, category.* AS category_record FROM notes WHERE ${filters.join(' AND ')};`, {
    account, tag: tag || null, search: search || null,
  }, workspaceId);
  rows.sort((a, b) => (Number(Boolean(b.is_top)) - Number(Boolean(a.is_top))) || new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  const ids = rows.map((row) => new RecordId('notes', recordId(row.id)));
  const attachmentRows = ids.length ? await tq('attachments.byNotes', 'SELECT * FROM attachments WHERE note IN $ids ORDER BY created_at ASC;', { ids }, workspaceId) : [];
  const byNote = new Map();
  for (const attachment of attachmentRows) {
    const noteId = recordId(attachment.note);
    if (!byNote.has(noteId)) byNote.set(noteId, []);
    byNote.get(noteId).push(publicAttachment(attachment));
  }
  return rows.map((row) => publicNote(row, byNote.get(recordId(row.id)) || []));
}

app.get('/api/notes', auth, async (req, res) => {
  const notes = await loadNoteList({
    account: req.account.sub,
    category: req.query.category ? String(req.query.category) : null,
    view: ['archive', 'recycle'].includes(String(req.query.view)) ? String(req.query.view) : null,
    tag: req.query.tag ? String(req.query.tag) : null,
    search: req.query.q ? String(req.query.q) : null,
    workspaceId: req.workspaceId,
  });
  res.json(notes);
});

const countWords = (content) => String(content || '').trim().split(/\s+/).filter(Boolean).length;

// Maintain the explicit wiki-link edges for a note. Unresolved targets have no
// OUT record to point at, so they are not stored as edges — the graph endpoint
// still surfaces them by parsing content, which keeps the edge table clean.
async function syncNoteLinks(noteId, content, accountSub, workspaceId = 'default') {
  const targets = wikiLinkTargets(content);
  await q('DELETE note_link WHERE in = type::thing("notes", $id);', { id: noteId });
  let resolvedCount = 0;
  for (const target of targets.slice(0, 200)) {
    const match = await findNoteByTitle(target, workspaceId);
    const targetId = match ? recordId(match.id) : null;
    if (!targetId || targetId === noteId) continue;
    try {
      // One edge row per (source, target, label) so the UNIQUE index holds.
      await upsertEdge('note_link', 'notes', noteId, 'notes', targetId, {
        label: target.slice(0, 200), resolved: true, workspace: new RecordId('workspace', workspaceId),
        created_by: new RecordId('account', recordId(accountSub)), created_at: new Date(),
      }, target.slice(0, 60));
      resolvedCount += 1;
    } catch { /* UNIQUE edge already present */ }
  }
  return { linkCount: targets.length, resolvedCount };
}

app.post('/api/notes', auth, requirePermission('notes:write'), async (req, res) => {
  const content = String(req.body.content || '').trim();
  const category = String(req.body.category || 'notes');
  if (!content) return res.status(400).json({ error: 'Note content is required' });
  try {
    const lane = await requireCategory(category, req.workspaceId);
    const tagIds = await ensureTags(Array.isArray(req.body.tags) ? req.body.tags : [], req.workspaceId);
    const status = ['backlog', 'todo', 'doing', 'review', 'done'].includes(String(req.body.status)) ? String(req.body.status) : 'todo';
    const priority = ['low', 'medium', 'high', 'urgent'].includes(String(req.body.priority)) ? String(req.body.priority) : 'medium';
    // option<datetime> fields only accept a datetime or NONE, so absent dates
    // are omitted entirely (literalAssignments drops undefined) rather than
    // bound as null, which the schema would reject.
    const validDate = (value) => {
      const parsed = value ? new Date(value) : null;
      return parsed && !Number.isNaN(parsed.getTime()) ? parsed : undefined;
    };
    const data = {
      content,
      category: { tb: 'category', id: recordId(lane.id) },
      account: { tb: 'account', id: recordId(req.account.sub) },
      created_by: { tb: 'account', id: recordId(req.account.sub) },
      workspace: { tb: 'workspace', id: req.workspaceId },
      tags: tagIds,
      is_archived: false,
      is_recycle: false,
      is_top: false,
      is_share: false,
      status,
      priority,
      position: Number(req.body.position) || 0,
      flags: {},
      metadata: {},
      word_count: countWords(content),
      created_at: new Date(),
      updated_at: new Date(),
    };
    const dueDate = validDate(req.body.dueDate); if (dueDate) data.due_date = dueDate;
    const startDate = validDate(req.body.startDate); if (startDate) data.start_date = startDate;
    const endDate = validDate(req.body.endDate); if (endDate) data.end_date = endDate;
    if (typeof req.body.eventColor === 'string' && req.body.eventColor.trim()) data.event_color = req.body.eventColor.trim().slice(0, 32);
    data.position = Number(req.body.position) || 0;
    const rows = await q(`CREATE notes SET ${literalAssignments(data).join(', ')} RETURN *, category.* AS category_record;`);
    const links = await syncNoteLinks(recordId(rows[0].id), content, req.account.sub, req.workspaceId);
    if (links.linkCount) await q('UPDATE type::thing("notes", $id) MERGE { link_count: $links };', { id: recordId(rows[0].id), links: links.linkCount });
    await recordNoteActivity(recordId(rows[0].id), req.workspaceId, 'note.created', req.account.sub, { category, tags: tagIds.length, links: links.linkCount });
    await recordAudit('note.create', req.account.sub, { category, links: links.resolvedCount }, recordId(rows[0].id), req.workspaceId);
    res.status(201).json(publicNote({ ...rows[0], link_count: links.linkCount }));
  } catch (error) {
    res.status(error.statusCode || 500).json({ error: error.statusCode ? error.message : 'Unable to save note' });
  }
});

app.patch('/api/notes/:id', auth, requirePermission('notes:write'), async (req, res) => {
  const updates = {};
  let contentChanged = false;
  if (req.body.content !== undefined) {
    const content = String(req.body.content).trim();
    if (!content) return res.status(400).json({ error: 'Note content is required' });
    updates.content = content;
    updates.word_count = countWords(content);
    contentChanged = true;
  }
  if (req.body.category !== undefined) {
    const nextCategory = String(req.body.category);
    const lane = await requireCategory(nextCategory, req.workspaceId);
    updates.category = new RecordId('category', recordId(lane.id));
  }
  for (const [key, field] of [['isTop', 'is_top'], ['isArchived', 'is_archived'], ['isRecycle', 'is_recycle'], ['isShare', 'is_share']]) {
    if (req.body[key] !== undefined) updates[field] = Boolean(req.body[key]);
  }
  if (req.body.tags !== undefined) {
    if (!Array.isArray(req.body.tags)) return res.status(400).json({ error: 'Tags must be an array' });
    updates.tags = await ensureTags(req.body.tags, req.workspaceId);
  }
  if (req.body.metadata !== undefined) {
    if (req.body.metadata === null || typeof req.body.metadata !== 'object' || Array.isArray(req.body.metadata)) return res.status(400).json({ error: 'Metadata must be an object' });
    updates.metadata = req.body.metadata;
  }
  // Planning fields: kanban status/priority/position and calendar dates.
  const planningStatuses = ['backlog', 'todo', 'doing', 'review', 'done'];
  if (req.body.status !== undefined) {
    const status = String(req.body.status);
    if (!planningStatuses.includes(status)) return res.status(400).json({ error: `Status must be one of: ${planningStatuses.join(', ')}` });
    updates.status = status;
  }
  if (req.body.priority !== undefined) {
    const priority = String(req.body.priority);
    if (!['low', 'medium', 'high', 'urgent'].includes(priority)) return res.status(400).json({ error: 'Priority must be low, medium, high, or urgent' });
    updates.priority = priority;
  }
  if (req.body.position !== undefined) updates.position = Number(req.body.position) || 0;
  // Clearable planning fields. `literalAssignments` drops null/undefined values
  // (correct for CREATE paths, where defaults must apply), so a null here cannot
  // ride in `updates` — SURREALDB must be told NONE explicitly. Without this a
  // note could never lose a due date once set. Field names are fixed constants.
  const clears = [];
  if (req.body.eventColor === null) clears.push('event_color');
  else if (req.body.eventColor !== undefined) updates.event_color = String(req.body.eventColor).slice(0, 32);
  for (const [key, field] of [['dueDate', 'due_date'], ['startDate', 'start_date'], ['endDate', 'end_date']]) {
    if (req.body[key] === undefined) continue;
    if (req.body[key] === null) { clears.push(field); continue; }
    const date = new Date(req.body[key]);
    if (Number.isNaN(date.getTime())) return res.status(400).json({ error: `${key} must be a valid date` });
    updates[field] = date;
  }
  if (!Object.keys(updates).length && !clears.length) return res.status(400).json({ error: 'No changes provided' });
  updates.updated_at = new Date();
  updates.updated_by = new RecordId('account', recordId(req.account.sub));
  if (contentChanged) updates.link_count = wikiLinkTargets(updates.content).length;
  // Literal assignments keep nested objects (metadata) intact, which bound
  // parameters drop.
  const assignments = [...literalAssignments(updates), ...clears.map((field) => `${field} = NONE`)];
  const rows = await q(`UPDATE type::thing('notes', $id) SET ${assignments.join(', ')}
    WHERE workspace = ${wsLiteral(req)}
    RETURN *, category.* AS category_record;`, { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Note not found' });
  if (contentChanged) await syncNoteLinks(req.params.id, updates.content, req.account.sub, req.workspaceId);
  await recordNoteActivity(req.params.id, req.workspaceId, 'note.updated', req.account.sub, {
    content: contentChanged,
    category: req.body.category !== undefined ? String(req.body.category) : undefined,
    tags: req.body.tags !== undefined ? (Array.isArray(req.body.tags) ? req.body.tags.length : undefined) : undefined,
  });
  const attachmentRows = await q('SELECT * FROM attachments WHERE note = type::thing("notes", $id) ORDER BY created_at ASC;', { id: req.params.id });
  res.json(publicNote(rows[0], attachmentRows));
});

app.delete('/api/notes/:id', auth, requirePermission('notes:write'), async (req, res) => {
  const rows = await q(`DELETE type::thing('notes', $id) WHERE workspace = ${wsLiteral(req)} RETURN BEFORE;`, {
    id: req.params.id,
  });
  if (!rows[0]) return res.status(404).json({ error: 'Note not found' });
  const attachmentRows = await q('SELECT * FROM attachments WHERE note = type::thing("notes", $id);', { id: req.params.id });
  for (const attachment of attachmentRows) {
    const filePath = path.join(uploadDir, path.basename(attachment.path));
    fs.rm(filePath, { force: true }, () => {});
  }
  // Phase 4 hardening: dependent rows and the note itself are removed in one
  // transaction, so a partial delete can never leave orphaned links/comments.
  await transaction([
    'DELETE attachments WHERE note = type::thing("notes", $id);',
    'DELETE note_comment WHERE note = type::thing("notes", $id);',
    'DELETE note_link WHERE in = type::thing("notes", $id) OR out = type::thing("notes", $id);',
    `DELETE type::thing('notes', $id);`,
  ], { id: req.params.id });
  await recordNoteActivity(req.params.id, req.workspaceId, 'note.deleted', req.account.sub, {});
  await recordAudit('note.delete', req.account.sub, {}, req.params.id, req.workspaceId);
  res.status(204).end();
});

app.get('/api/attachments', auth, async (req, res) => {
  const noteId = req.query.note ? String(req.query.note) : null;
  const rows = noteId
    ? await q('SELECT * FROM attachments WHERE note = type::thing("notes", $note) ORDER BY created_at ASC;', { note: noteId })
    : await q('SELECT * FROM attachments ORDER BY created_at DESC LIMIT 200;');
  res.json(rows.map(publicAttachment));
});

// type: () => true — an upload may legitimately arrive without a content-type
// header (fetch with a typeless Blob), and body-parser's type-is check would
// otherwise skip the body and reject a real file as empty.
app.post('/api/attachments', auth, requirePermission('notes:write'), express.raw({ type: () => true, limit: maxUploadBytes }), async (req, res) => {
  const name = String(req.headers['x-file-name'] || '').trim().slice(0, 200);
  const type = String(req.headers['x-file-type'] || 'application/octet-stream').slice(0, 120);
  const roomHeader = req.headers['x-room-id'] ? String(req.headers['x-room-id']) : null;
  if (!name) return res.status(400).json({ error: 'x-file-name header is required' });
  if (!req.body?.length) return res.status(400).json({ error: 'File body is required' });
  // Room attachments are limited to room members.
  if (roomHeader && !(await roomMembership(roomHeader, req.account.sub))) return res.status(403).json({ error: 'You are not a member of this room' });
  const id = crypto.randomBytes(8).toString('hex');
  const stored = `${id}-${name.replace(/[^a-zA-Z0-9._-]+/g, '_')}`;
  fs.writeFileSync(path.join(uploadDir, stored), req.body);
  // Extract text at upload time so markdown/PDF material can be turned into a
  // note later without the user re-uploading or retyping it.
  const extracted = extractAttachmentText(req.body, name, type);
  // option<record> fields reject explicit nulls in schemafull mode, so links
  // and extracted text are only included when they actually have a value —
  // that is what lets a file be uploaded standalone and imported later.
  const attachmentData = {
    name, path: stored, size: req.body.length, type,
    account: new RecordId('account', recordId(req.account.sub)),
    created_by: new RecordId('account', recordId(req.account.sub)),
    sort_order: 0,
    text_status: extracted.status,
  };
  if (extracted.text) attachmentData.text_content = extracted.text;
  if (req.headers['x-note-id']) attachmentData.note = new RecordId('notes', String(req.headers['x-note-id']));
  if (roomHeader) attachmentData.room = new RecordId('chat_room', roomHeader);
  try {
    const rows = await q('CREATE attachments CONTENT $data RETURN AFTER;', { data: attachmentData });
    res.status(201).json(publicAttachment(rows[0]));
  } catch (error) {
    fs.rm(path.join(uploadDir, stored), { force: true }, () => {});
    res.status(500).json({ error: 'Could not store the attachment', detail: error.message });
  }
});

app.patch('/api/attachments/:id', auth, requirePermission('notes:write'), async (req, res) => {
  const updates = {};
  if (req.body.name !== undefined) {
    const name = String(req.body.name).trim().slice(0, 200);
    if (!name) return res.status(400).json({ error: 'Name cannot be empty' });
    updates.name = name;
  }
  if (req.body.note !== undefined) updates.note = req.body.note ? new RecordId('notes', String(req.body.note)) : null;
  if (req.body.sortOrder !== undefined) updates.sort_order = Number(req.body.sortOrder) || 0;
  if (!Object.keys(updates).length) return res.status(400).json({ error: 'No changes provided' });
  const rows = await q('UPDATE type::thing("attachments", $id) MERGE $updates RETURN AFTER;', { id: req.params.id, updates });
  if (!rows[0]) return res.status(404).json({ error: 'Attachment not found' });
  res.json(publicAttachment(rows[0]));
});

app.delete('/api/attachments/:id', auth, requirePermission('notes:write'), async (req, res) => {
  const rows = await q('DELETE type::thing("attachments", $id) RETURN BEFORE;', { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Attachment not found' });
  fs.rm(path.join(uploadDir, path.basename(rows[0].path)), { force: true }, () => {});
  res.status(204).end();
});

app.get('/files/:id/:name', authQueryToken, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("attachments", $id) LIMIT 1;', { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Attachment not found' });
  const filePath = path.join(uploadDir, path.basename(rows[0].path));
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'File missing from storage' });
  res.setHeader('content-type', rows[0].type || 'application/octet-stream');
  res.setHeader('content-disposition', `inline; filename="${encodeURIComponent(rows[0].name)}"`);
  fs.createReadStream(filePath).pipe(res);
});

app.post('/api/auth/register', async (req, res) => {
  const name = String(req.body.name || '').trim();
  const password = String(req.body.password || '');
  const inviteCode = String(req.body.invite || '').trim();
  const ip = clientIp(req);
  const userAgent = String(req.headers['user-agent'] || '').slice(0, 200);
  const count = await q('SELECT count() AS count FROM account GROUP ALL;');
  const hasAccounts = Number(count[0]?.count || 0) > 0;
  // Like login, only rejected registrations count toward the limiter.
  const registerRejected = async (status, message, reason) => {
    const limit = await checkRateLimit('register', ip);
    if (!limit.allowed) {
      await recordSecurityEvent('rate.blocked', { name, ip, userAgent, detail: { scope: 'register' } });
      return res.status(429).json({ error: 'Too many attempts. Try again later.' });
    }
    await recordSecurityEvent('register.rejected', { name, ip, userAgent, detail: { reason } });
    return res.status(status).json({ error: message });
  };
  if (!hasAccounts) {
    // First account ever: bootstrap superadmin, no invite needed.
    if (name.length < 3 || password.length < 8) {
      return registerRejected(400, 'Username must be 3+ characters and password 8+ characters', 'weak-credentials');
    }
    const account = await ensureAccount(name, password);
    // The first account administers the default workspace, and the membership
    // edge is what makes that real for the switcher and the scope resolver.
    try {
      await upsertEdge('workspace_member', 'account', recordId(account.id), 'workspace', 'default', {
        role: 'superadmin', created_at: new Date(),
      });
    } catch { /* unique race — membership already present */ }
    await recordAudit('account.create', recordId(account.id), { role: 'superadmin' });
    await recordSecurityEvent('register.success', { name, ip, userAgent, detail: { bootstrap: true } });
    return res.status(201).json({ user: publicUser(account), token: issueToken(account) });
  }
  if (!inviteCode) {
    return registerRejected(403, 'Registration requires an invitation code', 'no-invite');
  }
  if (name.length < 3 || password.length < 8) {
    return registerRejected(400, 'Username must be 3+ characters and password 8+ characters', 'weak-credentials');
  }
  const invite = (await q('SELECT * FROM workspace_invitation WHERE code = $code LIMIT 1;', { code: inviteCode }))[0];
  if (!invite || invite.accepted_at || invite.revoked_at || inviteExpired(invite)) {
    return registerRejected(403, 'Invalid or already-used invitation code', 'invalid-code');
  }
  if (!roles.includes(invite.role) || invite.role === 'superadmin') {
    return registerRejected(403, 'That invitation carries an unknown role', 'unknown-role');
  }
  if (await findAccount(name)) {
    return registerRejected(409, 'A member with that name already exists', 'name-taken');
  }
  const inviteWorkspace = invite.workspace ? recordId(invite.workspace) : 'default';
  if (!(await findWorkspace(inviteWorkspace))) return res.status(404).json({ error: 'Workspace not found' });
  const account = await ensureAccount(name, password, invite.role, inviteWorkspace);
  // Redeem: mark used, wire the membership edge, audit — in that order, so a
  // concurrent registration can never collect the same code twice.
  const redeemed = await q('UPDATE workspace_invitation MERGE { accepted_at: time::now() } WHERE code = $code AND accepted_at IS NONE AND revoked_at IS NONE RETURN AFTER;', { code: inviteCode });
  if (!redeemed[0]) return res.status(403).json({ error: 'Invalid or already-used invitation code' });
  try {
    await addWorkspaceMember(recordId(account.id), inviteWorkspace, invite.role, invite.created_by ? recordId(invite.created_by) : null);
  } catch { /* unique race — membership already present */ }
  await recordAudit('invite.accept', recordId(account.id), { role: invite.role }, invite.code, inviteWorkspace);
  await recordSecurityEvent('register.success', { name, ip, userAgent, workspaceId: inviteWorkspace, detail: { via: 'invite', role: invite.role } });
  res.status(201).json({ user: publicUser(account, invite.role), token: issueToken(account), workspaceId: inviteWorkspace });
});

app.post('/api/auth/login', async (req, res) => {
  const name = String(req.body.name || '').trim();
  const ip = clientIp(req);
  const userAgent = String(req.headers['user-agent'] || '').slice(0, 200);
  const account = await findAccount(name);
  if (!account || !(await bcrypt.compare(String(req.body.password || ''), account.password_hash))) {
    // Only failures count toward the limiter: brute force is a pattern of
    // failures, while many successful sign-ins from one office IP are normal
    // and should never lock a team out.
    const limit = await checkRateLimit('login', ip);
    if (!limit.allowed) {
      await recordSecurityEvent('rate.blocked', { name, ip, userAgent, detail: { scope: 'login' } });
      return res.status(429).json({ error: 'Too many attempts. Try again later.' });
    }
    await recordSecurityEvent('login.failed', { name, ip, userAgent, detail: { reason: account ? 'bad-password' : 'unknown-user' } });
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  // Sign-in resolves the workspace up front so the client boots with the role
  // that workspace grants, not the account's legacy global role.
  const scope = await resolveWorkspaceScope(recordId(account.id));
  await recordSecurityEvent('login.success', { name, ip, userAgent, workspaceId: scope.workspaceId, detail: {} });
  res.json({ user: publicUser(account, scope.role), token: issueToken(account), workspaceId: scope.workspaceId, workspaceRole: scope.role });
});

app.get('/api/auth/profile', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("account", $id) LIMIT 1;', { id: req.account.sub });
  if (!rows[0]) return res.status(404).json({ error: 'User not found' });
  // The effective role is the membership role in the active workspace, so the
  // sidebar chip and the permission gates match what the server will allow.
  res.json({ user: publicUser(rows[0], req.workspaceRole), workspaceId: req.workspaceId, workspaceRole: req.workspaceRole });
});

// --- Phase 2: sharing, invitations, audit ---------------------------------

app.patch('/api/notes/:id/share', auth, requirePermission('notes:write'), async (req, res) => {
  const rows = await q(`UPDATE type::thing('notes', $id) MERGE { is_share: $share, updated_at: time::now() }
    WHERE workspace = ${wsLiteral(req)}
    RETURN *, category.* AS category_record;`, { id: req.params.id, share: Boolean(req.body.share) });
  if (!rows[0]) return res.status(404).json({ error: 'Note not found' });
  await recordAudit(req.body.share ? 'note.share' : 'note.unshare', req.account.sub, {}, req.params.id, req.workspaceId);
  res.json(publicNote(rows[0]));
});

// Public read-only rendering of a shared note; the shared renderer module
// keeps parity with the client. Design language ported from the main Planing
// source (app/src/pages/share/[id].tsx + GradientBackground): an animated
// shader-gradient backdrop (#4603ff / #FE8989 / #000 waterPlane) behind a
// centered glass-effect card with the magenta ambient shadow. Rebuilt here as
// a dependency-free canvas animation so the public page stays offline-safe.

// Three drifting radial blobs over a dark base reproduce the shader palette;
// prefers-reduced-motion paints a single static frame instead of animating.
const shareBackgroundScript = `
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canvas = document.getElementById('share-gradient');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var blobs = [
    { x: 0.30, y: 0.32, r: 0.62, c: [70, 3, 255],    ax: 0.070, ay: 0.052, sx: 0.00021, sy: 0.00017, px: 0.0, py: 1.7 },
    { x: 0.74, y: 0.62, r: 0.55, c: [254, 137, 137], ax: 0.055, ay: 0.070, sx: 0.00016, sy: 0.00023, px: 2.1, py: 0.4 },
    { x: 0.52, y: 0.86, r: 0.60, c: [22, 2, 44],     ax: 0.040, ay: 0.035, sx: 0.00013, sy: 0.00019, px: 4.2, py: 2.8 }
  ];
  function paint(t) {
    var w = canvas.width, h = canvas.height;
    ctx.globalCompositeOperation = 'source-over';
    var g0 = ctx.createLinearGradient(0, 0, w, h);
    g0.addColorStop(0, '#0a0416');
    g0.addColorStop(1, '#120626');
    ctx.fillStyle = g0;
    ctx.fillRect(0, 0, w, h);
    ctx.globalCompositeOperation = 'lighter';
    for (var i = 0; i < blobs.length; i++) {
      var b = blobs[i];
      var bx = (b.x + Math.sin(t * b.sx + b.px) * b.ax) * w;
      var by = (b.y + Math.cos(t * b.sy + b.py) * b.ay) * h;
      var br = b.r * Math.max(w, h);
      var g = ctx.createRadialGradient(bx, by, 0, bx, by, br);
      var c = b.c;
      g.addColorStop(0, 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',0.55)');
      g.addColorStop(0.55, 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',0.18)');
      g.addColorStop(1, 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',0)');
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
    }
    ctx.globalCompositeOperation = 'source-over';
  }
  function resize() {
    canvas.width = Math.max(1, Math.floor(window.innerWidth * 0.75));
    canvas.height = Math.max(1, Math.floor(window.innerHeight * 0.75));
    paint(1);
  }
  window.addEventListener('resize', resize);
  resize();
  if (reduce) return;
  (function loop(now) { paint(now); requestAnimationFrame(loop); })(performance.now());
})();
`;

// Glass card on the animated gradient: the share bar pills and the article use
// backdrop blur; the article carries the main source's magenta ambient shadow.
const shareStyles = `
:root{--share-ink:#17171c;--share-muted:#5c5f68;--share-accent:#5b3fd6;--share-line:rgba(23,23,28,.08)}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{min-height:100dvh;color:var(--share-ink);font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;background:#0a0416;-webkit-font-smoothing:antialiased}
#share-gradient{position:fixed;inset:0;width:100%;height:100%;z-index:0;transform:translateZ(0)}
.share-veil{position:fixed;inset:0;z-index:1;pointer-events:none;background:linear-gradient(rgba(8,3,18,.30),rgba(8,3,18,.30))}
main{position:relative;z-index:2;max-width:760px;margin:7vh auto 0;padding:0 20px 72px}
.sharebar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap;animation:rise .7s cubic-bezier(.22,1,.36,1) both}
.sharebar strong{font:750 .66rem/1 ui-monospace,'SFMono-Regular',Menlo,monospace;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.92);text-shadow:0 1px 8px rgba(10,4,22,.6)}
.sharebar span{display:flex;gap:8px;flex-wrap:wrap}
.sharebar a{font-size:.74rem;font-weight:600;text-decoration:none;color:#17171c;background:rgba(255,255,255,.92);border:1px solid rgba(255,255,255,.55);padding:7px 14px;border-radius:999px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-shadow:inset 0 1px 0 rgba(255,255,255,.7),0 4px 18px rgba(10,4,22,.28);transition:transform .35s cubic-bezier(.22,1,.36,1),box-shadow .35s ease,background .35s ease}
.sharebar a:hover{transform:translateY(-1px) scale(1.03);background:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.7),0 10px 26px rgba(10,4,22,.34)}
.sharebar a:active{transform:translateY(0) scale(.97);box-shadow:inset 0 1px 0 rgba(255,255,255,.7),0 3px 10px rgba(10,4,22,.3)}
article{background:rgba(255,255,255,.86);backdrop-filter:blur(14px) saturate(1.25);-webkit-backdrop-filter:blur(14px) saturate(1.25);border:1px solid rgba(255,255,255,.6);border-radius:18px;padding:clamp(24px,4vw,40px);box-shadow:inset 0 1px 0 rgba(255,255,255,.6),1px 0 25px 11px rgba(98,0,114,.17),0 24px 70px rgba(10,4,22,.45);animation:rise .8s .08s cubic-bezier(.22,1,.36,1) both,floaty 11s 1.6s ease-in-out infinite}
h1{margin:0 0 8px;font-size:clamp(1.5rem,1.1rem + 1.8vw,2.2rem);letter-spacing:-.022em;line-height:1.18;overflow-wrap:break-word}
time{display:inline-block;color:var(--share-muted);font-size:.7rem;letter-spacing:.09em;text-transform:uppercase;padding:5px 10px;border-radius:999px;background:rgba(91,63,214,.08);border:1px solid rgba(91,63,214,.16)}
.markdown-body{line-height:1.66;font-size:.95rem;margin-top:20px;color:#212127}
.markdown-body>*:first-child{margin-top:0}
.markdown-body table{border-collapse:collapse;width:100%;font-size:.86em;margin:0 0 .7em}
.markdown-body th,.markdown-body td{border:1px solid var(--share-line);padding:.45em .7em;text-align:start}
.markdown-body th{background:rgba(91,63,214,.07)}
.markdown-body hr{border:0;border-top:1px solid var(--share-line);margin:.9em 0}
.markdown-body mark{background:#efe7c8;padding:0 .15em;border-radius:3px}
.markdown-body pre{background:#14101f;color:#eceaf4;padding:26px 14px 12px;border-radius:12px;overflow:auto;position:relative;border:1px solid rgba(255,255,255,.07)}
.markdown-body pre[data-lang]::after{content:attr(data-lang);position:absolute;top:7px;right:11px;font:700 .56rem ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;color:#9d93c9}
.markdown-body code{font-family:ui-monospace,'SFMono-Regular',Menlo,monospace}
.markdown-body :not(pre)>code{font:600 .84em ui-monospace,monospace;background:rgba(91,63,214,.09);border:1px solid rgba(91,63,214,.14);border-radius:5px;padding:.1em .35em;color:#4a34b8}
.markdown-body blockquote{margin:0 0 .55em;padding:.2em .9em;border-left:3px solid var(--share-accent);background:rgba(91,63,214,.06);border-radius:6px}
.markdown-body li.task-item{display:flex;gap:.5em;list-style:none}
.markdown-body ul:has(> li.task-item){list-style:none;padding-left:.3em}
.markdown-body img{max-width:100%;border-radius:12px}
.markdown-body a{color:var(--share-accent);text-decoration-color:rgba(91,63,214,.35);text-underline-offset:2px;transition:color .25s ease}
.markdown-body a:hover{color:#7a5cff}
.markdown-body .wikilink{background:rgba(91,63,214,.1);border-radius:5px;padding:0 .25em;color:#4a34b8;font-weight:600;transition:background .25s ease}
.markdown-body .wikilink:hover{background:rgba(91,63,214,.18)}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes settle{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.markdown-body>*{animation:settle .6s cubic-bezier(.22,1,.36,1) both}
.markdown-body>*:nth-child(2){animation-delay:.06s}
.markdown-body>*:nth-child(3){animation-delay:.12s}
.markdown-body>*:nth-child(4){animation-delay:.18s}
.markdown-body>*:nth-child(5){animation-delay:.24s}
.markdown-body>*:nth-child(6){animation-delay:.3s}
.markdown-body>*:nth-child(7){animation-delay:.36s}
.markdown-body>*:nth-child(8){animation-delay:.42s}
.markdown-body>*:nth-child(9){animation-delay:.48s}
.markdown-body>*:nth-child(n+10){animation-delay:.54s}
@media (prefers-reduced-motion:reduce){article,.sharebar,.markdown-body>*{animation:none}.sharebar a,.markdown-body a{transition:none}}
@media (max-width:560px){main{margin-top:5vh;padding:0 12px 56px}article{border-radius:14px;box-shadow:inset 0 1px 0 rgba(255,255,255,.6),0 12px 34px rgba(10,4,22,.4);animation:rise .8s .08s cubic-bezier(.22,1,.36,1) both}}
`;

function share404Page(res) {
  res.status(404).send(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Note not shared</title><style>
  body{margin:0;color:#17171c;font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;display:grid;place-items:center;min-height:100dvh;background:#0a0416;-webkit-font-smoothing:antialiased}
  main{position:relative;max-width:520px;margin:20px;padding:34px;background:rgba(255,255,255,.86);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.6);border-radius:18px;box-shadow:inset 0 1px 0 rgba(255,255,255,.6),1px 0 25px 11px rgba(98,0,114,.17),0 24px 70px rgba(10,4,22,.45);animation:rise .7s cubic-bezier(.22,1,.36,1) both}
  h1{margin:0 0 8px;font-size:1.35rem;letter-spacing:-.02em}
  p{color:#5c5f68;line-height:1.6;font-size:.92rem}
  code{font:600 .82em ui-monospace,monospace;background:rgba(91,63,214,.09);border:1px solid rgba(91,63,214,.14);border-radius:5px;padding:.1em .35em;color:#4a34b8}
  ol{color:#5c5f68;font-size:.9rem;line-height:1.8}
  a.home{display:inline-block;margin-top:14px;font-size:.8rem;font-weight:600;color:#17171c;text-decoration:none;background:rgba(255,255,255,.92);border:1px solid rgba(255,255,255,.55);padding:8px 14px;border-radius:999px;box-shadow:0 4px 18px rgba(10,4,22,.28);transition:transform .35s cubic-bezier(.22,1,.36,1)}
  a.home:hover{transform:translateY(-1px)}
  a.home:active{transform:translateY(0) scale(.97)}
  @keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
  @media (prefers-reduced-motion:reduce){main{animation:none}a.home{transition:none}}
  </style></head><body><main>
    <h1>This note is not shared</h1>
    <p>The link is valid, but the note is private (or was unshared). A shared note is readable by anyone with the link until sharing is turned off.</p>
    <ol>
      <li>Open the note in the workspace.</li>
      <li>Choose <strong>Share</strong>, which copies the public link.</li>
      <li>Reopen the link — it renders here as a read-only page.</li>
    </ol>
    <p>Shared links also support raw markdown at <code>/share/&lt;note-id&gt;/raw</code>.</p>
    <a class="home" href="/">Open the workspace →</a>
  </main></body></html>`);
}

app.get('/share/:id/raw', async (req, res) => {
  const rows = await q(`SELECT * FROM type::thing('notes', $id) WHERE is_share = true AND is_recycle = false;`, { id: req.params.id });
  if (!rows[0]) return share404Page(res);
  const note = publicNote(rows[0]);
  const title = (note.content.split('\n').find((line) => line.trim()) || 'note').replace(/^#+\s*/, '').trim().slice(0, 60) || 'note';
  res.setHeader('content-type', 'text/markdown; charset=utf-8');
  res.setHeader('content-disposition', `inline; filename="${title.replace(/[^\w.-]+/g, '-').toLowerCase()}.md"`);
  res.send(note.content);
});

app.get('/share/:id', async (req, res) => {
  const rows = await q(`SELECT *, category.* AS category_record FROM type::thing('notes', $id)
    WHERE is_share = true AND is_recycle = false;`, { id: req.params.id });
  if (!rows[0]) return share404Page(res);
  const note = publicNote(rows[0]);
  const heading = ((note.content.split('\n').find((line) => line.trim()) || 'Shared note').replace(/^#+\s*/, '').trim()).slice(0, 90) || 'Shared note';
  res.send(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="Read-only shared note"><title>${escapeFragment(heading)} — shared note</title><style>${shareStyles}</style></head><body>
  <canvas id="share-gradient" aria-hidden="true"></canvas>
  <div class="share-veil" aria-hidden="true"></div>
  <main>
  <div class="sharebar"><strong>PLANING · SHARED NOTE</strong><span><a href="/share/${encodeURIComponent(req.params.id)}/raw" download>Download .md</a> <a href="/share/${encodeURIComponent(req.params.id)}/raw">Raw markdown</a></span></div>
  <article><h1>${escapeFragment(heading)}</h1><time>${new Date(note.updatedAt).toISOString().slice(0, 10)} · ${escapeFragment(note.category?.name || 'notes')}</time><div class="markdown-body">${renderSharedMarkdown(note.content)}</div></article>
  </main>
  <script>${shareBackgroundScript}</script>
  </body></html>`);
});

// Per-note activity: the timeline behind the workspace audit stream. Readers
// only need notes:read, because everything here is already workspace-scoped.
app.get('/api/notes/:id/activity', auth, requirePermission('notes:read'), async (req, res) => {
  const noteRows = await q(`SELECT id FROM type::thing("notes", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  if (!noteRows[0]) return res.status(404).json({ error: 'Note not found' });
  const rows = await q(`SELECT * FROM note_activity WHERE note = type::thing("notes", $id) ORDER BY created_at DESC LIMIT 50;`, { id: req.params.id });
  const actorIds = [...new Set(rows.map((row) => row.actor ? recordId(row.actor) : null).filter(Boolean))];
  const names = await accountNames(actorIds);
  res.json(rows.map((row) => ({
    id: recordId(row.id),
    action: row.action,
    actor: row.actor ? recordId(row.actor) : null,
    actorName: row.actor ? names.get(recordId(row.actor)) || null : null,
    detail: row.detail || {},
    createdAt: isoOrNull(row.created_at),
  })));
});

app.get('/api/audit', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q(`SELECT * FROM audit_event WHERE workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT 100;`);
  res.json(rows.map((row) => ({
    id: recordId(row.id),
    action: row.action,
    actor: row.actor ? recordId(row.actor) : null,
    target: row.target,
    detail: row.detail || {},
    createdAt: row.created_at instanceof Date ? row.created_at.toISOString() : row.created_at,
  })));
});

// Security events answer to settings:write like the audit stream — they can
// contain names and IPs, which viewers should not browse.

// Phase 2 closeout: run the retention purge on demand (settings gate). The
// hourly sweep still runs; this button just makes the sweep observable.
app.post('/api/retention/purge', auth, requirePermission('settings:write'), async (req, res) => {
  const result = await purgeExpiredContent();
  await recordAudit('retention.purge', req.account.sub, result, null, req.workspaceId);
  res.json(result);
});

// Phase 4 query-budget telemetry: aggregated per shape over a lookback window.
// Shapes are caller-declared names — no SQL text, no bound values, no note
// content ever reaches this ledger.
app.get('/api/telemetry/queries', auth, requirePermission('settings:write'), async (req, res) => {
  const hours = Math.min(Math.max(Number(req.query.hours) || 24, 1), 168);
  const rows = await q(
    `SELECT shape, count() AS total, math::sum(duration_ms) AS total_ms, math::max(duration_ms) AS max_ms, math::mean(duration_ms) AS avg_ms FROM query_metric WHERE created_at > time::now() - ${hours}h GROUP BY shape ORDER BY total DESC LIMIT 50;`,
  );
  const failures = await q(
    `SELECT shape, error_kind, count() AS total FROM query_metric WHERE created_at > time::now() - ${hours}h AND ok = false GROUP BY shape, error_kind ORDER BY total DESC LIMIT 50;`,
  );
  res.json({
    windowHours: hours,
    shapes: rows.map((row) => ({
      shape: row.shape,
      total: Number(row.total) || 0,
      avgMs: Math.round((Number(row.avg_ms) || 0) * 10) / 10,
      maxMs: Number(row.max_ms) || 0,
      p95Ms: null,
    })),
    failures: failures.map((row) => ({ shape: row.shape, errorKind: row.error_kind || 'unknown', total: Number(row.total) || 0 })),
  });
});

app.get('/api/security/events', auth, requirePermission('settings:write'), async (req, res) => {
  const limit = Math.min(Math.max(Number(req.query.limit) || 50, 1), 200);
  const rows = await q(`SELECT * FROM security_event ORDER BY created_at DESC LIMIT ${limit};`);
  res.json(rows.map((row) => ({
    id: recordId(row.id),
    kind: row.kind,
    workspace: row.workspace ? recordId(row.workspace) : null,
    name: row.name || null,
    ip: row.ip || null,
    userAgent: row.user_agent || null,
    detail: row.detail || {},
    createdAt: isoOrNull(row.created_at),
  })));
});

const asIso = (value) => (value instanceof Date ? value.toISOString() : value || null);
const inviteExpired = (invite) => Boolean(invite?.expires_at && new Date(invite.expires_at).getTime() <= Date.now());

// Codes belong to the workspace that created them: the People tab in workspace A
// never lists, revokes, or redeems a code from workspace B.
app.get('/api/invitations', auth, requirePermission('members:write'), async (req, res) => {
  const rows = await q(`SELECT * FROM workspace_invitation WHERE workspace = ${wsLiteral(req)} AND accepted_at IS NONE AND revoked_at IS NONE ORDER BY created_at DESC LIMIT 50;`);
  const creatorIds = [...new Set(rows.map((row) => recordId(row.created_by)).filter(Boolean))];
  const creators = creatorIds.length
    ? await q(`SELECT id, name FROM account WHERE id IN [${creatorIds.map((id) => recordLiteral('account', id)).join(', ')}];`)
    : [];
  const nameById = new Map(creators.map((row) => [recordId(row.id), row.name]));
  res.json(rows.map((row) => ({
    id: recordId(row.id),
    code: row.code,
    role: row.role,
    createdBy: nameById.get(recordId(row.created_by)) || null,
    workspaceId: recordId(row.workspace),
    createdAt: asIso(row.created_at),
    expiresAt: asIso(row.expires_at),
    expired: inviteExpired(row),
  })));
});

app.post('/api/invitations', auth, requirePermission('members:write'), async (req, res) => {
  const role = String(req.body.role || 'viewer');
  if (!canGrantRole(req.workspaceRole, role)) return res.status(403).json({ error: 'Your role cannot grant that role' });
  const code = crypto.randomBytes(9).toString('base64url');
  const expiresAt = new Date(Date.now() + inviteTtlDays * 24 * 60 * 60 * 1000);
  try {
    const rows = await q(`CREATE workspace_invitation SET ${literalAssignments({
      code,
      role,
      workspace: new RecordId('workspace', req.workspaceId),
      created_by: new RecordId('account', recordId(req.account.sub)),
      created_at: new Date(),
      expires_at: expiresAt,
    }).join(', ')} RETURN AFTER;`);
    await recordAudit('invite.create', req.account.sub, { role }, rows[0].code, req.workspaceId);
    res.status(201).json({ id: recordId(rows[0].id), code: rows[0].code, role: rows[0].role, workspaceId: req.workspaceId, expiresAt: expiresAt.toISOString() });
  } catch {
    res.status(500).json({ error: 'Could not create invitation' });
  }
});

app.delete('/api/invitations/:code', auth, requirePermission('members:write'), async (req, res) => {
  const rows = await q(`UPDATE workspace_invitation MERGE { revoked_at: time::now() } WHERE code = $code AND workspace = ${wsLiteral(req)} AND accepted_at IS NONE AND revoked_at IS NONE RETURN AFTER;`, { code: req.params.code });
  if (!rows[0]) return res.status(404).json({ error: 'Invitation not found in this workspace' });
  await recordAudit('invite.revoke', req.account.sub, {}, req.params.code, req.workspaceId);
  res.status(204).end();
});

// An account that already exists joins another workspace with a code. The code
// is the consent record, and it only ever grants the role the inviter was
// allowed to grant in the first place.
async function redeemInvitation(invite, accountId) {
  const workspaceId = invite.workspace ? recordId(invite.workspace) : 'default';
  const workspace = await findWorkspace(workspaceId);
  if (!workspace) return { error: 'Workspace not found', status: 404 };
  if (workspace.is_archived) return { error: 'That workspace is archived', status: 400 };
  if (await membershipEdge(accountId, workspaceId)) return { error: 'You are already a member of that workspace', status: 409 };
  // Claim the code and create the membership edge inside one transaction: a
  // concurrent redeem of the same code either claims first or sees the accepted
  // timestamp and refuses — the code can never be half-spent (Phase 4).
  const claimed = await transaction([
    'UPDATE workspace_invitation MERGE { accepted_at: time::now() } WHERE code = $code AND accepted_at IS NONE AND revoked_at IS NONE RETURN AFTER;',
  ], { code: invite.code });
  if (!claimed[0]) return { error: 'Invalid or already-used invitation code', status: 403 };
  try {
    await addWorkspaceMember(accountId, workspaceId, invite.role, invite.created_by ? recordId(invite.created_by) : null);
    await q(`UPDATE type::thing("account", $id) SET active_workspace = ${recordLiteral('workspace', workspaceId)};`, { id: recordId(accountId) });
  } catch (error) {
    // Release the claim so the code stays redeemable after a transient failure.
    await q('UPDATE workspace_invitation MERGE { accepted_at: NONE } WHERE code = $code;', { code: invite.code }).catch(() => {});
    throw error;
  }
  await recordAudit('invite.join', accountId, { role: invite.role }, invite.code, workspaceId);
  return { workspace, workspaceId, role: invite.role };
}

// Unknown, expired, revoked, and already-used codes all answer with the same
// message, so a probe cannot tell a spent code from a wrong one.
app.post('/api/invitations/redeem', auth, async (req, res) => {
  const code = String(req.body?.code || '').trim();
  if (!code) return res.status(400).json({ error: 'Provide an invitation code' });
  const limit = await checkRateLimit('redeem', recordId(req.account.sub));
  if (!limit.allowed) {
    await recordSecurityEvent('rate.blocked', { name: req.account.name || null, ip: clientIp(req), userAgent: String(req.headers['user-agent'] || '').slice(0, 200), detail: { scope: 'redeem' } });
    return res.status(429).json({ error: 'Too many attempts. Try again later.' });
  }
  const rows = await q('SELECT * FROM workspace_invitation WHERE code = $code LIMIT 1;', { code });
  const invite = rows[0];
  if (!invite || invite.accepted_at || invite.revoked_at || inviteExpired(invite)) {
    await recordSecurityEvent('invite.rejected', { name: req.account.name || null, ip: clientIp(req), userAgent: String(req.headers['user-agent'] || '').slice(0, 200), detail: { reason: 'invalid-code', via: 'redeem' } });
    return res.status(403).json({ error: 'Invalid or already-used invitation code' });
  }
  if (!roles.includes(invite.role) || invite.role === 'superadmin') return res.status(403).json({ error: 'That invitation carries an unknown role' });
  const result = await redeemInvitation(invite, req.account.sub);
  if (result.error) return res.status(result.status).json({ error: result.error });
  const memberships = await workspaceMemberships(req.account.sub);
  res.json({
    workspace: publicWorkspaceSummary(result.workspace, { role: result.role, isActive: true }),
    role: result.role,
    workspaceId: result.workspaceId,
    memberships,
  });
});

/* ---------- Note comments (Phase 2, per-workspace threads) ---------- */

// A comment is only reachable through a note that belongs to the workspace the
// request is in, so a guessed comment id from elsewhere resolves to nothing.
async function noteInWorkspace(req, noteId) {
  const rows = await q(`SELECT * FROM type::thing('notes', $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: noteId });
  return rows[0] || null;
}

const canComment = (role) => Boolean(rolePermissions[role]?.includes('comments:write'));
const canModerateComments = (role) => Boolean(rolePermissions[role]?.includes('members:write'));

function publicComment(row, { viewerId = null, canModerate = false, authorName = null } = {}) {
  const authorId = row.author ? recordId(row.author) : null;
  const isOwn = Boolean(viewerId && authorId && authorId === recordId(viewerId));
  const isDeleted = Boolean(row.is_deleted);
  return {
    id: recordId(row.id),
    noteId: recordId(row.note),
    // A deleted comment keeps its place in the thread but not its text.
    body: isDeleted ? '' : row.body,
    author: authorId,
    authorName,
    isOwn,
    isDeleted,
    canEdit: isOwn && !isDeleted,
    canDelete: !isDeleted && (isOwn || canModerate),
    edited: Boolean(row.edited_at),
    createdAt: asIso(row.created_at),
    updatedAt: asIso(row.updated_at),
  };
}

async function commentRows(req, noteId) {
  return q(`SELECT * FROM note_comment WHERE note = type::thing('notes', $id) AND workspace = ${wsLiteral(req)} ORDER BY created_at ASC LIMIT 200;`, { id: noteId });
}

app.get('/api/notes/:id/comments', auth, async (req, res) => {
  const note = await noteInWorkspace(req, req.params.id);
  if (!note) return res.status(404).json({ error: 'Note not found' });
  const rows = await commentRows(req, req.params.id);
  const nameById = await accountNames(rows.map((row) => recordId(row.author)));
  const canModerate = canModerateComments(req.workspaceRole);
  res.json({
    noteId: recordId(note.id),
    canComment: canComment(req.workspaceRole),
    canModerate,
    count: rows.filter((row) => !row.is_deleted).length,
    comments: rows.map((row) => publicComment(row, {
      viewerId: req.account.sub,
      canModerate,
      authorName: row.author ? nameById.get(recordId(row.author)) || null : null,
    })),
  });
});

app.post('/api/notes/:id/comments', auth, requirePermission('comments:write'), async (req, res) => {
  const body = String(req.body?.body || '').trim().slice(0, 4000);
  if (!body) return res.status(400).json({ error: 'Write something first' });
  const note = await noteInWorkspace(req, req.params.id);
  if (!note) return res.status(404).json({ error: 'Note not found' });
  const rows = await q(`CREATE note_comment SET ${literalAssignments({
    body,
    note: { tb: 'notes', id: recordId(note.id) },
    workspace: { tb: 'workspace', id: req.workspaceId },
    author: { tb: 'account', id: recordId(req.account.sub) },
    metadata: {},
    created_at: new Date(),
    updated_at: new Date(),
  }).join(', ')} RETURN AFTER;`);
  await recordAudit('comment.create', req.account.sub, { length: body.length }, recordId(note.id), req.workspaceId);
  const nameById = await accountNames([recordId(req.account.sub)]);
  res.status(201).json(publicComment(rows[0], {
    viewerId: req.account.sub,
    canModerate: canModerateComments(req.workspaceRole),
    authorName: nameById.get(recordId(req.account.sub)) || null,
  }));
});

app.patch('/api/comments/:id', auth, requirePermission('comments:write'), async (req, res) => {
  const body = String(req.body?.body || '').trim().slice(0, 4000);
  if (!body) return res.status(400).json({ error: 'Write something first' });
  const rows = await q(`SELECT * FROM type::thing('note_comment', $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const comment = rows[0];
  if (!comment) return res.status(404).json({ error: 'Comment not found' });
  if (recordId(comment.author) !== recordId(req.account.sub)) return res.status(403).json({ error: 'You can only edit your own comment' });
  if (comment.is_deleted) return res.status(400).json({ error: 'That comment was deleted' });
  const updated = await q(`UPDATE type::thing('note_comment', $id) MERGE { body: $body, edited_at: time::now(), updated_at: time::now() } RETURN AFTER;`, { id: req.params.id, body });
  await recordAudit('comment.edit', req.account.sub, {}, recordId(comment.note), req.workspaceId);
  const nameById = await accountNames([recordId(req.account.sub)]);
  res.json(publicComment(updated[0], {
    viewerId: req.account.sub,
    canModerate: canModerateComments(req.workspaceRole),
    authorName: nameById.get(recordId(req.account.sub)) || null,
  }));
});

app.delete('/api/comments/:id', auth, requirePermission('comments:write'), async (req, res) => {
  const rows = await q(`SELECT * FROM type::thing('note_comment', $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const comment = rows[0];
  if (!comment) return res.status(404).json({ error: 'Comment not found' });
  const isOwn = recordId(comment.author) === recordId(req.account.sub);
  // Authors remove their own reply; a member who can manage people also
  // moderates the thread.
  if (!isOwn && !canModerateComments(req.workspaceRole)) return res.status(403).json({ error: 'You can only delete your own comment' });
  await q(`UPDATE type::thing('note_comment', $id) MERGE { is_deleted: true, body: '', updated_at: time::now() } RETURN AFTER;`, { id: req.params.id });
  await recordAudit('comment.delete', req.account.sub, { moderated: !isOwn }, recordId(comment.note), req.workspaceId);
  res.status(204).end();
});

app.get('/api/export', auth, async (req, res) => {
  const [workspace, categories, tags, notes, attachments] = await Promise.all([
    q(`SELECT * FROM ${wsLiteral(req)};`),
    q(`SELECT * FROM category WHERE workspace = ${wsLiteral(req)};`),
    q('SELECT * FROM tag;'),
    q(`SELECT *, category.* AS category_record FROM notes WHERE workspace = ${wsLiteral(req)};`),
    q(`SELECT * FROM attachments WHERE workspace = ${wsLiteral(req)};`),
  ]);
  res.setHeader('content-disposition', 'attachment; filename="planing-export.json"');
  res.json({ schemaVersion, exportedAt: new Date().toISOString(), workspace: publicWorkspace(workspace[0] || {}), categories: categories.map(publicCategory), tags: tags.map(publicTag), notes: notes.map((row) => publicNote(row)), attachments: attachments.map(publicAttachment) });
});

/* ---------- Workspace bundle: move a whole workspace between deployments ---------- */

const bundleVersion = 1;

// A bundle carries everything the workspace owns that is portable: its settings,
// lanes, tags, notes, study cards, comment threads, attachment metadata, and
// custom prompts. Deployment state is deliberately excluded — AI providers hold
// credentials, a chat belongs to a provider, and audit rows are history rather
// than content. Note ids travel so [[wiki links]], share links, and study cards
// keep pointing at the same records after a move.
async function buildWorkspaceBundle(workspaceId) {
  const ws = recordLiteral('workspace', workspaceId);
  const [workspace, categories, tags, notes, study, comments, attachments, prompts] = await Promise.all([
    findWorkspace(workspaceId),
    q(`SELECT * FROM category WHERE workspace = ${ws} ORDER BY sort_order ASC, name ASC;`),
    q(`SELECT * FROM tag WHERE workspace = ${ws} ORDER BY name ASC;`),
    q(`SELECT *, category.* AS category_record FROM notes WHERE workspace = ${ws} ORDER BY created_at ASC;`),
    q(`SELECT * FROM study_item WHERE workspace = ${ws};`),
    q(`SELECT * FROM note_comment WHERE workspace = ${ws} ORDER BY created_at ASC;`),
    q(`SELECT * FROM attachments WHERE workspace = ${ws};`),
    q(`SELECT * FROM prompt_template WHERE is_system = false AND workspace = ${ws};`),
  ]);
  return {
    bundleVersion,
    schemaVersion,
    exportedAt: new Date().toISOString(),
    source: { workspaceId, workspaceName: workspace?.name || 'workspace' },
    workspace: {
      name: workspace?.name || '',
      description: workspace?.description || '',
      defaultCategory: workspace?.default_category || 'notes',
      aiContext: workspace?.ai_context || '',
      theme: workspace?.theme || 'system',
      accent: workspace?.accent || 'violet',
      fontScale: workspace?.font_scale || 'default',
      contextRoots: Array.isArray(workspace?.context_roots) ? workspace.context_roots.map(String) : [],
    },
    categories: categories.map((row) => ({
      slug: recordId(row.slug),
      name: row.name,
      color: row.color || '#64748b',
      icon: row.icon || 'N',
      isSystem: Boolean(row.is_system),
      isDefault: Boolean(row.is_default),
      sortOrder: Number(row.sort_order || 0),
    })),
    tags: tags.map(publicTag),
    notes: notes.map(publicNote),
    study: study.map((row) => ({
      id: recordId(row.id),
      note: row.note ? recordId(row.note) : null,
      question: row.question,
      answer: row.answer,
      box: Number(row.box || 0),
      dueAt: isoOrNull(row.due_at),
      reviewCount: Number(row.review_count || 0),
      lapses: Number(row.lapses || 0),
      source: row.source || 'manual',
    })),
    comments: comments.map((row) => ({
      id: recordId(row.id),
      note: row.note ? recordId(row.note) : null,
      author: row.author ? recordId(row.author) : null,
      body: row.body,
      isDeleted: Boolean(row.is_deleted),
      createdAt: isoOrNull(row.created_at),
      updatedAt: isoOrNull(row.updated_at),
    })),
    attachments: attachments.map((row) => ({
      id: recordId(row.id),
      name: row.name,
      size: Number(row.size || 0),
      type: row.type || 'application/octet-stream',
      note: row.note ? recordId(row.note) : null,
      sortOrder: Number(row.sort_order || 0),
    })),
    prompts: prompts.map((row) => ({ id: recordId(row.id), title: row.title, body: row.body })),
  };
}

// The bundle filename and the imported workspace name come from the source name,
// which is user input, so both are normalised once here.
const bundleSlug = (value, fallback) => String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40) || fallback;

async function uniqueWorkspaceName(base) {
  const rows = await q('SELECT name FROM workspace;');
  const taken = new Set(rows.map((row) => String(row.name || '').toLowerCase()));
  const trimmed = String(base || '').trim().slice(0, 80) || 'Imported workspace';
  if (!taken.has(trimmed.toLowerCase())) return trimmed;
  for (let index = 2; index < 100; index += 1) {
    const candidate = `${trimmed} (${index})`.slice(0, 80);
    if (!taken.has(candidate.toLowerCase())) return candidate;
  }
  return `${trimmed} (${Date.now()})`.slice(0, 80);
}

// Restore a bundle as a NEW workspace: importing never merges into or overwrites
// what is already here. Note, study, and comment ids are preserved when they are
// free and remapped when they are taken, and the remap is applied to every
// dependent record so a moved workspace stays internally consistent.
async function restoreWorkspaceBundle(bundle, accountId) {
  const name = await uniqueWorkspaceName(bundle.workspace.name);
  const slug = bundleSlug(name, 'workspace');
  const rows = await q(`CREATE workspace SET ${literalAssignments({
    name,
    slug,
    description: String(bundle.workspace.description || '').slice(0, 200),
    default_category: String(bundle.workspace.defaultCategory || 'notes').slice(0, 60),
    ai_context: String(bundle.workspace.aiContext || '').slice(0, 2000),
    theme: themes.includes(bundle.workspace.theme) ? bundle.workspace.theme : 'system',
    accent: accents.includes(bundle.workspace.accent) ? bundle.workspace.accent : 'violet',
    font_scale: fontScales.includes(bundle.workspace.fontScale) ? bundle.workspace.fontScale : 'default',
    context_roots: Array.isArray(bundle.workspace.contextRoots) ? bundle.workspace.contextRoots.map(String).filter((id) => contextRoot(id)) : [],
    is_archived: false,
    metadata: { importedAt: new Date(), bundleVersion: Number(bundle.bundleVersion || 1) },
    created_by: { tb: 'account', id: recordId(accountId) },
    created_at: new Date(),
    updated_at: new Date(),
  }).join(', ')} RETURN AFTER;`);
  const workspaceId = recordId(rows[0].id);
  await addWorkspaceMember(accountId, workspaceId, 'owner', accountId);

  const imported = { categories: 0, tags: 0, notes: 0, remapped: 0, study: 0, comments: 0, prompts: 0, links: 0, skipped: 0 };
  const created = [];
  for (const lane of Array.isArray(bundle.categories) ? bundle.categories : []) {
    const laneSlug = bundleSlug(String(lane.slug || lane.name || ''), '');
    if (!laneSlug) { imported.skipped += 1; continue; }
    if (await findCategory(laneSlug, workspaceId)) continue;
    created.push(q(`CREATE category SET ${literalAssignments({
      name: String(lane.name || laneSlug).slice(0, 80),
      slug: laneSlug,
      color: /^#[0-9a-fA-F]{6}$/.test(String(lane.color || '')) ? lane.color : '#64748b',
      icon: String(lane.icon || 'N').slice(0, 2),
      is_system: Boolean(lane.isSystem),
      is_default: Boolean(lane.isDefault),
      workspace: { tb: 'workspace', id: workspaceId },
      sort_order: Number(lane.sortOrder || 0),
      created_by: { tb: 'account', id: recordId(accountId) },
      created_at: new Date(),
      updated_at: new Date(),
    }).join(', ')};`));
    imported.categories += 1;
  }
  await Promise.all(created);
  // A bundle from an older release may not carry every system lane; seed what is
  // missing so the imported workspace is never lane-less.
  await seedWorkspaceLanes(workspaceId, accountId);

  // Notes first, so study cards and comments can point at the restored records.
  const noteIdMap = new Map();
  for (const note of Array.isArray(bundle.notes) ? bundle.notes : []) {
    const content = String(note.content || '').trim();
    if (!content) { imported.skipped += 1; continue; }
    const sourceId = String(note.id || '').trim().replace(/[⟨⟩]/g, '');
    const wantedId = sourceId && !(await q('SELECT id FROM type::thing("notes", $id) LIMIT 1;', { id: sourceId }))[0] ? sourceId : null;
    if (sourceId && !wantedId) imported.remapped += 1;
    const laneSlug = bundleSlug(String(note.category?.slug || note.category || 'notes'), 'notes');
    const lane = await findCategory(laneSlug, workspaceId) || await findCategory('notes', workspaceId);
    if (!lane) { imported.skipped += 1; continue; }
    const tagIds = await ensureTags(Array.isArray(note.tags) ? note.tags.map((tag) => (typeof tag === 'string' ? tag : tag?.name)) : [], workspaceId);
    imported.tags += tagIds.length;
    const parseDate = (value, fallback) => {
      const parsed = value ? new Date(value) : null;
      return parsed && !Number.isNaN(parsed.getTime()) ? parsed : fallback;
    };
    const fields = {
      content,
      category: new RecordId('category', recordId(lane.id)),
      account: new RecordId('account', recordId(accountId)),
      created_by: new RecordId('account', recordId(accountId)),
      workspace: new RecordId('workspace', workspaceId),
      tags: tagIds,
      is_archived: Boolean(note.isArchived),
      is_recycle: Boolean(note.isRecycle),
      is_top: Boolean(note.isTop),
      is_share: Boolean(note.isShare),
      metadata: note.metadata && typeof note.metadata === 'object' && !Array.isArray(note.metadata) ? note.metadata : {},
      word_count: countWords(content),
      link_count: wikiLinkTargets(content).length,
      created_at: parseDate(note.createdAt, new Date()),
      updated_at: parseDate(note.updatedAt, new Date()),
    };
    const inserted = wantedId
      ? await q(`CREATE ${recordLiteral('notes', wantedId)} SET ${literalAssignments(fields).join(', ')} RETURN AFTER;`)
      : await q(`CREATE notes SET ${literalAssignments(fields).join(', ')} RETURN AFTER;`);
    const newId = recordId(inserted[0].id);
    if (sourceId) noteIdMap.set(sourceId, newId);
    imported.notes += 1;
  }

  for (const item of Array.isArray(bundle.study) ? bundle.study : []) {
    const question = String(item.question || '').trim();
    if (!question) { imported.skipped += 1; continue; }
    const noteId = item.note ? noteIdMap.get(String(item.note)) : null;
    await q(`CREATE study_item SET ${literalAssignments({
      question: question.slice(0, 2000),
      answer: String(item.answer || '').slice(0, 4000),
      box: Number(item.box || 0),
      due_at: item.dueAt ? new Date(item.dueAt) : new Date(),
      review_count: Number(item.reviewCount || 0),
      lapses: Number(item.lapses || 0),
      source: String(item.source || 'manual').slice(0, 40),
      note: noteId ? { tb: 'notes', id: noteId } : undefined,
      workspace: { tb: 'workspace', id: workspaceId },
      created_by: { tb: 'account', id: recordId(accountId) },
      created_at: new Date(),
      updated_at: new Date(),
    }).join(', ')};`);
    imported.study += 1;
  }

  for (const comment of Array.isArray(bundle.comments) ? bundle.comments : []) {
    const body = String(comment.body || '').trim();
    const noteId = comment.note ? noteIdMap.get(String(comment.note)) : null;
    if (!body && !comment.isDeleted) { imported.skipped += 1; continue; }
    if (!noteId) { imported.skipped += 1; continue; }
    await q(`CREATE note_comment SET ${literalAssignments({
      body,
      is_deleted: Boolean(comment.isDeleted),
      note: { tb: 'notes', id: noteId },
      workspace: { tb: 'workspace', id: workspaceId },
      author: comment.author ? { tb: 'account', id: String(comment.author) } : undefined,
      metadata: {},
      created_at: comment.createdAt ? new Date(comment.createdAt) : new Date(),
      updated_at: comment.updatedAt ? new Date(comment.updatedAt) : new Date(),
    }).join(', ')};`);
    imported.comments += 1;
  }

  for (const prompt of Array.isArray(bundle.prompts) ? bundle.prompts : []) {
    const title = String(prompt.title || '').trim();
    const body = String(prompt.body || '').trim();
    if (!title || !body) { imported.skipped += 1; continue; }
    // Prompt ids are global, so a taken id gets a fresh suffix rather than
    // overwriting a prompt another workspace already owns.
    const wanted = bundleSlug(prompt.id || title, 'prompt');
    const promptId = (await q('SELECT id FROM type::thing("prompt_template", $id) LIMIT 1;', { id: wanted }))[0]
      ? `${wanted}-${Math.random().toString(36).slice(2, 6)}`
      : wanted;
    await q(`CREATE ${recordLiteral('prompt_template', promptId)} SET ${literalAssignments({
      title: title.slice(0, 120),
      body: body.slice(0, 4000),
      is_system: false,
      workspace: { tb: 'workspace', id: workspaceId },
      created_at: new Date(),
    }).join(', ')};`);
    imported.prompts += 1;
  }

  // Rebuild the wiki-link edges only after every note exists, so links resolve
  // inside the imported workspace instead of pointing at the source deployment.
  const contentBySourceId = new Map((Array.isArray(bundle.notes) ? bundle.notes : []).map((note) => [String(note.id), String(note.content || '')]));
  for (const [sourceId, newId] of noteIdMap) {
    if (imported.links >= 500) break;
    const content = contentBySourceId.get(sourceId);
    if (!content) continue;
    const { resolvedCount } = await syncNoteLinks(newId, content, accountId, workspaceId);
    imported.links += resolvedCount;
  }

  await recordAudit('workspace.bundle.import', accountId, { name, notes: imported.notes }, workspaceId, workspaceId);
  return { workspaceId, name, imported };
}

app.get('/api/workspaces/:id/bundle', auth, requirePermission('settings:write'), async (req, res) => {
  const membership = (req.memberships || []).find((entry) => entry.id === req.params.id);
  if (!membership) return res.status(403).json({ error: 'You are not a member of that workspace' });
  const bundle = await buildWorkspaceBundle(req.params.id);
  await recordAudit('workspace.bundle.export', req.account.sub, { notes: bundle.notes.length }, req.params.id, req.params.id);
  res.setHeader('content-disposition', `attachment; filename="${bundleSlug(bundle.workspace.name, 'workspace')}-bundle.json"`);
  res.json(bundle);
});

app.post('/api/workspaces/import', auth, requirePermission('settings:write'), async (req, res) => {
  const bundle = req.body || {};
  if (!bundle.workspace || !Array.isArray(bundle.notes)) return res.status(400).json({ error: 'That file is not a workspace bundle' });
  if (Number(bundle.bundleVersion || 0) > bundleVersion) return res.status(400).json({ error: 'That bundle was written by a newer release' });
  if (bundle.notes.length > 5000) return res.status(400).json({ error: 'That bundle is too large to import' });
  try {
    const result = await restoreWorkspaceBundle(bundle, req.account.sub);
    // Moving a workspace is also a switch: land in the copy that just arrived.
    await q(`UPDATE type::thing("account", $id) SET active_workspace = ${recordLiteral('workspace', result.workspaceId)};`, { id: req.account.sub });
    const workspace = await findWorkspace(result.workspaceId);
    res.status(201).json({ workspace: publicWorkspaceSummary(workspace, { role: 'owner', isActive: true }), imported: result.imported });
  } catch (error) {
    res.status(500).json({ error: 'Import failed partway; the partial workspace is kept so the file can be re-imported', detail: error.message });
  }
});

// Import a previously exported JSON file. Idempotent: existing categories,
// tags, and notes are left untouched (matched by id/slug) and only missing
// records are created, so re-importing the same export never duplicates data.
/* ---------- htmx fragments: server-rendered HTML for live-refreshing lists ---------- */

const escapeFragment = (value) => String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));

// The HTML fragment routes run behind `auth` but not the JSON permission
// middleware, so the role is resolved from the same active-workspace scope the
// JSON route uses — never from the default workspace.
function requirePermissionHtml(permission) {
  return async (req, res, next) => {
    try {
      const scope = await resolveWorkspaceScope(req.account.sub);
      req.workspaceId = scope.workspaceId;
      req.workspaceRole = scope.role;
      if (!rolePermissions[scope.role]?.includes(permission)) return res.status(403).send('<p class="panel-copy">Not allowed.</p>');
      next();
    } catch (error) {
      res.status(503).send(`<p class="panel-copy">${escapeFragment(error.message)}</p>`);
    }
  };
}

app.get('/fragments/audit', auth, requirePermissionHtml('settings:write'), async (req, res) => {
  const rows = await q(`SELECT * FROM audit_event WHERE workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT 30;`);
  res.send(rows.length
    ? rows.map((row) => `<div class="audit-row"><code>${escapeFragment(row.action)}</code><span>${escapeFragment(row.actor ? recordId(row.actor) : '—')}</span>${row.target ? `<code>${escapeFragment(row.target)}</code>` : ''}<time>${escapeFragment(row.created_at instanceof Date ? row.created_at.toISOString().slice(0, 16).replace('T', ' ') : '')}</time></div>`).join('')
    : '<p class="panel-copy">No activity recorded yet.</p>');
});

app.get('/fragments/members', auth, requirePermissionHtml('members:write'), async (_req, res) => {
  const rows = await q('SELECT id, name, role FROM account ORDER BY created_at ASC;');
  res.send(rows.map((row) => `<article class="member-row"><span class="avatar">${escapeFragment(String(row.name).slice(0, 1).toUpperCase())}</span><span class="member-identity"><strong>${escapeFragment(row.name)}</strong><small>${escapeFragment(row.role)}</small></span></article>`).join(''));
});

/* ---------- AI providers, chat, and prompt templates ---------- */

app.get('/api/providers', auth, requirePermission('settings:write'), async (_req, res) => {
  const rows = await q('SELECT * FROM ai_provider ORDER BY created_at ASC;');
  res.json(rows.map(publicProvider));
});

async function deactivateProviders(exceptId = null) {
  if (exceptId) await q('UPDATE ai_provider SET is_active = false WHERE id != type::thing("ai_provider", $id) AND is_active = true;', { id: exceptId });
  else await q('UPDATE ai_provider SET is_active = false WHERE is_active = true;');
}

app.post('/api/providers', auth, requirePermission('settings:write'), async (req, res) => {
  const name = String(req.body.name || '').trim().slice(0, 60);
  const kind = ['openai-compatible'].includes(String(req.body.kind)) ? String(req.body.kind) : 'openai-compatible';
  const baseUrl = String(req.body.baseUrl || '').trim();
  const apiKey = String(req.body.apiKey || '').trim();
  const model = String(req.body.model || '').trim().slice(0, 120);
  if (!name || !baseUrl || !model) return res.status(400).json({ error: 'Name, base URL, and model are required' });
  if (!/^https?:\/\//.test(baseUrl)) return res.status(400).json({ error: 'Base URL must start with http(s)://' });
  try {
    const existing = await q('SELECT * FROM type::thing("ai_provider", $name) LIMIT 1;', { name });
    if (existing[0]) {
      const merged = { kind, base_url: baseUrl, model };
      if (apiKey) merged.api_key = apiKey; // empty key keeps the stored one
      const rows = await q('UPDATE type::thing("ai_provider", $name) MERGE $data RETURN AFTER;', { name, data: merged });
      if (req.body.activate) await deactivateProviders(name);
      if (req.body.activate) await q('UPDATE type::thing("ai_provider", $name) MERGE { is_active: true };', { name });
      return res.json(publicProvider(rows[0]));
    }
    const rows = await q('CREATE type::thing("ai_provider", $name) CONTENT $data RETURN AFTER;', {
      name,
      data: { name, kind, base_url: baseUrl, api_key: apiKey, model, is_active: Boolean(req.body.activate), created_at: new Date() },
    });
    if (req.body.activate) await deactivateProviders(name);
    await recordAudit('provider.save', req.account.sub, { name, model }, name);
    res.status(201).json(publicProvider(rows[0]));
  } catch (error) {
    res.status(500).json({ error: 'Could not save provider', detail: error.message });
  }
});

app.patch('/api/providers/:name/active', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ai_provider", $name) LIMIT 1;', { name: req.params.name });
  if (!rows[0]) return res.status(404).json({ error: 'Provider not found' });
  await deactivateProviders(req.params.name);
  await q('UPDATE type::thing("ai_provider", $name) MERGE { is_active: true };', { name: req.params.name });
  await recordAudit('provider.activate', req.account.sub, { name: req.params.name }, req.params.name);
  res.json(publicProvider((await q('SELECT * FROM type::thing("ai_provider", $name) LIMIT 1;', { name: req.params.name }))[0]));
});

app.delete('/api/providers/:name', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ai_provider", $name) LIMIT 1;', { name: req.params.name });
  if (!rows[0]) return res.status(404).json({ error: 'Provider not found' });
  await q('DELETE type::thing("ai_provider", $name);', { name: req.params.name });
  await recordAudit('provider.delete', req.account.sub, { name: req.params.name }, req.params.name);
  res.status(204).end();
});

// Verify a provider by calling /models on its base URL with its stored key.
app.post('/api/providers/:name/verify', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("ai_provider", $name) LIMIT 1;', { name: req.params.name });
  const provider = rows[0];
  if (!provider) return res.status(404).json({ error: 'Provider not found' });
  try {
    const response = await fetch(new URL('models', provider.base_url.endsWith('/') ? provider.base_url : provider.base_url + '/'), {
      headers: { authorization: `Bearer ${provider.api_key}` },
      signal: AbortSignal.timeout(8000),
    });
    res.json({ ok: response.ok, status: response.status });
  } catch (error) {
    res.json({ ok: false, status: 0, detail: error.message });
  }
});

/* ---------- chat context: project and document directories ---------- */

// The roots a member may browse and hand to a chat. Only configuration can add
// a root; the client picks from this list.
app.get('/api/context/roots', auth, async (req, res) => {
  const workspace = await findWorkspace(req.workspaceId);
  res.json(contextRootsForWorkspace(workspace).map(publicContextRoot));
});

// A root that the workspace has not enabled behaves exactly like an unknown
// root, so a guessed id cannot reach a directory the workspace cannot use.
async function rootInWorkspace(req, rootId) {
  const workspace = await findWorkspace(req.workspaceId);
  const enabled = contextRootsForWorkspace(workspace).map((root) => root.id);
  if (!enabled.includes(rootId)) return null;
  return contextRoot(rootId);
}

app.get('/api/context/roots/:root/tree', auth, async (req, res) => {
  const root = await rootInWorkspace(req, req.params.root);
  if (!root) return res.status(404).json({ error: 'Unknown context root' });
  const resolved = resolveContextPath(root, req.query.path);
  if (!resolved) return res.status(400).json({ error: 'That path is outside the context root' });
  let stat;
  try { stat = fs.statSync(resolved.abs); } catch { return res.status(404).json({ error: 'Folder not found' }); }
  if (!stat.isDirectory()) return res.status(400).json({ error: 'That path is not a folder' });
  let entries;
  try { entries = listContextDir(root, resolved); } catch { return res.status(403).json({ error: 'That folder cannot be read' }); }
  res.json({ root: publicContextRoot(root), path: resolved.relative, entries });
});

app.get('/api/context/roots/:root/file', auth, async (req, res) => {
  const root = await rootInWorkspace(req, req.params.root);
  if (!root) return res.status(404).json({ error: 'Unknown context root' });
  const resolved = resolveContextPath(root, req.query.path);
  if (!resolved) return res.status(400).json({ error: 'That path is outside the context root' });
  const file = readContextFile(`${root.id}:${resolved.relative}`);
  if (!file) return res.status(415).json({ error: 'Only text, PDF, and image files can be read as context' });
  // The data URL stays server-side: the browser previews text and PDF text, and
  // never needs the base64 payload that only the provider call consumes.
  const { dataUrl, ...rest } = file;
  res.json({ ...rest, hasImage: Boolean(dataUrl) });
});

// Writing is limited to the writable roots (documents, notes) so a task can
// produce an artifact next to the material it was given.
app.post('/api/context/roots/:root/file', auth, requirePermission('notes:write'), async (req, res) => {
  const root = await rootInWorkspace(req, req.params.root);
  if (!root) return res.status(404).json({ error: 'Unknown context root' });
  if (!root.writable) return res.status(403).json({ error: 'That context root is read-only' });
  const content = String(req.body?.content ?? '');
  if (Buffer.byteLength(content) > maxContextBytes) return res.status(413).json({ error: 'That file is larger than the context limit' });
  const resolved = resolveContextPath(root, req.body?.path);
  if (!resolved) return res.status(400).json({ error: 'That path is outside the context root' });
  // Only text can be written through JSON: PDFs and images arrive as uploads,
  // so a binary name here would store a corrupt file.
  if (contextFileKind(path.basename(resolved.abs)) !== 'text') return res.status(415).json({ error: 'Only text and markdown files can be written here' });
  fs.mkdirSync(path.dirname(resolved.abs), { recursive: true });
  fs.writeFileSync(resolved.abs, content);
  await recordAudit('context.file.write', req.account.sub, { root: root.id, path: resolved.relative, bytes: Buffer.byteLength(content) }, null);
  res.status(201).json({ ref: `${root.id}:${resolved.relative}`, name: path.basename(resolved.abs), path: resolved.relative, size: Buffer.byteLength(content) });
});

// Attach (or clear) the set of context files a chat sends with every message.
app.patch('/api/chat/sessions/:id/context', auth, requirePermission('notes:read'), async (req, res) => {
  const sessionRows = await q(`SELECT * FROM type::thing("chat_session", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const session = sessionRows[0];
  if (!session) return res.status(404).json({ error: 'Session not found' });
  if (recordId(session.created_by) !== recordId(req.account.sub)) return res.status(403).json({ error: 'This chat belongs to another member' });
  const refs = sanitizeContextRefs(req.body?.files, contextRootsForWorkspace(await findWorkspace(req.workspaceId)).map((root) => root.id));
  const rows = await q(`UPDATE type::thing("chat_session", $id) SET context_files = ${inlineValue(refs)} RETURN AFTER;`, { id: req.params.id });
  await recordAudit('chat.context', req.account.sub, { session: recordId(session.id), files: refs.length }, recordId(session.id));
  res.json({ ...publicSession(rows[0] || session), contextFiles: refs, rejected: Array.isArray(req.body?.files) ? req.body.files.length - refs.length : 0 });
});

// Built-in prompts are shared by every workspace; custom prompts belong to the
// workspace that wrote them.
app.get('/api/prompts', auth, async (req, res) => {
  const rows = await q(`SELECT * FROM prompt_template WHERE is_system = true OR workspace = ${wsLiteral(req)} ORDER BY is_system DESC, title ASC;`);
  res.json(rows.map(publicPrompt));
});

app.post('/api/prompts', auth, requirePermission('settings:write'), async (req, res) => {
  const id = String(req.body.id || '').trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);
  const title = String(req.body.title || '').trim().slice(0, 80);
  const body = String(req.body.body || '').trim().slice(0, 2000);
  if (!id || !title || !body) return res.status(400).json({ error: 'Title and prompt text are required' });
  const existing = await q('SELECT id FROM type::thing("prompt_template", $id) LIMIT 1;', { id });
  if (existing[0]) return res.status(409).json({ error: 'A prompt with that id already exists' });
  const rows = await q(`CREATE ${recordLiteral('prompt_template', id)} SET ${literalAssignments({ title, body, is_system: false, workspace: { tb: 'workspace', id: req.workspaceId }, created_at: new Date() }).join(', ')};`);
  res.status(201).json(publicPrompt(rows[0]));
});

app.patch('/api/prompts/:id', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("prompt_template", $id) LIMIT 1;', { id: req.params.id });
  const prompt = rows[0];
  if (!prompt) return res.status(404).json({ error: 'Prompt not found' });
  if (prompt.is_system) return res.status(400).json({ error: 'Built-in prompts are read-only — duplicate one to edit it' });
  if (prompt.workspace && recordId(prompt.workspace) !== req.workspaceId) return res.status(403).json({ error: 'That prompt belongs to another workspace' });
  const title = String(req.body?.title || '').trim().slice(0, 80);
  const body = String(req.body?.body || '').trim().slice(0, 2000);
  if (!title || !body) return res.status(400).json({ error: 'Title and prompt text are required' });
  const updated = await q(`UPDATE type::thing("prompt_template", $id) SET title = ${inlineValue(title)}, body = ${inlineValue(body)} RETURN AFTER;`, { id: req.params.id });
  res.json(publicPrompt(updated[0] || prompt));
});

app.delete('/api/prompts/:id', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("prompt_template", $id) LIMIT 1;', { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Prompt not found' });
  if (rows[0].is_system) return res.status(400).json({ error: 'Built-in prompts cannot be deleted' });
  if (rows[0].workspace && recordId(rows[0].workspace) !== req.workspaceId) return res.status(403).json({ error: 'That prompt belongs to another workspace' });
  await q('DELETE type::thing("prompt_template", $id);', { id: req.params.id });
  res.status(204).end();
});

app.get('/api/chat/sessions', auth, async (req, res) => {
  const rows = await q(`SELECT * FROM chat_session WHERE created_by = type::thing("account", $id) AND workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT 50;`, { id: req.account.sub });
  res.json(rows.map(publicSession));
});

app.post('/api/chat/sessions', auth, async (req, res) => {
  const title = String(req.body.title || 'New chat').trim().slice(0, 80) || 'New chat';
  const promptId = req.body.promptId ? String(req.body.promptId).slice(0, 60) : null;
  const { provider } = await resolveProviderForWorkspace(req.workspaceId);
  // option<record> fields reject an explicit null in schemafull mode, so the
  // provider link is only included when one is resolvable.
  const sessionData = {
    title,
    created_by: new RecordId('account', recordId(req.account.sub)),
    workspace: new RecordId('workspace', req.workspaceId),
    created_at: new Date(),
  };
  if (promptId) sessionData.prompt_id = promptId;
  if (provider) sessionData.provider = new RecordId('ai_provider', recordId(provider.id));
  const rows = await q('CREATE chat_session CONTENT $data;', { data: sessionData });
  res.status(201).json({ ...publicSession(rows[0]), messages: [] });
});

// AI policy for the active workspace, with the provider names resolved for the
// client (the picker shows every active provider and which ones are allowed).
app.get('/api/ai/policy', auth, requirePermission('settings:write'), async (req, res) => {
  const [workspace, all, capInfo, budgetInfo, usage] = await Promise.all([
    findWorkspace(req.workspaceId),
    q('SELECT id, name, model, is_active FROM ai_provider;'),
    aiCapForWorkspace(req.workspaceId),
    aiBudgetForWorkspace(req.workspaceId),
    aiUsageSummary(req.workspaceId),
  ]);
  const policy = aiPolicyFor(workspace);
  res.json({
    ...policy,
    providers: all.map((row) => ({
      id: recordId(row.id),
      name: row.name,
      model: row.model,
      isActive: Boolean(row.is_active),
      allowed: !policy.allowedProviders.length || policy.allowedProviders.includes(recordId(row.id)),
    })),
    cap: capInfo,
    budget: budgetInfo,
    usage,
  });
});

app.patch('/api/ai/policy', auth, requirePermission('settings:write'), async (req, res) => {
  const updates = {};
  if (req.body.allowedProviders !== undefined) {
    if (!Array.isArray(req.body.allowedProviders)) return res.status(400).json({ error: 'allowedProviders must be an array' });
    updates.ai_allowed_providers = req.body.allowedProviders.map((value) => String(value).slice(0, 80)).slice(0, 50);
  }
  if (req.body.defaultProvider !== undefined) {
    const value = req.body.defaultProvider === null ? null : String(req.body.defaultProvider).slice(0, 80);
    if (value) {
      const exists = (await q('SELECT id FROM ai_provider WHERE id = type::thing("ai_provider", $name) LIMIT 1;', { name: value }))[0];
      if (!exists) return res.status(400).json({ error: 'Unknown provider' });
      updates.ai_default_provider = value;
    } else {
      // option<...> fields reject explicit nulls; SET = NONE drops the field
      // (SurrealDB 1.x has no UPDATE ... REMOVE clause).
      await q('UPDATE type::thing("workspace", $id) SET ai_default_provider = NONE;', { id: req.workspaceId });
    }
  }
  if (req.body.runCap !== undefined) {
    const cap = Number(req.body.runCap);
    if (req.body.runCap !== null && (!Number.isFinite(cap) || cap < 1 || cap > 100000)) return res.status(400).json({ error: 'runCap must be a number between 1 and 100000' });
    if (req.body.runCap === null) await q('UPDATE type::thing("workspace", $id) SET ai_run_cap = NONE;', { id: req.workspaceId });
    else updates.ai_run_cap = Math.round(cap);
  }
  if (req.body.monthlyBudgetMicros !== undefined) {
    const budget = Number(req.body.monthlyBudgetMicros);
    if (req.body.monthlyBudgetMicros === null) await q('UPDATE type::thing("workspace", $id) SET ai_monthly_budget_micros = NONE;', { id: req.workspaceId });
    else {
      if (!Number.isFinite(budget) || budget < 0 || budget > 1e12) return res.status(400).json({ error: 'monthlyBudgetMicros must be between 0 and 1e12' });
      updates.ai_monthly_budget_micros = Math.round(budget);
    }
  }
  if (Object.keys(updates).length) {
    await q(`UPDATE type::thing("workspace", $id) SET ${literalAssignments(updates).join(', ')};`, { id: req.workspaceId });
  }
  await recordAudit('ai.policy', req.account.sub, { allowed: updates.ai_allowed_providers?.length, cap: updates.ai_run_cap ?? null }, null, req.workspaceId);
  const [workspace, all] = await Promise.all([
    findWorkspace(req.workspaceId),
    q('SELECT id, name, model, is_active FROM ai_provider;'),
  ]);
  const policy = aiPolicyFor(workspace);
  res.json({
    ...policy,
    providers: all.map((row) => ({
      id: recordId(row.id),
      name: row.name,
      model: row.model,
      isActive: Boolean(row.is_active),
      allowed: !policy.allowedProviders.length || policy.allowedProviders.includes(recordId(row.id)),
    })),
  });
});

// Per-provider usage totals for the ledger: calls, tokens, and estimated cost
// by provider + model, so spend can be compared across providers.
app.get('/api/ai/usage', auth, requirePermission('settings:write'), async (req, res) => {
  res.json(await aiUsageSummary(req.workspaceId));
});

// Queued AI runs. Members with notes:write may enqueue; jobs run through the
// same policy + cap path as direct calls (the worker resolves the provider
// through the workspace).
app.get('/api/ai/jobs', auth, async (req, res) => {
  const rows = await q(`SELECT * FROM ai_job WHERE workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT 50;`);
  res.json(rows.map(publicAiJob));
});

app.post('/api/ai/jobs', auth, requirePermission('notes:write'), async (req, res) => {
  const kind = String(req.body?.kind || '').trim();
  if (!['study.generate', 'summarize.note'].includes(kind)) return res.status(400).json({ error: 'Unknown job kind' });
  const noteId = String(req.body?.noteId || '').trim();
  const attachmentId = String(req.body?.attachmentId || '').trim();
  if (kind === 'study.generate' && !noteId) return res.status(400).json({ error: 'noteId is required' });
  if (kind === 'summarize.note' && !noteId && !attachmentId) return res.status(400).json({ error: 'noteId or attachmentId is required' });
  if (noteId) {
    const noteRows = await q(`SELECT id FROM type::thing("notes", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: noteId });
    if (!noteRows[0]) return res.status(404).json({ error: 'Note not found' });
  }
  if (attachmentId) {
    const attachmentRows = await q('SELECT id, text_status FROM type::thing("attachments", $id) LIMIT 1;', { id: attachmentId });
    if (!attachmentRows[0]) return res.status(404).json({ error: 'Attachment not found' });
    if (attachmentRows[0].text_status !== 'ready') return res.status(400).json({ error: 'That attachment has no extracted text to summarize' });
  }
  const maxAttempts = Math.min(Math.max(Number(req.body?.maxAttempts) || 3, 1), 5);
  // Optional schedule: an ISO runAt pushes first execution up to an hour out,
  // which also gives clients a deterministic way to keep a queued job queued.
  let runAt = null;
  if (req.body?.runAt) {
    const parsed = new Date(req.body.runAt);
    if (Number.isNaN(parsed.getTime())) return res.status(400).json({ error: 'runAt must be an ISO date' });
    const delta = parsed.getTime() - Date.now();
    if (delta < -5000) return res.status(400).json({ error: 'runAt is in the past' });
    if (delta > 60 * 60_000) return res.status(400).json({ error: 'runAt may be at most one hour ahead' });
    runAt = parsed;
  }
  // Idempotency: a caller key wins; otherwise the key is derived from the
  // operation identity. An existing queued/running job with the same key is
  // returned instead of queueing duplicate provider work.
  const idempotencyKey = req.body?.idempotencyKey ? String(req.body.idempotencyKey).slice(0, 64) : null;
  const guard = await aiGuardForWorkspace(req.workspaceId);
  if (guard.blocked) return res.status(guard.status).json(guard.body);
  const { job, created } = await createAiJob({
    workspaceId: req.workspaceId,
    kind,
    payload: kind === 'study.generate'
      ? { noteId, promptId: req.body?.promptId ? String(req.body.promptId).slice(0, 60) : 'flashcards' }
      : { noteId: noteId || null, attachmentId: attachmentId || null, style: String(req.body?.style || 'study').slice(0, 40) },
    accountId: req.account.sub,
    maxAttempts,
    idempotencyKey,
    runAt,
  });
  if (created) await recordAudit('ai_job.queued', req.account.sub, { kind, note: noteId || null, attachment: attachmentId || null }, recordId(job.id), req.workspaceId);
  res.status(created ? 201 : 200).json({ ...publicAiJob(job), created });
});

// Cancelling is only possible before the worker picks the job up: a running
// call is left to finish (the provider has already been asked), and a finished
// job is history, not a control point.
app.post('/api/ai/jobs/:id/cancel', auth, async (req, res) => {
  const rows = await q(`SELECT * FROM type::thing("ai_job", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const job = rows[0];
  if (!job) return res.status(404).json({ error: 'Job not found' });
  const isRequester = job.requested_by && recordId(job.requested_by) === recordId(req.account.sub);
  const isManager = ['owner', 'admin', 'superadmin'].includes(req.workspaceRole);
  if (!isRequester && !isManager) return res.status(403).json({ error: 'Only the requester or a workspace admin can cancel this job' });
  if (job.status !== 'queued') return res.status(409).json({ error: `A ${job.status} job cannot be cancelled` });
  const cancelled = await q(
    // SET form (not MERGE) so the <string>id reference is evaluated: the key
    // is released with the same per-row marker the worker's finishJob uses.
    `UPDATE type::thing("ai_job", $id) SET status = 'cancelled', finished_at = time::now(), updated_at = time::now(), idempotency_key = string::concat('released:', <string>id) WHERE status = 'queued' RETURN AFTER;`,
    { id: req.params.id },
  );
  if (!cancelled[0]) return res.status(409).json({ error: 'The job already started running' });
  await recordAudit('ai_job.cancelled', req.account.sub, { kind: job.kind }, recordId(job.id), req.workspaceId);
  res.json(publicAiJob(cancelled[0]));
});

// The AI run ledger for this workspace: who ran what, against which provider,
// and what it cost in latency. newest first.
app.get('/api/ai/runs', auth, requirePermission('settings:write'), async (req, res) => {
  const limit = Math.min(Math.max(Number(req.query.limit) || 50, 1), 200);
  const rows = await q(`SELECT * FROM ai_run WHERE workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT ${limit};`);
  const accountIds = [...new Set(rows.map((row) => row.account ? recordId(row.account) : null).filter(Boolean))];
  const names = await accountNames(accountIds);
  res.json(rows.map((row) => ({
    id: recordId(row.id),
    feature: row.feature,
    status: row.status,
    model: row.model || null,
    provider: row.provider ? recordId(row.provider) : null,
    promptChars: Number(row.prompt_chars || 0),
    responseChars: Number(row.response_chars || 0),
    durationMs: Number(row.duration_ms || 0),
    promptTokens: Number(row.prompt_tokens || 0),
    completionTokens: Number(row.completion_tokens || 0),
    totalTokens: Number(row.total_tokens || 0),
    costMicros: Number(row.cost_micros || 0),
    costCurrency: row.cost_currency || null,
    error: row.error_message || null,
    account: row.account ? recordId(row.account) : null,
    accountName: row.account ? names.get(recordId(row.account)) || null : null,
    session: row.session ? recordId(row.session) : null,
    job: row.job ? recordId(row.job) : null,
    attempt: Number(row.attempt || 0),
    note: row.note ? recordId(row.note) : null,
    createdAt: isoOrNull(row.created_at),
  })));
});

app.get('/api/chat/sessions/:id', auth, async (req, res) => {
  const sessionRows = await q(`SELECT * FROM type::thing("chat_session", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const session = sessionRows[0];
  if (!session) return res.status(404).json({ error: 'Session not found' });
  if (recordId(session.created_by) !== recordId(req.account.sub) && !req.account.permissions?.includes('settings:write')) {
    return res.status(403).json({ error: 'This chat belongs to another member' });
  }
  const messages = await q('SELECT * FROM chat_message WHERE session = type::thing("chat_session", $id) ORDER BY created_at ASC;', { id: req.params.id });
  res.json({ ...publicSession(session), messages: messages.map(publicMessage) });
});

// Resolve the provider a workspace may use: the workspace default, the
// session's pinned provider, or the instance's active one — always filtered
// through the workspace policy, so a disabled provider is unreachable even
// when a session still points at it.
async function resolveProviderForWorkspace(workspaceId, { pinned = null } = {}) {
  const [workspaceRows, activeRows] = await Promise.all([
    findWorkspace(workspaceId),
    q('SELECT * FROM ai_provider WHERE is_active = true;'),
  ]);
  const workspace = workspaceRows;
  const active = activeRows;
  if (!active.length) return { provider: null, workspace: aiPolicyFor(workspace || {}) };
  const policy = aiPolicyFor(workspace || {});
  const byName = (name) => active.find((row) => recordId(row.id) === String(name));
  const allowed = policy.allowedProviders.length ? active.filter((row) => policy.allowedProviders.includes(recordId(row.id))) : active;
  const candidates = [];
  if (pinned) candidates.push(byName(pinned));
  if (policy.defaultProvider) candidates.push(byName(policy.defaultProvider));
  candidates.push(active.find((row) => row.is_active));
  for (const candidate of candidates) {
    if (candidate && allowed.includes(candidate)) return { provider: candidate, workspace: policy };
  }
  // Every candidate fell outside the allow-list; fall back to any allowed one.
  const fallback = allowed[0] || null;
  return { provider: fallback, workspace: policy };
}

// Call the provider and return { content, usage }: usage is the standard
// OpenAI token report when the provider sends one, else estimated from text
// length (~4 chars/token), so accounting works against every endpoint.
async function callProvider(provider, messages, model) {
  const response = await fetch(new URL('chat/completions', provider.base_url.endsWith('/') ? provider.base_url : provider.base_url + '/'), {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${provider.api_key}` },
    body: JSON.stringify({ model: model || provider.model, messages, temperature: 0.4 }),
    signal: AbortSignal.timeout(30000),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body?.error?.message || body?.error || `Provider returned ${response.status}`;
    const error = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    error.statusCode = 502;
    throw error;
  }
  const content = body?.choices?.[0]?.message?.content;
  if (!content) throw Object.assign(new Error('Provider returned no content'), { statusCode: 502 });
  const reported = body?.usage || null;
  const usage = {
    promptTokens: Math.max(0, Math.round(Number(reported?.prompt_tokens) || 0)) || Math.round(JSON.stringify(messages).length / 4),
    completionTokens: Math.max(0, Math.round(Number(reported?.completion_tokens) || 0)) || Math.round(String(content).length / 4),
  };
  usage.totalTokens = Math.max(0, Math.round(Number(reported?.total_tokens) || 0)) || usage.promptTokens + usage.completionTokens;
  return { content, usage };
}

app.post('/api/chat/sessions/:id/messages', auth, async (req, res) => {
  const sessionRows = await q(`SELECT * FROM type::thing("chat_session", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const session = sessionRows[0];
  if (!session) return res.status(404).json({ error: 'Session not found' });
  if (recordId(session.created_by) !== recordId(req.account.sub)) return res.status(403).json({ error: 'This chat belongs to another member' });
  const content = String(req.body.content || '').trim().slice(0, 8000);
  if (!content) return res.status(400).json({ error: 'Message content is required' });
  const promptId = req.body.promptId ? String(req.body.promptId).slice(0, 60) : session.prompt_id || null;
  // Context files attached to the chat (or overridden for this one message) are
  // read server-side and injected as a read-only block, so the browser only
  // ever names files that this server already exposes.
  const allowedRoots = contextRootsForWorkspace(await findWorkspace(req.workspaceId)).map((root) => root.id);
  const contextFiles = req.body.contextFiles === undefined
    ? sanitizeContextRefs(session.context_files, allowedRoots)
    : sanitizeContextRefs(req.body.contextFiles, allowedRoots);

  // option<...> fields reject an explicit null in schemafull mode, so the
  // prompt link is only written when a prompt style is actually selected.
  const userData = { session: new RecordId('chat_session', recordId(session.id)), role: 'user', content, created_at: new Date() };
  if (promptId) userData.prompt_id = promptId;
  const userMessage = await q('CREATE chat_message CONTENT $data;', { data: userData });

  const history = await q('SELECT * FROM chat_message WHERE session = type::thing("chat_session", $id) ORDER BY created_at ASC LIMIT 40;', { id: recordId(session.id) });
  // The workspace policy decides which provider may answer: a pinned or
  // default provider outside the allow-list is skipped like a missing one.
  const { provider } = await resolveProviderForWorkspace(req.workspaceId, { pinned: session.provider ? recordId(session.provider) : null });
  // Cap and monthly budget are checked before the user message is persisted,
  // so a refused call leaves no half-written turn in the session.
  if (provider) {
    const guard = await aiGuardForWorkspace(req.workspaceId);
    if (guard.blocked) return res.status(guard.status).json(guard.body);
  }

  let assistant;
  if (!provider) {
    assistant = await q('CREATE chat_message CONTENT $data;', {
      data: { session: new RecordId('chat_session', recordId(session.id)), role: 'assistant', content: 'No active AI provider is configured. Add one in Settings → AI, then retry.', error: true, created_at: new Date() },
    });
  } else {
    const started = Date.now();
    const runRow = await beginAiRun({
      workspaceId: req.workspaceId,
      provider: recordId(provider.id),
      model: provider.model,
      feature: 'chat',
      accountId: req.account.sub,
      sessionId: recordId(session.id),
    });
    try {
      const promptRows = promptId ? await q('SELECT * FROM type::thing("prompt_template", $id) LIMIT 1;', { id: promptId }) : [];
      const aiContextRows = await q(`SELECT ai_context FROM ${wsLiteral(req)} LIMIT 1;`);
      const systemParts = [];
      if (promptRows[0]?.body) systemParts.push(promptRows[0].body);
      if (aiContextRows[0]?.ai_context) systemParts.push(aiContextRows[0].ai_context);
      const context = buildContextBlock(contextFiles);
      if (context.text) systemParts.push(context.text);
      // Images ride on the current user turn as multimodal parts; earlier turns
      // stay plain text so the conversation history does not re-send them.
      const imageParts = context.images.map((image) => ({ type: 'image_url', image_url: { url: image.dataUrl } }));
      const turns = history.map((row, index) => {
        const isUser = row.role !== 'assistant';
        const isCurrent = index === history.length - 1 && isUser;
        if (isCurrent && imageParts.length) {
          return { role: 'user', content: [{ type: 'text', text: row.content }, ...imageParts] };
        }
        return { role: isUser ? 'user' : 'assistant', content: row.content };
      });
      const promptPayload = JSON.stringify([
        ...(systemParts.length ? [{ role: 'system', content: systemParts.join('\n\n') }] : []),
        ...turns,
      ]);
      const { content: reply, usage } = await callProvider(provider, JSON.parse(promptPayload), provider.model);
      await completeAiRun(runRow, { reply, usage, startedAt: started });
      assistant = await q('CREATE chat_message CONTENT $data;', {
        data: { session: new RecordId('chat_session', recordId(session.id)), role: 'assistant', content: reply, model: provider.model, created_at: new Date() },
      });
    } catch (error) {
      await completeAiRun(runRow, { error: error.message, startedAt: started });
      assistant = await q('CREATE chat_message CONTENT $data;', {
        data: { session: new RecordId('chat_session', recordId(session.id)), role: 'assistant', content: `Provider error: ${error.message}`, error: true, created_at: new Date() },
      });
    }
  }
  await recordAudit('chat.message', req.account.sub, { session: recordId(session.id), context: contextFiles.length }, recordId(session.id));
  res.status(201).json({ user: publicMessage(userMessage[0]), assistant: publicMessage(assistant[0]), contextFiles });
});

app.delete('/api/chat/sessions/:id', auth, async (req, res) => {
  const sessionRows = await q(`SELECT * FROM type::thing("chat_session", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const session = sessionRows[0];
  if (!session) return res.status(404).json({ error: 'Session not found' });
  if (recordId(session.created_by) !== recordId(req.account.sub) && !req.account.permissions?.includes('settings:write')) {
    return res.status(403).json({ error: 'This chat belongs to another member' });
  }
  await q('DELETE chat_message WHERE session = type::thing("chat_session", $id);', { id: req.params.id });
  await q('DELETE type::thing("chat_session", $id);', { id: req.params.id });
  res.status(204).end();
});

// Shared idempotent import core: existing categories (by slug), tags, and
// notes (by id) are skipped; only missing records are created, so re-running
// the same payload never duplicates data. Used by the JSON import endpoint
// and the sample-content loader.
// `overwrite` refreshes notes that already exist at the given id instead of
// skipping them. Only the curated sample loader uses it (its ids are owned by
// the app), so a user's own JSON import can never be silently rewritten.
async function applyImport(body, accountSub, { overwrite = false, workspaceId = 'default' } = {}) {
  const created = { categories: 0, tags: 0, notes: 0, updated: 0, skipped: 0 };
  const seedLane = (slug, name) => q(`CREATE ${recordLiteral('category', slug)} SET ${literalAssignments({
    name, slug, color: '#7c3aed', icon: '📁', is_system: false, is_default: false,
    workspace: { tb: 'workspace', id: workspaceId }, sort_order: 0, created_at: new Date(), updated_at: new Date(),
  }).join(', ')};`);
  try {
    for (const raw of body.categories) {
      const slug = String(raw.slug || '').trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);
      const name = String(raw.name || '').trim().slice(0, 80);
      if (!slug || !name) { created.skipped++; continue; }
      const existing = await findCategory(slug, workspaceId);
      if (existing) continue;
      const color = /^#[0-9a-fA-F]{6}$/.test(String(raw.color || '')) ? String(raw.color) : '#7c3aed';
      const icon = String(raw.icon || '📁').slice(0, 2) || '📁';
      // Imported lanes always land in the importing workspace, and only the
      // default workspace may reuse the readable `category:<slug>` ids.
      if (workspaceId === 'default') await seedLane(slug, name);
      else await q(`CREATE category SET ${literalAssignments({
        name, slug, color, icon, is_system: false, is_default: false,
        workspace: { tb: 'workspace', id: workspaceId }, sort_order: 0, created_at: new Date(), updated_at: new Date(),
      }).join(', ')};`);
      created.categories++;
    }
    for (const note of body.notes) {
      const id = String(note.id || '').trim().replace(/[⟨⟩]/g, '');
      const content = String(note.content || '').trim();
      if (!id || !content) { created.skipped++; continue; }
      const categorySlug = note.category?.slug ? String(note.category.slug) : String(note.category || 'notes');
      const categoryRow = await findCategory(categorySlug, workspaceId) || await findCategory('notes', workspaceId);
      if (!categoryRow) { created.skipped++; continue; }
      const existingNote = await q('SELECT id FROM type::thing("notes", $id) LIMIT 1;', { id });
      if (existingNote[0] && !overwrite) { created.skipped++; continue; }
      const tagIds = await ensureTags(Array.isArray(note.tags) ? note.tags.map((tag) => (typeof tag === 'string' ? tag : tag?.name)) : [], workspaceId);
      created.tags += tagIds.length;
      const parseDate = (value, fallback) => {
        const parsed = value ? new Date(value) : null;
        return parsed && !Number.isNaN(parsed.getTime()) ? parsed : fallback;
      };
      const fields = {
        content,
        category: new RecordId('category', recordId(categoryRow.id)),
        account: new RecordId('account', recordId(accountSub)),
        created_by: new RecordId('account', recordId(accountSub)),
        workspace: new RecordId('workspace', workspaceId),
        tags: tagIds,
        is_archived: Boolean(note.isArchived),
        is_recycle: Boolean(note.isRecycle),
        is_top: Boolean(note.isTop),
        is_share: Boolean(note.isShare),
        status: ['backlog', 'todo', 'doing', 'review', 'done'].includes(String(note.status)) ? String(note.status) : 'todo',
        priority: ['low', 'medium', 'high', 'urgent'].includes(String(note.priority)) ? String(note.priority) : 'medium',
        position: Number(note.position) || 0,
        due_date: parseDate(note.dueDate, null),
        start_date: parseDate(note.startDate, null),
        end_date: parseDate(note.endDate, null),
        event_color: note.eventColor ? String(note.eventColor).slice(0, 32) : null,
        metadata: note.metadata && typeof note.metadata === 'object' && !Array.isArray(note.metadata) ? note.metadata : {},
        word_count: countWords(content),
        link_count: wikiLinkTargets(content).length,
        created_at: parseDate(note.createdAt, new Date()),
        updated_at: parseDate(note.updatedAt, new Date()),
      };
      const recordKey = `:⟨${String(id).replace(/[^A-Za-z0-9_-]+/g, '_')}⟩`;
      if (existingNote[0]) {
        // Keep the original authorship/timestamp; refresh presentation fields so
        // re-loading the curated set reflects the current source content.
        // Inline SET assignments (not MERGE $data) are required here: binding
        // the object as a parameter sends SQL NULL for absent dates, which
        // option<datetime> fields reject. Inlined through inlineValue, null
        // becomes NONE — the correct "clear this optional" value.
        const refresh = { ...fields };
        delete refresh.created_at;
        delete refresh.created_by;
        const refreshAssignments = Object.entries(refresh)
          .map(([key, value]) => `${key} = ${inlineValue(value)}`);
        await q(`UPDATE type::thing('notes', $id) SET ${refreshAssignments.join(', ')};`, { id });
        created.updated++;
      } else {
        await createRecord('notes', fields, recordKey);
        created.notes++;
      }
    }
    return { created, error: null };
  } catch (error) {
    return { created, error };
  }
}

// Import a previously exported JSON file. Idempotent (see applyImport).
app.post('/api/import', auth, requirePermission('settings:write'), async (req, res) => {
  const body = req.body || {};
  if (!Array.isArray(body.categories) || !Array.isArray(body.notes)) {
    return res.status(400).json({ error: 'Import payload must include categories and notes arrays' });
  }
  const { created, error } = await applyImport(body, req.account.sub, { workspaceId: req.workspaceId });
  if (error) return res.status(500).json({ error: 'Import failed partway; re-run the same file to finish idempotently', detail: error.message, imported: created });
  res.status(200).json({ imported: created, schemaVersion });
});

// Load curated sample notes (idempotent) so markdown and GFM rendering can be
// previewed without typing demo content by hand.
app.post('/api/samples', auth, requirePermission('notes:write'), async (req, res) => {
  const { created, error } = await applyImport(sampleContent(), req.account.sub, { overwrite: true, workspaceId: req.workspaceId });
  if (error) return res.status(500).json({ error: 'Sample load failed partway; re-run to finish idempotently', detail: error.message, imported: created });
  const tickets = await seedSampleTickets(req.account.sub, req.workspaceId);
  res.status(200).json({ imported: { ...created, tickets }, schemaVersion });
});

// Seed support-ticket demo data: three field definitions (one of each complex
// type) and six tickets across the whole status range with replies. Idempotent
// by fixed record ids — re-running refreshes instead of duplicating.
async function seedSampleTickets(accountSub, workspaceId) {
  const day = 24 * 60 * 60 * 1000;
  const fields = [
    { id: 'sample-field-region', label: 'Region', type: 'select', options: ['EU', 'US', 'APAC'], required: true, sort_order: 0 },
    { id: 'sample-field-users', label: 'Affected users', type: 'number', options: [], required: false, sort_order: 1 },
    { id: 'sample-field-sla', label: 'SLA due', type: 'date', options: [], required: false, sort_order: 2 },
  ];
  for (const field of fields) {
    const existing = await q('SELECT id FROM type::thing("ticket_field", $id) LIMIT 1;', { id: field.id });
    const data = {
      label: field.label, type: field.type, options: field.options, required: field.required,
      sort_order: field.sort_order, workspace: new RecordId('workspace', workspaceId), created_at: new Date(),
    };
    if (existing[0]) {
      await q('UPDATE type::thing("ticket_field", $id) SET ' + literalAssignments(data).join(', ') + ';', { id: field.id });
    } else {
      await q('CREATE type::thing("ticket_field", $id) SET ' + literalAssignments(data).join(', ') + ';', { id: field.id });
    }
  }
  const tickets = [
    { id: 'sample-ticket-login-outage', subject: 'Login fails for SSO customers', description: 'Since 09:00 UTC the SSO handshake returns 500 for the EU cluster.', status: 'open', priority: 'urgent', age: -2, custom: { 'sample-field-region': 'EU', 'sample-field-users': '1200', 'sample-field-sla': '' }, replies: [
      { body: 'Rolled back the identity-provider config change; handshake succeeding again.', age: -1 },
    ] },
    { id: 'sample-ticket-export-csv', subject: 'CSV export truncates rows', description: 'Exports over 10k rows stop mid-file with no error surfaced.', status: 'pending', priority: 'high', age: -5, custom: { 'sample-field-region': 'US', 'sample-field-users': '35', 'sample-field-sla': '' }, replies: [
      { body: 'Could you share the export request id so we can trace the stream?', age: -4 },
      { body: 'Sent: exp-8842. It stops at exactly 10,240 rows every time.', age: -3 },
    ] },
    { id: 'sample-ticket-dark-mode', subject: 'Request: dark mode for public share pages', description: 'Shared links always render light even when the workspace is dark.', status: 'new', priority: 'low', age: -1, custom: { 'sample-field-region': 'APAC', 'sample-field-users': '0', 'sample-field-sla': '' }, replies: [] },
    { id: 'sample-ticket-webhook-retry', subject: 'Webhook retries arrive out of order', description: 'Retry storms deliver older events after newer ones.', status: 'resolved', priority: 'medium', age: -9, custom: { 'sample-field-region': 'EU', 'sample-field-users': '8', 'sample-field-sla': '' }, replies: [
      { body: 'Fixed in the queue worker: retries now carry the original sequence number.', age: -7 },
    ] },
    { id: 'sample-ticket-invoice-vat', subject: 'Invoice shows wrong VAT rate', description: 'April invoices used 19% instead of 20%.', status: 'closed', priority: 'high', age: -21, custom: { 'sample-field-region': 'EU', 'sample-field-users': '1', 'sample-field-sla': '' }, replies: [
      { body: 'Credit note issued and billing table corrected.', age: -19 },
    ] },
    { id: 'sample-ticket-mobile-push', subject: 'Mobile push notifications delayed', description: 'Push arrives 10-20 minutes late on Android only.', status: 'open', priority: 'medium', age: -3, custom: { 'sample-field-region': 'US', 'sample-field-users': '240', 'sample-field-sla': '' }, replies: [] },
  ];
  let created = 0;
  for (const ticket of tickets) {
    const createdAt = new Date(Date.now() + ticket.age * day);
    const existing = await q('SELECT id FROM type::thing("ticket", $id) LIMIT 1;', { id: ticket.id });
    const data = {
      subject: ticket.subject,
      description: ticket.description,
      status: ticket.status,
      priority: ticket.priority,
      requester: new RecordId('account', recordId(accountSub)),
      assignee: null,
      custom_fields: ticket.custom,
      reply_count: ticket.replies.length,
      workspace: new RecordId('workspace', workspaceId),
      created_at: createdAt,
      updated_at: new Date(Date.now() + (ticket.age + 1) * day),
    };
    if (existing[0]) {
      const { created_at: _keep, ...refresh } = data;
      await q('UPDATE type::thing("ticket", $id) SET ' + literalAssignments(refresh).join(', ') + ';', { id: ticket.id });
    } else {
      await q('CREATE type::thing("ticket", $id) SET ' + literalAssignments(data).join(', ') + ';', { id: ticket.id });
      created++;
    }
    const existingReplies = await q('SELECT id FROM ticket_reply WHERE ticket = type::thing("ticket", $id);', { id: ticket.id });
    if (!existingReplies.length) {
      let offset = 0;
      for (const reply of ticket.replies) {
        await createRecord('ticket_reply', {
          ticket: new RecordId('ticket', ticket.id),
          author: new RecordId('account', recordId(accountSub)),
          body: reply.body,
          workspace: new RecordId('workspace', workspaceId),
          created_at: new Date(Date.now() + (reply.age * day) + (offset++ * 1000)),
        });
      }
    }
  }
  return { fields: fields.length, tickets: tickets.length, created };
}

/* ---------- study notes: wikilink graph + markdown file import ---------- */

// The display title of a note: its first markdown heading, or the first
// non-empty line. Used to match [[Wiki links]] against note titles.
function noteTitle(content) {
  const line = String(content || '').split('\n').map((row) => row.trim()).find((row) => row.length > 0) || '';
  return line.replace(/^#+\s*/, '').trim();
}

// Resolve a single wikilink target to a note in this workspace (title match,
// then slug-ish id match). Returns null when nothing matches yet.
async function findNoteByTitle(title, workspaceId = 'default') {
  const needle = String(title || '').trim();
  if (!needle) return null;
  const rows = await q(`SELECT * FROM notes
    WHERE workspace = ${recordLiteral('workspace', workspaceId)} AND is_recycle = false
      AND string::lowercase(content) CONTAINS string::lowercase($needle)
    ORDER BY updated_at DESC LIMIT 25;`, { needle });
  const lowered = needle.toLowerCase();
  return rows.find((row) => noteTitle(row.content).toLowerCase() === lowered)
    || rows.find((row) => noteTitle(row.content).toLowerCase().startsWith(lowered))
    || rows[0] || null;
}

// The note graph for one note: outgoing [[links]] (resolved where possible)
// and incoming backlinks (notes whose markdown references this note's title).
app.get('/api/notes/:id/backlinks', auth, async (req, res) => {
  const rows = await q(`SELECT * FROM type::thing('notes', $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  const note = rows[0];
  if (!note) return res.status(404).json({ error: 'Note not found' });
  const title = noteTitle(note.content);
  const targets = [...new Set([...String(note.content).matchAll(/\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g)].map((match) => match[1].trim()))].slice(0, 40);
  const links = [];
  for (const target of targets) {
    const match = await findNoteByTitle(target, req.workspaceId);
    links.push({ title: target, note: match ? publicNote(match) : null });
  }
  const backlinks = title
    ? (await q(`SELECT * FROM notes
        WHERE workspace = ${wsLiteral(req)} AND is_recycle = false AND id != type::thing('notes', $id)
          AND string::lowercase(content) CONTAINS string::lowercase($needle)
        ORDER BY updated_at DESC LIMIT 40;`, { id: req.params.id, needle: `[[${title}]]` })).map((row) => publicNote(row))
    : [];
  res.json({ title, links, backlinks });
});

// Import one or more markdown files as notes. Files are matched against the
// workspace default lane; content that already exists verbatim is skipped so
// re-importing the same folder never duplicates notes.
app.post('/api/notes/import-markdown', auth, requirePermission('notes:write'), async (req, res) => {
  const body = req.body || {};
  const files = Array.isArray(body.files) ? body.files : (body.name && body.text !== undefined ? [{ name: body.name, text: body.text }] : []);
  if (!files.length) return res.status(400).json({ error: 'Provide files: [{ name, text }]' });
  const lane = await findCategory('notes', req.workspaceId) || await findCategory('imported', req.workspaceId) || await findCategory('default', req.workspaceId);
  if (!lane) return res.status(500).json({ error: 'No default lane available for imports' });
  const created = [];
  let skipped = 0;
  for (const file of files.slice(0, 50)) {
    const text = String(file.text ?? '').replace(/\r\n/g, '\n').trim();
    const name = String(file.name || 'note.md').trim();
    if (!text) { skipped++; continue; }
    const duplicate = await q(`SELECT id FROM notes
      WHERE workspace = ${wsLiteral(req)} AND is_recycle = false AND content = $text LIMIT 1;`, { text });
    if (duplicate[0]) { skipped++; continue; }
    const heading = noteTitle(text);
    const fromFile = name.replace(/\.(md|markdown|mdx|txt)$/i, '').replace(/[-_]+/g, ' ').trim();
    const content = /^#\s/.test(text) ? text : `# ${heading || fromFile || 'Untitled note'}\n\n${text}`;
    const rows = await q(`CREATE notes CONTENT {
      content: $content,
      category: ${recordLiteral('category', recordId(lane.id))},
      account: type::thing('account', $account),
      workspace: ${wsLiteral(req)},
      tags: [],
      is_archived: false, is_recycle: false, is_top: false, is_share: false,
      metadata: ${inlineValue({ importedFrom: name.slice(0, 160) })},
      word_count: ${countWords(content)},
      created_at: time::now(), updated_at: time::now()
    } RETURN *, category.* AS category_record;`, {
      content,
      account: req.account.sub,
    });
    await recordAudit('note.import', req.account.sub, { name: name.slice(0, 120) }, recordId(rows[0].id), req.workspaceId);
    created.push(publicNote(rows[0]));
  }
  res.status(201).json({ imported: { notes: created.length, skipped }, notes: created });
});

/* ---------- Phase 5: markdown bundles, attachment text, graph, spaced recall ---------- */

// --- dependency-free ZIP writer (stored entries) ---------------------------

const crcTable = (() => {
  const table = new Int32Array(256);
  for (let index = 0; index < 256; index++) {
    let value = index;
    for (let bit = 0; bit < 8; bit++) value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
    table[index] = value;
  }
  return table;
})();

function crc32(buffer) {
  let crc = -1;
  for (let index = 0; index < buffer.length; index++) crc = (crc >>> 8) ^ crcTable[(crc ^ buffer[index]) & 0xff];
  return (crc ^ -1) >>> 0;
}

// Notes are small markdown files, so entries are stored uncompressed: that
// keeps the bundle dependency-free (no archiver package) and the output is
// readable by every unzip implementation.
function buildZip(entries) {
  const DOS_DATE = 0x0021; // 1980-01-01, the ZIP epoch
  const locals = [];
  const centrals = [];
  let offset = 0;
  let count = 0;
  for (const entry of entries) {
    const nameBuf = Buffer.from(entry.name, 'utf8');
    const data = Buffer.from(entry.content, 'utf8');
    const crc = crc32(data);

    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);       // version needed to extract
    local.writeUInt16LE(0x0800, 6);   // UTF-8 file names
    local.writeUInt16LE(0, 8);        // method: stored
    local.writeUInt16LE(0, 10);       // mod time
    local.writeUInt16LE(DOS_DATE, 12);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(data.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(nameBuf.length, 26);
    local.writeUInt16LE(0, 28);
    locals.push(local, nameBuf, data);

    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);     // version made by
    central.writeUInt16LE(20, 6);     // version needed
    central.writeUInt16LE(0x0800, 8);
    central.writeUInt16LE(0, 10);
    central.writeUInt16LE(0, 12);
    central.writeUInt16LE(DOS_DATE, 14);
    central.writeUInt32LE(crc, 16);
    central.writeUInt32LE(data.length, 20);
    central.writeUInt32LE(data.length, 24);
    central.writeUInt16LE(nameBuf.length, 28);
    central.writeUInt32LE(offset, 42);
    centrals.push(central, nameBuf);

    offset += local.length + nameBuf.length + data.length;
    count += 1;
  }
  const centralBuf = Buffer.concat(centrals);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(count, 8);
  end.writeUInt16LE(count, 10);
  end.writeUInt32LE(centralBuf.length, 12);
  end.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, centralBuf, end]);
}

const slugifyName = (value) => String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80) || 'untitled';

function wikiLinkTargets(content) {
  return [...new Set([...String(content || '').matchAll(/\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g)].map((match) => match[1].trim()).filter(Boolean))];
}

// Portable single-note markdown: front-matter carries the metadata that a
// plain markdown editor cannot infer, and [[wiki links]] stay verbatim so the
// bundle can be re-imported through the markdown importer.
function noteToBundleFile(note, laneSlug, index) {
  const title = noteTitle(note.content) || 'Untitled note';
  const quoted = (value) => JSON.stringify(String(value ?? ''));
  const frontMatter = [
    '---',
    `title: ${quoted(title)}`,
    `note_id: ${quoted(note.id)}`,
    `lane: ${quoted(laneSlug)}`,
    `tags: [${(note.tags || []).map((tag) => quoted(typeof tag === 'string' ? tag : tag?.name || '')).filter((value) => value !== '""').join(', ')}]`,
    `links: [${wikiLinkTargets(note.content).map(quoted).join(', ')}]`,
    `created: ${quoted(note.createdAt)}`,
    `updated: ${quoted(note.updatedAt)}`,
    `shared: ${note.isShare ? 'true' : 'false'}`,
    '---',
    '',
  ].join('\n');
  const body = /^#\s/m.test(note.content) ? note.content : `# ${title}\n\n${note.content}`;
  return { name: `${String(index).padStart(3, '0')}-${slugifyName(title)}.md`, content: `${frontMatter}${body.trimEnd()}\n` };
}

// Export a lane or a tag (or every note) as a .zip of linked markdown files.
app.get('/api/export/markdown', auth, async (req, res) => {
  const category = req.query.category && String(req.query.category) !== 'all' ? String(req.query.category) : null;
  const tag = req.query.tag ? String(req.query.tag).replace(/^#/, '').trim() : null;
  const filters = [`workspace = ${wsLiteral(req)}`, 'is_recycle = false'];
  const vars = { tag: tag || null };
  if (category) {
    const laneRow = await findCategory(category, req.workspaceId);
    filters.push(`category = ${laneRow ? recordLiteral('category', recordId(laneRow.id)) : recordLiteral('category', '__missing__')}`);
  }
  if (tag) filters.push('type::thing(\'tag\', $tag) IN tags');
  const rows = await q(`SELECT *, category.* AS category_record FROM notes WHERE ${filters.join(' AND ')} LIMIT 1000;`, vars);
  rows.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  const notes = rows.map((row) => publicNote(row));
  const lane = category || 'all-notes';
  const entries = notes.map((note, index) => noteToBundleFile(note, note.category?.slug || lane, index + 1));
  const label = category ? slugifyName(category) : (tag ? `tag-${slugifyName(tag)}` : 'notes');
  res.setHeader('content-type', 'application/zip');
  res.setHeader('x-note-count', String(entries.length));
  res.setHeader('content-disposition', `attachment; filename="planing-${label}-${new Date().toISOString().slice(0, 10)}.zip"`);
  res.send(buildZip(entries.length ? entries : [{ name: 'README.md', content: '# Nothing to export\n\nNo notes matched this lane or tag.\n' }]));
});

// --- attachment text extraction -------------------------------------------

const TEXTUAL_TYPES = /^(text\/|application\/(json|xml|x-yaml|markdown|javascript))/i;
const TEXTUAL_EXTENSIONS = ['md', 'markdown', 'mdx', 'txt', 'csv', 'json', 'yml', 'yaml', 'log', 'tsv'];
const MAX_EXTRACTED_CHARS = 200_000;

const pdfUnescape = (value) => value
  .replace(/\\([nrtbf])/g, (_, code) => ({ n: '\n', r: '\r', t: '\t', b: '', f: '' }[code]))
  .replace(/\\([()\\])/g, '$1');

// Best-effort PDF text pull: inflate each content stream and keep the strings
// shown by text operators. Scanned/image-only PDFs yield nothing, which is
// reported as 'unsupported' rather than pretending the file was read.
function extractPdfText(buffer) {
  const raw = buffer.toString('latin1');
  const pages = [];
  const streamPattern = /stream\r?\n([\s\S]*?)\r?\nendstream/g;
  let match;
  while ((match = streamPattern.exec(raw))) {
    let decoded = match[1];
    try {
      decoded = zlib.inflateSync(Buffer.from(decoded, 'latin1')).toString('latin1');
    } catch { /* not a flate stream — fall back to the raw bytes */ }
    if (!/(Tj|TJ|T\*)/.test(decoded)) continue;
    const strings = [...decoded.matchAll(/\(((?:\\.|[^()\\])*)\)/g)].map((entry) => pdfUnescape(entry[1]));
    if (strings.length) pages.push(strings.join(' ').replace(/\s+/g, ' ').trim());
  }
  return pages.filter(Boolean).join('\n\n');
}

function extractAttachmentText(buffer, name, type) {
  const extension = (String(name).match(/\.([a-z0-9]+)$/i)?.[1] || '').toLowerCase();
  if (type === 'application/pdf' || extension === 'pdf') {
    const text = extractPdfText(buffer).trim();
    return text ? { text: text.slice(0, MAX_EXTRACTED_CHARS), status: 'ready' } : { text: '', status: 'unsupported' };
  }
  if (TEXTUAL_TYPES.test(type) || TEXTUAL_EXTENSIONS.includes(extension)) {
    const text = buffer.toString('utf8').replace(/\u0000/g, '').trim();
    return text ? { text: text.slice(0, MAX_EXTRACTED_CHARS), status: 'ready' } : { text: '', status: 'empty' };
  }
  return { text: '', status: 'none' };
}

app.get('/api/attachments/:id/text', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("attachments", $id) LIMIT 1;', { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Attachment not found' });
  res.json({ id: recordId(rows[0].id), name: rows[0].name, status: rows[0].text_status || 'none', text: rows[0].text_content || '' });
});

// Turn an attachment's extracted text into a note (creating the note if the
// attachment was uploaded unattached).
app.post('/api/attachments/:id/to-note', auth, requirePermission('notes:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("attachments", $id) LIMIT 1;', { id: req.params.id });
  const attachment = rows[0];
  if (!attachment) return res.status(404).json({ error: 'Attachment not found' });
  const text = String(attachment.text_content || '').trim();
  if (!text) return res.status(400).json({ error: 'No extracted text available for this file' });
  const laneSlug = String(req.body?.category || '').trim() || (await findWorkspace(req.workspaceId))?.default_category || 'notes';
  const lane = await findCategory(laneSlug, req.workspaceId) || await findCategory('notes', req.workspaceId);
  if (!lane) return res.status(500).json({ error: 'No lane available for the new note' });
  const heading = noteTitle(text);
  const fallbackTitle = attachment.name.replace(/\.[a-z0-9]+$/i, '').replace(/[-_]+/g, ' ').trim();
  const content = /^#\s/.test(text) ? text : `# ${heading || fallbackTitle || 'Imported file'}\n\n${text}`;
  const created = await q(`CREATE notes CONTENT {
    content: $content,
    category: ${recordLiteral('category', recordId(lane.id))},
    account: type::thing('account', $account),
    created_by: type::thing('account', $account),
    workspace: ${wsLiteral(req)},
    tags: [],
    is_archived: false, is_recycle: false, is_top: false, is_share: false,
    metadata: ${inlineValue({ importedFrom: attachment.name.slice(0, 160), attachment: recordId(attachment.id) })},
    word_count: ${countWords(content)},
    created_at: time::now(), updated_at: time::now()
  } RETURN *, category.* AS category_record;`, {
    content,
    account: req.account.sub,
  });
  await recordAudit('note.import', req.account.sub, { name: attachment.name.slice(0, 120), source: 'attachment' }, recordId(created[0].id), req.workspaceId);
  res.status(201).json(publicNote(created[0]));
});

// --- knowledge graph ------------------------------------------------------

app.get('/api/graph', auth, async (req, res) => {
  const rows = await tq('graph.notes', `SELECT *, category.* AS category_record FROM notes
    WHERE workspace = ${wsLiteral(req)} AND is_recycle = false
    ORDER BY updated_at DESC LIMIT 500;`, {}, req.workspaceId);
  const notes = rows.map((row) => publicNote(row));
  const visible = new Set(notes.map((note) => note.id));
  const edges = [];
  const seen = new Set();
  // Stored edges first: they are the relation of record for wiki links.
  const stored = await tq('graph.edges', `SELECT * FROM note_link WHERE workspace = ${wsLiteral(req)} LIMIT 2000;`, {}, req.workspaceId);
  for (const edge of stored) {
    const source = recordId(edge.in);
    const target = recordId(edge.out);
    if (!visible.has(source) || !visible.has(target)) continue;
    const key = `${source}->${target}`;
    if (seen.has(key)) continue;
    seen.add(key);
    edges.push({ source, target, label: edge.label, resolved: true });
  }
  // Then anything by title: covers notes imported before the edge table existed
  // and unresolved targets, which have no OUT record to relate to.
  const byTitle = new Map();
  for (const note of notes) {
    const title = noteTitle(note.content).toLowerCase();
    if (title && !byTitle.has(title)) byTitle.set(title, note.id);
  }
  for (const note of notes) {
    for (const target of wikiLinkTargets(note.content)) {
      const resolved = byTitle.get(target.toLowerCase()) || null;
      if (resolved === note.id) continue;
      const key = resolved ? `${note.id}->${resolved}` : `${note.id}->?${target.toLowerCase()}`;
      if (seen.has(key)) continue;
      seen.add(key);
      edges.push({ source: note.id, target: resolved, label: target, resolved: Boolean(resolved) });
    }
  }
  const outgoing = new Map();
  const incoming = new Map();
  for (const edge of edges) {
    outgoing.set(edge.source, (outgoing.get(edge.source) || 0) + 1);
    if (edge.target) incoming.set(edge.target, (incoming.get(edge.target) || 0) + 1);
  }
  res.json({
    nodes: notes.map((note) => ({
      id: note.id,
      title: noteTitle(note.content) || 'Untitled note',
      lane: note.category?.slug || 'notes',
      laneName: note.category?.name || 'Notes',
      color: note.category?.color || null,
      isShare: note.isShare,
      updatedAt: note.updatedAt,
      outgoing: outgoing.get(note.id) || 0,
      incoming: incoming.get(note.id) || 0,
    })),
    edges,
    stats: {
      notes: notes.length,
      edges: edges.length,
      resolved: edges.filter((edge) => edge.resolved).length,
      unresolved: edges.filter((edge) => !edge.resolved).length,
    },
  });
});

// --- spaced recall --------------------------------------------------------

// Leitner boxes with expanding intervals (days). Reviewing schedules the next
// due date; the due queue is a single indexed range read on due_at.
const studyIntervals = [0, 1, 3, 7, 16, 35, 70, 150];
const studyGrades = ['again', 'hard', 'good', 'easy'];

function scheduleStudyItem(item, grade) {
  const box = Number(item.box || 0);
  let nextBox = box;
  let minutes = 24 * 60;
  let lapses = Number(item.lapses || 0);
  if (grade === 'again') { nextBox = 0; minutes = 10; lapses += 1; }
  else if (grade === 'hard') { nextBox = Math.max(1, box); minutes = 24 * 60; }
  else if (grade === 'easy') { nextBox = Math.min(box + 2, studyIntervals.length - 1); minutes = studyIntervals[nextBox] * 24 * 60; }
  else { nextBox = Math.min(box + 1, studyIntervals.length - 1); minutes = studyIntervals[nextBox] * 24 * 60; }
  return { box: nextBox, dueAt: new Date(Date.now() + minutes * 60_000), lapses, intervalDays: Math.round(minutes / (24 * 60)) };
}

const isoOrNull = (value) => (value instanceof Date ? value.toISOString() : (value || null));

function publicStudyItem(row, noteTitleValue) {
  return {
    id: recordId(row.id),
    note: row.note ? recordId(row.note) : null,
    noteTitle: noteTitleValue || null,
    question: row.question,
    answer: row.answer,
    box: Number(row.box || 0),
    dueAt: isoOrNull(row.due_at),
    reviewedAt: isoOrNull(row.reviewed_at),
    reviewCount: Number(row.review_count || 0),
    lapses: Number(row.lapses || 0),
    source: row.source || 'manual',
    createdAt: isoOrNull(row.created_at),
    updatedAt: isoOrNull(row.updated_at),
  };
}

async function noteTitlesFor(rows) {
  const ids = [...new Set(rows.map((row) => (row.note ? recordId(row.note) : null)).filter(Boolean))];
  if (!ids.length) return new Map();
  const notes = await q('SELECT id, content FROM notes WHERE id IN $ids;', { ids: ids.map((id) => new RecordId('notes', id)) });
  return new Map(notes.map((note) => [recordId(note.id), noteTitle(note.content) || 'Untitled note']));
}


// --- kanban board --------------------------------------------------------

const planningStatuses = ['backlog', 'todo', 'doing', 'review', 'done'];

app.get('/api/kanban', auth, async (req, res) => {
  const [categories, notes, counts] = await Promise.all([
    q(`SELECT * FROM category WHERE workspace = ${wsLiteral(req)} ORDER BY sort_order, created_at;`),
    q(`SELECT * FROM notes WHERE workspace = ${wsLiteral(req)} AND is_recycle = false AND is_archived = false ORDER BY position ASC, updated_at DESC LIMIT 500;`),
    q(`SELECT status, count() AS count FROM notes WHERE workspace = ${wsLiteral(req)} AND is_recycle = false AND is_archived = false GROUP BY status;`),
  ]);
  const countByStatus = Object.fromEntries(counts.map((row) => [row.status || 'todo', Number(row.count || 0)]));
  const columns = planningStatuses.map((status) => ({ status, count: countByStatus[status] || 0 }));
  res.json({ columns, categories, notes: notes.map((row) => publicNote(row)) });
});

// Move a card: set its column (status) and order position in one call.
app.post('/api/kanban/move', auth, requirePermission('notes:write'), async (req, res) => {
  const status = String(req.body.status || '');
  if (!planningStatuses.includes(status)) return res.status(400).json({ error: `Status must be one of: ${planningStatuses.join(', ')}` });
  const id = String(req.body.noteId || '');
  if (!id) return res.status(400).json({ error: 'noteId is required' });
  const position = Number(req.body.position) || 0;
  const rows = await q(`UPDATE type::thing('notes', $id) SET status = $status, position = $position, updated_at = time::now()
    WHERE workspace = ${wsLiteral(req)}
    RETURN *, category.* AS category_record;`, { id, status, position });
  if (!rows[0]) return res.status(404).json({ error: 'Note not found' });
  await recordNoteActivity(id, req.workspaceId, 'note.moved', req.account.sub, { status, position });
  res.json(publicNote(rows[0]));
});

// --- calendar ------------------------------------------------------------

app.get('/api/calendar', auth, async (req, res) => {
  // Plan items that carry any planning date. `from`/`to` bound the range when
  // the client only needs one month or week.
  const params = {};
  const bounds = [];
  if (req.query.from) { bounds.push('start_date >= $from OR due_date >= $from'); params.from = new Date(String(req.query.from)); }
  if (req.query.to) { bounds.push('start_date <= $to OR due_date <= $to'); params.to = new Date(String(req.query.to)); }
  // SurrealDB distinguishes NONE (absent) from NULL, and `IS NOT NULL` is true
  // for NONE, so the presence test must be explicit: only notes that really
  // carry a due or start date belong on the calendar.
  const where = bounds.length ? ` AND (${bounds.join(') AND (')})` : '';
  const notes = await q(`
    SELECT id, content, category, status, priority, due_date, start_date, end_date, event_color, updated_at, created_at
    FROM notes
    WHERE workspace = ${wsLiteral(req)}
      AND is_recycle = false
      AND is_archived = false
      AND (due_date IS NOT NONE OR start_date IS NOT NONE)${where}
    ORDER BY start_date ASC, due_date ASC, updated_at DESC LIMIT 500;
  `, params);
  const events = notes.map((row) => {
    const start = row.start_date || row.due_date || row.updated_at;
    const end = row.end_date || row.due_date || start;
    const category = row.category ? publicCategory(row.category) : null;
    return {
      id: recordId(row.id),
      noteId: recordId(row.id),
      title: noteTitle(row.content) || 'Untitled plan item',
      start: isoOrNull(start),
      end: isoOrNull(end),
      allDay: !row.start_date,
      status: row.status || 'todo',
      priority: row.priority || 'medium',
      color: row.event_color || (category ? category.color : null),
      category: category ? category.slug : null,
    };
  });
  res.json({ events });
});

// --- notes: add due date support to flags --------------------------------

// The notes API already supports flags, so due dates can be stored in note.flags.due_date
// The kanban and calendar views will read from these flags



async function studyStats(workspaceId = 'default') {
  const scope = recordLiteral('workspace', workspaceId);
  const [total, due] = await Promise.all([
    q(`SELECT count() AS count FROM study_item WHERE workspace = ${scope} GROUP ALL;`),
    q(`SELECT count() AS count FROM study_item WHERE workspace = ${scope} AND due_at <= time::now() GROUP ALL;`),
  ]);
  return { total: Number(total[0]?.count || 0), due: Number(due[0]?.count || 0) };
}

app.get('/api/study/stats', auth, async (req, res) => {
  const [byBox, stats] = await Promise.all([
    q(`SELECT box, count() AS count FROM study_item WHERE workspace = ${wsLiteral(req)} GROUP BY box;`),
    studyStats(req.workspaceId),
  ]);
  res.json({ ...stats, boxes: byBox.map((row) => ({ box: Number(row.box || 0), count: Number(row.count || 0) })) });
});

// The review queue: everything due now, oldest first.
app.get('/api/study/due', auth, async (req, res) => {
  const limit = Math.min(Number(req.query.limit || 25) || 25, 100);
  const rows = await q(`SELECT * FROM study_item
    WHERE workspace = ${wsLiteral(req)} AND due_at <= time::now()
    ORDER BY due_at ASC LIMIT $limit;`, { limit });
  const titles = await noteTitlesFor(rows);
  const stats = await studyStats(req.workspaceId);
  res.json({ items: rows.map((row) => publicStudyItem(row, titles.get(row.note ? recordId(row.note) : ''))), ...stats });
});

// Review analytics: retention per tag, lapse hotspots, an activity strip, and a
// due forecast. The aggregation runs in process over bounded reads because the
// pinned engine handles nested aggregation poorly and card counts are small.
const studyForecastDays = 7;
const studyActivityDays = 14;

app.get('/api/study/analytics', auth, async (req, res) => {
  const scope = wsLiteral(req);
  const [items, reviews, notes, tags] = await Promise.all([
    q(`SELECT * FROM study_item WHERE workspace = ${scope} LIMIT 1000;`),
    q(`SELECT * FROM study_review WHERE workspace = ${scope} ORDER BY created_at DESC LIMIT 2000;`),
    q(`SELECT id, content, tags FROM notes WHERE workspace = ${scope} LIMIT 1000;`),
    q('SELECT * FROM tag;'),
  ]);

  const tagNames = new Map(tags.map((tag) => [recordId(tag.id), String(tag.name || recordId(tag.id))]));
  const noteTags = new Map(notes.map((note) => [
    recordId(note.id),
    (Array.isArray(note.tags) ? note.tags : []).map((tag) => tagNames.get(recordId(tag))).filter(Boolean),
  ]));
  const itemTags = new Map(items.map((item) => [recordId(item.id), item.note ? (noteTags.get(recordId(item.note)) || []) : []]));

  const now = Date.now();
  const success = (grade) => grade === 'good' || grade === 'easy';
  const buckets = new Map();
  const bucketFor = (key, label) => {
    if (!buckets.has(key)) buckets.set(key, { key, label, cards: 0, reviews: 0, successes: 0, lapses: 0, boxTotal: 0, due: 0 });
    return buckets.get(key);
  };

  for (const item of items) {
    const bucketKeys = ['all', ...itemTags.get(recordId(item.id)) || []];
    const due = item.due_at && new Date(item.due_at).getTime() <= now;
    for (const key of bucketKeys) {
      const bucket = bucketFor(key, key === 'all' ? 'All cards' : key);
      bucket.cards += 1;
      bucket.boxTotal += Number(item.box || 0);
      if (due) bucket.due += 1;
    }
  }

  const itemById = new Map(items.map((item) => [recordId(item.id), item]));
  const activity = new Map();
  for (let offset = studyActivityDays - 1; offset >= 0; offset -= 1) {
    activity.set(new Date(now - offset * 86400_000).toISOString().slice(0, 10), { date: null, reviews: 0, again: 0 });
  }
  for (const review of reviews) {
    const dayKey = new Date(review.created_at).toISOString().slice(0, 10);
    if (activity.has(dayKey)) {
      const entry = activity.get(dayKey);
      entry.reviews += 1;
      if (review.grade === 'again') entry.again += 1;
    }
    const item = itemById.get(recordId(review.item));
    const bucketKeys = ['all', ...(item ? itemTags.get(recordId(item.id)) || [] : [])];
    for (const key of bucketKeys) {
      const bucket = bucketFor(key, key === 'all' ? 'All cards' : key);
      bucket.reviews += 1;
      if (success(review.grade)) bucket.successes += 1;
      else if (review.grade === 'again') bucket.lapses += 1;
    }
  }

  const rate = (part, whole) => (whole ? Math.round((part / whole) * 1000) / 10 : null);
  const byTag = [...buckets.values()]
    .map((bucket) => ({
      tag: bucket.key === 'all' ? null : bucket.key,
      label: bucket.label,
      cards: bucket.cards,
      reviews: bucket.reviews,
      lapses: bucket.lapses,
      due: bucket.due,
      averageBox: bucket.cards ? Math.round((bucket.boxTotal / bucket.cards) * 10) / 10 : 0,
      retention: rate(bucket.successes, bucket.reviews),
    }))
    // The overall row is reported separately, and an unreviewed tag carries no
    // retention signal — it stays in the table with a null rate.
    .sort((a, b) => (b.reviews - a.reviews) || (b.cards - a.cards));

  const hotspots = items
    .map((item) => ({
      id: recordId(item.id),
      question: item.question,
      answer: item.answer,
      box: Number(item.box || 0),
      lapses: Number(item.lapses || 0),
      reviewCount: Number(item.review_count || 0),
      dueAt: isoOrNull(item.due_at),
      tags: itemTags.get(recordId(item.id)) || [],
    }))
    .filter((item) => item.lapses > 0 || (item.reviewCount > 0 && item.box === 0))
    .sort((a, b) => (b.lapses - a.lapses) || (a.box - b.box) || (a.reviewCount - b.reviewCount))
    .slice(0, 8);

  const forecast = [];
  for (let offset = 0; offset < studyForecastDays; offset += 1) {
    const day = new Date(now + offset * 86400_000);
    const key = day.toISOString().slice(0, 10);
    const count = items.filter((item) => item.due_at && new Date(item.due_at).toISOString().slice(0, 10) === key).length;
    forecast.push({ date: key, offset, count });
  }

  const totalReviews = reviews.length;
  const totalSuccesses = reviews.filter((review) => success(review.grade)).length;
  const reviewedCards = items.filter((item) => Number(item.review_count || 0) > 0).length;
  res.json({
    totals: {
      cards: items.length,
      reviewedCards,
      reviews: totalReviews,
      lapses: reviews.filter((review) => review.grade === 'again').length,
      dueNow: items.filter((item) => item.due_at && new Date(item.due_at).getTime() <= now).length,
      retention: rate(totalSuccesses, totalReviews),
      averageBox: items.length ? Math.round((items.reduce((sum, item) => sum + Number(item.box || 0), 0) / items.length) * 10) / 10 : 0,
    },
    tags: byTag,
    hotspots,
    forecast,
    activity: [...activity.entries()].map(([date, entry]) => ({ date, reviews: entry.reviews, lapses: entry.again })),
  });
});

app.get('/api/study/items', auth, async (req, res) => {
  const noteId = req.query.note ? String(req.query.note) : null;
  const limit = Math.min(Number(req.query.limit || 100) || 100, 300);
  const rows = noteId
    ? await q(`SELECT * FROM study_item WHERE workspace = ${wsLiteral(req)} AND note = type::thing("notes", $note) ORDER BY created_at ASC LIMIT $limit;`, { note: noteId, limit })
    : await q(`SELECT * FROM study_item WHERE workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT $limit;`, { limit });
  const titles = await noteTitlesFor(rows);
  res.json(rows.map((row) => publicStudyItem(row, titles.get(row.note ? recordId(row.note) : ''))));
});

// Deterministic offline extraction: heading sections and `term :: definition`
// lines become cards, so card generation works with no provider configured.
function generateStudyCandidates(content) {
  const lines = String(content || '').split('\n');
  const items = [];
  let heading = null;
  let buffer = [];
  const flush = () => {
    const body = buffer.join('\n').trim();
    if (heading && body && !/^[-*]\s*$/.test(body)) {
      items.push({ question: `What does "${heading}" cover?`, answer: body.slice(0, 1200) });
    }
    buffer = [];
  };
  for (const line of lines) {
    const section = line.match(/^#{2,4}\s+(.+?)\s*$/);
    if (section) { flush(); heading = section[1].trim(); continue; }
    if (/^#\s+/.test(line)) { flush(); heading = null; continue; }
    const definition = line.match(/^\s*[-*]\s+(.+?)\s*(?:::|—|–|--)\s+(.+)$/);
    if (definition) {
      items.push({ question: definition[1].replace(/[*`]/g, '').trim(), answer: definition[2].trim() });
      continue;
    }
    buffer.push(line);
  }
  flush();
  const seen = new Set();
  return items.filter((item) => {
    const key = item.question.toLowerCase();
    if (!item.question || !item.answer || seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 40);
}

// Optional provider pass: ask the active model for flashcards as JSON and fall
// back to the offline extractor whenever that is unavailable or unparseable.
async function generateStudyCandidatesWithProvider(note, prompt, workspaceId = 'default', accountId = null, { jobId = null, attempt = 0 } = {}) {
  const { provider } = await resolveProviderForWorkspace(workspaceId);
  if (!provider) return null;
  const instruction = prompt?.body || 'Produce flashcards from the material as a JSON array of {"question": ..., "answer": ...} objects.';
  const userContent = `${instruction}\n\n---\n${String(note.content).slice(0, 6000)}`;
  const systemContent = 'You write study flashcards. Reply with a JSON array of {"question": string, "answer": string} objects and nothing else.';
  const started = Date.now();
  const runRow = await beginAiRun({
    workspaceId,
    provider: recordId(provider.id),
    model: provider.model,
    feature: 'study.generate',
    accountId,
    noteId: recordId(note.id),
    jobId,
    attempt,
    promptChars: systemContent.length + userContent.length,
  });
  try {
    const { content: reply, usage } = await callProvider(provider, [
      { role: 'system', content: systemContent },
      { role: 'user', content: userContent },
    ]);
    await completeAiRun(runRow, { reply, usage, startedAt: started });
    const json = reply.match(/\[[\s\S]*\]/)?.[0];
    if (!json) return null;
    const parsed = JSON.parse(json);
    const candidates = parsed
      .filter((entry) => entry && typeof entry.question === 'string' && typeof entry.answer === 'string')
      .map((entry) => ({ question: entry.question.trim().slice(0, 400), answer: entry.answer.trim().slice(0, 2000) }))
      .filter((entry) => entry.question && entry.answer)
      .slice(0, 40);
    return candidates.length ? candidates : null;
  } catch (error) {
    await completeAiRun(runRow, { error: error.message, startedAt: started });
    throw error;
  }
}

async function createStudyItems({ candidates, noteId, source, accountSub, workspaceId = 'default' }) {
  const existing = noteId
    ? await q(`SELECT question FROM study_item WHERE workspace = ${recordLiteral('workspace', workspaceId)} AND note = type::thing("notes", $note);`, { note: noteId })
    : [];
  const known = new Set(existing.map((row) => String(row.question).toLowerCase()));
  const created = [];
  for (const candidate of candidates) {
    const question = String(candidate.question || '').trim().slice(0, 400);
    const answer = String(candidate.answer || '').trim().slice(0, 2000);
    if (!question || !answer || known.has(question.toLowerCase())) continue;
    known.add(question.toLowerCase());
    const data = {
      question,
      answer,
      box: 0,
      due_at: new Date(),
      review_count: 0,
      lapses: 0,
      source,
      // The card belongs to the workspace that generated it. Relying on the
      // field default filed every card under workspace:default, so a card made
      // in any other workspace was invisible to the workspace that made it.
      workspace: new RecordId('workspace', workspaceId),
      created_by: new RecordId('account', recordId(accountSub)),
      created_at: new Date(),
      updated_at: new Date(),
    };
    if (noteId) data.note = new RecordId('notes', String(noteId));
    const rows = await q('CREATE study_item CONTENT $data;', { data });
    created.push(rows[0]);
  }
  return created;
}

app.post('/api/study/items', auth, requirePermission('notes:write'), async (req, res) => {
  const body = req.body || {};
  const noteId = body.noteId ? String(body.noteId) : (body.note ? String(body.note) : null);
  const candidates = Array.isArray(body.items) && body.items.length ? body.items : [{ question: body.question, answer: body.answer }];
  if (!candidates.some((candidate) => String(candidate.question || '').trim() && String(candidate.answer || '').trim())) {
    return res.status(400).json({ error: 'A question and answer are required' });
  }
  const created = await createStudyItems({ candidates, noteId, source: 'manual', accountSub: req.account.sub, workspaceId: req.workspaceId });
  if (noteId) await recordAudit('study.create', req.account.sub, { count: created.length }, noteId, req.workspaceId);
  const titles = await noteTitlesFor(created);
  res.status(201).json({ created: created.length, items: created.map((row) => publicStudyItem(row, titles.get(row.note ? recordId(row.note) : ''))) });
});

app.patch('/api/study/items/:id', auth, requirePermission('notes:write'), async (req, res) => {
  const scope = await q(`SELECT id FROM type::thing("study_item", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  if (!scope[0]) return res.status(404).json({ error: 'Study item not found' });
  const updates = { updated_at: new Date() };
  if (req.body.question !== undefined) {
    const question = String(req.body.question).trim().slice(0, 400);
    if (!question) return res.status(400).json({ error: 'Question cannot be empty' });
    updates.question = question;
  }
  if (req.body.answer !== undefined) {
    const answer = String(req.body.answer).trim().slice(0, 2000);
    if (!answer) return res.status(400).json({ error: 'Answer cannot be empty' });
    updates.answer = answer;
  }
  const rows = await q('UPDATE type::thing("study_item", $id) MERGE $updates RETURN AFTER;', { id: req.params.id, updates });
  if (!rows[0]) return res.status(404).json({ error: 'Study item not found' });
  res.json(publicStudyItem(rows[0]));
});

app.delete('/api/study/items/:id', auth, requirePermission('notes:write'), async (req, res) => {
  const rows = await q(`DELETE type::thing("study_item", $id) WHERE workspace = ${wsLiteral(req)} RETURN BEFORE;`, { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Study item not found' });
  res.status(204).end();
});

// Review one card: grade it, reschedule it, and report what is still due.
app.post('/api/study/items/:id/review', auth, requirePermission('notes:read'), async (req, res) => {
  const grade = String(req.body?.grade || 'good');
  if (!studyGrades.includes(grade)) return res.status(400).json({ error: `Grade must be one of ${studyGrades.join(', ')}` });
  const rows = await q(`SELECT * FROM type::thing("study_item", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Study item not found' });
  const schedule = scheduleStudyItem(rows[0], grade);
  const updated = await q(`UPDATE type::thing("study_item", $id) MERGE {
    box: $box, due_at: $dueAt, lapses: $lapses, reviewed_at: time::now(),
    review_count: (review_count ?? 0) + 1, updated_at: time::now()
  } RETURN AFTER;`, { id: req.params.id, box: schedule.box, dueAt: schedule.dueAt, lapses: schedule.lapses });
  // The log row is what the analytics read; a failure here must not fail the
  // review itself, since the schedule on the card is already committed.
  try {
    const review = {
      item: { tb: 'study_item', id: req.params.id },
      grade,
      box_before: Number(rows[0].box || 0),
      box_after: schedule.box,
      interval_days: schedule.intervalDays || 0,
      account: { tb: 'account', id: req.account.sub },
      // The log row carries the workspace too, so analytics in a non-default
      // workspace see the reviews its members wrote.
      workspace: { tb: 'workspace', id: req.workspaceId },
      created_at: new Date(),
    };
    if (rows[0].note) review.note = { tb: 'notes', id: recordId(rows[0].note) };
    await createRecord('study_review', review);
  } catch (error) {
    console.warn('study.review log failed:', error.message);
  }
  const stats = await studyStats(req.workspaceId);
  res.json({ item: publicStudyItem(updated[0]), grade, ...stats });
});

// Build cards from a note: 'auto' tries the active provider first and falls
// back to the offline extractor, so this always produces something useful.
app.post('/api/study/generate', auth, requirePermission('notes:write'), async (req, res) => {
  const noteId = String(req.body?.noteId || '').trim();
  if (!noteId) return res.status(400).json({ error: 'noteId is required' });
  const rows = await q(`SELECT * FROM type::thing("notes", $id) WHERE workspace = ${wsLiteral(req)} LIMIT 1;`, { id: noteId });
  const note = rows[0];
  if (!note) return res.status(404).json({ error: 'Note not found' });
  const mode = String(req.body?.mode || 'auto');
  const promptId = req.body?.promptId ? String(req.body.promptId).slice(0, 60) : 'flashcards';
  // Caps and budget guard provider calls, not offline extraction:
  // mode=offline still works when either limit is spent.
  if (mode !== 'offline') {
    const guard = await aiGuardForWorkspace(req.workspaceId);
    if (guard.blocked) return res.status(guard.status).json(guard.body);
  }
  let candidates = null;
  let generatedBy = 'offline';
  if (mode !== 'offline') {
    try {
      const prompt = (await q('SELECT * FROM type::thing("prompt_template", $id) LIMIT 1;', { id: promptId }))[0];
      candidates = await generateStudyCandidatesWithProvider(note, prompt, req.workspaceId, req.account.sub);
      if (candidates) generatedBy = 'provider';
    } catch (error) {
      console.warn('study.generate provider fallback:', error.message);
    }
  }
  if (!candidates) candidates = generateStudyCandidates(note.content);
  const created = await createStudyItems({ candidates, noteId: recordId(note.id), source: generatedBy, accountSub: req.account.sub, workspaceId: req.workspaceId });
  await recordAudit('study.generate', req.account.sub, { count: created.length, generatedBy }, recordId(note.id), req.workspaceId);
  res.status(201).json({ created: created.length, skipped: candidates.length - created.length, generatedBy, items: created.map((row) => publicStudyItem(row)) });
});

/* ---------- Integrations: mapping + flags for external systems ---------- */

const integrationKinds = ['webhook', 'openai', 'slack', 'notion', 'github', 'obsidian', 'custom'];
const integrationDirections = ['outbound', 'inbound', 'bidirectional'];

function publicIntegration(row) {
  return {
    id: recordId(row.id),
    name: row.name,
    kind: row.kind,
    direction: row.direction || 'outbound',
    endpoint: row.endpoint || null,
    mapping: row.mapping || {},
    flags: row.flags || {},
    isEnabled: Boolean(row.is_enabled),
    hasSecret: Boolean(row.secret),
    lastStatus: row.last_status || null,
    lastRunAt: isoOrNull(row.last_run_at),
    createdAt: isoOrNull(row.created_at),
    updatedAt: isoOrNull(row.updated_at),
  };
}

const objectOrEmpty = (value) => (value && typeof value === 'object' && !Array.isArray(value) ? value : null);

app.get('/api/integrations', auth, async (_req, res) => {
  const rows = await q(`SELECT * FROM integration WHERE workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT 100;`);
  res.json(rows.map(publicIntegration));
});

app.post('/api/integrations', auth, requirePermission('settings:write'), async (req, res) => {
  const name = String(req.body?.name || '').trim().slice(0, 80);
  if (!name) return res.status(400).json({ error: 'A name is required' });
  const kind = integrationKinds.includes(String(req.body?.kind)) ? String(req.body.kind) : 'custom';
  const direction = integrationDirections.includes(String(req.body?.direction)) ? String(req.body.direction) : 'outbound';
  const data = {
    name, kind, direction,
    mapping: objectOrEmpty(req.body?.mapping) || {},
    flags: objectOrEmpty(req.body?.flags) || {},
    is_enabled: Boolean(req.body?.isEnabled),
    workspace: new RecordId('workspace', req.workspaceId),
    created_by: new RecordId('account', recordId(req.account.sub)),
    created_at: new Date(), updated_at: new Date(),
  };
  if (req.body?.endpoint) data.endpoint = String(req.body.endpoint).slice(0, 400);
  if (req.body?.secret) data.secret = String(req.body.secret).slice(0, 400);
  try {
    const rows = await createRecord('integration', data);
    await recordAudit('integration.create', req.account.sub, { kind, direction }, recordId(rows[0].id));
    res.status(201).json(publicIntegration(rows[0]));
  } catch (error) {
    if (/already contains/i.test(String(error.message))) return res.status(409).json({ error: 'An integration with that name already exists' });
    res.status(500).json({ error: 'Could not create the integration' });
  }
});

app.patch('/api/integrations/:id', auth, requirePermission('settings:write'), async (req, res) => {
  const updates = { updated_at: new Date() };
  if (req.body?.name !== undefined) {
    const name = String(req.body.name).trim().slice(0, 80);
    if (!name) return res.status(400).json({ error: 'Name cannot be empty' });
    updates.name = name;
  }
  if (req.body?.kind !== undefined && integrationKinds.includes(String(req.body.kind))) updates.kind = String(req.body.kind);
  if (req.body?.direction !== undefined && integrationDirections.includes(String(req.body.direction))) updates.direction = String(req.body.direction);
  if (req.body?.endpoint !== undefined) updates.endpoint = String(req.body.endpoint).slice(0, 400) || null;
  if (req.body?.secret) updates.secret = String(req.body.secret).slice(0, 400);
  if (req.body?.mapping !== undefined) updates.mapping = objectOrEmpty(req.body.mapping) || {};
  if (req.body?.flags !== undefined) updates.flags = objectOrEmpty(req.body.flags) || {};
  if (req.body?.isEnabled !== undefined) updates.is_enabled = Boolean(req.body.isEnabled);
  const existing = await q('SELECT id FROM type::thing("integration", $id) LIMIT 1;', { id: req.params.id });
  if (!existing[0]) return res.status(404).json({ error: 'Integration not found' });
  const rows = await updateRecord('integration', req.params.id, updates);
  await recordAudit('integration.update', req.account.sub, {}, req.params.id);
  res.json(publicIntegration(rows[0]));
});

app.delete('/api/integrations/:id', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('DELETE type::thing("integration", $id) RETURN BEFORE;', { id: req.params.id });
  if (!rows[0]) return res.status(404).json({ error: 'Integration not found' });
  await recordAudit('integration.delete', req.account.sub, {}, req.params.id);
  res.status(204).end();
});

// Probe the configured endpoint and record the outcome on the integration, so
// Settings can show whether the mapping target is actually reachable.
app.post('/api/integrations/:id/test', auth, requirePermission('settings:write'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("integration", $id) LIMIT 1;', { id: req.params.id });
  const integration = rows[0];
  if (!integration) return res.status(404).json({ error: 'Integration not found' });
  let status = 'skipped';
  let detail = '';
  if (integration.endpoint && /^https?:\/\//i.test(integration.endpoint)) {
    try {
      const response = await fetch(integration.endpoint, {
        method: 'POST',
        headers: { 'content-type': 'application/json', ...(integration.secret ? { 'x-planing-secret': integration.secret } : {}) },
        body: JSON.stringify({ event: 'ping', source: 'planing', at: new Date().toISOString() }),
        signal: AbortSignal.timeout(6000),
      });
      status = response.ok ? 'ok' : 'failed';
      detail = `HTTP ${response.status}`;
    } catch (error) { status = 'failed'; detail = error.message; }
  } else {
    detail = 'No http(s) endpoint configured';
  }
  const updated = await q('UPDATE type::thing("integration", $id) MERGE { last_status: $status, last_run_at: time::now(), updated_at: time::now() } RETURN AFTER;', { id: req.params.id, status });
  res.json({ ...publicIntegration(updated[0]), detail });
});

/* ---------- Team chat: temporary rooms, invites, and attachments ---------- */

const roomDefaultTtlHours = 24;
const roomMaxTtlHours = 24 * 30;

function isRoomOpen(room) {
  if (!room.expires_at) return true;
  return new Date(room.expires_at).getTime() > Date.now();
}

function publicRoom(row, extras = {}) {
  return {
    id: recordId(row.id),
    name: row.name,
    topic: row.topic || null,
    isTemporary: Boolean(row.is_temporary),
    expiresAt: isoOrNull(row.expires_at),
    createdBy: row.created_by ? recordId(row.created_by) : null,
    createdAt: isoOrNull(row.created_at),
    ...extras,
  };
}

function publicRoomMessage(row, authors = new Map()) {
  const authorId = row.author ? recordId(row.author) : null;
  return {
    id: recordId(row.id),
    room: recordId(row.room),
    author: authorId,
    authorName: authorId ? authors.get(authorId) || null : null,
    content: row.content,
    attachments: (Array.isArray(row.attachments) ? row.attachments : []).map((entry) => recordId(entry)),
    isSystem: Boolean(row.is_system),
    createdAt: isoOrNull(row.created_at),
  };
}

async function roomMembership(roomId, accountSub) {
  const rows = await q('SELECT * FROM chat_room_member WHERE in = type::thing("account", $id) AND out = type::thing("chat_room", $room) LIMIT 1;', { id: recordId(accountSub), room: roomId });
  return rows[0] || null;
}

// Temporary rooms clean themselves up: anything past expires_at is removed with
// its messages, membership edges, and attachment files.
async function purgeExpiredRooms() {
  const expired = await q('SELECT * FROM chat_room WHERE expires_at != NONE AND expires_at <= time::now() LIMIT 50;');
  for (const room of expired) {
    const id = recordId(room.id);
    const files = await q('SELECT * FROM attachments WHERE room = type::thing("chat_room", $id);', { id });
    for (const file of files) fs.rm(path.join(uploadDir, path.basename(file.path)), { force: true }, () => {});
    await q('DELETE attachments WHERE room = type::thing("chat_room", $id);', { id });
    await q('DELETE chat_room_message WHERE room = type::thing("chat_room", $id);', { id });
    await q('DELETE chat_room_member WHERE out = type::thing("chat_room", $id);', { id });
    await q('DELETE type::thing("chat_room", $id);', { id });
  }
  return expired.length;
}

async function roomSummary(room, accountSub) {
  const id = recordId(room.id);
  const [members, last] = await Promise.all([
    q('SELECT * FROM chat_room_member WHERE out = type::thing("chat_room", $id);', { id }),
    q('SELECT * FROM chat_room_message WHERE room = type::thing("chat_room", $id) ORDER BY created_at DESC LIMIT 1;', { id }),
  ]);
  return publicRoom(room, {
    memberCount: members.length,
    isOwner: recordId(room.created_by || '') === recordId(accountSub),
    lastMessage: last[0] ? { content: String(last[0].content).slice(0, 140), createdAt: isoOrNull(last[0].created_at), author: last[0].author ? recordId(last[0].author) : null, isSystem: Boolean(last[0].is_system) } : null,
  });
}

app.get('/api/chat/rooms', auth, async (req, res) => {
  await purgeExpiredRooms();
  const edges = await q('SELECT * FROM chat_room_member WHERE in = type::thing("account", $id);', { id: recordId(req.account.sub) });
  const roomIds = [...new Set(edges.map((edge) => recordId(edge.out)))];
  if (!roomIds.length) return res.json([]);
  // Rooms are workspace-scoped as well as membership-scoped, so a room in
  // another workspace never leaks into this one's room list.
  const rooms = await q(`SELECT * FROM chat_room WHERE id IN $ids AND workspace = ${wsLiteral(req)} ORDER BY created_at DESC LIMIT 50;`, { ids: roomIds.map((id) => new RecordId('chat_room', id)) });
  res.json(await Promise.all(rooms.map((room) => roomSummary(room, req.account.sub))));
});

app.post('/api/chat/rooms', auth, requirePermission('notes:write'), async (req, res) => {
  const fallbackName = `Room ${new Date().toISOString().slice(11, 16)}`;
  const name = String(req.body?.name || '').trim().slice(0, 80) || fallbackName;
  const ttl = Math.min(Math.max(Number(req.body?.ttlHours) || roomDefaultTtlHours, 1), roomMaxTtlHours);
  const isTemporary = req.body?.isTemporary === undefined ? true : Boolean(req.body.isTemporary);
  const data = {
    name,
    is_temporary: isTemporary,
    workspace: new RecordId('workspace', req.workspaceId),
    created_by: new RecordId('account', recordId(req.account.sub)),
    created_at: new Date(), updated_at: new Date(),
  };
  if (req.body?.topic) data.topic = String(req.body.topic).slice(0, 200);
  if (isTemporary) data.expires_at = new Date(Date.now() + ttl * 3_600_000);
  const rows = await q('CREATE chat_room CONTENT $data;', { data });
  const roomId = recordId(rows[0].id);
  await upsertEdge('chat_room_member', 'account', recordId(req.account.sub), 'chat_room', roomId, { role: 'owner', created_at: new Date() });
  const invited = await addRoomMembers(roomId, req.body?.members, req.account.sub);
  await q('CREATE chat_room_message CONTENT $data;', { data: { room: new RecordId('chat_room', roomId), content: `Room created by ${req.account.name || 'a member'}`, is_system: true, created_at: new Date() } });
  await recordAudit('room.create', req.account.sub, { invited: invited.length, temporary: isTemporary }, roomId);
  res.status(201).json({ ...(await roomSummary(rows[0], req.account.sub)), invited });
});

// Invite existing workspace members by name (or account id). Unknown names are
// reported back instead of silently dropped.
async function addRoomMembers(roomId, members, accountSub) {
  const wanted = (Array.isArray(members) ? members : (members ? [members] : [])).map((entry) => String(entry).trim()).filter(Boolean).slice(0, 50);
  const added = [];
  for (const entry of wanted) {
    const account = /^\w{6,}$/.test(entry) && !entry.includes('-') && !entry.includes(' ')
      ? (await q('SELECT * FROM account WHERE name = $name OR id = type::thing("account", $name) LIMIT 1;', { name: entry }))[0]
      : (await q('SELECT * FROM account WHERE name = $name LIMIT 1;', { name: entry }))[0];
    if (!account) { added.push({ name: entry, added: false, reason: 'unknown' }); continue; }
    const accountId = recordId(account.id);
    try {
      await upsertEdge('chat_room_member', 'account', accountId, 'chat_room', roomId, { role: 'member', created_by: new RecordId('account', recordId(accountSub)), created_at: new Date() });
      added.push({ name: account.name, added: true });
    } catch {
      added.push({ name: account.name, added: false, reason: 'already-member' });
    }
  }
  return added;
}

app.get('/api/chat/rooms/:id', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("chat_room", $id) LIMIT 1;', { id: req.params.id });
  const room = rows[0];
  if (!room) return res.status(404).json({ error: 'Room not found' });
  const membership = await roomMembership(recordId(room.id), req.account.sub);
  if (!membership) return res.status(403).json({ error: 'You are not a member of this room' });
  const members = await q('SELECT * FROM chat_room_member WHERE out = type::thing("chat_room", $id);', { id: recordId(room.id) });
  const memberIds = members.map((edge) => recordId(edge.in));
  const accounts = memberIds.length ? await q('SELECT id, name, role FROM account WHERE id IN $ids;', { ids: memberIds.map((id) => new RecordId('account', id)) }) : [];
  const names = new Map(accounts.map((account) => [recordId(account.id), account.name]));
  const messages = await q('SELECT * FROM chat_room_message WHERE room = type::thing("chat_room", $id) ORDER BY created_at ASC LIMIT 300;', { id: recordId(room.id) });
  const attachmentIds = [...new Set(messages.flatMap((message) => (Array.isArray(message.attachments) ? message.attachments : []).map((entry) => recordId(entry))))];
  const files = attachmentIds.length ? await q('SELECT * FROM attachments WHERE id IN $ids;', { ids: attachmentIds.map((id) => new RecordId('attachments', id)) }) : [];
  res.json({
    room: publicRoom(room, { isOwner: recordId(room.created_by) === recordId(req.account.sub), isOpen: isRoomOpen(room), expiresAt: isoOrNull(room.expires_at) }),
    members: members.map((edge) => ({ account: recordId(edge.in), name: names.get(recordId(edge.in)) || 'member', role: edge.role || 'member' })),
    messages: messages.map((message) => publicRoomMessage(message, names)),
    attachments: files.map(publicAttachment),
  });
});

app.patch('/api/chat/rooms/:id', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("chat_room", $id) LIMIT 1;', { id: req.params.id });
  const room = rows[0];
  if (!room) return res.status(404).json({ error: 'Room not found' });
  const isOwner = recordId(room.created_by) === recordId(req.account.sub);
  if (!isOwner && !req.account.permissions?.includes('settings:write')) return res.status(403).json({ error: 'Only the room owner can change it' });
  const updates = { updated_at: new Date() };
  if (req.body?.name !== undefined) {
    const name = String(req.body.name).trim().slice(0, 80);
    if (!name) return res.status(400).json({ error: 'Name cannot be empty' });
    updates.name = name;
  }
  if (req.body?.topic !== undefined) updates.topic = String(req.body.topic).slice(0, 200);
  let clearExpiry = false;
  if (req.body?.isTemporary !== undefined) updates.is_temporary = Boolean(req.body.isTemporary);
  if (req.body?.ttlHours !== undefined) {
    const ttl = Math.min(Math.max(Number(req.body.ttlHours) || roomDefaultTtlHours, 1), roomMaxTtlHours);
    updates.expires_at = new Date(Date.now() + ttl * 3_600_000);
  } else if (req.body?.isTemporary === false) {
    // A permanent room has no expiry; NONE is written inline because an
    // explicit null is rejected for option<datetime> fields.
    clearExpiry = true;
  }
  const assignments = literalAssignments(updates);
  if (clearExpiry) assignments.push('expires_at = NONE');
  const updated = await q(`UPDATE type::thing("chat_room", $id) SET ${assignments.join(', ')} RETURN AFTER;`, { id: req.params.id });
  res.json(publicRoom(updated[0]));
});

app.delete('/api/chat/rooms/:id', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("chat_room", $id) LIMIT 1;', { id: req.params.id });
  const room = rows[0];
  if (!room) return res.status(404).json({ error: 'Room not found' });
  if (recordId(room.created_by) !== recordId(req.account.sub) && !req.account.permissions?.includes('settings:write')) return res.status(403).json({ error: 'Only the room owner can delete it' });
  const id = recordId(room.id);
  const files = await q('SELECT * FROM attachments WHERE room = type::thing("chat_room", $id);', { id });
  for (const file of files) fs.rm(path.join(uploadDir, path.basename(file.path)), { force: true }, () => {});
  await q('DELETE attachments WHERE room = type::thing("chat_room", $id);', { id });
  await q('DELETE chat_room_message WHERE room = type::thing("chat_room", $id);', { id });
  await q('DELETE chat_room_member WHERE out = type::thing("chat_room", $id);', { id });
  await q('DELETE type::thing("chat_room", $id);', { id });
  await recordAudit('room.delete', req.account.sub, {}, id);
  res.status(204).end();
});

app.post('/api/chat/rooms/:id/members', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("chat_room", $id) LIMIT 1;', { id: req.params.id });
  const room = rows[0];
  if (!room) return res.status(404).json({ error: 'Room not found' });
  if (!(await roomMembership(recordId(room.id), req.account.sub))) return res.status(403).json({ error: 'You are not a member of this room' });
  const added = await addRoomMembers(recordId(room.id), req.body?.members, req.account.sub);
  for (const entry of added.filter((item) => item.added)) {
    await q('CREATE chat_room_message CONTENT $data;', { data: { room: new RecordId('chat_room', recordId(room.id)), content: `${entry.name} joined the room`, is_system: true, created_at: new Date() } });
  }
  await recordAudit('room.invite', req.account.sub, { added: added.filter((item) => item.added).length }, recordId(room.id));
  res.status(201).json({ invited: added });
});

app.delete('/api/chat/rooms/:id/members/:accountId', auth, async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("chat_room", $id) LIMIT 1;', { id: req.params.id });
  const room = rows[0];
  if (!room) return res.status(404).json({ error: 'Room not found' });
  const isOwner = recordId(room.created_by) === recordId(req.account.sub);
  if (!isOwner && recordId(req.params.accountId) !== recordId(req.account.sub)) return res.status(403).json({ error: 'Only the room owner can remove members' });
  await q('DELETE chat_room_member WHERE in = type::thing("account", $id) AND out = type::thing("chat_room", $room);', { id: req.params.accountId, room: recordId(room.id) });
  res.status(204).end();
});

app.post('/api/chat/rooms/:id/messages', auth, requirePermission('notes:read'), async (req, res) => {
  const rows = await q('SELECT * FROM type::thing("chat_room", $id) LIMIT 1;', { id: req.params.id });
  const room = rows[0];
  if (!room) return res.status(404).json({ error: 'Room not found' });
  if (!(await roomMembership(recordId(room.id), req.account.sub))) return res.status(403).json({ error: 'You are not a member of this room' });
  if (!isRoomOpen(room)) return res.status(410).json({ error: 'This temporary room has expired' });
  const content = String(req.body?.content || '').trim().slice(0, 4000);
  const attachmentIds = [...new Set((Array.isArray(req.body?.attachmentIds) ? req.body.attachmentIds : []).map((id) => String(id)))].slice(0, 10);
  if (!content && !attachmentIds.length) return res.status(400).json({ error: 'A message or an attachment is required' });
  const data = {
    room: new RecordId('chat_room', recordId(room.id)),
    author: new RecordId('account', recordId(req.account.sub)),
    content,
    is_system: false,
    created_at: new Date(),
  };
  if (attachmentIds.length) {
    // Only attach files the sender owns, and bind them to this room.
    const owned = await q('SELECT id FROM attachments WHERE id IN $ids AND account = type::thing("account", $account);', {
      ids: attachmentIds.map((id) => new RecordId('attachments', id)), account: recordId(req.account.sub),
    });
    data.attachments = owned.map((row) => new RecordId('attachments', recordId(row.id)));
    for (const row of owned) await q('UPDATE type::thing("attachments", $id) MERGE { room: type::thing("chat_room", $room) };', { id: recordId(row.id), room: recordId(room.id) });
  }
  const created = await q('CREATE chat_room_message CONTENT $data;', { data });
  await q('UPDATE type::thing("chat_room", $id) MERGE { updated_at: time::now() };', { id: recordId(room.id) });
  res.status(201).json(publicRoomMessage(created[0], new Map([[recordId(req.account.sub), req.account.name || 'member']])));
});

app.use((req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

await connectSurreal();
// Phase 4: telemetry ledger + retention sweeps start with the server; the
// first flush piggybacks on the hourly sweep so steady-state write volume is
// one batched transaction per hour, not one row per query.
telemetryEnabled = true;
startRetentionSweeps();
app.listen(port, '0.0.0.0', () => console.log(`Planing Surreal runtime listening on ${port}`));
