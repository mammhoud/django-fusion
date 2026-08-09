# Generated package — do not edit directly

`formint-community/` is generated from the Community edition
`projects/formints/formintA/` by `make community-bundle`
(`scripts/publish/community-bundle.cjs`), which applies the rename contract:

| Field | In-repo | Community version |
|-------|---------|-------------------|
| package name | `formint-pos` | `formint-community` |
| Tauri product | Formint | Formints Community |
| Tauri identifier | `com.mammhoud.pos` | `com.mammhoud.formint-community` |
| window title | Formint | Formints Community |

Make feature changes in `formintA/`, then run `make community-bundle` to
refresh this folder. To publish: `git init`, commit, and push to https://github.com/mammhoud/formint-community.
