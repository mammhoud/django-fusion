"""Watch theme files and rerun BEM conversion plus SCSS compilation."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

from .bem import convert_paths


def watch_theme(paths: Sequence[Path], scss_command: Sequence[str] | None = None) -> None:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            path = Path(event.src_path)
            if path.suffix in {".html", ".scss", ".css"}:
                convert_paths([path])
                if scss_command:
                    subprocess.run(list(scss_command), check=False)

    observer = Observer()
    handler = Handler()
    for path in paths:
        observer.schedule(handler, str(path), recursive=True)
    observer.start()
    try:
        observer.join()
    finally:
        observer.stop()
