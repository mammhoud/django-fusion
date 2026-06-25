"""
Hero Section Block for Wagtail StreamField
------------------------------------------

This module defines a flexible hero/section block that replicates the original
HTML snippet. Editors can modify the title, background image, dark overlay,
and call-to-action button.

Usage
-----
Include this block in a StreamField on any Wagtail page. The template
`blocks/hero_section.html` will be used to render it.

Example
-------
page.hero_section = [
    ("hero_section", {
        "title": "Andor Studio Multipurpose HTML5 Template",
        "background_image": <Image>,
        "overlay_opacity": "0.6",
        "button_text": "Contact Us",
        "button_link": "/contact/"
    })
]
"""

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HeroSectionBlock(blocks.StructBlock):
    """A customizable hero/landing section with background image and CTA."""

    title = blocks.CharBlock(required=True, help_text="Main heading text.")
    background_image = ImageChooserBlock(required=True, help_text="Background image.")
    overlay_opacity = blocks.DecimalBlock(
        required=False,
        default=0.6,
        help_text="Dark overlay opacity (0–1).",
    )
    button_text = blocks.CharBlock(required=True, default="Learn More")
    button_link = blocks.URLBlock(required=True)

    class Meta:
        icon = "image"
        label = "Hero Section"
