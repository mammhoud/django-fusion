"""
Pydoll test helpers (sync wrapper + async helpers).

This file provides:
- PydollTestCase: a small helper that runs async pydoll interactions from sync tests.
- It uses asyncio.run internally for convenience; for full async pytest tests prefer using pydoll_tab fixture.
"""
from __future__ import annotations
import asyncio
from typing import Any, Callable


class PydollTestCase:
    """
    Small adapter for writing synchronous test methods that call async pydoll helpers.

    Example:
        class MyTest(PydollTestCase):
            def test_title(self):
                def _run(tab):
                    return tab.title  # async property awaits inside helper

                title = self.run_on_tab(_run, url="https://example.com")
                assert "Example" in title
    """
    def run_async(self, coro):
        """Run an async coroutine in a fresh event loop."""
        return asyncio.run(coro)

    def run_on_browser(self, action: Callable[[Any], Any], url: str = "about:blank"):
        """
        Convenience: create a browser in-context, open a tab, run action(tab), cleanup.
        This is useful for small smoke tests from sync test functions.
        """
        async def _inner():
            try:
                from pydoll.browser.chromium import Chrome
            except Exception as e:
                raise RuntimeError("pydoll is required for this test. Install pydoll.") from e

            async with Chrome() as browser:
                tab = await browser.start()
                # if url appears to be a path, treat relative to /
                if url.startswith("/"):
                    await tab.go_to(url)
                else:
                    await tab.go_to(url)
                res = action(tab)
                if asyncio.iscoroutine(res):
                    res = await res
                return res

        return self.run_async(_inner())
