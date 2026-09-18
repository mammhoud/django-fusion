"""
 video blocks with dual-framework styling support.
Includes video players, galleries, and advanced video features.
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock


class SimpleVideoBlock(BaseBlock):
    """
    A simple video block with minimal data.
    """

    embed_url = blocks.URLBlock(
        required=True,
        label=_("Embed URL / Video URL"),
        help_text=_("URL from YouTube, Vimeo, or other video service."),
    )

    class Meta:
        icon = "media"
        label = _("Simple Video")
        # template was: blocks/simple_video.html
        group = _("Media")

    def get_player_attributes(self, value):
        return {'loading': 'lazy'}


class VideoBlock(BaseBlock):
    """
     video block with advanced features.
    """

    # Embed Source
    embed_url = blocks.URLBlock(
        required=False,
        label=_("Embed URL"),
        help_text=_("URL from YouTube, Vimeo, or other embeddable video service."),
    )

    # Content
    video_title = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Video Title"),
        help_text=_("Title displayed above or with the video."),
    )

    video_description = blocks.RichTextBlock(
        required=False,
        label=_("Video Description"),
        features=['bold', 'italic', 'link'],
        help_text=_("Description displayed with the video."),
    )

    # Thumbnail & Preview
    thumbnail_image = ImageChooserBlock(
        required=False,
        label=_("Thumbnail Image"),
        help_text=_("Custom thumbnail image. If not provided, will use service thumbnail."),
    )

    class Meta:
        icon = "media"
        label = _("Full Video Player")
        # template was: blocks/enhanced_video.html
        group = _("Media")

    def get_player_attributes(self, value):
        """Get attributes for the video player."""
        return {'loading': 'lazy'}

    def get_player_classes(self, value):
        """Get CSS classes for the video player container."""
        classes = []

        # Size classes
        size = value.get('player_size', 'medium')
        if self.style_framework == 'tailwind':
            size_map = {
                'small': f"{self.css_prefix}max-w-md",
                'medium': f"{self.css_prefix}max-w-2xl",
                'large': f"{self.css_prefix}max-w-4xl",
                'full': f"{self.css_prefix}w-full",
            }
        else:  # Bootstrap
            size_map = {
                'small': 'col-md-6',
                'medium': 'col-md-8 col-lg-6',
                'large': 'col-md-10 col-lg-8',
                'full': 'col-12',
            }

        if size in size_map:
            classes.append(size_map[size])

        # Alignment classes
        alignment = value.get('alignment', 'center')
        if alignment == 'center':
            classes.append('mx-auto')
        elif alignment == 'left':
            classes.append('me-auto')
        elif alignment == 'right':
            classes.append('ms-auto')

        # Aspect ratio classes
        ratio = value.get('player_ratio', '16:9')
        if ratio == '16:9':
            classes.append('ratio ratio-16x9')
        elif ratio == '4:3':
            classes.append('ratio ratio-4x3')
        elif ratio == '1:1':
            classes.append('ratio ratio-1x1')

        return ' '.join(filter(None, classes))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context['player_attributes'] = self.get_player_attributes(value)
        context['player_classes'] = self.get_player_classes(value)
        return context


class VideoGalleryBlock(BaseBlock):
    """
    Gallery block for multiple videos with playlist functionality.
    """

    gallery_title = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Gallery Title"),
    )

    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('grid', _('Video Grid')),
            ('playlist', _('Video Playlist')),
            ('carousel', _('Video Carousel')),
        ],
        default='grid',
        label=_("Layout Style"),
    )

    show_playlist = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Playlist"),
        help_text=_("Display a playlist of all videos."),
    )

    playlist_position = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('side', _('Sidebar')),
            ('bottom', _('Bottom')),
            ('hidden', _('Hidden (Mobile Only)')),
        ],
        default='side',
        label=_("Playlist Position"),
    )

    autoplay_next = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Autoplay Next Video"),
        help_text=_("Automatically play next video when current ends."),
    )

    videos = blocks.ListBlock(
        SimpleVideoBlock(template="blocks/media/video_lite.html"),
        label=_("Gallery Videos"),
        help_text=_("Add videos to the gallery."),
    )

    class Meta:
        icon = "media"
        label = _("Video Gallery")
        group = _("Media")
