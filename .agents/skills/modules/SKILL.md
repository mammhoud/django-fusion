---
name: modules
description: >
  Add a Coder module from registry.coder.com/modules to an existing
  Coder template, or update one that is already there. Use for
  requests like "add the Cursor IDE to my template", "give workspaces
  JetBrains access", "set up code-server", "wire in dotfiles",
  "install Claude Code in this template", or "pin module versions".
  Do not use for installing or upgrading Coder itself (use the setup
  skill), authoring a brand-new template from scratch (use the
  templates skill), or publishing a custom module to the registry.
---

# Modules

Add or update Coder modules inside an existing Coder template.
Modules are Terraform snippets published at registry.coder.com that
extend a workspace with IDEs, AI agents, secrets, login flows, cloud
regions, and other tools.

## Source of Truth

Read current upstream docs before applying anything topic-specific:

- <https://coder.com/docs/llms.txt> for the docs index.
- <https://coder.com/docs/llms-full.txt> only when the index is not
  enough.
- Each module's page on registry.coder.com has the canonical Terraform
  snippet and version. Prefer that over a memorized version.

This skill keeps only the integration workflow, user interaction
rules, and a few module-specific gotchas.

## User Interaction

The user wants a working module integration, not a Terraform lesson.

- Confirm which template you are editing when the user has more than
  one.
- Show the proposed snippet before writing it. Ask for one yes/no.
- Never bump a module version silently. Call out version changes.
- Do not lecture the user on Coder concepts unless they ask.

## Workflow

### 1. Identify the module

Search for what the user described. Try these in order and stop at
the first hit:

1. The registry MCP server at `https://registry.coder.com/mcp` with
   the `search_modules` tool.
2. The website at <https://registry.coder.com/modules>.
3. `find registry/coder/modules -maxdepth 1 -type d` against a local
   clone of `coder/registry`.

If the request is ambiguous, list two or three matching options with
one-line descriptions and ask the user to pick one.

### 2. Locate the target template

Coder modules go inside a Coder template, which is Terraform code on
disk. Confirm:

- A directory with `main.tf`.
- A `coder_agent` resource. Most modules need an `agent_id`.
- A `data "coder_workspace" "me"` data source. Most modules gate on
  `data.coder_workspace.me.start_count`.

If no template directory exists, stop and offer the templates skill.

### 3. Read the module page

Fetch the canonical snippet:

- From the module's README on registry.coder.com.
- Or from `registry/coder/modules/<name>/README.md` in a local clone
  of `coder/registry`.

Always pin the version shown on the page. Never use `latest`. Never
fabricate a version that is not listed.

### 4. Insert the module

Add the snippet to `main.tf`. Common rules:

- Set `agent_id` to the existing `coder_agent` resource. Templates
  usually have exactly one.
- Keep `count = data.coder_workspace.me.start_count` for modules that
  should only run while the workspace is started.
- Match the surrounding indentation and quoting style.
- Modules with extra inputs (JetBrains IDE selection, Vault auth,
  JFrog instance URL, MCP config) take additional arguments. Read the
  module README's Examples section before guessing.

### 5. Validate

In the template directory:

```sh
terraform init
terraform fmt
terraform validate
```

`terraform fmt` may reformat unrelated parts of the file the user has
not touched. If that happens, ask before committing.

### 6. Push

If the user wants the change live on a Coder deployment:

```sh
coder templates push "$TEMPLATE_NAME" -d "$TEMPLATE_DIR" --yes
coder templates versions list "$TEMPLATE_NAME"
```

The `versions list` output confirms the new version is registered.
If the user wants the new version to become active automatically,
add `--activate` to `push`; otherwise leave the existing active
version alone.

## Common Modules

Curated shortlist of the most-requested categories. Full catalogue at
<https://registry.coder.com/modules>.

- IDEs: `cursor`, `jetbrains`, `code-server`, `vscode-desktop`,
  `vscode-web`, `windsurf`, `zed`, `kiro`.
- AI agents: `claude-code`, `aider`, `goose`, `amazon-q`, `agentapi`.
- Dev environment: `dotfiles`, `git-clone`, `git-config`,
  `personalize`, `coder-login`.
- Secrets: `hcp-vault-secrets`, `vault-cli`, `vault-github`,
  `vault-jwt`, `vault-token`.
- Apps: `filebrowser`, `jupyterlab`, `jupyter-notebook`,
  `rstudio-server`, `kasmvnc`.
- Cloud regions: `aws-region`, `azure-region`, `gcp-region`,
  `fly-region`.

## Safeguards

- Do not add a module to a template that has no `coder_agent`. The
  module will not function and the workspace will silently miss the
  integration.
- Do not add a module that needs admin-level configuration (Vault
  backend, JFrog instance, external auth providers) without
  confirming the deployment has that side configured.
- Do not run `coder templates push` without telling the user which
  template version they will get.
- Do not edit `main.tf` if the user has uncommitted changes; offer to
  stash or commit first.
- Do not invent module names or versions. If you cannot find the
  module on registry.coder.com, say so.

## Bundled Resources

No per-module recipes ship with this skill. Defer to each module's
README on registry.coder.com and to upstream Coder docs.
