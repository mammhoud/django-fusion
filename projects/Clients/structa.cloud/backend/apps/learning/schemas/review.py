from __future__ import annotations

from apps.learning.models import Review


def review_to_dict(review: Review) -> dict:
    """Public JSON shape for a published review (Precis ``ReviewSchema`` parity)."""
    return {
        "id": review.pk,
        "course": {
            "id": review.course_id,
            "title": review.course.title,
            "slug": review.course.slug,
        },
        "user": {
            "id": review.user_id,
            "username": review.user.username,
            "first_name": review.user.first_name,
            "last_name": review.user.last_name,
        },
        "rating": review.rating,
        "comment": review.body,
        "stars": review.stars,
        "created_at": review.created_at.isoformat(),
    }
