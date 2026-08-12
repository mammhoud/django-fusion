# Community edition

`formint-community/` is the in-repo **Community** edition of Formints —
a free, offline-first desktop point of sale (Tauri 2 + React 19 +
Rust/Diesel, no Python sidecar). This is the canonical source; make feature
changes here directly.

The standalone public repo bundle (`github.com/mammhoud/formint-community`)
is refreshed from this edition by:

```bash
make community-bundle   # from projects/formints/
```

which runs `scripts/publish/community-bundle.cjs` and writes a git-initializable
copy to `publish/community-bundle/` (a git-ignored staging dir), applying the
publish rename contract:

| Field | In-repo | Community publish |
|-------|---------|-------------------|
| package name | `formint-community` | `formint-community` |
| Tauri product | Formints Community | Formints Community |
| Tauri identifier | `com.mammhoud.formint-community` | `com.mammhoud.formint-community` |

To publish: `git init publish/community-bundle`, commit, and push to
https://github.com/mammhoud/formint-community.
