from django.dispatch import Signal

# Signal sent when a file is written by the MCP server.
# Provides: filepath (str), content (str)
file_written = Signal()
