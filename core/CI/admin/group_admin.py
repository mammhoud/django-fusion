"""
Django admin configuration for Wagtail group and role management.

Provides admin interface for managing groups, roles, and content access.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.CI.models.group import (
    GroupContentAccess,
    RoleEmailMapping,
    WagtailGroupRole,
)


@admin.register(WagtailGroupRole)
class WagtailGroupRoleAdmin(admin.ModelAdmin):
    """Admin interface for WagtailGroupRole."""

    list_display = (
        'group',
        'role_type',
        'parent_role',
        'is_active',
        'created_at',
    )
    list_filter = (
        'role_type',
        'is_active',
        'created_at',
    )
    search_fields = (
        'group__name',
        'description',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'group',
                'role_type',
                'description',
            )
        }),
        (_('Hierarchy'), {
            'fields': (
                'parent_role',
            )
        }),
        (_('Status'), {
            'fields': (
                'is_active',
            )
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('group', 'parent_role__group')


@admin.register(GroupContentAccess)
class GroupContentAccessAdmin(admin.ModelAdmin):
    """Admin interface for GroupContentAccess."""

    list_display = (
        'group',
        'content_type',
        'access_level',
        'content_id',
        'created_at',
    )
    list_filter = (
        'content_type',
        'access_level',
        'created_at',
    )
    search_fields = (
        'group__name',
        'content_type',
        'content_id',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (_('Group and Content'), {
            'fields': (
                'group',
                'content_type',
                'content_id',
            )
        }),
        (_('Access Control'), {
            'fields': (
                'access_level',
            )
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('group')


@admin.register(RoleEmailMapping)
class RoleEmailMappingAdmin(admin.ModelAdmin):
    """Admin interface for RoleEmailMapping."""

    list_display = (
        'email_role',
        'wagtail_group',
        'is_active',
        'created_at',
    )
    list_filter = (
        'is_active',
        'created_at',
    )
    search_fields = (
        'email_role',
        'wagtail_group__name',
        'description',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (_('Mapping'), {
            'fields': (
                'email_role',
                'wagtail_group',
            )
        }),
        (_('Description'), {
            'fields': (
                'description',
            )
        }),
        (_('Status'), {
            'fields': (
                'is_active',
            )
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('wagtail_group')
