# Guides Docs — AI Agent Prompts

> Specialized prompts for working with guide/instructional documentation.

---

## Creating Guides

```
Create a guide at `docs/Anytype/guides/[name].md`.

Include:
1. Frontmatter with Object type: Guide, Category, Target Audience, Platform
2. Prerequisites section
3. Step-by-step instructions with code blocks
4. Verification commands to confirm success
5. Troubleshooting table with common issues
6. Related docs links
```

## Creating Platform Install Guides

```
Create a platform install guide at `docs/Anytype/guides/install/[platform].md`.

Template:
1. Prerequisites and system requirements
2. Package manager installation (per OS)
3. Tool installation (nvm, pnpm, uv, rust)
4. Clone and setup instructions
5. Verification checks
6. Troubleshooting table
7. Related guides
```

## Reviewing Guides

```
Review guides for completeness:
1. Are prerequisites clearly stated?
2. Are steps numbered and actionable?
3. Are there verification commands?
4. Do troubleshooting tables address common failure modes?
5. Are platform-specific notes included?
```
