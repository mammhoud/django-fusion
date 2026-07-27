from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock

__all__ = ["ButtonBlock", "BadgeBlock", "CTABlock"]


class ButtonBlock(BaseBlock):
    """Reusable button component."""

    text = blocks.CharBlock(
        max_length=100,
        required=True,
        label=_("Button Text"),
        help_text=_("Text displayed on the button")
    )

    link = blocks.URLBlock(
        required=False,
        label=_("Link URL"),
        help_text=_("External URL for the button")
    )

    page = blocks.PageChooserBlock(
        required=False,
        label=_("Internal Page"),
        help_text=_("Link to an internal page")
    )

    style = blocks.ChoiceBlock(
        choices=[
            ('primary', _("Primary")),
            ('secondary', _("Secondary")),
            ('outline', _("Outline")),
            ('ghost', _("Ghost")),
            ('link', _("Text Link")),
        ],
        default='primary',
        label=_("Button Style"),
        help_text=_("Visual style of the button")
    )

    size = blocks.ChoiceBlock(
        choices=[
            ('sm', _("Small")),
            ('md', _("Medium")),
            ('lg', _("Large")),
        ],
        default='md',
        label=_("Button Size")
    )

    icon = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Icon Class"),
        help_text=_("Optional icon class (e.g., 'fa-arrow-right', 'icon-phone')")
    )

    icon_position = blocks.ChoiceBlock(
        choices=[
            ('left', _("Left")),
            ('right', _("Right")),
        ],
        default='right',
        required=False,
        label=_("Icon Position")
    )

    open_in_new_tab = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Open in New Tab")
    )

    class Meta:
        icon = "link"
        label = _("Button")
        # template was: blocks/button_block.html

    def get_link_url(self, value):
        """Resolve the actual URL from either external link or internal page."""
        if value.get('link'):
            return value['link']
        elif value.get('page'):
            return value['page'].url
        return "#"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context['url'] = self.get_link_url(value)
        return context


class BadgeBlock(blocks.StructBlock):
    """Optional badge component for CTAs."""

    text = blocks.CharBlock(
        max_length=50,
        required=True,
        label=_("Badge Text")
    )

    color = blocks.ChoiceBlock(
        choices=[
            ('default', _("Default")),
            ('primary', _("Primary")),
            ('success', _("Success")),
            ('warning', _("Warning")),
            ('danger', _("Danger")),
            ('info', _("Info")),
        ],
        default='primary',
        label=_("Badge Color")
    )

    style = blocks.ChoiceBlock(
        choices=[
            ('filled', _("Filled")),
            ('outline', _("Outline")),
            ('soft', _("Soft")),
        ],
        default='soft',
        label=_("Badge Style")
    )

    class Meta:
        icon = "tag"
        label = _("Badge")
        # template was: blocks/badge_block.html



class CTABlock(BaseBlock):
    """
    Comprehensive Call to Action block with multiple layouts and features.
    Supports hero CTAs, inline CTAs, cards, and more.
    """

    # -------------------------------------------------------------------------
    # BASIC SETTINGS
    # -------------------------------------------------------------------------
    layout = blocks.ChoiceBlock(
        choices=[
            ('simple', _("Simple")),
            ('centered', _("Centered")),
            ('split', _("Split Layout")),
            ('card', _("Card Style")),
            ('hero', _("Hero Style")),
            ('inline', _("Inline")),
        ],
        default='centered',
        label=_("Layout"),
        help_text=_("Choose the layout style for the CTA")
    )

    width = blocks.ChoiceBlock(
        choices=[
            ('full', _("Full Width")),
            ('container', _("Container Width")),
            ('narrow', _("Narrow Width")),
        ],
        default='container',
        label=_("Width"),
        help_text=_("Content width constraint")
    )

    alignment = blocks.ChoiceBlock(
        choices=[
            ('left', _("Left Aligned")),
            ('center', _("Center Aligned")),
            ('right', _("Right Aligned")),
        ],
        default='center',
        label=_("Text Alignment")
    )

    # -------------------------------------------------------------------------
    # VISUAL ELEMENTS
    # -------------------------------------------------------------------------
    background_type = blocks.ChoiceBlock(
        choices=[
            ('none', _("No Background")),
            ('color', _("Color")),
            ('gradient', _("Gradient")),
            ('image', _("Image")),
            ('pattern', _("Pattern")),
            ('video', _("Video Background")),
        ],
        default='color',
        label=_("Background Type"),
        help_text=_("Choose background style")
    )

    background_color = blocks.CharBlock(
        required=False,
        max_length=20,
        label=_("Background Color"),
        help_text=_("CSS color value (e.g., #f8f9fa, var(--primary-color), rgba(0,0,0,0.05))")
    )

    background_gradient = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Gradient"),
        help_text=_("CSS gradient value (e.g., linear-gradient(135deg, #667eea 0%, #764ba2 100%))")
    )

    background_image = ImageChooserBlock(
        required=False,
        label=_("Background Image"),
        help_text=_("Optional background image")
    )

    background_overlay = blocks.ChoiceBlock(
        choices=[
            ('none', _("None")),
            ('dark', _("Dark Overlay")),
            ('light', _("Light Overlay")),
            ('gradient', _("Gradient Overlay")),
        ],
        default='none',
        required=False,
        label=_("Background Overlay")
    )

    background_video = EmbedBlock(
        required=False,
        label=_("Background Video"),
        help_text=_("YouTube, Vimeo, or other embed URL")
    )

    # -------------------------------------------------------------------------
    # CONTENT
    # -------------------------------------------------------------------------
    badge = BadgeBlock(required=False,
        label=_("Optional Badge"), template="blocks/content/badge_block.html",
        help_text=_("Add a badge above the title")
    )

    title = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Title"),
        help_text=_("Main heading for the CTA")
    )

    title_tag = blocks.ChoiceBlock(
        choices=[
            ('h1', "H1"),
            ('h2', "H2"),
            ('h3', "H3"),
            ('h4', "H4"),
            ('h5', "H5"),
            ('div', "Div"),
        ],
        default='h2',
        label=_("Title HTML Tag")
    )

    subtitle = blocks.CharBlock(
        max_length=300,
        required=False,
        label=_("Subtitle"),
        help_text=_("Optional subtitle below the title")
    )

    content = blocks.RichTextBlock(
        required=False,
        label=_("Content"),
        features=['bold', 'italic', 'link', 'small'],
        help_text=_("Main content text")
    )

    # -------------------------------------------------------------------------
    # MEDIA (For split layout)
    # -------------------------------------------------------------------------
    media_type = blocks.ChoiceBlock(
        choices=[
            ('none', _("No Media")),
            ('image', _("Image")),
            ('icon', _("Icon")),
            ('video', _("Video")),
            ('illustration', _("Illustration")),
        ],
        default='none',
        label=_("Media Type"),
        help_text=_("Choose media to display alongside content")
    )

    media_image = ImageChooserBlock(
        required=False,
        label=_("Image"),
        help_text=_("Image to display (for split layout or card)")
    )

    media_icon = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Icon Class"),
        help_text=_("Icon class (e.g., 'fas fa-rocket', 'icon-phone')")
    )

    media_video = EmbedBlock(
        required=False,
        label=_("Video"),
        help_text=_("Embedded video")
    )

    media_position = blocks.ChoiceBlock(
        choices=[
            ('left', _("Left")),
            ('right', _("Right")),
            ('top', _("Top")),
            ('bottom', _("Bottom")),
        ],
        default='right',
        required=False,
        label=_("Media Position"),
        help_text=_("Position of media relative to content")
    )

    # -------------------------------------------------------------------------
    # BUTTONS
    # -------------------------------------------------------------------------
    primary_button = ButtonBlock(required=False,
        label=_("Primary Button"), template="blocks/content/button_block.html",
        help_text=_("Main call-to-action button")
    )

    secondary_button = ButtonBlock(required=False,
        label=_("Secondary Button"), template="blocks/content/button_block.html",
        help_text=_("Optional secondary button")
    )

    button_group_alignment = blocks.ChoiceBlock(
        choices=[
            ('left', _("Left")),
            ('center', _("Center")),
            ('right', _("Right")),
            ('space-between', _("Space Between")),
        ],
        default='center',
        label=_("Button Alignment"),
        help_text=_("Alignment of button group")
    )

    # -------------------------------------------------------------------------
    # ADDITIONAL ELEMENTS
    # -------------------------------------------------------------------------
    show_divider = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Divider"),
        help_text=_("Add a divider above or below the CTA")
    )

    divider_position = blocks.ChoiceBlock(
        choices=[
            ('top', _("Top")),
            ('bottom', _("Bottom")),
            ('both', _("Both")),
        ],
        default='bottom',
        required=False,
        label=_("Divider Position")
    )

    trust_indicators = blocks.ListBlock(
        blocks.StructBlock([
            ('text', blocks.CharBlock(max_length=100, label=_("Text"))),
            ('icon', blocks.CharBlock(max_length=50, required=False, label=_("Icon"))),
        ]),
        required=False,
        label=_("Trust Indicators"),
        help_text=_("Add trust badges or social proof below buttons")
    )

    # -------------------------------------------------------------------------
    # ADVANCED SETTINGS
    # -------------------------------------------------------------------------
    custom_classes = blocks.CharBlock(
        required=False,
        label=_("Custom CSS Classes"),
        help_text=_("Additional CSS classes for custom styling")
    )

    custom_id = blocks.CharBlock(
        required=False,
        label=_("Custom ID"),
        help_text=_("HTML ID attribute for the section")
    )

    spacing_top = blocks.ChoiceBlock(
        choices=[
            ('none', _("None")),
            ('small', _("Small")),
            ('medium', _("Medium")),
            ('large', _("Large")),
            ('xlarge', _("Extra Large")),
        ],
        default='medium',
        label=_("Top Spacing")
    )

    spacing_bottom = blocks.ChoiceBlock(
        choices=[
            ('none', _("None")),
            ('small', _("Small")),
            ('medium', _("Medium")),
            ('large', _("Large")),
            ('xlarge', _("Extra Large")),
        ],
        default='medium',
        label=_("Bottom Spacing")
    )

    animation = blocks.ChoiceBlock(
        choices=[
            ('none', _("None")),
            ('fade-in', _("Fade In")),
            ('slide-up', _("Slide Up")),
            ('slide-left', _("Slide Left")),
            ('zoom-in', _("Zoom In")),
        ],
        default='none',
        label=_("Animation"),
        help_text=_("Scroll animation effect")
    )

    visibility = blocks.MultipleChoiceBlock(
        choices=[
            ('desktop', _("Desktop")),
            ('tablet', _("Tablet")),
            ('mobile', _("Mobile")),
        ],
        default=['desktop', 'tablet', 'mobile'],
        label=_("Visibility"),
        help_text=_("Show on specific device sizes")
    )

    # -------------------------------------------------------------------------
    # FORM INTEGRATION (For lead capture CTAs)
    # -------------------------------------------------------------------------
    include_form = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Include Form"),
        help_text=_("Add a simple contact form to the CTA")
    )

    form_title = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Form Title"),
        help_text=_("Title for the embedded form")
    )

    form_fields = blocks.ListBlock(
        blocks.ChoiceBlock(choices=[
            ('name', _("Name")),
            ('email', _("Email")),
            ('phone', _("Phone")),
            ('company', _("Company")),
            ('message', _("Message")),
        ]),
        required=False,
        label=_("Form Fields"),
        help_text=_("Select fields to include in the form")
    )

    form_submit_text = blocks.CharBlock(
        required=False,
        max_length=50,
        default=_("Submit"),
        label=_("Form Submit Text")
    )

    # -------------------------------------------------------------------------
    # STATISTICS (For social proof)
    # -------------------------------------------------------------------------
    statistics = blocks.ListBlock(
        blocks.StructBlock([
            ('number', blocks.CharBlock(max_length=20, label=_("Number/Statistic"))),
            ('label', blocks.CharBlock(max_length=50, label=_("Label"))),
            ('prefix', blocks.CharBlock(max_length=10, required=False, label=_("Prefix"))),
            ('suffix', blocks.CharBlock(max_length=10, required=False, label=_("Suffix"))),
        ]),
        required=False,
        label=_("Statistics"),
        help_text=_("Add statistics or social proof numbers")
    )

    class Meta:
        icon = "bullhorn"
        label = _("Call to Action")
        # template was: blocks/cta_block.html
        group = _("Marketing")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        # Determine layout-specific context
        layout = value.get('layout', 'centered')
        context['is_split_layout'] = layout == 'split'
        context['is_card_layout'] = layout == 'card'
        context['is_hero_layout'] = layout == 'hero'

        # Determine if media should be shown
        media_type = value.get('media_type', 'none')
        context['has_media'] = media_type != 'none'

        # Determine if there are buttons
        context['has_primary_button'] = bool(value.get('primary_button'))
        context['has_secondary_button'] = bool(value.get('secondary_button'))
        context['has_buttons'] = context['has_primary_button'] or context['has_secondary_button']

        # Determine background style
        bg_type = value.get('background_type', 'color')
        context['has_background'] = bg_type != 'none'

        # Build CSS classes
        css_classes = []

        # Layout classes
        css_classes.append(f"cta-layout-{layout}")
        css_classes.append(f"cta-align-{value.get('alignment', 'center')}")
        css_classes.append(f"cta-width-{value.get('width', 'container')}")

        # Background classes
        if bg_type != 'none':
            css_classes.append(f"cta-bg-{bg_type}")
            if value.get('background_overlay') and value['background_overlay'] != 'none':
                css_classes.append(f"cta-overlay-{value['background_overlay']}")

        # Spacing classes
        css_classes.append(f"cta-spacing-top-{value.get('spacing_top', 'medium')}")
        css_classes.append(f"cta-spacing-bottom-{value.get('spacing_bottom', 'medium')}")

        # Animation class
        if value.get('animation') and value['animation'] != 'none':
            css_classes.append(f"cta-animate-{value['animation']}")

        # Add custom classes
        if value.get('custom_classes'):
            css_classes.extend(value['custom_classes'].split())

        context['css_classes'] = ' '.join(css_classes)

        # Build inline styles for background
        inline_styles = []

        if bg_type == 'color' and value.get('background_color'):
            inline_styles.append(f"background-color: {value['background_color']};")
        elif bg_type == 'gradient' and value.get('background_gradient'):
            inline_styles.append(f"background: {value['background_gradient']};")

        context['inline_styles'] = ' '.join(inline_styles)

        return context

    def clean(self, value):
        """Validate block data."""
        cleaned_data = super().clean(value)

        # Validate that either link or page is provided for buttons
        if cleaned_data.get('primary_button'):
            btn = cleaned_data['primary_button']
            if not btn.get('link') and not btn.get('page'):
                raise forms.ValidationError(_("Primary button must have either a link or a page selected."))

        if cleaned_data.get('secondary_button'):
            btn = cleaned_data['secondary_button']
            if not btn.get('link') and not btn.get('page'):
                raise forms.ValidationError(_("Secondary button must have either a link or a page selected."))

        # Validate media based on type
        media_type = cleaned_data.get('media_type', 'none')
        if media_type == 'image' and not cleaned_data.get('media_image'):
            raise forms.ValidationError(_("Image is required when media type is set to Image."))
        elif media_type == 'icon' and not cleaned_data.get('media_icon'):
            raise forms.ValidationError(_("Icon class is required when media type is set to Icon."))
        elif media_type == 'video' and not cleaned_data.get('media_video'):
            raise forms.ValidationError(_("Video embed is required when media type is set to Video."))

        # Validate split layout requires media
        if cleaned_data.get('layout') == 'split' and media_type == 'none':
            raise forms.ValidationError(_("Split layout requires media to be selected."))

        return cleaned_data
