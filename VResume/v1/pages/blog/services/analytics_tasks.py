"""
Blog Analytics Celery Tasks — Update engagement metrics and trending articles
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def update_article_engagement_metrics(self, post_id=None):
    """
    Periodic task: Update article engagement metrics from ArticleRead records.
    
    If post_id is provided, update only that post.
    Otherwise, update all posts with recent reads.
    """
    from pages.blog.models import BlogPost, ArticleEngagement, ArticleRead
    
    try:
        if post_id:
            # Update specific post
            posts = BlogPost.objects.filter(id=post_id)
        else:
            # Update posts with reads in the last 24 hours
            recent_reads = ArticleRead.objects.filter(
                read_at__gte=timezone.now() - timedelta(hours=24)
            ).values_list("post_id", flat=True).distinct()
            posts = BlogPost.objects.filter(id__in=recent_reads)
        
        updated_count = 0
        for post in posts:
            # Get or create engagement record
            engagement, created = ArticleEngagement.objects.get_or_create(post=post)
            
            # Update from reads
            engagement.update_from_reads()
            updated_count += 1
            
            if created:
                logger.info(f"Created engagement record for post {post.id}: {post.title}")
            else:
                logger.info(f"Updated engagement record for post {post.id}: {post.title}")
        
        logger.info(f"update_article_engagement_metrics: updated {updated_count} posts")
        return {"updated": updated_count}
        
    except Exception as e:
        logger.error(f"update_article_engagement_metrics failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=3)
def generate_trending_articles(self, days=7, limit=10):
    """
    Periodic task: Generate list of trending articles based on engagement score.
    
    Scores articles by engagement metrics from the last N days.
    
    Args:
        days: Number of days to consider for trending (default: 7)
        limit: Number of trending articles to return (default: 10)
    """
    from pages.blog.models import BlogPost, ArticleRead, ArticleEngagement
    
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get posts with reads in the last N days
        trending_posts = BlogPost.objects.filter(
            reads__read_at__gte=cutoff_date
        ).annotate(
            recent_reads=Count("reads", filter=Q(reads__read_at__gte=cutoff_date))
        ).order_by("-recent_reads")[:limit]
        
        # Update engagement metrics for trending posts
        for post in trending_posts:
            engagement, _ = ArticleEngagement.objects.get_or_create(post=post)
            engagement.update_from_reads()
        
        # Get top trending by engagement score
        trending = ArticleEngagement.objects.filter(
            post__in=trending_posts
        ).order_by("-engagement_score")[:limit]
        
        trending_data = [
            {
                "post_id": t.post.id,
                "title": t.post.title,
                "slug": t.post.slug,
                "engagement_score": t.engagement_score,
                "unique_readers": t.unique_readers,
                "total_reads": t.total_reads,
            }
            for t in trending
        ]
        
        logger.info(f"generate_trending_articles: found {len(trending_data)} trending articles")
        return {"trending": trending_data}
        
    except Exception as e:
        logger.error(f"generate_trending_articles failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=3)
def cleanup_old_article_reads(self, days_old=90):
    """
    Periodic task: Archive or delete old article read records.
    
    Runs daily to clean up reads older than `days_old` days.
    
    Args:
        days_old: Number of days to consider a read "old" (default: 90)
    """
    from pages.blog.models import ArticleRead
    
    try:
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Find old reads
        old_reads = ArticleRead.objects.filter(read_at__lt=cutoff_date)
        count = old_reads.count()
        
        if count > 0:
            # Delete old reads (or archive if you have an archive table)
            old_reads.delete()
            logger.info(f"cleanup_old_article_reads: deleted {count} reads older than {days_old} days")
        else:
            logger.info(f"cleanup_old_article_reads: no reads to delete (older than {days_old} days)")
        
        return {"deleted": count}
        
    except Exception as e:
        logger.error(f"cleanup_old_article_reads failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
