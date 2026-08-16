# Precis LMS — Media Images

These are Wagtail-managed media uploads used across Precis LMS pages.
They include WhatsApp-sourced photos, dashboard designs, course imagery,
and logos. The Wagtail CMS manages renditions via its image processing
pipeline.

## Categories

| Prefix | Description |
|--------|-------------|
| `WhatsApp_Image_*` | Uploaded photos from WhatsApp |
| `img-3*` | General imagery (courses, pages) |
| `0823-DashboardDesign*` | Dashboard design mockups |
| `default-course*` | Default course thumbnail |
| `ctc_research_logo*` | CTC Research logo (archived) |

Wagtail generates the suffixed renditions (`.fill-1920x1080`, `.max-165x165`, etc.)
automatically from uploaded originals.
