/* Curated sample content for previewing markdown, GFM rendering, the planning
   model (kanban + calendar), and the spaced-recall flow.
   Loaded via POST /api/samples (idempotent — same fixed ids as workspace
   import, so re-loading never duplicates). */

const categories = [
  { name: 'Playbook', slug: 'playbook', color: '#0a0a0a', icon: 'P', isSystem: false },
  { name: 'Specs', slug: 'specs', color: '#e61919', icon: 'S', isSystem: false },
  { name: 'Planning', slug: 'planning', color: '#e61919', icon: 'K', isSystem: false },
  { name: 'Release', slug: 'release', color: '#0a0a0a', icon: 'R', isSystem: false },
];

// Deterministic dates relative to first load so the calendar always has entries
// without hard-coding a year that will drift.
const day = 24 * 60 * 60 * 1000;
const at = (offsetDays, hour = 9) => {
  const date = new Date(Date.now() + offsetDays * day);
  date.setHours(hour, 0, 0, 0);
  return date.toISOString();
};

const note = (id, category, tags, content, extra = {}) => ({
  id, category, tags, content,
  isArchived: false, isRecycle: false, isTop: false, isShare: false,
  status: 'todo', priority: 'medium', position: 0,
  metadata: {}, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
  ...extra,
});

export function sampleContent() {
  // Every sample is also cross-linked by [[wiki link]] so the link graph, the
  // backlink panel, and the "linked from" side all have real data on a fresh
  // install instead of an empty "no outgoing links yet" state.
  return {
    schemaVersion: 'workspace-v1',
    categories,
    notes: [
      note('sample-gfm-showcase', 'playbook', ['markdown', 'guide'], `# Markdown showcase

Everything below renders through the **shared GFM renderer** used by note cards and public share pages.

## Text formatting

Bold **works**, italic *works*, underscore _italics too_, strikethrough ~~gone~~, ==highlighted text==, and \`inline code\`.

## Lists

- Unordered item one
- Unordered item two
- Nested children keep their lane
  - Child item A
  - Child item B

1. First ordered step
2. Second ordered step
3. Third ordered step

- [x] Ship the shared renderer
- [x] Keep escaping airtight
- [ ] Read this sample
- [ ] Try the copy-markdown action

## Table

| Feature | Status | Notes |
| :------ | :----: | ----: |
| Headings | OK | ATX style |
| Tables | OK | With alignment |
| Task lists | OK | Checkboxes render |

## Quote

> Capture the thought before it disappears.
> Keep the context close.

## Code

\`\`\`js
// fenced blocks show their language
export function greet(name) {
  return \`Hello, \${name}!\`;
}
\`\`\`

\`\`\`sql
SELECT * FROM notes WHERE is_share = true LIMIT 5;
\`\`\`

## Links and rules

See the reference design for this workspace.

## Connected notes

This sample set is wired together so the link graph has something to show:

- [[Agent operating brief]] — how agents should use this workspace
- [[Spec review checklist]] — the checklist this showcase is verified against
- [[Study note from source]] — turning a source document into cards
- [[Release notes: rename + planning]] — what changed in the latest release
- [[ملاحظة ثنائية الاتجاه]] — the Arabic sample, linked by its own title

---

*Edit any note to see the same content in the editor.*`, { status: 'done', priority: 'low' }),

      note('sample-agent-brief', 'agent', ['agent', 'brief'], `## Agent operating brief

> Keep answers concise. Cite the relevant note. Ask before changing shared context.

### Retrieval rules

1. Search the **Notes** lane before answering
2. Prefer notes tagged \`#agent\`
3. Quote at most three lines per citation

| Signal | Source |
| ------ | ------ |
| Voice | \`#brief\` notes |
| Tasks | \`#guide\` notes |

- [ ] Review this brief weekly
- [x] Register the operating context in Settings → AI

### Linked material

- [[Markdown showcase]] defines the formatting this brief assumes
- [[Spec review checklist]] tracks what still needs coverage`, { isTop: true, status: 'doing', priority: 'high' }),

      note('sample-spec-checklist', 'specs', ['guide', 'process'], `# Spec review checklist

### Before merge

- [x] Data model matches the SurrealDB schema
- [x] API contract documented
- [ ] Playwright coverage for the new flow
- [ ] EN/AR strings complete

### Rollback

1. Revert the deployment tag
2. Re-run the last \`/api/export\` backup if rows drifted
3. Confirm \`/health\` reports the previous \`schemaVersion\`

> A rollback that is not rehearsed is a rumor.

### References

- [[Agent operating brief]] owns the retrieval rules
- [[Markdown showcase]] is the rendering contract

- [ ] Cover the recall queue ([[Study note from source]] has the pattern)`, { status: 'review', priority: 'urgent', dueDate: at(2) }),

      note('sample-rtl-note', 'notes', ['arabic'], `# ملاحظة ثنائية الاتجاه

هذه ملاحظة تجريبية بالعربية لمعاينة الاتجاه من اليمين إلى اليسار مع تنسيق **غامق** و\`رمز برمجي\`.

- العنصر الأول
- العنصر الثاني
- [ ] مهمة غير مكتملة

> الاقتباسات تعمل أيضاً في الاتجاه المعاكس.

## ملاحظات مرتبطة

- [[Markdown showcase]] يعرض كل عناصر التنسيق
- [[Agent operating brief]] يشرح قواعد الاسترجاع
- [[Spec review checklist]] قائمة التحقق قبل الدمج
- [[Release notes: rename + planning]] أحدث التغييرات`, { status: 'backlog', priority: 'low' }),

      note('sample-study-source', 'playbook', ['study', 'recall'], `# Study note from source

A worked example of turning a source document into recallable cards. Use the **Cards** action on this note to build the queue.

## Photosynthesis

Light energy becomes chemical energy in the thylakoid membrane, then the Calvin cycle fixes carbon into sugar.

- Thylakoid :: the membrane stack where light reactions happen
- Calvin cycle :: the carbon-fixing stage that needs no light directly
- Chlorophyll :: the pigment that absorbs light energy

## Recall prompts

1. Where do the light reactions happen?
2. What does the Calvin cycle produce?
3. Why are leaves green?

### Related

- [[Markdown showcase]] shows how the cards render
- [[Spec review checklist]] tracks the recall-queue acceptance criteria
- [[Study deck: systems design]] continues the pattern`, { status: 'doing', priority: 'medium', position: 1 }),

      note('sample-study-deck', 'playbook', ['study', 'recall', 'systems'], `# Study deck: systems design

A second seed deck. Every \`term :: definition\` line below becomes a flashcard when you press **Cards**.

## Caching

- Cache stampede :: many requests rebuild the same expired entry at once
- Write-through :: writes go to the cache and the store in the same call
- Negative cache :: remembering that a lookup missed so it is not retried blindly

## Consistency

- CAP theorem :: under a partition you choose consistency or availability
- Read-your-writes :: a client always sees its own committed writes
- Idempotency key :: a caller token that makes a retried write safe

## Queues

- Backpressure :: refusing new work when the queue is already saturated
- Dead-letter queue :: where a message goes after its retry budget is spent
- Fan-out :: one event delivered to many independent consumers

## Recall checks

1. What problem does a cache stampede describe?
2. When is a negative cache useful?
3. What does an idempotency key protect against?

### Related

- [[Study note from source]] is the simpler worked example
- [[Release notes: rename + planning]] lists the flashcard changes`, { status: 'todo', priority: 'high', position: 2, dueDate: at(3) }),

      note('sample-planning-board', 'planning', ['kanban', 'calendar', 'planning'], `# Planning board seed

This note is a plan item. Open **Kanban** to see it as a card, and **Calendar** to see it on its due date.

## What the planning model stores

| Field | Meaning |
| ----- | ------- |
| \`status\` | Kanban column: backlog, todo, doing, review, done |
| \`priority\` | low, medium, high, urgent |
| \`position\` | Manual order inside the column |
| \`due_date\` | Calendar deadline |
| \`start_date\` / \`end_date\` | Calendar span |

## Checklist

- [x] Rename the tool
- [x] Add kanban columns
- [x] Add calendar month/week/day
- [ ] Wire drag-and-drop ordering to \`POST /api/kanban/move\`

### Related

- [[Release notes: rename + planning]] documents the release
- [[Spec review checklist]] gates the merge`, { status: 'doing', priority: 'urgent', position: 0, dueDate: at(1), startDate: at(0), endDate: at(1), eventColor: '#e61919' }),

      note('sample-release-notes', 'release', ['release', 'changelog', 'latest'], `# Release notes: rename + planning

## Latest changes

1. **Renamed** the tool to Planing everywhere: compose service, container, Makefile, Traefik route, API namespace, i18n, and the deployed runtime.
2. **Kanban board** added as a first-class view. Cards are notes; columns are \`status\`; drag-and-drop calls \`POST /api/kanban/move\`.
3. **Calendar** added with month, week, and day modes, reading the real \`due_date\` / \`start_date\` / \`end_date\` fields.
4. **Data model** extended with \`status\`, \`priority\`, \`position\`, \`due_date\`, \`start_date\`, \`end_date\`, \`event_color\`, and \`assignee\`, plus indexes for each planning query.
5. **Industrial UI** applied: aviation red accent, matte paper substrate, zero border-radius, mono uppercase telemetry.
6. **Schema consolidated** to a single \`workspace-v1\` base with an idempotent migration pass.

## Verification

- [x] \`node --check server.mjs\` passes
- [x] \`node --check public/app.js\` passes
- [x] \`GET /health\` reports \`schemaVersion: workspace-v1\`
- [x] \`GET /api/kanban\` returns status columns
- [x] \`GET /api/calendar\` returns dated events
- [ ] Run the Playwright suite

### Related

- [[Planning board seed]] is the working example
- [[Spec review checklist]] is the merge gate
- [[Agent operating brief]] explains how agents should read this`, { isTop: true, status: 'review', priority: 'high', dueDate: at(5) }),
      note('sample-study-memory', 'playbook', ['study', 'memory', 'recall'], `# Study note: memory systems

## Retrieval practice

Retrieval practice strengthens recall more reliably than rereading because the learner must reconstruct the answer.

- Retrieval cue :: a prompt that starts recall without giving away the answer
- Desirable difficulty :: a useful level of challenge that improves long-term retention
- Interleaving :: mixing related topics so the learner must choose a strategy

### Review loop

1. Attempt the answer before opening the source.
2. Grade confidence separately from correctness.
3. Schedule a short review for missed cards and a longer interval for stable cards.

### Related

- [[Study note from source]] demonstrates term extraction
- [[Study deck: systems design]] adds infrastructure examples`, { status: 'todo', priority: 'medium', position: 3, dueDate: at(4) }),

      note('sample-study-architecture', 'specs', ['study', 'architecture', 'recall'], `# Study note: architecture patterns

## Service boundaries

A boundary is useful when it makes ownership, failure handling, and data contracts explicit.

- Request id :: a value carried through a request so logs can be joined across services
- Health check :: a small dependency-aware probe that distinguishes ready from alive
- Circuit breaker :: a guard that stops repeated calls to a failing dependency
- Idempotency :: making a retry produce the same result as the first successful attempt

### Recall prompts

1. What does a request id help an operator do?
2. Why should a health check be dependency-aware?
3. Which property makes a retry safe?

### Related

- [[Release notes: rename + planning]] records the deployment checklist
- [[Spec review checklist]] defines the acceptance gate`, { status: 'review', priority: 'high', position: 4, dueDate: at(6) }),

      note('sample-study-quiz', 'planning', ['study', 'quiz', 'workflow'], `# Study quiz: operating a workspace

Use this note as a five-question practice set.

1. Which view shows linked notes and objects?
2. Which field controls the next review date?
3. What should happen when a provider token becomes stale?
4. Which deployment endpoint confirms storage and schema readiness?
5. Why should sample loading be idempotent?

### Answers

- Graph
- \`due_date\`
- Reconnect the client and retry once
- \`/health\`
- Re-running it must not duplicate content

### Related

- [[Study note: memory systems]] is the review method
- [[Study note: architecture patterns]] is the systems reference`, { status: 'backlog', priority: 'medium', position: 5, dueDate: at(7) }),
    ],
    tags: [],
  };
}

export function greet(name) {
  return `Hello, ${name}!`;
}
