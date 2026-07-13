from wagtail import blocks


class AssignmentBlock(blocks.StructBlock):
    """Block for course assignments"""

    title = blocks.CharBlock(required=True)
    instructions = blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])
    due_date = blocks.DateBlock(required=False)
    points = blocks.IntegerBlock(
        min_value=0, default=100, help_text="Total points for this assignment"
    )

    class Meta:
        app_label = "lms"
        icon = "edit"
        template = "courses/blocks/assignment_block.html"
