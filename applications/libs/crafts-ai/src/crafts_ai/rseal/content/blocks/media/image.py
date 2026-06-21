"""
 image blocks with dual-framework styling support.
Includes image blocks, galleries, and advanced image features.
"""

import json

from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock


class SimpleImageBlock(BaseBlock):
    """
    A simple image block with minimal data.
    """
    image = ImageChooserBlock(
        required=True,
        label=_("Image"),
        help_text=_("Upload or select an image."),
    )
    alternative_text = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Alternative Text (Alt Text)"),
        help_text=_("Descriptive text for screen readers and SEO."),
    )
    lazy_loading = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Lazy Loading"),
        help_text=_("Enable lazy loading for better performance."),
    )

    class Meta:
        icon = "image"
        label = _("Simple Image")
        # template was: blocks/simple_image.html
        group = _("Media")

    def get_image_attributes(self, value):
        """Get HTML attributes for the image tag."""
        return {
            'alt': value.get('alternative_text', ''),
            'loading': 'lazy' if value.get('lazy_loading', True) else 'eager',
        }


class ImageBlock(BaseBlock):
    """
    Full image block with advanced styling options and accessibility features.
    Unused fields (caption, attribution, links) have been removed or simplified.
    """

    image = ImageChooserBlock(
        required=True,
        label=_("Image"),
        help_text=_("Upload or select an image."),
    )

    alternative_text = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Alternative Text (Alt Text)"),
        help_text=_("Descriptive text for screen readers and SEO."),
    )

    # Styling Options
    alignment = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('left', _('Left Aligned')),
            ('center', _('Center Aligned')),
            ('right', _('Right Aligned')),
            ('full', _('Full Width')),
        ],
        default='center',
        label=_("Image Alignment"),
    )

    image_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('default', _('Default')),
            ('rounded', _('Rounded Corners')),
            ('circle', _('Circular')),
            ('shadow', _('With Shadow')),
            ('border', _('With Border')),
            ('polaroid', _('Polaroid Style')),
        ],
        default='default',
        label=_("Image Style"),
    )

    max_width = blocks.CharBlock(
        required=False,
        default="100%",
        max_length=20,
        label=_("Maximum Width"),
        help_text=_("CSS value for max-width (e.g., 100%, 800px, 50vw)."),
    )

    lazy_loading = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Lazy Loading"),
        help_text=_("Enable lazy loading for better performance."),
    )

    # Responsive Images
    responsive_sizes = blocks.CharBlock(
        required=False,
        default="(max-width: 768px) 100vw, 768px",
        label=_("Responsive Sizes"),
        help_text=_("HTML sizes attribute for responsive images."),
    )

    class Meta:
        icon = "image"
        label = _("Full Image")
        # template was: blocks/enhanced_image.html
        group = _("Media")

    def get_image_attributes(self, value):
        """Get HTML attributes for the image tag."""
        attrs = {
            'alt': value.get('alternative_text', ''),
            'class': self.get_image_classes(value),
            'loading': 'lazy' if value.get('lazy_loading', True) else 'eager',
        }

        if value.get('max_width'):
            attrs['style'] = f"max-width: {value['max_width']};"

        if value.get('responsive_sizes'):
            attrs['sizes'] = value['responsive_sizes']

        return attrs

    def get_image_classes(self, value):
        """Get CSS classes for the image."""
        classes = []

        # Framework-specific classes
        styling = self.get_styling_config()
        classes.append(styling.get('image', ''))

        # Image style classes
        image_style = value.get('image_style', 'default')
        if image_style == 'rounded':
            classes.append('rounded' if self.style_framework == 'bootstrap' else f"{self.css_prefix}rounded-lg")
        elif image_style == 'circle':
            classes.append('rounded-circle' if self.style_framework == 'bootstrap' else f"{self.css_prefix}rounded-full")
        elif image_style == 'shadow':
            classes.append('shadow' if self.style_framework == 'bootstrap' else f"{self.css_prefix}shadow-md")
        elif image_style == 'border':
            classes.append('border' if self.style_framework == 'bootstrap' else f"{self.css_prefix}border {self.css_prefix}border-gray-300")

        # Alignment classes
        alignment = value.get('alignment', 'center')
        if alignment == 'center':
            classes.append('mx-auto d-block' if self.style_framework == 'bootstrap' else f"{self.css_prefix}mx-auto")
        elif alignment == 'left':
            classes.append('float-start' if self.style_framework == 'bootstrap' else f"{self.css_prefix}float-left")
        elif alignment == 'right':
            classes.append('float-end' if self.style_framework == 'bootstrap' else f"{self.css_prefix}float-right")

        return ' '.join(filter(None, classes))


class ImageGalleryBlock(BaseBlock):
    """
     gallery block with multiple layout options and lightbox support.
    """

    gallery_title = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Gallery Title"),
        help_text=_("Optional title for the gallery section."),
    )

    gallery_description = blocks.RichTextBlock(
        required=False,
        label=_("Gallery Description"),
        features=['bold', 'italic', 'link'],
        help_text=_("Optional description for the gallery."),
    )

    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('grid', _('Grid Layout')),
            ('masonry', _('Masonry Layout')),
            ('carousel', _('Carousel/Slider')),
            ('justified', _('Justified Grid')),
            ('lightbox', _('Lightbox Gallery')),
        ],
        default='grid',
        label=_("Layout Style"),
    )

    columns_desktop = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('1', '1 Column'),
            ('2', '2 Columns'),
            ('3', '3 Columns'),
            ('4', '4 Columns'),
            ('5', '5 Columns'),
            ('6', '6 Columns'),
        ],
        default='3',
        label=_("Desktop Columns"),
    )

    columns_mobile = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('1', '1 Column'),
            ('2', '2 Columns'),
        ],
        default='1',
        label=_("Mobile Columns"),
    )

    image_aspect_ratio = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('original', _('Original Ratio')),
            ('square', _('Square (1:1)')),
            ('landscape', _('Landscape (16:9)')),
            ('portrait', _('Portrait (4:5)')),
        ],
        default='original',
        label=_("Aspect Ratio"),
    )

    gap_size = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('none', _('No Gap')),
            ('small', _('Small Gap')),
            ('medium', _('Medium Gap')),
            ('large', _('Large Gap')),
        ],
        default='medium',
        label=_("Gap Between Images"),
    )

    show_captions = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('never', _('Never Show')),
            ('hover', _('Show on Hover')),
            ('always', _('Always Show')),
        ],
        default='hover',
        label=_("Show Captions"),
    )

    lightbox_enabled = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Enable Lightbox"),
        help_text=_("Allow clicking images to open in lightbox view."),
    )

    images = blocks.ListBlock(
        ImageBlock(template="components/blocks/media/image.html"),
        label=_("Gallery Images"),
        help_text=_("Add images to the gallery."),
    )

    # Navigation
    show_navigation = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Navigation"),
        help_text=_("Show next/previous buttons for carousel layout."),
    )

    show_dots = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Dots"),
        help_text=_("Show navigation dots for carousel layout."),
    )

    autoplay = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Autoplay"),
        help_text=_("Automatically rotate slides in carousel layout."),
    )

    autoplay_speed = blocks.IntegerBlock(
        required=False,
        default=3000,
        min_value=1000,
        max_value=10000,
        label=_("Autoplay Speed (ms)"),
        help_text=_("Time between slides in milliseconds."),
    )

    class Meta:
        icon = "image"
        label = _(" Image Gallery")
        # template was: blocks/enhanced_image_gallery.html
        group = _("Media")

    def get_gallery_config(self, value):
        """Get gallery configuration for JavaScript."""
        config = {
            'layout': value.get('layout_style', 'grid'),
            'lightbox': value.get('lightbox_enabled', True),
            'columns': {
                'desktop': int(value.get('columns_desktop', '3')),
                'mobile': int(value.get('columns_mobile', '1')),
            },
            'carousel': {
                'navigation': value.get('show_navigation', True),
                'dots': value.get('show_dots', True),
                'autoplay': value.get('autoplay', False),
                'autoplaySpeed': value.get('autoplay_speed', 3000),
            }
        }
        return json.dumps(config)

    def get_gallery_classes(self, value):
        """Get CSS classes for the gallery container."""
        classes = []

        # Layout classes
        layout = value.get('layout_style', 'grid')
        if layout == 'grid':
            classes.append('gallery-grid')
        elif layout == 'masonry':
            classes.append('gallery-masonry')
        elif layout == 'carousel':
            classes.append('gallery-carousel')

        # Gap classes
        gap = value.get('gap_size', 'medium')
        if self.style_framework == 'tailwind':
            gap_map = {
                'none': f"{self.css_prefix}gap-0",
                'small': f"{self.css_prefix}gap-2",
                'medium': f"{self.css_prefix}gap-4",
                'large': f"{self.css_prefix}gap-6",
            }
        else:  # Bootstrap
            gap_map = {
                'none': 'g-0',
                'small': 'g-2',
                'medium': 'g-4',
                'large': 'g-5',
            }

        if gap in gap_map:
            classes.append(gap_map[gap])

        return ' '.join(filter(None, classes))
