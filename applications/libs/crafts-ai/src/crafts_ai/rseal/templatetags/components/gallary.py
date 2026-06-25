from django import template
from wagtail.images.models import Image

register = template.Library()


@register.inclusion_tag("tags/gallery.html", takes_context=True)
def gallery(context, gallery):
    images = Image.objects.filter(collection=gallery)

    return {
        "images": images,
        "request": context["request"],
    }

@register.inclusion_tag("blocks/gallery_blocks.html", takes_context=True)
def gallery_blocks(context, gallery, image_count=None):
    """
    Retrieves a gallery of images from the specified collection.
    If `image_count` is provided, it limits the number of images returned.
    """
    images = Image.objects.filter(collection=gallery)

    if image_count is not None:
        images = images[:image_count]

    return {
        "images": images,
        "images_count": images.count(),
        "request": context["request"],
    }

@register.inclusion_tag("setup/partials/about_brand_gallery.html", takes_context=True)
def gallery_brand(context, gallery, image_count=None):
    """
    Retrieves a gallery of images from the specified collection.
    """
    images = Image.objects.filter(collection=gallery)

    if image_count is not None:
        images = images[:image_count]

    return {
        "images": images,
        "images_count": images.count(),
        "request": context["request"],
    }
