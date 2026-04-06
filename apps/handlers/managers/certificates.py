import logging
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from django_grep.pipelines.managers import BaseManager, CachedManager, cached_method

logger = logging.getLogger(__name__)


class CertificateManager(BaseManager):
    """
    Enhanced manager for Certificate model.
    """
    
    def get_valid_certificates(self, content_object):
        """
        Get valid certificates for an object.
        
        Args:
            content_object: The object
        
        Returns:
            QuerySet of valid certificates
        """
        today = timezone.now().date()
        
        return self.filter(
            content_object=content_object,
            status='valid',
            issue_date__lte=today,
        ).filter(
            models.Q(expiry_date__isnull=True) |
            models.Q(expiry_date__gte=today)
        ).order_by('-issue_date')
    
    def get_expiring_soon(self, content_object, days=30):
        """
        Get certificates expiring soon.
        
        Args:
            content_object: The object
            days: Days threshold
        
        Returns:
            QuerySet of expiring certificates
        """
        today = timezone.now().date()
        expiry_threshold = today + timezone.timedelta(days=days)
        
        return self.filter(
            content_object=content_object,
            status='valid',
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=expiry_threshold
        ).order_by('expiry_date')
    
    def verify_certificate(self, certificate_id, verified_by, verification_status='verified'):
        """
        Verify a certificate.
        
        Args:
            certificate_id: Certificate ID
            verified_by: User verifying
            verification_status: Verification status
        
        Returns:
            Tuple of (success, message, certificate)
        """
        try:
            certificate = self.get(id=certificate_id)
            certificate.verify(verified_by, verification_status)
            return True, "Certificate verified successfully", certificate
        except self.model.DoesNotExist:
            return False, "Certificate not found", None
        except Exception as e:
            logger.error(f"Error verifying certificate: {e}")
            return False, f"Error: {str(e)}", None
    
    @cached_method(timeout=300)
    def get_certificate_stats(self, content_object):
        """
        Get certificate statistics.
        
        Args:
            content_object: The object
        
        Returns:
            Dictionary of statistics
        """
        certificates = self.filter(content_object=content_object)
        
        return {
            'total': certificates.count(),
            'valid': certificates.filter(status='valid').count(),
            'expired': certificates.filter(status='expired').count(),
            'pending': certificates.filter(status='pending').count(),
            'revoked': certificates.filter(status='revoked').count(),
            'verified': certificates.filter(is_verified=True).count(),
            'expiring_soon': self.get_expiring_soon(content_object, 30).count(),
            'by_issuer': dict(
                certificates.values_list('issuer')
                .annotate(count=models.Count('id'))
                .order_by('-count')[:10]
            ),
        }
    
    def get_certificates_by_issuer(self, issuer, valid_only=True):
        """
        Get certificates by issuer.
        
        Args:
            issuer: Issuer name
            valid_only: Only include valid certificates
        
        Returns:
            QuerySet of certificates
        """
        queryset = self.filter(issuer=issuer)
        
        if valid_only:
            today = timezone.now().date()
            queryset = queryset.filter(
                status='valid',
                issue_date__lte=today,
            ).filter(
                models.Q(expiry_date__isnull=True) |
                models.Q(expiry_date__gte=today)
            )
        
        return queryset.order_by('-issue_date')
    
    def bulk_verify_certificates(self, certificate_ids, verified_by, verification_status='verified'):
        """
        Bulk verify multiple certificates.
        
        Args:
            certificate_ids: List of certificate IDs
            verified_by: User verifying
            verification_status: Verification status
        
        Returns:
            Dictionary with results
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(certificate_ids),
        }
        
        for cert_id in certificate_ids:
            success, message, certificate = self.verify_certificate(
                cert_id, verified_by, verification_status
            )
            
            if success:
                results['successful'].append({
                    'id': cert_id,
                    'message': message,
                })
            else:
                results['failed'].append({
                    'id': cert_id,
                    'error': message,
                })
        
        return results

