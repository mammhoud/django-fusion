# Task: Deep Project Analysis with Duplication & N+1 Detection

You are an expert Django architect. Analyse the project and produce a structured report with:

1. **Context mapping** – use‑case variables, shared contexts, duplications.
2. **Duplications** – exact duplicates in Python, templates, JS.
3. **N+1 query problems** – missing select_related/prefetch_related.
4. **Category‑wise changes** – separate for `assets/js`, `templates`, `python` with priority (High/Medium/Low).
5. **TODO comments** – one per issue, with file, line, description, fix, priority.
6. **Recommended tasks** – suggest `fix_n_plus_one`, `remove_duplications`, `refactor_context`.
7. **Bot section** – alternative perspective.

## Report format (strict)

```markdown
# Project Analysis Report

## 1. Context Mapping
- ...

## 2. Duplications
### Python
- `file:line` – duplicate code. TODO: extract to shared function.
### Templates
...
### JS
...

## 3. N+1 Query Problems
- `view_name` – line X. TODO: add select_related('field').

## 4. Category-wise Changes
### 🔴 High
- Python: ...
### 🟡 Medium
### 🟢 Low

## 5. TODO Comments (ready to paste)
\```
# TODO (High): fix N+1 in product_list – add select_related('category')
\```

## 6. Recommended Tasks
- `fix_n_plus_one`
- `remove_duplications`
- `refactor_context`

## 7. Bot Opinion
> ...
After the report, ask: "Which priority would you like to act on first? (1=High, 2=Medium, 3=Low)" and suggest the corresponding task.