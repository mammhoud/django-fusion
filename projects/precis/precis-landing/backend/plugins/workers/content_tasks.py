"""Precis Landing content background tasks.

Uses ``@task`` from ``django_fusion.tasks`` for broker-agnostic enqueue.
"""

from __future__ import annotations

import logging

from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="content", max_retries=3)
def warm_page_cache(page_id: int):
    """Pre-render and cache a Wagtail page for the landing surface.

    Useful after publishing a high-traffic page (homepage, pricing, blog
    index) so the first visitor doesn't pay the cold-render penalty.

    The actual cache-warming strategy depends on the project's cache
    backend (Redis, file-based, CDN purge + pre-warm).  This task acts
    as the trigger; the real work is done by the cache-backend invalidation
    layer (e.g. wagtail-cache or a CDN purge API).
    """
    from django.core.cache import cache
    from wagtail.models import Page  # noqa: PLC0415

    page = Page.objects.filter(id=page_id, live=True).specific().first()
    if page is None:
        logger.warning("Page %d not found or not live — skipping cache warm.", page_id)
        return

    # CACHE_KEY_PREFIX is a common Wagtail convention
    prefix = getattr(
        __import__("django.conf", fromlist=["settings"]).settings,
        "CACHE_KEY_PREFIX",
        "wagtail",
    )
    cache_key = f"{prefix}:page:{page.id}:rendered"

    # Attempt to serve the page to prime the cache.  The response itself
    # is discarded — the cache backend stores the rendered output.
    try:
        from django.test import RequestFactory
        from wagtail.views.serve import serve

        request = RequestFactory().get(page.url)
        response = serve(request, page.url_path)
        if response.status_code == 200:
            cache.set(cache_key, response.content, timeout=3600)
            logger.info("Page %d cache warmed: %s", page.id, page.title)
        else:
            logger.warning(
                "Page %d returned %d — cache not warmed.",
                page.id,
                response.status_code,
            )
    except Exception:
        logger.exception("Failed to warm cache for page %d", page.id)


@task(queue="content", max_retries=2)
def generate_blog_preview_images(post_id: int):
    """Generate social-media preview (og:image) images for a blog post.

    Renders the Open Graph image template for the blog post and saves it
    to the Wagtail image library so the post can serve a branded card
    on Twitter/Facebook/LinkedIn.
    """
    from wagtail.models import Page  # noqa: PLC0415

    blog_post = Page.objects.filter(id=post_id, live=True).specific().first()
    if blog_post is None:
        logger.warning("Blog post %d not found — skipping preview image.", post_id)
        return

    try:
        from wagtail.images.models import Image  # noqa: PLC0415
    except ImportError:
        logger.warning("Wagtail images not available — skipping preview image.")
        return

    from io import BytesIO

    # ── Render the OG image as a PNG ────────────────────────────────
    # This requires Pillow (PIL) to be installed.  If it's not available,
    # the task fails gracefully and can be retried.
    try:
        from PIL import Image as PILImage  # noqa: PLC0415
        from PIL import ImageDraw, ImageFont
    except ImportError:
        logger.warning("Pillow not installed — skipping preview image generation.")
        return

    title = getattr(blog_post, "title", "Blog Post")
    author = getattr(blog_post, "owner", None)
    author_name = getattr(author, "get_full_name", lambda: "Structa Cloud")()

    # Create a 1200x630 social card (optimal for Twitter/Facebook/LinkedIn)
    img = PILImage.new("RGB", (1200, 630), color=(15, 23, 42))  # dark brand bg
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48
        )
        font_body = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28
        )
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_body = font_title

    # Draw title text (centred, wrapped)
    lines = _wrap_text(title, font_title, 1100)
    y = 200
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        x = (1200 - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill=(255, 255, 255), font=font_title)
        y += 70

    # Draw author attribution
    draw.text(
        (60, 570),
        f"by {author_name}",
        fill=(148, 163, 184),
        font=font_body,
    )

    # Save to a BytesIO buffer and store as a Wagtail Image
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    image = Image(
        title=f"Preview: {title[:200]}",
        file=None,
    )
    # Wagtail images require the file to be saved via the Image model
    # file field — use the standard Django file storage.
    try:
        from django.core.files.base import ContentFile
        image.file.save(
            f"blog_previews/{post_id}.png",
            ContentFile(buf.read()),
            save=True,
        )
        logger.info("Blog preview image created for post %d: %s", post_id, image.id)
    except Exception:
        logger.exception("Failed to save blog preview image for post %d", post_id)


def _wrap_text(text: str, font, max_width: int) -> list[str]:
    """Wrap text to fit within ``max_width`` pixels using the given font."""
    words = text.split()
    lines: list[str] = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)
    return lines or [text]
