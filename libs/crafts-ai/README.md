# crafts-ai

`crafts-ai` is the merged Structa AI, MCP, customizer, and former rseal toolkit. Source code uses the `src/` layout under `src/crafts_ai/`.

## Editable install

```bash
pip install -e applications/libs/crafts-ai
```

## Key workflows

- `python manage.py generate_agents` scans component templates and writes `.kilo/agent` configs.
- `python manage.py convert_to_bem` rewrites template/style class and ID names to strict BEM.
- `crafts_ai.mcp.server` exposes Theme Analyzer, Component Mapper, Config Inspector, and agent-config loading tools.
