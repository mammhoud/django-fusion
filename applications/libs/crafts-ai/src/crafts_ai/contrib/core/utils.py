from __future__ import annotations

import pathlib
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any, TypeVar
from uuid import uuid4

from django.conf import settings
from django.urls import reverse


def file_generate_name(original_file_name):
    extension = pathlib.Path(original_file_name).suffix

    return f"{uuid4().hex}{extension}"


def file_generate_upload_path(instance, filename):
    return f"files/{instance.file_name}"


def file_generate_local_upload_url(*, file_id: str):
    url = reverse("api:files:upload:direct:local", kwargs={"file_id": file_id})

    app_domain: str = settings.APP_DOMAIN  # type: ignore

    return f"{app_domain}{url}"


def bytes_to_mib(value: int) -> float:
    # 1 bytes = 9.5367431640625E-7 mebibytes
    return value * 9.5367431640625e-7

def get_files_from_dirs(
    dirs: Iterable[Path],
    pattern: str = "*",
) -> Generator[tuple[Path, Path], Any, None]:
    for dir in dirs:
        for path in dir.rglob(pattern):
            if path.is_file():
                yield path, dir


Item = TypeVar("Item")


def unique_ordered(items: Iterable[Item]) -> list[Item]:
    return list(dict.fromkeys(items))
