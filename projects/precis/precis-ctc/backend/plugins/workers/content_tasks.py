"""Precis LMS content processing background tasks.

Uses ``@task`` from ``django_fusion.tasks`` for broker-agnostic enqueue.
"""

from __future__ import annotations

import logging

from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="content", max_retries=3)
def process_uploaded_video(video_id: int):
    """Transcode and generate a thumbnail for a newly uploaded course video.

    Requires ``ffmpeg`` to be available on the worker host.  If the video
    is already processed (has a thumbnail), this task is idempotent and
    returns early.
    """
    try:
        from apps.content.models import Video  # noqa: PLC0415
        video = Video.objects.filter(id=video_id).first()
    except ImportError:
        logger.warning("Video model not available — skipping.")
        return

    if video is None:
        logger.warning("Video %d not found.", video_id)
        return

    # Idempotency: skip if already processed
    if getattr(video, "thumbnail", None) or getattr(video, "transcoded", False):
        logger.info("Video %d already processed — skipping.", video_id)
        return

    import subprocess
    import tempfile
    from pathlib import Path

    source_path = Path(video.file.path) if hasattr(video, "file") and video.file else None
    if source_path is None or not source_path.exists():
        logger.warning("Video %d has no source file.", video_id)
        return

    # Generate thumbnail at 5 seconds
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as thumb:
        thumb_path = Path(thumb.name)

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(source_path),
                "-ss", "00:00:05",
                "-vframes", "1",
                "-q:v", "2",
                str(thumb_path),
            ],
            capture_output=True,
            timeout=120,
            check=True,
        )

        # Attach thumbnail to the Video model
        from django.core.files import File
        with open(thumb_path, "rb") as f:
            video.thumbnail.save(
                f"thumb_{video_id}.jpg",
                File(f),
                save=True,
            )

        video.transcoded = True
        video.save(update_fields=["transcoded"])
        logger.info("Video %d processed successfully.", video_id)

    except subprocess.CalledProcessError as exc:
        logger.error("ffmpeg failed for video %d: %s", video_id, exc.stderr)
        raise
    finally:
        if thumb_path.exists():
            thumb_path.unlink()


@task(queue="content", max_retries=3)
def generate_ai_course_description(course_id: int):
    """Generate an SEO-optimised course description using an LLM.

    Calls an external AI provider (OpenAI, Anthropic, or DeepSeek) to
    produce a compelling, keyword-rich description based on the course
    title, syllabus, and target audience.

    Requires ``OPENAI_API_KEY`` (or equivalent) in the environment.
    """
    import os

    try:
        from apps.learning.models import Course  # noqa: PLC0415
        course = Course.objects.filter(id=course_id).first()
    except ImportError:
        logger.warning("Course model not available — skipping AI description.")
        return

    if course is None:
        logger.warning("Course %d not found.", course_id)
        return

    # Skip if already has a manually written description
    if getattr(course, "ai_description_generated", False):
        logger.info("Course %d already has an AI description — skipping.", course_id)
        return

    provider = os.environ.get("AI_PROVIDER", "openai").lower()
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or ""

    if not api_key:
        logger.warning("No AI API key configured — skipping description generation.")
        return

    syllabus = getattr(course, "syllabus", "") or ""
    prompt = (
        f"Write a compelling, SEO-optimized course description (200-300 words) "
        f"for a course titled '{course.title}'. "
        f"The syllabus covers: {syllabus[:500]}. "
        f"Target audience: {getattr(course, 'audience', 'general learners')}. "
        f"Use a professional yet approachable tone. Include keywords naturally."
    )

    description = ""

    if provider == "openai":
        try:
            from openai import OpenAI  # noqa: PLC0415
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
            )
            description = response.choices[0].message.content or ""
        except ImportError:
            logger.warning("openai package not installed — skipping.")
            return
        except Exception:
            logger.exception("OpenAI API call failed for course %d", course_id)
            raise

    elif provider == "anthropic":
        try:
            from anthropic import Anthropic  # noqa: PLC0415
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            description = response.content[0].text
        except ImportError:
            logger.warning("anthropic package not installed — skipping.")
            return
        except Exception:
            logger.exception("Anthropic API call failed for course %d", course_id)
            raise

    elif provider == "deepseek":
        try:
            from openai import OpenAI  # noqa: PLC0415
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            description = response.choices[0].message.content or ""
        except Exception:
            logger.exception("DeepSeek API call failed for course %d", course_id)
            raise

    if description:
        course.description = description
        course.ai_description_generated = True
        course.save(update_fields=["description", "ai_description_generated"])
        logger.info("AI description generated for course %s.", course.slug)
    else:
        logger.warning("Empty description returned for course %d.", course_id)
