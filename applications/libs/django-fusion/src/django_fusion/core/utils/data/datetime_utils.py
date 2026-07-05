"""
Date and time utility functions for django-fusion.
Provides datetime formatting and manipulation utilities.
"""
from datetime import datetime, timedelta

from django.utils import timezone


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., '2 hours ago').

    Args:
        dt: Datetime object to format

    Returns:
        Human-readable relative time string
    """
    if not dt:
        return ""

    now = timezone.now()
    diff = now - dt

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"


def format_duration(seconds: int) -> str:
    """
    Format seconds as human-readable duration.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        parts = [f"{hours}h"]
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0:
            parts.append(f"{secs}s")

        return " ".join(parts)


def format_date_range(start_date: datetime, end_date: datetime) -> str:
    """
    Format date range as human-readable string.

    Args:
        start_date: Start datetime
        end_date: End datetime

    Returns:
        Formatted date range string
    """
    if not start_date or not end_date:
        return ""

    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}"
        else:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    else:
        return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"


def get_time_until(target_date: datetime) -> str:
    """
    Get human-readable time until target date.

    Args:
        target_date: Target datetime

    Returns:
        Time until target date string
    """
    if not target_date:
        return ""

    now = timezone.now()
    diff = target_date - now

    if diff.total_seconds() < 0:
        return "expired"

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''}"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "less than a minute"


def is_business_day(date: datetime) -> bool:
    """
    Check if date is a business day (Monday-Friday).

    Args:
        date: Date to check

    Returns:
        True if business day, False otherwise
    """
    return date.weekday() < 5  # 0-4 are Monday-Friday


def get_next_business_day(date: datetime = None) -> datetime:
    """
    Get next business day from given date.

    Args:
        date: Starting date (default: today)

    Returns:
        Next business day datetime
    """
    if date is None:
        date = timezone.now()

    next_day = date + timedelta(days=1)

    while not is_business_day(next_day):
        next_day += timedelta(days=1)

    return next_day
