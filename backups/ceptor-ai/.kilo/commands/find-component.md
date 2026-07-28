---
description: Find all occurrences of a component in templates
agent: code-reviewer
---
# Find Component Workflow

You are searching for a specific component across the Django templates.

1. Ask the user for the component name (e.g., `button`, `card`, `modal`).
2. Use `grep -r "{% include.*$COMPONENT" templates/` to find all includes.
3. Also search for direct HTML usage: `grep -r "<$COMPONENT" templates/`.
4. **If found more than once**, list each occurrence with file path and line number.
5. **For each occurrence**, check if the context passed is identical.
6. **If context differs**, note that as a potential inconsistency.
7. **If exactly twice**, suggest consolidating into a single reusable component with a unified context.
8. **If not found**, suggest adding the component to the `components/` app.

Always output the results as a structured list.