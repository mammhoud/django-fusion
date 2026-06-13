# Portfolio Management

## Overview
Managing portfolio projects in VResume is simple thanks to Wagtail CMS.

## Feature Tags
 (`apps/pages/models/pages/portfolio.py`)

#### New Field:
```python
featured_tags = models.ManyToManyField(
    PortfolioTag,
    blank=True,
    related_name="featured_in_portfolio_page",
    verbose_name=_("Featured Tags"),
    help_text=_("Select tags to display prominently on the portfolio page")
)
```

#### Updated Admin Interface:
```python
content_panels = BasePage.content_panels + [
    FieldPanel("projects"),
    FieldPanel("featured_tags"),
]

edit_handler = TabbedInterface([
    ObjectList(content_panels, heading=_("Content")),
    ObjectList(BasePage.promote_panels, heading=_("Promote")),
    ObjectList(BasePage.settings_panels, heading=_("Settings")),
])
```

#### New Method:
```python
def get_featured_tags(self):
    """Get featured tags selected for this portfolio page."""
    return self.featured_tags.all().order_by('name')
```

#### Updated Context:
- Added `featured_tags` to context in `get_context()` method
- Available in templates as `{{ featured_tags }}`

---


