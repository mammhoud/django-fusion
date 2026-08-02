"""
About section blocks with counters, team galleries, and content sections.
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock
from ..media.gallery import MediaGalleryItemBlock
from .team import TeamMemberBlock


class CounterItemBlock(BaseBlock):
    """
    Individual counter item for statistics display.
    """
    
    icon = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Icon Class"),
        help_text=_("Font Awesome or custom icon class (e.g., 'fas fa-users')."),
    )
    
    icon_background = blocks.CharBlock(
        required=False,
        default="#3b82f6",
        max_length=20,
        label=_("Icon Background Color"),
        help_text=_("CSS color for icon background."),
    )
    
    icon_color = blocks.CharBlock(
        required=False,
        default="white",
        max_length=20,
        label=_("Icon Color"),
        help_text=_("CSS color for icon."),
    )
    
    number = blocks.IntegerBlock(
        required=True,
        min_value=0,
        label=_("Number"),
        help_text=_("The statistic number to display."),
    )
    
    number_prefix = blocks.CharBlock(
        required=False,
        max_length=10,
        label=_("Number Prefix"),
        help_text=_("Text before number (e.g., '$', '+')."),
    )
    
    number_suffix = blocks.CharBlock(
        required=False,
        max_length=10,
        label=_("Number Suffix"),
        help_text=_("Text after number (e.g., 'K', 'M', '+')."),
    )
    
    label = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Label"),
        help_text=_("Description of the statistic (e.g., 'Happy Clients')."),
    )
    
    description = blocks.TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Optional detailed description."),
    )
    
    animation = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Animate Number"),
        help_text=_("Animate the number counting up on scroll."),
    )
    
    animation_duration = blocks.IntegerBlock(
        required=False,
        default=2000,
        min_value=500,
        max_value=10000,
        label=_("Animation Duration (ms)"),
        help_text=_("Duration of counting animation in milliseconds."),
    )
    
    class Meta:
        icon = "plus-inverse"
        label = _("Counter Item")
        group = _("About")


class AboutSectionBlock(BaseBlock):
    """
     about section with video, team, counters, and content.
    """
    
    # Header Content
    welcome_text = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Welcome/Subtitle"),
        help_text=_("Small text above main title (e.g., 'Welcome', 'About Us')."),
    )
    
    main_title = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Main Title"),
        help_text=_("Primary heading for the section."),
    )
    
    tagline = blocks.CharBlock(
        required=False,
        max_length=300,
        label=_("Tagline"),
        help_text=_("Short, impactful statement."),
    )
    
    description = blocks.RichTextBlock(
        required=False,
        label=_("Description"),
        features=['bold', 'italic', 'link', 'ul', 'ol'],
        help_text=_("Main content describing your organization."),
    )
    
    # Visual Elements
    background_image = ImageChooserBlock(
        required=False,
        label=_("Background Image"),
        help_text=_("Optional background image for the section."),
    )
    
    background_overlay = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Background Overlay"),
        help_text=_("Add dark overlay over background image for better text contrast."),
    )
    
    # Video Section
    show_video = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Video Section"),
    )
    
    video_title = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Video Title"),
    )
    
    video_description = blocks.RichTextBlock(
        required=False,
        label=_("Video Description"),
    )
    
    video_link = blocks.URLBlock(
        required=False,
        label=_("Video URL"),
        help_text=_("YouTube, Vimeo, or hosted video URL."),
    )
    
    video_thumbnail = ImageChooserBlock(
        required=False,
        label=_("Video Thumbnail"),
        help_text=_("Custom thumbnail for the video."),
    )
    
    # Statistics Counters
    show_counters = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Statistics Counters"),
    )
    
    counters_title = blocks.CharBlock(
        required=False,
        default=_("Our Impact in Numbers"),
        max_length=200,
        label=_("Counters Section Title"),
    )
    
    counters = blocks.ListBlock(
        CounterItemBlock(template="blocks/pages/enhanced_about_section.html"),
        label=_("Statistics Counters"),
        max_num=8,
    )
    
    # Team Section
    show_team = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Team Section"),
    )
    
    team_title = blocks.CharBlock(
        required=False,
        default=_("Meet Our Team"),
        max_length=200,
        label=_("Team Section Title"),
    )
    
    team_description = blocks.RichTextBlock(
        required=False,
        label=_("Team Description"),
    )
    
    team_members = blocks.ListBlock(
        TeamMemberBlock(template="blocks/pages/enhanced_team_member.html"),
        label=_("Team Members"),
    )
    
    # Gallery Section
    show_gallery = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Gallery"),
    )
    
    gallery_title = blocks.CharBlock(
        required=False,
        default=_("Our Work in Action"),
        max_length=200,
        label=_("Gallery Title"),
    )
    
    gallery_items = blocks.ListBlock(
        MediaGalleryItemBlock(template="blocks/media/media_gallery_item.html"),
        label=_("Gallery Items"),
    )
    
    # Call to Action
    show_cta = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Call to Action"),
    )
    
    cta_title = blocks.CharBlock(
        required=False,
        default=_("Ready to Work With Us?"),
        max_length=200,
        label=_("CTA Title"),
    )
    
    cta_description = blocks.RichTextBlock(
        required=False,
        label=_("CTA Description"),
    )
    
    cta_button_text = blocks.CharBlock(
        required=False,
        default=_("Get in Touch"),
        max_length=50,
        label=_("CTA Button Text"),
    )
    
    cta_button_url = blocks.URLBlock(
        required=False,
        label=_("CTA Button URL"),
    )
    
    # Layout Options
    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('standard', _('Standard Layout')),
            ('split', _('Split Layout')),
            ('centered', _('Centered Layout')),
            ('modern', _('Modern Card Layout')),
        ],
        default='standard',
        label=_("Layout Style"),
    )
    
    content_alignment = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('left', _('Left Aligned')),
            ('center', _('Center Aligned')),
            ('right', _('Right Aligned')),
        ],
        default='left',
        label=_("Content Alignment"),
    )
    
    class Meta:
        icon = "info-circle"
        label = _(" About Section")
        # template was: blocks/enhanced_about_section.html
        group = _("About")
    
    def get_section_classes(self, value):
        """Get CSS classes for the about section."""
        classes = ['about-section']
        
        # Layout style
        layout = value.get('layout_style', 'standard')
        classes.append(f'about-section--{layout}')
        
        # Background overlay
        if value.get('background_overlay'):
            classes.append('has-background-overlay')
        
        # Content alignment
        alignment = value.get('content_alignment', 'left')
        if alignment == 'center':
            classes.append('text-center')
        elif alignment == 'right':
            classes.append('text-end')
        
        return ' '.join(classes)