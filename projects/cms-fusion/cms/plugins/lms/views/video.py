"""
Video streaming and management views for LMS.

Provides:
1. ``video_stream`` — Stream video files with HTTP range request support
   (required for HTML5 video seeking and scrubbing).
2. ``video_upload`` — Upload a new video file via multipart form.
3. ``video_detail`` — JSON endpoint for video metadata (used by frontend).
4. ``video_list`` — List videos for a lesson.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from plugins.lms.models import Lesson, Video

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RANGE_RE = re.compile(r"^bytes=(?P<start>\d+)-(?P<end>\d*)$")

def _parse_range(range_header: str, file_size: int) -> tuple[int, int] | None:
    """Parse HTTP Range header into (start, end) tuple.

    Returns ``None`` if the header is invalid or unsatisfiable.
    """
    match = RANGE_RE.match(range_header.strip())
    if not match:
        return None
    start = int(match.group("start"))
    end_str = match.group("end")
    end = int(end_str) if end_str else file_size - 1
    if start >= file_size or end >= file_size or start > end:
        return None
    return start, end


def _get_content_type(file_path: str) -> str:
    """Determine MIME type from file extension."""
    ext = Path(file_path).suffix.lower()
    content_types = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
        ".ogv": "video/ogg",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".mkv": "video/x-matroska",
        ".m4v": "video/x-m4v",
        ".vtt": "text/vtt",
        ".srt": "text/plain",
    }
    return content_types.get(ext, "application/octet-stream")


# ---------------------------------------------------------------------------
# 1. Video Streaming Endpoint (with Range Request Support)
# ---------------------------------------------------------------------------


@require_GET
def video_stream(request: HttpRequest, video_id: int) -> HttpResponse:
    """Stream a video file with HTTP range request support.

    Required by HTML5 ``<video>`` elements for seeking, scrubbing, and
    adaptive playback.  Without range responses, the browser must download
    the entire file before playback can begin.

    Headers:
    - ``Accept-Ranges: bytes`` — informs the client that range requests
      are supported.
    - ``Content-Range`` — included in 206 Partial Content responses.
    - ``Cache-Control: public, max-age=86400`` — CDN-friendly 24h cache.

    Usage in template::

        <video controls>
            <source src="{% url 'lms:video-stream' video_id=video.pk %}"
                    type="video/mp4">
        </video>
    """
    video = get_object_or_404(Video, pk=video_id, is_active=True)

    if video.processing_status != Video.ProcessingStatus.READY:
        return JsonResponse(
            {"error": "Video is still processing", "status": video.processing_status},
            status=503,
        )

    file_path = video.file.path
    if not os.path.exists(file_path):
        logger.warning("Video file not found on disk: %s (pk=%d)", file_path, video_id)
        raise Http404("Video file not found")

    file_size = os.path.getsize(file_path)
    content_type = _get_content_type(file_path)

    # -- Range request handling --
    range_header = request.headers.get("Range", "")
    if range_header:
        parsed = _parse_range(range_header, file_size)
        if parsed is None:
            return HttpResponse(status=416)  # Range Not Satisfiable

        start, end = parsed
        length = end - start + 1

        response = HttpResponse(
            streaming_content=_file_slice_iter(file_path, start, length),
            content_type=content_type,
            status=206,
        )
        response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        response["Content-Length"] = str(length)
    else:
        # Full file response
        response = FileResponse(
            open(file_path, "rb"),  # noqa: SIM115
            content_type=content_type,
        )
        response["Content-Length"] = str(file_size)

    response["Accept-Ranges"] = "bytes"
    response["Cache-Control"] = "public, max-age=86400"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _file_slice_iter(file_path: str, start: int, length: int):
    """Generator that yields byte slices from a file.

    Memory-efficient for large files — reads in 64KB chunks.
    """
    chunk_size = 64 * 1024  # 64KB
    remaining = length
    with open(file_path, "rb") as f:
        f.seek(start)
        while remaining > 0:
            read_size = min(chunk_size, remaining)
            data = f.read(read_size)
            if not data:
                break
            remaining -= len(data)
            yield data


# ---------------------------------------------------------------------------
# 2. Video Upload Endpoint
# ---------------------------------------------------------------------------


@require_POST
@login_required
@csrf_exempt
def video_upload(request: HttpRequest) -> JsonResponse:
    """Upload a video file and associate it with a lesson.

    Requires authentication. Accepts multipart/form-data with fields:
    - ``lesson_id`` (int, required) — FK to the lesson.
    - ``file`` (File, required) — the video file.
    - ``title`` (str, optional) — display title.
    - ``is_preview`` (bool, optional) — free preview flag.
    - ``description`` (str, optional) — video description.

    Returns JSON with the created Video metadata.
    """
    lesson_id = request.POST.get("lesson_id")
    if not lesson_id:
        return JsonResponse({"error": "lesson_id is required"}, status=400)

    lesson = get_object_or_404(Lesson, pk=lesson_id)

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    # Validate file size (max 2GB)
    if uploaded_file.size > 2 * 1024 * 1024 * 1024:
        return JsonResponse(
            {"error": "File too large. Maximum size is 2GB."}, status=413
        )

    # Validate file type
    ext = Path(uploaded_file.name).suffix.lower()
    allowed_extensions = {".mp4", ".webm", ".ogv", ".mov", ".m4v", ".avi", ".mkv"}
    if ext not in allowed_extensions:
        return JsonResponse(
            {
                "error": f"Unsupported file format '{ext}'. "
                f"Allowed: {', '.join(sorted(allowed_extensions))}"
            },
            status=415,
        )

    title = request.POST.get("title", "").strip() or Path(uploaded_file.name).stem
    is_preview = request.POST.get("is_preview", "").lower() in ("true", "1", "yes")

    video = Video.objects.create(
        lesson=lesson,
        title=title,
        description=request.POST.get("description", "").strip(),
        file=uploaded_file,
        file_size=uploaded_file.size,
        video_format=ext.lstrip("."),
        is_preview=is_preview,
        processing_status=Video.ProcessingStatus.PENDING,
    )

    logger.info("Video uploaded: %s (pk=%d, size=%d)", video.title, video.pk, uploaded_file.size)

    from django.urls import reverse

    data = {
        "id": video.pk,
        "title": video.title,
        "duration": video.duration_display,
        "duration_seconds": video.duration_seconds,
        "file_size": video.file_size_display,
        "format": video.get_video_format_display(),
        "streaming_url": video.streaming_url,
        "processing_status": video.processing_status,
        "is_preview": video.is_preview,
        "created_at": video.created_at.isoformat(),
    }
    response = JsonResponse(data, status=201)
    response["Location"] = reverse("lms:video-detail", kwargs={"video_id": video.pk})
    return response


# ---------------------------------------------------------------------------
# 3. Video Detail / Metadata Endpoint
# ---------------------------------------------------------------------------


@require_GET
def video_detail(request: HttpRequest, video_id: int) -> JsonResponse:
    """Return JSON metadata for a video.

    Used by the frontend to populate the video player and lesson UI.
    """
    video = get_object_or_404(Video, pk=video_id, is_active=True)

    return JsonResponse({
        "id": video.pk,
        "lesson_id": video.lesson_id,
        "title": video.title,
        "description": video.description,
        "duration": video.duration_display,
        "duration_seconds": video.duration_seconds,
        "resolution": video.resolution_display,
        "width": video.width,
        "height": video.height,
        "file_size": video.file_size_display,
        "file_size_bytes": video.file_size,
        "format": video.get_video_format_display(),
        "processing_status": video.processing_status,
        "is_preview": video.is_preview,
        "thumbnail_url": video.thumbnail.url if video.thumbnail else "",
        "streaming_url": video.streaming_url,
        "captions": list(
            video.caption_tracks.values("language", "label", "is_default")
        ) if hasattr(video, "caption_tracks") else [],
        "created_at": video.created_at.isoformat(),
    })


# ---------------------------------------------------------------------------
# 4. Video List for a Lesson
# ---------------------------------------------------------------------------


@require_GET
def video_list(request: HttpRequest, lesson_id: int) -> JsonResponse:
    """List all active videos for a lesson."""
    videos = Video.objects.filter(
        lesson_id=lesson_id, is_active=True,
    ).order_by("sort_order", "created_at")

    return JsonResponse({
        "count": videos.count(),
        "results": [
            {
                "id": v.pk,
                "title": v.title,
                "duration": v.duration_display,
                "duration_seconds": v.duration_seconds,
                "resolution": v.resolution_display,
                "format": v.get_video_format_display(),
                "processing_status": v.processing_status,
                "is_preview": v.is_preview,
                "streaming_url": v.streaming_url,
                "thumbnail_url": v.thumbnail.url if v.thumbnail else "",
            }
            for v in videos
        ],
    })


# ---------------------------------------------------------------------------
# 5. Video Delete
# ---------------------------------------------------------------------------


def video_delete(request: HttpRequest, video_id: int) -> JsonResponse:
    """Soft-delete a video (marks inactive).

    Uses POST/DELETE to avoid accidental triggers from link previewers.
    """
    if request.method not in ("POST", "DELETE"):
        return JsonResponse({"error": "Use POST or DELETE"}, status=405)
    video = get_object_or_404(Video, pk=video_id)
    video.is_active = False
    video.save(update_fields=["is_active", "updated_at"])
    logger.info("Video soft-deleted: %s (pk=%d)", video.title, video.pk)
    return JsonResponse({"status": "deleted", "id": video_id})


# ---------------------------------------------------------------------------
# 6. Video Processing Status Update (for background workers)
# ---------------------------------------------------------------------------


@require_POST
@csrf_exempt
def video_processing_callback(request: HttpRequest, video_id: int) -> JsonResponse:
    """Callback endpoint for background video processing workers.

    Accepts JSON with:
    - ``status``: "ready" or "failed"
    - ``duration``: int (seconds)
    - ``width``: int
    - ``height``: int
    - ``bitrate``: int (kbps)
    - ``format``: str (e.g. "mp4")
    - ``error``: str (if failed)
    """
    import json

    video = get_object_or_404(Video, pk=video_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    status = data.get("status", "")

    if status == "ready":
        video.mark_ready(
            duration=data.get("duration", 0),
            width=data.get("width", 0),
            height=data.get("height", 0),
            bitrate=data.get("bitrate", 0),
            fmt=data.get("format", "mp4"),
        )
        logger.info("Video ready: %s (pk=%d)", video.title, video.pk)
    elif status == "failed":
        video.mark_failed(data.get("error", "Unknown error"))
        logger.error("Video processing failed: %s (pk=%d): %s", video.title, video.pk, data.get("error", ""))
    else:
        return JsonResponse({"error": f"Unknown status: {status}"}, status=400)

    return JsonResponse({"status": "ok"})
