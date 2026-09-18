# Phase 4 — Note Privacy, Share Modal & Session-Guarded Preview

**Status:** Planned  
**Scope:** `runtime/server.mjs`, `planing/app/src/`  
**Owner:** Backend + Frontend  
**Depends on:** Phase 2 (SurrealDB file mode)  
**Can run in parallel with:** Phase 3, Phase 5

---

## Objective

1. Notes are **private by default** — `is_share = false` on creation.
2. Every note records `created_by` (the creating account).
3. The `/share/:id` preview route requires a valid session for private notes;
   unauthenticated access to a private note returns 401.
4. Sharing uses a new **Share Modal** with two panels:
   - **Link panel** — toggle share on/off, copy URL, set optional password/expiry.
   - **Email panel** — enter email addresses, send invite links.

---

## Current State

### Backend (`runtime/server.mjs`)

- `POST /api/notes` already sets `is_share: false` as SurrealDB field default.
- `created_by` field is defined on the `notes` SCHEMAFULL table.
- BUT: `created_by` is not explicitly set in the `CREATE notes SET ...`
  statement — it defaults to `NONE`.
- The note preview endpoint does **not** check session for private notes;
  unauthenticated requests receive the full note content.

### Frontend (`planing/app/src/`)

- `pages/share/[id].tsx` calls `api.notes.publicDetail.mutate(...)` — no
  auth check.
- `components/BlinkoShareDialog/index.tsx` — single panel with `isShare`
  toggle, password, expiry date, max views. No email input. No link copy button.
- `blinkoStore.tsx` has `internalShareNote` (share with specific users on the
  same instance) but no email-based external sharing.

---

## Backend Changes (`runtime/server.mjs`)

### 4.1 — Set `created_by` on every note creation

In `POST /api/notes`:
```js
const data = {
  ...noteFields,
  is_share: false,                                      // explicit default
  created_by: new RecordId('account', req.account.sub), // always set
  created_at: new Date(),
  updated_at: new Date(),
};
```

Also backfill existing notes missing `created_by`:
```sql
UPDATE notes SET created_by = NONE WHERE created_by IS NONE;
-- (idempotent no-op for already-set notes)
```

Add to schema bootstrap DDL (idempotent):
```sql
DEFINE FIELD created_by ON notes TYPE option<record<account>> DEFAULT NONE;
DEFINE FIELD is_share   ON notes TYPE option<bool>            DEFAULT false;
```

---

### 4.2 — Session-guarded share preview

Identify the share preview endpoint. Currently it is likely served from the
frontend SPA (React Router). Ensure the API endpoint used by the preview page
checks `is_share`:

In `GET /api/notes/:id` (or a dedicated `/api/notes/:id/preview`):
```js
app.get('/api/notes/:id/preview', optionalAuth, async (req, res) => {
  const note = await q(
    'SELECT * FROM type::thing("notes", $id);',
    { id: req.params.id }
  );
  if (!note[0]) return res.status(404).json({ error: 'Note not found' });

  const isShared = note[0].is_share === true;
  const hasSession = !!req.account;         // set by optionalAuth middleware
  const isOwner = hasSession &&
    recordId(note[0].created_by) === req.account.sub;

  if (!isShared && !isOwner) {
    return res.status(401).json({
      error: 'This note is private.',
      requiresAuth: true,
      redirect: `/signin?redirect=/share/${req.params.id}`
    });
  }
  res.json({ note: publicNote(note[0]) });
});
```

Add `optionalAuth` middleware:
```js
function optionalAuth(req, res, next) {
  const token = (req.headers.authorization || '').replace(/^Bearer /, '');
  if (!token) return next();
  try {
    req.account = jwt.verify(token, jwtSecret);
  } catch {
    // expired/invalid token — treat as unauthenticated
  }
  next();
}
```

---

### 4.3 — Email share invite endpoint

```
POST /api/notes/:id/share-invite
Body: { emails: string[], message?: string }
Auth: required (notes:write)
```

Behaviour:
1. Validate note exists and `req.account` owns it or has write permission.
2. Ensure `is_share = true` (toggle if not).
3. For each email:
   - Create an `audit_event` record: `{ action: 'note.share_invite', target: noteId, meta: { email } }`.
   - If `SMTP_HOST` is configured, send an email via `nodemailer` with the
     note's share URL.
   - If no SMTP, return the share URL in the response so the frontend can
     show a "copy to share" fallback.
4. Return `{ sent: number, shareUrl: string, fallback?: boolean }`.

---

## Frontend Changes

### 4.4 — `pages/share/[id].tsx` — 401 handling

```tsx
// After API call returns 401:
if (error?.status === 401 && error?.requiresAuth) {
  return (
    <div className="share-private-card">
      <LockIcon />
      <h2>This note is private</h2>
      <p>Sign in to view this note.</p>
      <Button href={error.redirect}>Sign in</Button>
    </div>
  );
}
```

Apply `x-data="{ visible: false }"` + `x-init="setTimeout(() => visible=true, 50)"` +
`x-show="visible"` + `x-transition` to animate the card in via Alpine.js.

---

### 4.5 — Rewrite `BlinkoShareDialog`

New structure (two-tab layout):

```
┌─────────────────────────────────┐
│  Share note                  ✕  │
├─────────────────────────────────┤
│  [🔗 Link]  [✉ Email]           │  ← Alpine.js tab switcher
├─────────────────────────────────┤
│ LINK TAB:                       │
│  ○ Private  ● Shared            │  ← toggle
│  https://tools.structa.cloud/   │
│  share/abc123          [Copy]   │
│  Password: [__________]  opt.   │
│  Expires:  [date]        opt.   │
│  Max views:[___]         opt.   │
├─────────────────────────────────┤
│ EMAIL TAB:                      │
│  To: [email@... ×] [email@...×] │  ← tag-input
│  Note: [optional message]       │
│  [Send invites]                 │
└─────────────────────────────────┘
```

Alpine.js tab logic:
```html
<div x-data="{ tab: 'link' }">
  <button @click="tab = 'link'" :class="tab === 'link' ? 'active' : ''">Link</button>
  <button @click="tab = 'email'" :class="tab === 'email' ? 'active' : ''">Email</button>

  <div x-show="tab === 'link'" x-transition>…</div>
  <div x-show="tab === 'email'" x-transition>…</div>
</div>
```

Calls:
- Toggle share: `blinko.shareNote.call({ id, isCancel: !isShare })`
- Copy link: `navigator.clipboard.writeText(shareUrl)`
- Send invites: `fetch('/api/notes/:id/share-invite', { method: 'POST', body: { emails } })`

---

### 4.6 — Note card `created_by` display

In `BlinkoCard/cardHeader.tsx`:
- Show author avatar/name when `note.created_by` is set and the viewer is not
  the owner (relevant on multi-user instances).
- Hide on single-user instances where `created_by === currentUser`.

---

## Data Model Changes (SurrealDB)

Fields added/enforced on `notes` table:

| Field | Type | Default | Notes |
|---|---|---|---|
| `created_by` | `option<record<account>>` | `NONE` | Set explicitly on every create |
| `is_share` | `option<bool>` | `false` | Always explicit now |
| `share_url` | `option<string>` | `NONE` | Computed on first share toggle |
| `share_expires_at` | `option<datetime>` | `NONE` | Optional expiry |
| `share_password` | `option<string>` | `NONE` | Optional password hash |
| `share_max_views` | `option<int>` | `NONE` | Optional view cap |
| `share_view_count` | `int` | `0` | Incremented on public view |

All changes are additive and backfill-safe via the existing `UPDATE notes SET field = field ?? default` pattern in `connectSurreal()`.

---

## Verification

```bash
# 1. Create note — confirm is_share=false and created_by set
curl -X POST http://localhost:1111/api/notes \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"private note","category":"notes"}'
# → { "is_share": false, "created_by": "account:xxx" }

# 2. Access preview without auth — expect 401
curl http://localhost:1111/api/notes/<id>/preview
# → { "error": "This note is private.", "requiresAuth": true }

# 3. Share the note
curl -X PATCH http://localhost:1111/api/notes/<id> \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"is_share": true}'

# 4. Access preview without auth — expect 200
curl http://localhost:1111/api/notes/<id>/preview
# → { "note": { ... } }

# 5. Send email invite
curl -X POST http://localhost:1111/api/notes/<id>/share-invite \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"emails":["user@example.com"]}'
# → { "sent": 1, "shareUrl": "https://..." }
```
