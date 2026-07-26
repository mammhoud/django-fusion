"""
Blog Analytics Models — Article read tracking and engagement metrics
"""
from django.db import models
from django.utils import timezone


class ArticleRead(models.Model):
    """
    Track individual article reads for analytics.
    
    Fields:
        post: FK to BlogPage
        session_key: Django session key (for anonymous users)
        ip_address: IP address of reader
        read_at: Timestamp of read
        read_duration_seconds: How long user spent reading (optional)
        scroll_depth: How far down the page user scrolled (0-100)
        is_unique: Whether this is a unique read (first in last hour)
    """
    post = models.ForeignKey(
        'blog.BlogPage',
        on_delete=models.CASCADE,
        related_name='article_reads',
    )
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    read_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_duration_seconds = models.IntegerField(null=True, blank=True)
    scroll_depth = models.IntegerField(default=0, help_text="Scroll depth percentage (0-100)")
    is_unique = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'blog'
        verbose_name = 'Article Read'
        verbose_name_plural = 'Article Reads'
        indexes = [
            models.Index(fields=['post', 'read_at']),
            models.Index(fields=['session_key', 'read_at']),
        ]
    
    def __str__(self):
        return f"{self.post.title} - {self.read_at.strftime('%Y-%m-%d %H:%M')}"


class ArticleEngagement(models.Model):
    """
    Aggregate engagement metrics for articles.
    
    Fields:
        post: FK to BlogPage (unique)
        reads: Total read count
        unique_readers: Count of unique session keys
        likes: Like count (optional)
        shares: Share count (optional)
        bookmarks: Bookmark count (optional)
        updated_at: Last update timestamp
    """
    post = models.OneToOneField(
        'blog.BlogPage',
        on_delete=models.CASCADE,
        related_name='engagement_metrics',
    )
    reads = models.IntegerField(default=0)
    unique_readers = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    bookmarks = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'blog'
        verbose_name = 'Article Engagement'
        verbose_name_plural = 'Article Engagements'
    
    def __str__(self):
        return f"{self.post.title} - {self.reads} reads"
    
    @property
    def engagement_score(self):
        """Calculate engagement score based on all metrics."""
        return (
            self.reads * 1 +
            self.unique_readers * 2 +
            self.likes * 5 +
            self.shares * 10 +
            self.bookmarks * 3
        )
