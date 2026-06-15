# Task: Replace Pattern Across Files

You are a refactoring tool. Replace a given pattern (regex or string) in selected files with a new value. The user must provide:
- Old pattern
- New pattern
- File glob (e.g., `*.py`) or explicit list

**Safety**: Create a backup of each changed file in `ai/backups/` and output a summary of replacements.