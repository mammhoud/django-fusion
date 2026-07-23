"""
Tag managers for person tagging system.

Canonical imports::
    from django_fusion.core.managers import PersonTagCategoryManager
    from django_fusion.core.managers import PersonTagManager
    from django_fusion.core.managers import TaggedPersonManager
"""

import logging

from django.db import models
from django.db.models.aggregates import Count, Max
from django.utils import timezone

from .base import CachedManager, cached_method

logger = logging.getLogger(__name__)


class PersonTagCategoryManager(CachedManager):
    """
    Enhanced manager for PersonTagCategory with specialized methods.

    Canonical import: from django_fusion.core.managers import PersonTagCategoryManager
    """

    @cached_method(timeout=300)
    def get_categories_with_stats(self, user=None):
        """
        Get categories with statistics.

        Args:
            user: Optional user for filtering

        Returns:
            QuerySet with annotated stats
        """
        from django.db.models import Count, Q

        qs = self.annotate_with(
            annotations={
                'total_tags': Count('tags', distinct=True),
                'published_tags': Count('tags', filter=Q(tags__live=True), distinct=True),
                'active_tags': Count(
                    'tags',
                    filter=Q(tags__tagged_persons__content_object__is_active=True),
                    distinct=True
                ),
            },
            ordering=['name']
        )

        if user:
            qs = qs.filter(
                tags__tagged_persons__content_object__user=user
            ).distinct()

        return qs

    def get_popular_categories(self, limit=10):
        """
        Get most popular categories based on tag usage.

        Args:
            limit: Maximum categories to return

        Returns:
            List of popular categories
        """
        from django.db.models import Count

        return self.annotate_with(
            annotations={
                'usage_count': Count(
                    'tags__tagged_persons',
                    filter=models.Q(tags__tagged_persons__content_object__is_active=True),
                    distinct=True
                ),
                'tag_count': Count('tags', distinct=True),
            },
            ordering=['-usage_count']
        )[:limit]

    def get_category_tree(self):
        """
        Get hierarchical category structure.

        Returns:
            Nested category structure
        """
        categories = self.all()
        tree = []

        # Build tree structure
        for category in categories:
            tree.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'total_tags': category.tags.count(),
                'published_tags': category.tags.filter(live=True).count(),
            })

        return tree

    def cleanup_unused_categories(self, days_threshold=90):
        """
        Clean up categories with no recent activity.

        Args:
            days_threshold: Days of inactivity

        Returns:
            Number of deleted categories
        """
        from django.db.models import Max

        cutoff_date = timezone.now() - timezone.timedelta(days=days_threshold)

        # Find categories with no recent tag usage
        unused_categories = self.annotate_with(
            annotations={
                'last_used': Max('tags__last_used'),
                'tag_count': Count('tags'),
            }
        ).filter(
            tag_count=0,
            created_at__lt=cutoff_date
        )

        count = unused_categories.count()
        unused_categories.delete()

        return count

    def get_category_with_tags(self, category_slug):
        """
        Get category with all its tags.

        Args:
            category_slug: Category slug

        Returns:
            Category with prefetched tags
        """
        return self.filter(slug=category_slug).prefetch_related(
            'tags',
            'tags__tagged_persons'
        ).first()


class PersonTagManager(CachedManager):
    """
    Enhanced manager for PersonTag with advanced query capabilities.

    Canonical import: from django_fusion.core.managers import PersonTagManager
    """

    @cached_method(timeout=300)
    def get_tags_with_stats(self, category=None, user=None):
        """
        Get tags with comprehensive statistics.

        Args:
            category: Optional category filter
            user: Optional user filter

        Returns:
            QuerySet with annotated stats
        """
        from django.db.models import Count, Max, Q

        qs = self.annotate_with(
            annotations={
                'usage_count': Count(
                    'tagged_persons',
                    filter=Q(tagged_persons__content_object__is_active=True),
                    distinct=True
                ),
                'recent_usage': Max(
                    'tagged_persons__created_at',
                    filter=Q(tagged_persons__content_object__is_active=True)
                ),
                'category_name': models.F('category__name'),
                'category_slug': models.F('category__slug'),
            },
            ordering=['-usage_count', 'name']
        )

        if category:
            qs = qs.filter(category=category)

        if user:
            qs = qs.filter(
                tagged_persons__content_object__user=user
            ).distinct()

        return qs

    def search_tags(self, query, category=None, limit=20):
        """
        Search tags with advanced filtering.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results

        Returns:
            QuerySet of matching tags
        """
        from django.db.models import Q

        qs = self.all()

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(slug__icontains=query)
            )

        if category:
            qs = qs.filter(category=category)

        return qs[:limit]

    def get_popular_tags(self, limit=20, days=None):
        """
        Get popular tags based on usage.

        Args:
            limit: Maximum tags to return
            days: Optional time limit for usage

        Returns:
            List of popular tags
        """
        from django.db.models import Count, Q

        qs = self.all()

        if days:
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            qs = qs.annotate(
                recent_usage_count=Count(
                    'tagged_persons',
                    filter=Q(
                        tagged_persons__content_object__is_active=True,
                        tagged_persons__created_at__gte=cutoff_date
                    ),
                    distinct=True
                )
            ).order_by('-recent_usage_count')
        else:
            qs = qs.annotate(
                usage_count=Count(
                    'tagged_persons',
                    filter=Q(tagged_persons__content_object__is_active=True),
                    distinct=True
                )
            ).order_by('-usage_count')

        return qs[:limit]

    def get_related_tags(self, tag, limit=10):
        """
        Get tags related to a given tag.

        Args:
            tag: The tag to find related tags for
            limit: Maximum related tags

        Returns:
            List of related tags
        """
        from django.db.models import Count

        # Get persons tagged with this tag
        person_ids = tag.tagged_persons.filter(
            content_object__is_active=True
        ).values_list('content_object_id', flat=True)

        # Find other tags used by these persons
        related_tags = self.exclude(id=tag.id).filter(
            tagged_persons__content_object_id__in=person_ids,
            tagged_persons__content_object__is_active=True
        ).annotate(
            common_count=Count('id')
        ).order_by('-common_count')[:limit]

        return related_tags

    def merge_tags(self, source_tag, target_tag, user=None):
        """
        Merge one tag into another.

        Args:
            source_tag: Tag to merge from
            target_tag: Tag to merge into
            user: User performing the merge

        Returns:
            Tuple of (success, message, stats)
        """
        try:
            # Get all tagged items from source tag
            tagged_items = source_tag.tagged_persons.all()

            # Move tagged items to target tag
            moved_count = 0
            skipped_count = 0

            for tagged_item in tagged_items:
                # Check if target tag already exists for this object
                existing = target_tag.tagged_persons.filter(
                    content_object=tagged_item.content_object
                ).exists()

                if not existing:
                    # Create new tagged item with target tag
                    tagged_item.tag = target_tag
                    tagged_item.save()
                    moved_count += 1
                else:
                    # Skip - already tagged with target
                    tagged_item.delete()
                    skipped_count += 1

            # Update stats
            target_tag.update_usage_stats()

            # Delete source tag if it has no more tagged items
            if source_tag.tagged_persons.count() == 0:
                source_tag.delete()

            stats = {
                'moved': moved_count,
                'skipped': skipped_count,
                'source_deleted': source_tag.tagged_persons.count() == 0,
            }

            return True, f"Merged {moved_count} items to target tag", stats

        except Exception as e:
            logger.error(f"Error merging tags: {e}")
            return False, f"Error merging tags: {str(e)}", None

    def cleanup_unused_tags(self, days_threshold=180):
        """
        Clean up unused tags.

        Args:
            days_threshold: Days of inactivity

        Returns:
            Number of deleted tags
        """
        unused_tags = self.annotate_with(
            annotations={
                'last_used': models.Max('tagged_persons__created_at'),
                'usage_count': models.Count('tagged_persons'),
            }
        ).filter(
            usage_count=0,
            created_at__lt=timezone.now() - timezone.timedelta(days=days_threshold)
        )

        count = unused_tags.count()
        unused_tags.delete()

        return count

    def get_tags_by_category(self, category_slug, include_stats=True):
        """
        Get all tags in a category.

        Args:
            category_slug: Category slug
            include_stats: Include usage statistics

        Returns:
            QuerySet of tags
        """
        qs = self.filter(category__slug=category_slug)

        if include_stats:
            qs = qs.annotate(
                usage_count=models.Count(
                    'tagged_persons',
                    filter=models.Q(tagged_persons__content_object__is_active=True)
                )
            )

        return qs.order_by('name')

    def bulk_create_tags(self, tag_data_list, category=None):
        """
        Bulk create tags.

        Args:
            tag_data_list: List of tag data dictionaries
            category: Optional category for all tags

        Returns:
            List of created tags
        """
        tags = []
        for tag_data in tag_data_list:
            if category and 'category' not in tag_data:
                tag_data['category'] = category

            tag = self.create(**tag_data)
            tags.append(tag)

        return tags


class TaggedPersonManager(models.Manager):
    """
    Manager for TaggedPerson through model.

    Canonical import: from django_fusion.core.managers import TaggedPersonManager
    """

    def get_tags_for_person(self, person, include_notes=False):
        """
        Get all tags for a person.

        Args:
            person: Person object
            include_notes: Include tag notes

        Returns:
            QuerySet of tags
        """
        qs = self.filter(content_object=person)

        if include_notes:
            qs = qs.select_related('tag').only('tag', 'notes')
        else:
            qs = qs.select_related('tag')

        return qs.order_by('tag__name')

    def add_tag_to_person(self, person, tag, notes=''):
        """
        Add a tag to a person.

        Args:
            person: Person object
            tag: Tag object
            notes: Optional notes

        Returns:
            TaggedPerson object
        """
        tagged_person, created = self.get_or_create(
            content_object=person,
            tag=tag,
            defaults={'notes': notes}
        )

        if not created and notes:
            tagged_person.notes = notes
            tagged_person.save()

        return tagged_person

    def remove_tag_from_person(self, person, tag):
        """
        Remove a tag from a person.

        Args:
            person: Person object
            tag: Tag object

        Returns:
            True if removed, False if not found
        """
        try:
            tagged_person = self.get(content_object=person, tag=tag)
            tagged_person.delete()
            return True
        except self.model.DoesNotExist:
            return False

    def bulk_tag_persons(self, persons, tags, notes=''):
        """
        Bulk tag multiple persons with multiple tags.

        Args:
            persons: List of Person objects
            tags: List of Tag objects
            notes: Optional notes

        Returns:
            Dictionary with results
        """
        results = {
            'added': 0,
            'skipped': 0,
            'errors': []
        }

        for person in persons:
            for tag in tags:
                try:
                    self.add_tag_to_person(person, tag, notes)
                    results['added'] += 1
                except Exception as e:
                    results['errors'].append({
                        'person': str(person),
                        'tag': str(tag),
                        'error': str(e)
                    })
                    results['skipped'] += 1

        return results

    def get_persons_by_tag(self, tag, active_only=True):
        """
        Get all persons with a specific tag.

        Args:
            tag: Tag object
            active_only: Only active persons

        Returns:
            QuerySet of persons
        """
        qs = self.filter(tag=tag).select_related('content_object')

        if active_only:
            qs = qs.filter(content_object__is_active=True)

        return qs.order_by('content_object__full_name')

    def get_tag_usage_stats(self, tag):
        """
        Get usage statistics for a tag.

        Args:
            tag: Tag object

        Returns:
            Dictionary with statistics
        """
        qs = self.filter(tag=tag)

        stats = qs.aggregate(
            total_usage=Count('id'),
            active_persons=Count('content_object', filter=Q(content_object__is_active=True), distinct=True),
            recent_usage=Max('created_at'),
        )

        return {
            'tag_id': tag.id,
            'tag_name': tag.name,
            'total_usage': stats['total_usage'] or 0,
            'active_persons': stats['active_persons'] or 0,
            'recent_usage': stats['recent_usage'],
            'usage_by_month': self._get_usage_by_month(tag),
        }

    def _get_usage_by_month(self, tag):
        """Get tag usage by month."""
        from django.db.models.functions import TruncMonth

        return list(
            self.filter(tag=tag)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('-month')[:12]
        )

    def cleanup_orphaned_tags(self):
        """
        Remove tag associations for deleted persons.

        Returns:
            Number of deleted associations
        """
        # Find tagged persons where the person no longer exists
        from django.contrib.contenttypes.models import ContentType

        person_type = ContentType.objects.get_for_model(self.model.content_object.field.related_model)

        # Get all person IDs that exist
        existing_person_ids = self.model.content_object.field.related_model.objects.values_list('id', flat=True)

        # Find associations with non-existent persons
        orphaned = self.filter(
            content_type=person_type
        ).exclude(
            object_id__in=existing_person_ids
        )

        count = orphaned.count()
        orphaned.delete()

        return count
