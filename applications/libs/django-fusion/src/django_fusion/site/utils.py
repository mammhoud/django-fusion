from __future__ import annotations

import pathlib
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any, TypeVar
from uuid import uuid4

from django.conf import settings
from django.urls import reverse


class viewprop:  # noqa: N801
    """
    A descriptor that works like ``@property`` but whose computed value can be
    overridden on a per-instance basis.

    Inspired by django-material's ``viewprop`` (Mikhail Podgurskiy, AGPL).

    Usage::

        class MyViewset(Viewset):
            @viewprop
            def viewsets(self):
                return [MyChildViewset()]

        # Override on an instance:
        obj = MyViewset()
        obj.viewsets = [OtherViewset()]   # stored in obj.__dict__

    How it works:
    - On first ``__get__`` the getter is called and the result is cached in
      ``obj.__dict__`` under the function name, so subsequent reads are O(1).
    - ``__set__`` writes directly to ``obj.__dict__``, bypassing the descriptor
      entirely on future reads (standard Python descriptor protocol).
    - This makes it safe to use in classes that also inherit from Django's
      ``View``, where ``View.__init__`` does *not* call ``super().__init__()``.
    """

    def __init__(self, func: Any) -> None:
        self.__doc__ = func.__doc__
        self.fget = func

    def __get__(self, obj: Any | None, objtype: type[Any] | None = None) -> Any:
        if obj is None:
            return self
        name = self.fget.__name__
        if name not in obj.__dict__:
            obj.__dict__[name] = self.fget(obj)
        return obj.__dict__[name]

    def __set__(self, obj: Any, value: Any) -> None:
        obj.__dict__[self.fget.__name__] = value

    def __repr__(self) -> str:
        return f"<viewprop func={self.fget}>"


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


# ── URL utilities ─────────────────────────────────────────────────────────────

def get_default_language() -> str:
    """Return the primary language code from LANGUAGE_CODE setting."""
    from django.conf import settings

    if hasattr(settings, "LANGUAGE_CODE"):
        return settings.LANGUAGE_CODE.split("-")[0]
    return "en"


def get_root_redirect_pattern():
    """
    Generate the root path redirect pattern to the default language prefix.

    Usage in urls.py::

        from django_fusion.site.utils import get_root_redirect_pattern

        urlpatterns += [get_root_redirect_pattern()]
    """
    from django.urls import path
    from django.views.generic import RedirectView

    default_language = get_default_language()
    return path(
        "",
        RedirectView.as_view(url=f"/{default_language}/", permanent=False),
        name="root-redirect",
    )
