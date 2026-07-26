"""
Forms for blog app.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import BlogCategory, BlogPost, BlogTag

try:
    from wagtail.images import get_image_model
    WagtailImage = get_image_model()
except Exception:
    WagtailImage = None


class BlogTagForm(forms.ModelForm):
    """Form for creating and editing blog tags."""

    class Meta:
        model = BlogTag
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tag name')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL-friendly slug')
            }),
        }


class BlogPostFilterForm(forms.Form):
    """Form for filtering blog posts."""

    tags = forms.ModelMultipleChoiceField(
        queryset=BlogTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_('Tags')
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=BlogCategory.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_('Categories')
    )
    status = forms.ChoiceField(
        choices=[
            ('', _('All')),
            ('published', _('Published')),
            ('draft', _('Draft')),
            ('archived', _('Archived')),
        ],
        required=False,
        label=_('Status')
    )

    def filter_queryset(self, queryset):
        """Apply filters to a queryset."""
        if self.is_valid():
            tags = self.cleaned_data.get('tags')
            categories = self.cleaned_data.get('categories')
            status = self.cleaned_data.get('status')

            if tags:
                queryset = queryset.filter(tags__in=tags).distinct()

            if categories:
                queryset = queryset.filter(categories__in=categories).distinct()

            if status:
                queryset = queryset.filter(status=status)

        return queryset


class BlogPostForm(forms.ModelForm):
    """Form for creating and editing blog posts from the user profile."""

    # Slug field — auto-generated from title via JS, but editable
    slug = forms.SlugField(
        required=False,
        label=_('Slug'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('auto-generated-from-title'),
            'id': 'id_slug',
        }),
        help_text=_('URL-friendly identifier. Auto-generated from title if left blank.'),
    )

    # Published date for scheduling
    published_date = forms.DateTimeField(
        required=False,
        label=_('Publish Date'),
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
        }),
        help_text=_('Schedule when this post goes live. Leave blank to publish immediately.'),
    )

    # Simple file upload for featured image (alternative to Wagtail chooser)
    featured_image_upload = forms.ImageField(
        required=False,
        label=_('Featured Image'),
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        help_text=_('Upload a featured image for this post (JPEG, PNG, WebP).'),
    )

    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'excerpt', 'content',
            'categories', 'tags', 'status', 'published_date',
            'meta_description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Post title'),
                'id': 'id_title',
                'required': True,
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Short summary (optional)'),
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('Write your post content here...'),
                'required': True,
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input',
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_status',
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('SEO description (max 160 chars)'),
                'maxlength': '160',
            }),
        }
        labels = {
            'meta_description': _('SEO Description'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill published_date from instance if editing
        if self.instance and self.instance.pk and self.instance.published_date:
            import datetime
            dt = self.instance.published_date
            # Convert to local-datetime string for datetime-local input
            self.fields['published_date'].initial = dt.strftime('%Y-%m-%dT%H:%M')

    def clean_slug(self):
        """Auto-generate slug from title if not provided."""
        from django.utils.text import slugify
        slug = self.cleaned_data.get('slug', '').strip()
        if not slug:
            title = self.cleaned_data.get('title', '')
            slug = slugify(title)
        return slug

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        content = cleaned_data.get('content', '').strip()
        title = cleaned_data.get('title', '').strip()

        if not title:
            self.add_error('title', _('Title is required.'))

        if not content:
            self.add_error('content', _('Content is required.'))

        # If publishing, require content
        if status == 'published' and not content:
            self.add_error('content', _('Content is required before publishing.'))

        return cleaned_data
