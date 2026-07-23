"""
Text utility functions for django-fusion.
Provides text manipulation and slug generation utilities.
"""
from django.utils.text import slugify as django_slugify


def slugify_unique(model_class, text, slug_field="slug", max_length=50):
    """
    Generate unique slug for a model instance.

    Args:
        model_class: Django model class
        text: Text to slugify
        slug_field: Name of the slug field (default: 'slug')
        max_length: Maximum length of slug (default: 50)

    Returns:
        Unique slug string

    Example:
        >>> from myapp.models import Article
        >>> slug = slugify_unique(Article, "My Article Title")
        >>> # Returns: "my-article-title" or "my-article-title-2" if exists
    """
    base_slug = django_slugify(text)[:max_length]
    slug = base_slug
    counter = 1

    while model_class.objects.filter(**{slug_field: slug}).exists():
        suffix = f"-{counter}"
        max_base_length = max_length - len(suffix)
        slug = f"{base_slug[:max_base_length]}{suffix}"
        counter += 1

    return slug


def generate_unique_slug(model_class, title, slug_field="slug"):
    """
    Generate unique slug for a model instance (alias for slugify_unique).

    Args:
        model_class: Django model class
        title: Title text to slugify
        slug_field: Name of the slug field (default: 'slug')

    Returns:
        Unique slug string

    Example:
        >>> from myapp.models import Post
        >>> slug = generate_unique_slug(Post, "Hello World")
        >>> # Returns: "hello-world" or "hello-world-2" if exists
    """
    return slugify_unique(model_class, title, slug_field)


def truncate_words(text, num_words=50, suffix="..."):
    """
    Truncate text to specified number of words.

    Args:
        text: Text to truncate
        num_words: Maximum number of words (default: 50)
        suffix: Suffix to add if truncated (default: '...')

    Returns:
        Truncated text string

    Example:
        >>> text = "This is a very long text that needs to be truncated"
        >>> truncate_words(text, 5)
        'This is a very long...'
    """
    if not text:
        return ""

    words = text.split()
    if len(words) <= num_words:
        return text

    return " ".join(words[:num_words]) + suffix


def truncate_chars(text, num_chars=100, suffix="..."):
    """
    Truncate text to specified number of characters.

    Args:
        text: Text to truncate
        num_chars: Maximum number of characters (default: 100)
        suffix: Suffix to add if truncated (default: '...')

    Returns:
        Truncated text string

    Example:
        >>> text = "This is a very long text"
        >>> truncate_chars(text, 10)
        'This is a...'
    """
    if not text:
        return ""

    if len(text) <= num_chars:
        return text

    return text[:num_chars] + suffix


def strip_html_tags(text):
    """
    Remove HTML tags from text.

    Args:
        text: Text containing HTML tags

    Returns:
        Text with HTML tags removed

    Example:
        >>> strip_html_tags("<p>Hello <strong>World</strong></p>")
        'Hello World'
    """
    import re

    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def capitalize_words(text):
    """
    Capitalize first letter of each word.

    Args:
        text: Text to capitalize

    Returns:
        Text with capitalized words

    Example:
        >>> capitalize_words("hello world")
        'Hello World'
    """
    return " ".join(word.capitalize() for word in text.split())
