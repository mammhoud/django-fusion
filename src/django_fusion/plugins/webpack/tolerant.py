# ============================================================
# Tolerant webpack loader — opt-in via settings
# ============================================================
# A fresh checkout (or any environment where `make build-assets` has not run
# yet) has no bundles.json. django-webpack-loader raises from get_bundle(),
# which turns EVERY page that renders ``{% render_bundle %}`` into a 500 —
# the site looks completely broken instead of merely unstyled.
#
# This loader subclasses the (django-fusion-patched) WebpackLoader and
# returns an empty bundle when the stats file cannot be read, logging a
# warning so the missing build stays visible without taking the site down.
# The real fix is always to run the documented build workflow; this keeps
# the render road alive until someone does.
#
# Opt in per site (site-local settings, self-contained):
#
#     WEBPACK_LOADER = {
#         "DEFAULT": {
#             "STATS_FILE": str(BASE_DIR / "…" / "bundles.json"),
#             "LOADER_CLASS": (
#                 "django_fusion.plugins.webpack.tolerant.TolerantWebpackLoader"
#             ),
#         }
#     }
#
# Compatibility notes:
# * ``webpack_compat._patch_webpack_loader`` patches methods on the BASE
#   ``WebpackLoader`` class. This subclass overrides ``get_bundle`` (the
#   chokepoint every ``{% render_bundle %}`` call hits) and wraps the
#   patched super() implementation, so dict-chunk normalisation still runs
#   when the stats file exists.
# * django-webpack-loader's cache (`CACHE=True`) caches successful loads
#   only; a failure is raised every render, which is exactly the path we
#   intercept here.
# ============================================================
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _loader_class():
    """Resolve the base WebpackLoader, tolerating import/layout differences."""
    from webpack_loader.loaders import WebpackLoader

    return WebpackLoader


class TolerantWebpackLoader(_loader_class()):  # type: ignore[misc, valid-type]
    """WebpackLoader that renders no bundle links instead of raising.

    Failure modes handled:
    * stats file missing (build not run yet),
    * unreadable / invalid JSON (interrupted build),
    * stats present but the requested bundle unknown (returns no chunks —
      the stock implementation already yields ``[]`` for that case).
    """

    def get_bundle(self, bundle_name: str) -> list:  # noqa: D401
        """Return the bundle's chunks, or ``[]`` when the build is missing."""
        try:
            return super().get_bundle(bundle_name)
        except Exception as exc:  # IOError / WebpackBundleLookupError / JSON errors
            logger.warning(
                "webpack bundle %r unavailable (%s) — rendering page without it. "
                "Run the project's asset build (e.g. `make build-assets`) to "
                "generate the stats file.",
                bundle_name,
                exc,
            )
            return []


__all__ = ["TolerantWebpackLoader"]
