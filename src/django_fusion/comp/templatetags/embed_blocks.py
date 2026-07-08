from django import template

register = template.Library()

@register.filter
def youtube_embed_url(url):
    """
    Convert YouTube URL to embed URL
    """
    if 'youtube.com/watch?v=' in url:
        video_id = url.split('youtube.com/watch?v=')[1].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    return url

@register.filter
def vimeo_embed_url(url):
    """
    Convert Vimeo URL to embed URL
    """
    if 'vimeo.com/' in url:
        video_id = url.split('vimeo.com/')[1].split('/')[-1]
        return f'https://player.vimeo.com/video/{video_id}'
    return url

@register.filter
def is_youtube_url(url):
    return 'youtube.com' in url or 'youtu.be' in url

@register.filter
def is_vimeo_url(url):
    return 'vimeo.com' in url
