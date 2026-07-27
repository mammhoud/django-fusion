"""
 table blocks with styling and functionality.
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock

from ..base import BaseBlock


class TableBlock(BaseBlock):
    """
     table block with styling, sorting, and export features.
    """
    
    table = WagtailTableBlock(required=True,
        label=_("Table Data"), template="blocks/partials/enhanced_table.html",
        help_text=_("Enter table data with rows and columns."),
    )
    
    # Table Options
    caption = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Table Caption"),
        help_text=_("Optional caption displayed above or below the table."),
    )
    
    caption_position = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('top', _('Top')),
            ('bottom', _('Bottom')),
        ],
        default='top',
        label=_("Caption Position"),
    )
    
    # Styling Options
    table_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('default', _('Default')),
            ('striped', _('Striped Rows')),
            ('bordered', _('Bordered')),
            ('hover', _('Hover Effects')),
            ('condensed', _('Condensed')),
            ('responsive', _('Responsive Scroll')),
        ],
        default='default',
        label=_("Table Style"),
    )
    
    header_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('default', _('Default Header')),
            ('dark', _('Dark Header')),
            ('light', _('Light Header')),
            ('primary', _('Primary Color')),
            ('secondary', _('Secondary Color')),
        ],
        default='default',
        label=_("Header Style"),
    )
    
    zebra_striping = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Zebra Striping"),
        help_text=_("Alternate row background colors for better readability."),
    )
    
    # Functionality
    sortable = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Sortable Columns"),
        help_text=_("Allow sorting by clicking column headers."),
    )
    
    searchable = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Searchable"),
        help_text=_("Add search/filter functionality."),
    )
    
    pagination = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Pagination"),
        help_text=_("Split large tables into pages."),
    )
    
    rows_per_page = blocks.IntegerBlock(
        required=False,
        default=10,
        min_value=5,
        max_value=100,
        label=_("Rows Per Page"),
    )
    
    # Export Options
    exportable = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Exportable"),
        help_text=_("Allow exporting table data to CSV/Excel."),
    )
    
    export_formats = blocks.ListBlock(
        blocks.ChoiceBlock(choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel'),
            ('pdf', 'PDF'),
            ('print', 'Print'),
        ]),
        required=False,
        default=['csv'],
        label=_("Export Formats"),
    )
    
    # Advanced
    fixed_header = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Fixed Header"),
        help_text=_("Keep header visible while scrolling."),
    )
    
    column_resizing = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Column Resizing"),
        help_text=_("Allow users to resize columns."),
    )
    
    row_selection = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Row Selection"),
        help_text=_("Allow selecting rows (checkboxes)."),
    )
    
    class Meta:
        icon = "table"
        label = _(" Table")
        # template was: blocks/enhanced_table.html
        group = _("Content")
    
    def get_table_classes(self, value):
        """Get CSS classes for the table."""
        classes = ['table']
        
        # Table style classes
        style = value.get('table_style', 'default')
        if style == 'striped':
            classes.append('table-striped')
        elif style == 'bordered':
            classes.append('table-bordered')
        elif style == 'hover':
            classes.append('table-hover')
        elif style == 'condensed':
            classes.append('table-sm')
        
        # Header style classes
        header_style = value.get('header_style', 'default')
        if header_style == 'dark':
            classes.append('table-dark')
        elif header_style == 'primary':
            classes.append('table-primary')
        elif header_style == 'secondary':
            classes.append('table-secondary')
        
        # Zebra striping
        if value.get('zebra_striping', True):
            classes.append('table-zebra')
        
        return ' '.join(filter(None, classes))
    
    def get_table_config(self, value):
        """Get JavaScript configuration for table functionality."""
        import json
        
        config = {
            'sortable': value.get('sortable', False),
            'searchable': value.get('searchable', False),
            'pagination': value.get('pagination', False),
            'rowsPerPage': value.get('rows_per_page', 10),
            'exportable': value.get('exportable', False),
            'exportFormats': value.get('export_formats', ['csv']),
            'fixedHeader': value.get('fixed_header', False),
            'columnResizing': value.get('column_resizing', False),
            'rowSelection': value.get('row_selection', False),
        }
        return json.dumps(config)


class TypedTableSectionBlock(BaseBlock):
    """
    Section block for typed tables with column definitions.
    """
    
    table_title = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Table Title"),
    )
    
    table_description = blocks.RichTextBlock(
        required=False,
        label=_("Table Description"),
    )
    
    column_definitions = blocks.StreamBlock([
        ('text_column', blocks.StructBlock([
            ('name', blocks.CharBlock(required=True, label=_("Column Name"))),
            ('required', blocks.BooleanBlock(default=False, label=_("Required"))),
            ('max_length', blocks.IntegerBlock(required=False, label=_("Max Length"))),
        ], label=_("Text Column"))),
        
        ('number_column', blocks.StructBlock([
            ('name', blocks.CharBlock(required=True, label=_("Column Name"))),
            ('required', blocks.BooleanBlock(default=False, label=_("Required"))),
            ('min_value', blocks.IntegerBlock(required=False, label=_("Minimum Value"))),
            ('max_value', blocks.IntegerBlock(required=False, label=_("Maximum Value"))),
        ], label=_("Number Column"))),
        
        ('date_column', blocks.StructBlock([
            ('name', blocks.CharBlock(required=True, label=_("Column Name"))),
            ('required', blocks.BooleanBlock(default=False, label=_("Required"))),
            ('format', blocks.CharBlock(default="YYYY-MM-DD", label=_("Date Format"))),
        ], label=_("Date Column"))),
        
        ('choice_column', blocks.StructBlock([
            ('name', blocks.CharBlock(required=True, label=_("Column Name"))),
            ('required', blocks.BooleanBlock(default=False, label=_("Required"))),
            ('choices', blocks.ListBlock(
                blocks.CharBlock(label=_("Option")),
                label=_("Choices"),
            )),
        ], label=_("Choice Column"))),
    ], label=_("Column Definitions"), max_num=10)
    
    table_data = TypedTableBlock([],
        label=_("Table Data"), template="blocks/partials/enhanced_table.html",
        help_text=_("Table data will be dynamically generated based on column definitions."),
    )
    
    class Meta:
        icon = "list-ul"
        label = _("Typed Table Section")
        group = _("Content")
