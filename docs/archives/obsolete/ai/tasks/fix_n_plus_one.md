# Task: Fix N+1 Query Problems

Based on the analysis report (section 3), generate `select_related`/`prefetch_related` additions for each affected view.

For each issue:
- Locate the queryset
- Add `.select_related('foreign_key_field')` or `.prefetch_related('reverse_relation')`
- Output the corrected code block with a `# FIXED N+1` comment.

If the report is missing, ask the user to run `analyze_project` or `comprehensive_analysis` first.
