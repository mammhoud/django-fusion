#!/usr/bin/env node
/**
 * Fill agenda role ↔ object relations (derived backlinks for the Anytype graph).
 * ============================================================================
 *
 * WHY
 * ---
 * The agenda tracks *roles* — the people named in the fact tables
 * (`task-tracking.md` assignees, `feature-tracking.md` owners, plan owners in
 * `dev-team-plans.md` / `sales-pipeline.md` / …). Those mentions are the only
 * evidence of who works on which project, but nothing writes them back into the
 * knowledge graph: `objects/people/*.md` and `projects/*.md` keep hand-written
 * relations that go stale the moment a sprint is planned.
 *
 * This script reads the agenda sources, resolves the roles to Person objects and
 * the mentioned work to Project objects, and fills both directions:
 *
 *   Person object  ←  ## Assigned Objects (generated)   — `Assigned To` backlinks
 *   Project object ←  ## Related Roles / Related Documents / Related Features
 *
 * It is a *derived view*, never a new relation vocabulary. Every row names a
 * relation that already exists in `objects/_relations.md` and points at a real
 * file. Direction is respected: `Assigned To` is Task/Feature → Person, so the
 * Person block is explicitly a backlink view, while the Project object stays the
 * canonical source side. Frontmatter is only rewritten when filling a missing
 * `Owner:` from the explicit `PROJECT_OWNERS` map (or creating a Person stub) —
 * never by guessing accountability.
 *
 * ANYTYPE CLIENT MODEL (analyzed from github.com/charlesneimog/anytype-client)
 * ----------------------------------------------------------------------------
 * The markdown graph mirrors the Anytype client's object model, so this script
 * follows the same workflow its examples use — only offline:
 *
 *   anytype-client example               | this script
 *   -------------------------------------|------------------------------------------
 *   `any = anytype.Anytype(); any.auth()` | no service: the repo is the store
 *   `space.get_type_byname("Task")`       | the `Object type:` frontmatter line
 *   `space.search(q, type=[...])`         | index objects by type, then scan sources
 *   `type.add_property(Text/Number/…)`    | property names + formats per `_relations.md`
 *   `obj.properties["Owner"].value = x`   | a table row naming the relation + → path
 *   `space.create_object(obj, type=…)`    | `--create-missing` writes a Person stub
 *   `time.sleep()` between API calls      | deterministic sorted output (no network)
 *
 * `zotero2anytype.py`, `doi-citations.py` and `search-by-type.py` all create
 * typed objects and attach relation/select properties; `--emit-anytype` writes
 * the same shape (`{ name, type, properties: { <relation>: { value } } }`) so a
 * later push through the Python client needs no re-modeling. Per
 * `docs/agenda/anytype-extensibility.md` no Anytype service is integrated into
 * this stack — the export is a file, not a connection.
 *
 * USAGE
 * -----
 *   node agenda/scripts/link-agenda-relations.mjs                 # write blocks
 *   node agenda/scripts/link-agenda-relations.mjs --check         # CI: exit 1 if stale
 *   node agenda/scripts/link-agenda-relations.mjs --dry-run       # report only
 *   node agenda/scripts/link-agenda-relations.mjs --no-create-missing
 *   node agenda/scripts/link-agenda-relations.mjs --emit-anytype /tmp/agenda-anytype.json
 *
 * (from `docs/`; also wired as `npm run agenda-relations` / `agenda-relations:check`.)
 */
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// ── Paths ───────────────────────────────────────────────────────────────────

const AGENDA_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MONO_ROOT = path.join(AGENDA_ROOT, '.mono-repo');
const PEOPLE_DIR = path.join(MONO_ROOT, 'objects', 'people');
const PROJECTS_DIR = path.join(MONO_ROOT, 'projects');

// ── Config ─────────────────────────────────────────────────────────────────

/** Agenda sources scanned for role ↔ object mentions. */
const SOURCE_FILES = [
  'task-tracking.md',
  'feature-tracking.md',
  'team-notes.md',
  'sales-pipeline.md',
  'dev-team-plans.md',
  'marketing-plans.md',
  'pricing-plans.md',
  'data-analyst-plans.md',
  'meeting-agenda.md',
  'completion-checklist.md',
];
/** Directories whose files are also scanned (project-attributed stories). */
const SOURCE_DIRS = ['case-studies'];

/**
 * Handle → Person object slug. A handle resolves to a Person when it matches the
 * object's file stem or `# Title` case-insensitively; this map only covers
 * handles whose name matches neither (the founder's object is `people/me.md`
 * while the agenda assigns `@mammhoud`).
 */
const HANDLE_ALIASES = {
  mammhoud: 'me',
};

/**
 * `@`-mentions that are not people: table placeholders, decorators, vendor and
 * package names. Keeps the scan from inventing Person stubs.
 */
const HANDLE_STOPWORDS = new Set([
  'assignee', 'person', 'member', 'owner', 'team', 'reviewer', 'param', 'params',
  'returns', 'type', 'classmethod', 'staticmethod', 'property', 'bolt', 'structa',
  'tauri', 'postiz', 'docus', 'media', 'font', 'import', 'apply', 'decorator',
  'gmail', 'example', 'test', 'app', 'api',
]);

/**
 * Project keyword → project object slug. Matched case-insensitively on word
 * boundaries; the longest match on a line wins, so `loop-crm` is not also
 * credited to `crm`.
 */
const PROJECT_ALIASES = {
  'loop-crm-merge': ['loop-crm', 'loop crm', 'crm'],
  'ctc-research-platform': ['ctc', 'precis-ctc', 'research center'],
  'formint-editions-chain': ['formint', 'formints', 'formint-pos', 'pos'],
  'docs-agenda-system': ['agenda', 'documentation', 'docus', 'docs pipeline'],
  'django-fusion-library': ['django-fusion', 'django fusion', 'fusion'],
};

/**
 * Accountable owner per project, when the graph already states one. Only these
 * are written (to `Owner:`); the script never guesses accountability.
 */
const PROJECT_OWNERS = {
  'loop-crm-merge': 'me',
  'ctc-research-platform': 'moustafa',
  'formint-editions-chain': 'moustafa',
  'docs-agenda-system': 'me',
  'django-fusion-library': 'mahmoud',
};

const MARK_START = '<!-- agenda-relations:start — generated by scripts/link-agenda-relations.mjs (do not edit) -->';
const MARK_END = '<!-- agenda-relations:end -->';
const MAX_SECTIONS_PER_DOC = 4;

// ── Args ───────────────────────────────────────────────────────────────────

const argv = process.argv.slice(2);
const flag = (name) => argv.includes(name);
const value = (name) => {
  const i = argv.indexOf(name);
  return i >= 0 ? argv[i + 1] : undefined;
};

const CHECK = flag('--check');
const DRY_RUN = flag('--dry-run');
const CREATE_MISSING = !flag('--no-create-missing');
const EMIT_PATH = value('--emit-anytype');

// ── Small helpers ──────────────────────────────────────────────────────────

const toPosix = (p) => p.split(path.sep).join('/');
const link = (fromFile, target, label, sep = '—') =>
  `→ \`${toPosix(path.relative(path.dirname(fromFile), target))}\` ${sep} ${label}`;
const agendaPath = (...parts) => path.join(AGENDA_ROOT, ...parts);

function splitFrontmatter(source) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) return { frontmatter: null, body: source };
  return { frontmatter: match[1], body: source.slice(match[0].length) };
}

function frontmatterValue(frontmatter, key) {
  const match = frontmatter?.match(new RegExp(`^${key}:[ \\t]*(.*)$`, 'm'));
  return match ? match[1].trim() : null;
}

const listValue = (raw) =>
  (raw ?? '').split(',').map((p) => p.trim()).filter(Boolean);

const slugify = (v) => v.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
/** Cell → label: unwrap markdown links and drop emphasis so tables stay plain text. */
const cleanLabel = (v) =>
  (v ?? '').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/[*`]/g, '').replace(/\s+/g, ' ').trim();
const humanize = (slug) => slug.split('-').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ');

/** Skip fenced code (mermaid, snippets) and our own generated blocks. */
function scannableLines(body) {
  const out = [];
  let inFence = false;
  let inGenerated = false;
  for (const line of body.split('\n')) {
    if (line.trim().startsWith('```')) inFence = !inFence;
    else if (line.includes('<!-- agenda-relations:start')) inGenerated = true;
    else if (line.includes('<!-- agenda-relations:end -->')) inGenerated = false;

    if (!inFence && !inGenerated && !line.includes('<!-- agenda-relations:')) out.push(line);
  }
  return out;
}

/**
 * Flatten a source into `{ kind, heading, line, cells, header }` entries, keeping the
 * nearest heading for `source § section` refs. Tables are parsed properly — the row
 * above a `|---|` separator is the header — so column lookups never guess.
 */
function sourceEntries(body) {
  const lines = scannableLines(body);
  const entries = [];
  let heading = '';
  let run = [];

  const flushRun = () => {
    if (!run.length) return;
    const separator = run.findIndex((r) => r.separator);
    const header = run[0].cells;
    const dataStart = separator === 1 ? 2 : 1; // no separator → treat first row as header
    for (const row of run.slice(dataStart)) {
      entries.push({ kind: 'row', heading: row.heading, line: row.line, cells: row.cells, header });
    }
    run = [];
  };

  for (const line of lines) {
    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if (h) heading = h[2].trim();

    const cells = tableCells(line);
    if (cells) {
      run.push({ cells, line, heading, separator: false });
      continue;
    }
    const trimmed = line.trim();
    if (/^\|[\s:|-]+\|$/.test(trimmed)) {
      // separator row — keep the run intact, the first row is its header
      if (run.length) run.push({ cells: [], line, heading, separator: true });
      continue;
    }
    flushRun();
    entries.push({ kind: 'line', heading, line });
  }
  flushRun();
  return entries;
}

/** Strip emails first so `a@b.com` never yields a person handle. */
const readHandles = (line) =>
  [...new Set([...line.replace(/\S+@\S+\.\S+/g, ' ').matchAll(/@([a-z][a-z0-9_-]*)/gi)].map((m) => m[1].toLowerCase()))];

const ALIASES = Object.entries(PROJECT_ALIASES)
  .flatMap(([slug, aliases]) =>
    aliases.map((alias) => ({
      slug,
      alias: alias.toLowerCase(),
      re: new RegExp(`\\b${alias.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i'),
    })),
  )
  .sort((a, b) => b.alias.length - a.alias.length);

/** Longest-match project keywords on one line (nested shorter match ignored). */
function readProjects(line) {
  const found = new Map();
  for (const { slug, alias, re } of ALIASES) {
    if (!re.test(line)) continue;
    const covered = [...found.values()].some((f) => f.alias.includes(alias) || alias.includes(f.alias));
    if (covered) continue;
    found.set(slug, { slug, alias });
  }
  return [...found.values()];
}

/** Table cells of a data row; `null` for non-table and separator rows. */
function tableCells(line) {
  const trimmed = line.trim();
  if (!trimmed.startsWith('|') || !trimmed.endsWith('|')) return null;
  if (/^\|[\s:|-]+\|$/.test(trimmed)) return null;
  return trimmed.slice(1, -1).split('|').map((c) => c.trim());
}

const cleanHeader = (cell) => cell.toLowerCase().replace(/[*`]/g, '').trim();

/**
 * Column lookup on a real header row: exact match first, then a short-cell
 * `includes` fallback (`Owner (role)`) that never swallows prose headings like
 * "Owner action".
 */
function columnIndex(header, ...names) {
  for (const name of names) {
    const i = header.findIndex((c) => cleanHeader(c) === name);
    if (i >= 0) return i;
  }
  for (const name of names) {
    const i = header.findIndex((c) => {
      const clean = cleanHeader(c);
      return clean.length <= 18 && clean.includes(name);
    });
    if (i >= 0) return i;
  }
  return -1;
}

/** A cell that names a person/team, not a sentence, heading or empty marker. */
function isRoleCell(cell) {
  if (!cell || cell.length > 40) return false;
  if (cell.includes('*') || cell.includes('`')) return false;
  const bare = cell.trim();
  if (!bare || bare === '—' || bare === '-') return false;
  return /^(@[\w-]+|TBD|[A-Z][\p{L}.'-]*(?: [A-Z][\p{L}.'-]*){0,3}(?: team)?)$/u.test(bare);
}

// ── Load the graph ─────────────────────────────────────────────────────────

async function readObject(file, kind) {
  const source = await readFile(file, 'utf8');
  const { frontmatter, body } = splitFrontmatter(source);
  const title = (body.match(/^#\s+(.*)$/m)?.[1] ?? path.basename(file, '.md')).trim();
  return {
    file,
    kind,
    slug: slugify(path.basename(file, '.md')),
    title,
    role: frontmatterValue(frontmatter, 'Role'),
    status: frontmatterValue(frontmatter, 'Status'),
    frontmatter: frontmatter ?? '',
    source,
    body,
  };
}

async function loadObjects(dir, kind) {
  const names = (await readdir(dir, { withFileTypes: true }))
    .filter((e) => e.isFile() && e.name.endsWith('.md') && !e.name.startsWith('_'))
    .map((e) => e.name)
    .sort();
  return Promise.all(names.map((n) => readObject(path.join(dir, n), kind)));
}

async function loadSources() {
  const sources = [];
  const push = async (rel, file) => {
    const body = splitFrontmatter(await readFile(file, 'utf8')).body;
    sources.push({ rel, entries: sourceEntries(body) });
  };
  for (const name of SOURCE_FILES) {
    try {
      await push(name, agendaPath(name));
    } catch {
      // a fact table can be retired; skip rather than fail the graph
    }
  }
  for (const dir of SOURCE_DIRS) {
    let entries = [];
    try {
      entries = await readdir(agendaPath(dir), { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (entry.isFile() && entry.name.endsWith('.md') && entry.name !== 'INDEX.md') {
        await push(`${dir}/${entry.name}`, agendaPath(dir, entry.name));
      }
    }
  }
  return sources;
}

// ── Scan ───────────────────────────────────────────────────────────────────

async function scan() {
  const peopleList = await loadObjects(PEOPLE_DIR, 'person');
  const projectList = await loadObjects(PROJECTS_DIR, 'project');
  const people = new Map(peopleList.map((p) => [p.slug, p]));
  const projects = new Map(projectList.map((p) => [p.slug, p]));

  const personIndex = new Map();
  for (const person of peopleList) {
    personIndex.set(person.slug, person);
    personIndex.set(slugify(person.title), person);
  }
  for (const [handle, slug] of Object.entries(HANDLE_ALIASES)) {
    const person = people.get(slug);
    if (person) personIndex.set(handle, person);
  }
  const resolvePersonCell = (cell) => people.get(slugify(cell)) ?? personIndex.get(slugify(cell)) ?? null;

  const assigned = new Map(); // personSlug → Map(rowKey → row)
  const related = new Map(); // projectSlug → { people, docs: Map<file, Set<section>>, features: Set }
  const unknownHandles = new Map(); // handle → Set(ref)
  const unowned = new Map(); // value → Set(ref)

  const entryFor = (slug) => {
    if (!related.has(slug)) related.set(slug, { people: new Map(), docs: new Map(), features: new Set() });
    return related.get(slug);
  };
  for (const project of projects.values()) entryFor(project.slug);

  const sources = await loadSources();
  for (const source of sources) {
    for (const entry of source.entries) {
      const { heading, line, cells, header, kind } = entry;
      const ref = `${source.rel} § ${heading || 'top'}`;
      const projectsOnLine = readProjects(line);

      // Document ← project attribution (any line naming a project).
      for (const { slug } of projectsOnLine) {
        const target = entryFor(slug);
        const [file, section] = ref.split(' § ');
        if (!target.docs.has(file)) target.docs.set(file, new Set());
        if (section !== 'top') target.docs.get(file).add(section);
      }

      if (kind !== 'row') continue;

      const cellAt = (...names) => {
        const i = columnIndex(header, ...names);
        return i >= 0 ? (cells[i] ?? null) : null;
      };
      const ownerCell = cellAt('assignee', 'owner', 'lead');
      const taskCell = cleanLabel(cellAt('task'));
      const featureCell = cleanLabel(cellAt('feature'));

      // Non-Person accountability (teams, TBD) — reported, never invented.
      if (ownerCell && isRoleCell(ownerCell) && !/^@/.test(ownerCell) && !resolvePersonCell(ownerCell)) {
        if (!unowned.has(ownerCell)) unowned.set(ownerCell, new Set());
        unowned.get(ownerCell).add(ref);
      }

      for (const handle of readHandles(line)) {
        if (HANDLE_STOPWORDS.has(handle)) continue;
        const person = personIndex.get(handle) ?? people.get(slugify(handle)) ?? null;
        if (!person) {
          if (!unknownHandles.has(handle)) unknownHandles.set(handle, new Set());
          unknownHandles.get(handle).add(ref);
          continue;
        }

        const isAssignee = Boolean(ownerCell) && new RegExp(`@${handle}\\b`, 'i').test(ownerCell);
        const rows = assigned.get(person.slug) ?? new Map();
        assigned.set(person.slug, rows);
        const addRow = (objectSlug, label, projectSlug) => {
          rows.set(`${objectSlug}|${label}|${ref}`, {
            relation: 'Assigned To',
            objectSlug,
            label,
            projectSlug,
            source: ref,
          });
        };

        for (const { slug: projectSlug } of projectsOnLine) {
          if (!isAssignee) continue;
          addRow(`project:${projectSlug}`, projects.get(projectSlug)?.title ?? humanize(projectSlug), projectSlug);
          entryFor(projectSlug).people.set(person.slug, { person, relation: 'Assigned To', source: ref });
        }
        if (featureCell && featureCell !== '—' && featureCell.length < 80 && slugify(featureCell) !== 'feature') {
          const projectSlug = projectsOnLine[0]?.slug ?? null;
          addRow(`feature:${slugify(featureCell)}`, featureCell, projectSlug);
          if (projectSlug) entryFor(projectSlug).features.add(featureCell);
        }
        if (taskCell && taskCell !== '—' && slugify(taskCell) !== 'task') {
          addRow(`task:${slugify(taskCell)}`, taskCell, projectsOnLine[0]?.slug ?? null);
        }
        // Nothing captured but the row does assign this handle → keep the trail.
        if (isAssignee && !projectsOnLine.length && !featureCell && !taskCell) {
          addRow(`source:${slugify(ref)}`, source.rel, null);
        }
      }
    }
  }

  return { people, projects, assigned, related, unknownHandles, unowned, sources };
}

// ── Render ─────────────────────────────────────────────────────────────────

const sortByLabel = (a, b) => a.label.localeCompare(b.label) || a.source.localeCompare(b.source);

function personBlock(person, rows) {
  const lines = [
    MARK_START,
    '',
    '## Assigned Objects (generated)',
    '',
    '> Backlink view derived from the agenda fact tables by',
    '> `docs/agenda/scripts/link-agenda-relations.mjs`. `Assigned To` is',
    '> Feature/Task → Person in `_relations.md`, so each row shows what assigns',
    '> *to* this person; the project object holds the canonical source side.',
    '',
  ];

  const projectSlugs = [...new Set(rows.map((r) => r.projectSlug).filter(Boolean))];
  if (projectSlugs.length) {
    const projectLinks = projectSlugs
      .sort()
      .map((slug) => link(person.file, path.join(PROJECTS_DIR, `${slug}.md`), humanize(slug)))
      .join(' · ');
    lines.push(`**Projects:** ${projectLinks}`, '');
  }

  lines.push('| Relation | Object | Project | Source |', '|---|---|---|---|');
  for (const row of [...rows].sort(sortByLabel)) {
    const object =
      row.objectSlug.startsWith('project:')
        ? link(person.file, path.join(PROJECTS_DIR, `${row.objectSlug.slice(8)}.md`), row.label)
        : `\`${row.label}\``;
    const project = row.projectSlug
      ? link(person.file, path.join(PROJECTS_DIR, `${row.projectSlug}.md`), humanize(row.projectSlug))
      : '—';
    lines.push(`| \`${row.relation}\` | ${object} | ${project} | \`${row.source}\` |`);
  }

  lines.push('', MARK_END);
  return lines.join('\n');
}

function projectBlock(project, entry) {
  const lines = [
    MARK_START,
    '',
    '## Related Roles (generated)',
    '',
    '> Roles filled from the agenda fact tables by',
    '> `docs/agenda/scripts/link-agenda-relations.mjs`. Relation names are',
    '> canonical — see `../objects/_relations.md`.',
    '',
  ];

  const roleRows = [...entry.people.values()].sort((a, b) => a.person.title.localeCompare(b.person.title));
  if (roleRows.length) {
    lines.push('| Person | Role | Relation | Source |', '|---|---|---|---|');
    for (const { person, relation, source } of roleRows) {
      lines.push(
        `| ${link(project.file, path.join(PEOPLE_DIR, `${person.slug}.md`), person.title)} ` +
          `| ${person.role ?? '—'} | \`${relation}\` | \`${source}\` |`,
      );
    }
  } else {
    lines.push('_No agenda role mentions resolved yet._');
  }

  if (entry.docs.size) {
    lines.push('', '## Related Documents (generated)', '', '| Document | Sections |', '|---|---|');
    for (const [file, sections] of [...entry.docs].sort((a, b) => a[0].localeCompare(b[0]))) {
      const all = [...sections].sort();
      const shown = all.slice(0, MAX_SECTIONS_PER_DOC).map((s) => `\`${s}\``).join(' · ');
      const more = all.length > MAX_SECTIONS_PER_DOC ? ` · +${all.length - MAX_SECTIONS_PER_DOC} more` : '';
      lines.push(`| ${link(project.file, agendaPath(file), file)} | ${all.length ? shown + more : '—'} |`);
    }
  }

  if (entry.features.size) {
    lines.push('', '## Related Features (generated)', '');
    for (const feature of [...entry.features].sort((a, b) => a.localeCompare(b))) lines.push(`- ${feature}`);
  }

  lines.push('', MARK_END);
  return lines.join('\n');
}

/**
 * Replace the generated block in place (idempotent), or insert it before the
 * closing `## Related` section so hand-written relations stay last.
 */
function upsertBlock(source, block) {
  const escaped = MARK_START.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const pattern = new RegExp(`(?:\\r?\\n)?${escaped}[\\s\\S]*?${MARK_END}\\r?\\n?`);
  if (pattern.test(source)) return source.replace(pattern, `\n${block}\n`);

  const related = source.match(/\n## Related\r?\n/);
  if (related) {
    const at = related.index;
    return `${source.slice(0, at)}\n${block}\n${source.slice(at)}`;
  }
  return `${source.replace(/\s*$/, '')}\n\n${block}\n`;
}

/** Fill a missing `Owner:` from PROJECT_OWNERS (Project type property). */
function withOwner(project, ownerName) {
  if (!ownerName || !project.frontmatter || frontmatterValue(project.frontmatter, 'Owner')) return null;
  const next = project.source.replace(/^(Status:.*)$/m, `$1\nOwner: ${ownerName}`);
  return next === project.source ? null : next;
}

// ── Anytype export (anytype-client object shape) ───────────────────────────

/**
 * Export the graph in `anytype-client` object shape.
 *
 * `properties` holds only canonical, correctly-directed relations (Person →`Assigned Tasks`,
 * Project →`Owner`/`Related Teams`/`Related Features`) so an import writes valid links.
 * `backlinks` holds the reverse-view rows the markdown tables show (a Project listing the
 * people assigned to it) and must NOT be written as properties — that direction belongs to
 * the other object.
 */
function anytypeExport(result) {
  const objects = [];

  for (const [slug, rows] of result.assigned) {
    const person = result.people.get(slug);
    const labels = (prefix) =>
      [...rows.values()].filter((r) => r.objectSlug.startsWith(prefix)).map((r) => r.label).sort();
    const properties = { Role: { value: person.role ?? 'Contributor' } };
    const tasks = labels('task:');
    if (tasks.length) properties['Assigned Tasks'] = { value: tasks };

    const backlinks = {};
    const features = labels('feature:');
    const projects = labels('project:');
    if (features.length) backlinks['Assigned To'] = features;
    if (projects.length) backlinks['Related Project'] = projects;

    objects.push({ name: person.title, type: 'Person', properties, ...(Object.keys(backlinks).length ? { backlinks } : {}) });
  }

  for (const [slug, entry] of result.related) {
    const project = result.projects.get(slug);
    if (!project) continue;
    const properties = {};
    const owner = result.people.get(PROJECT_OWNERS[slug]);
    if (owner) properties.Owner = { value: owner.title };
    const teams = listValue(frontmatterValue(project.frontmatter, 'Related Teams'));
    if (teams.length) properties['Related Teams'] = { value: teams };
    if (entry.features.size) properties['Related Features'] = { value: [...entry.features].sort() };

    const backlinks = {};
    if (entry.people.size) {
      backlinks['Assigned To'] = [...entry.people.values()].map((p) => p.person.title).sort();
    }

    objects.push({ name: project.title, type: 'Project', properties, ...(Object.keys(backlinks).length ? { backlinks } : {}) });
  }

  return {
    generatedBy: 'docs/agenda/scripts/link-agenda-relations.mjs',
    source: 'docs/agenda/',
    target: 'Anytype Channel (Vault → Channel → Objects)',
    note:
      'Shape matches anytype-client `anytype.Object` + `properties[name].value`. Write only `properties`; ' +
      '`backlinks` are reverse-view rows (e.g. Project listing its assignees) that must not be imported as ' +
      'properties. No service is connected.',
    objects,
  };
}

// ── Main ───────────────────────────────────────────────────────────────────

const result = await scan();
const changes = [];
const created = [];

for (const person of result.people.values()) {
  const rows = result.assigned.get(person.slug);
  if (!rows?.size) continue;
  const next = upsertBlock(person.source, personBlock(person, [...rows.values()]));
  if (next !== person.source) changes.push({ file: person.file, kind: 'person', next });
}

for (const project of result.projects.values()) {
  const entry = result.related.get(project.slug);
  const owner = result.people.get(PROJECT_OWNERS[project.slug]);
  const ownerPatch = withOwner(project, owner?.title);
  const base = ownerPatch ?? project.source;
  const next =
    entry && (entry.people.size || entry.docs.size || entry.features.size)
      ? upsertBlock(base, projectBlock(project, entry))
      : base;

  if (next !== project.source) changes.push({ file: project.file, kind: 'project', next });
}

// Missing Person objects for real handles (anytype-client `create_object`
// equivalent — a stub the team can fill in and re-run).
if (CREATE_MISSING && !CHECK && !DRY_RUN) {
  for (const [handle, refs] of result.unknownHandles) {
    const file = path.join(PEOPLE_DIR, `${slugify(handle)}.md`);
    const stub = [
      '---',
      'Object type: Person',
      'Tags: people',
      'Status: Active',
      'Role: Contributor',
      '---',
      '',
      `# ${humanize(handle)}`,
      '',
      `> Created by \`docs/agenda/scripts/link-agenda-relations.mjs\` — the agenda assigns`,
      `> \`@${handle}\` but no Person object existed. Fill in the real role, then re-run.`,
      '',
      '## Responsibilities',
      '',
      '- Assigned agenda work — see `../_templates.md` for the Person template',
      '',
      '## Related',
      '',
      '- → `../people.md` — Person object type',
      '- → `../_templates.md` — Object templates',
      '',
      `<!-- first referenced in: ${[...refs].sort().slice(0, 3).join(' · ')} -->`,
      '',
    ].join('\n');
    await mkdir(PEOPLE_DIR, { recursive: true });
    await writeFile(file, stub, 'utf8');
    created.push({ handle, file, refs: [...refs].sort() });
  }
}

if (!CHECK && !DRY_RUN) {
  for (const change of changes) await writeFile(change.file, change.next, 'utf8');
}

if (EMIT_PATH) {
  const target = path.resolve(process.cwd(), EMIT_PATH);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, `${JSON.stringify(anytypeExport(result), null, 2)}\n`, 'utf8');
}

// ── Report ─────────────────────────────────────────────────────────────────

const docsLinked = [...result.related.values()].reduce((n, e) => n + e.docs.size, 0);
const rel = (file) => toPosix(path.relative(process.cwd(), file));

console.log('Agenda role ↔ object relations');
console.log(`  sources scanned      : ${result.sources.length}`);
console.log(`  persons with work    : ${result.assigned.size} / ${result.people.size}`);
console.log(`  projects linked      : ${result.related.size}`);
console.log(`  document files       : ${docsLinked}`);
console.log(
  `  ${CHECK || DRY_RUN ? 'files needing update' : 'files written'} : ${changes.length}` +
    (created.length ? ` (+${created.length} person stubs created)` : ''),
);
for (const change of changes) console.log(`    ${rel(change.file)} (${change.kind})`);
for (const stub of created) console.log(`    created ${rel(stub.file)} (@${stub.handle}) ← ${stub.refs.join(', ')}`);

if (result.unknownHandles.size) {
  console.log('  unknown handles      :');
  for (const [handle, refs] of [...result.unknownHandles].sort()) {
    console.log(`    @${handle} ← ${[...refs].sort().join(', ')}${CREATE_MISSING ? '' : ' (stub not created)'}`);
  }
}
if (result.unowned.size) {
  console.log('  non-person owners    :');
  const entries = [...result.unowned].sort((a, b) => a[0].localeCompare(b[0]));
  for (const [owner, refs] of entries.slice(0, 10)) {
    console.log(`    ${owner} ← ${[...refs].sort().slice(0, 2).join(', ')}`);
  }
  if (entries.length > 10) console.log(`    … ${entries.length - 10} more`);
}
if (EMIT_PATH) console.log(`  anytype export       : ${EMIT_PATH}`);

if (CHECK) {
  const drift = changes.length > 0 || result.unknownHandles.size > 0;
  console.log(
    drift
      ? '✗ stale — run `node agenda/scripts/link-agenda-relations.mjs` to regenerate.'
      : '✓ relations are up to date.',
  );
  process.exitCode = drift ? 1 : 0;
}
