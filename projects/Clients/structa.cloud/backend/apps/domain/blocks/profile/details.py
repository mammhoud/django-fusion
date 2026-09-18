from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class SkillBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Skill or service name")
    percentage = blocks.IntegerBlock(required=True, min_value=0, max_value=100)

class AboutVideoBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    description = blocks.RichTextBlock(required=False)
    video_link = blocks.URLBlock(required=False)
    main_image = ImageChooserBlock(required=False)
    extra_images = blocks.ListBlock(ImageChooserBlock(required=False))
    skills = blocks.ListBlock(SkillBlock())

    class Meta:
        icon = "user"
        label = "About Section (Video + Skills)"

__all__ = ["SkillBlock", "AboutVideoBlock"]
