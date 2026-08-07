"""
Brand-kit strategy data — the *why* behind each product's mark.

Mirrors frontend/src/lib/brand.ts (one source per render road; the logo SVG
glyphs themselves live in content/blocks/product_logo.html and
frontend/src/components/ui/ProductLogo.astro).

Each entry carries the brandkit-style story for one product:
- ``essence``  — the one-line brand promise (large type on the board).
- ``metaphor`` — the symbolic idea the mark is built from.
- ``construction`` — the geometry/negative-space logic of the mark.
- ``voice`` — the typographic character (display vs mono emphasis).
- ``palette`` — the shared system swatches the brand sits in (accent first).
"""

BRAND_SPEC = {

    "formint-pos": {
        "brand": "formints",
        "mark": "crest",
        "name": "Formints",
        "role": "Desktop point of sale · Community · Standard · Pro · Cloud",
        "essence": "The till, made trustworthy.",
        "metaphor": "A merchant seal — the shield of a counter you can trust.",
        "construction": "Shield (trust) + till bar (the counter) + a check cut in negative space (a verified sale).",
        "voice": "Bricolage display for the wordmark · JetBrains Mono for prices.",
        "palette": ["formints", "paper", "ink", "line", "link"],
    },
    "lms": {
        "brand": "precis",
        "mark": "ribbon",
        "name": "Precis LMS",
        "role": "The learning platform behind structa.cloud · courses · enrollments · payments",
        "essence": "Learning, precisely.",
        "metaphor": "An award ribbon — recognition for progress, precisely measured.",
        "construction": "A ribbon band with tails, an ascending arrow rising from the centre: progress, marked.",
        "voice": "Bricolage display for headings · Public Sans for course copy.",
        "palette": ["precis", "paper", "ink", "line", "live"],
    },
    "cms": {
        "brand": "loop",
        "mark": "isometric",
        "name": "Loop",
        "role": "Content CMS · build sites from Wagtail blocks · 2 editions",
        "essence": "Content, composed.",
        "metaphor": "Blocks inside blocks — sites assembled from content, not templates.",
        "construction": "An isometric cube containing a nested cube: blocks composing blocks, all the way down.",
        "voice": "Bricolage display for the mark · Public Sans for editorial body.",
        "palette": ["loop", "paper", "ink", "line", "mark"],
    },
    "cypercloud": {
        "brand": "syntara",
        "mark": "orbit",
        "name": "Syntara",
        "role": "AI chat customizer · ceptor-ai powered · MCP · 2 editions · under development",
        "essence": "Chat, routed around your brand.",
        "metaphor": "A signal core with crossing conversation orbits — every chat routed around your model, your data.",
        "construction": "A core node (the model) + two elliptical orbits (conversation paths) + a satellite: customization in motion.",
        "voice": "JetBrains Mono accent — an API product, labelled like one.",
        "palette": ["syntara", "paper", "ink", "line", "link"],
    },
    "vresume": {
        "brand": "vresume",
        "mark": "ascent",
        "name": "vResume",
        "role": "Portfolio & resume platform · Syntara-powered summaries · cloud hosted",
        "essence": "Your career, on the record.",
        "metaphor": "A staircase — work shown step by step, a check at the summit.",
        "construction": "A rising stair path with a baseline rule and a verified check at the peak: growth, evidenced.",
        "voice": "Bricolage display for the wordmark · Public Sans for the resume body.",
        "palette": ["vresume", "paper", "ink", "line", "link"],
    },
}


# System swatch tokens → CSS variables (resolved at build so templates stay
# dumb and both render roads match exactly).
_SYSTEM_SWATCH_VARS = {
    "paper": "var(--fu-paper)",
    "ink": "var(--fu-ink)",
    "line": "var(--fu-line)",
    "link": "var(--fu-link)",
    "live": "var(--fu-live)",
    "mark": "var(--fu-mark)",
}


def swatch_style(token: str) -> str:
    """Inline ``background:`` style for one palette swatch token.

    Brand tokens (formints/precis/loop/syntara/vresume) use their own hue
    (``--brand-<token>``); system tokens (paper/ink/line/…) map to the shared
    fu-* variables. Mirrors ``swatchVar()`` in frontend/src/lib/brand.ts.
    """
    system = _SYSTEM_SWATCH_VARS.get(token)
    return f"background:hsl({system})" if system else f"background:hsl(var(--brand-{token}))"


def get_brand_boards(products_page=None) -> list[dict]:
    """The brand kit boards — one per live, non-hidden product card.

    Single source of truth for the /brand/ page, the Astro brand.astro road
    and the product-tooltip brand modal: each board joins the product card
    (title/href/logo) with its BRAND_SPEC story and pre-resolved swatches.
    """
    from apps.pages.models import ProductsPage

    page = products_page or ProductsPage.objects.first()
    if page is None:
        return []
    cards = page.get_product_cards()
    boards = []
    for card in cards:
        spec = BRAND_SPEC.get(card["slug"], {})
        if not spec:
            continue
        boards.append(
            {
                **card,
                **spec,
                "mark": spec.get("mark", card["logo_style"]),
                "swatches": [
                    {"token": token, "style": swatch_style(token)}
                    for token in spec.get("palette", [])
                ],
                # href comes from the product card (get_product_cards sets it).
            }
        )
    return boards

