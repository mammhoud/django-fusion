
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

from django.core.cache import cache
from django.db.models.aggregates import Avg, Count
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class CertificateService:
    """
    Service for certificate operations.
    """
    
    @staticmethod
    def issue_certificate(
        content_object,
        name: str,
        issuer: str,
        issue_date: datetime = None,
        expiry_date: datetime = None,
        **kwargs
    ) -> Tuple[bool, str, Any]:
        """
        Issue a new certificate.
        
        Args:
            content_object: Certificate recipient
            name: Certificate name
            issuer: Issuing organization
            issue_date: Issue date (defaults to today)
            expiry_date: Expiry date
            **kwargs: Additional certificate fields
        
        Returns:
            Tuple of (success, message, certificate)
        """
        from apps.core.models import Certificate
        
        try:
            # Set default issue date
            if not issue_date:
                issue_date = timezone.now().date()
            
            # Create certificate
            certificate = Certificate.objects.create(
                content_object=content_object,
                name=name,
                issuer=issuer,
                issue_date=issue_date,
                expiry_date=expiry_date,
                **kwargs
            )
            
            # Generate certificate ID if not provided
            if not certificate.certificate_id:
                certificate.certificate_id = f"CERT-{certificate.id.hex[:8].upper()}"
                certificate.save()
            
            return True, "Certificate issued successfully", certificate
            
        except Exception as e:
            logger.error(f"Error issuing certificate: {e}")
            return False, f"Error issuing certificate: {str(e)}", None
    
    @staticmethod
    def validate_certificate(
        certificate_id: str,
        issuer: str = None,
        recipient_name: str = None
    ) -> Tuple[bool, str, Any]:
        """
        Validate a certificate.
        
        Args:
            certificate_id: Certificate ID
            issuer: Expected issuer (optional)
            recipient_name: Expected recipient (optional)
        
        Returns:
            Tuple of (valid, message, certificate_data)
        """
        from apps.core.models import Certificate
        
        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)
            
            # Check if certificate is valid
            if certificate.status != 'valid':
                return False, "Certificate is not valid", None
            
            if certificate.is_expired:
                return False, "Certificate has expired", None
            
            if not certificate.is_verified:
                return False, "Certificate is not verified", None
            
            # Validate issuer if provided
            if issuer and certificate.issuer != issuer:
                return False, "Issuer does not match", None
            
            # Validate recipient if provided
            if recipient_name:
                recipient = certificate.content_object
                if hasattr(recipient, 'full_name'):
                    if recipient.full_name != recipient_name:
                        return False, "Recipient does not match", None
            
            # Return certificate data
            certificate_data = {
                'id': str(certificate.id),
                'certificate_id': certificate.certificate_id,
                'name': certificate.name,
                'issuer': certificate.issuer,
                'issue_date': certificate.issue_date,
                'expiry_date': certificate.expiry_date,
                'recipient': str(certificate.content_object),
                'status': certificate.status,
                'is_verified': certificate.is_verified,
                'verification_status': certificate.verification_status,
            }
            
            return True, "Certificate is valid", certificate_data
            
        except Certificate.DoesNotExist:
            return False, "Certificate not found", None
        except Exception as e:
            logger.error(f"Error validating certificate: {e}")
            return False, f"Error validating certificate: {str(e)}", None
    
    @staticmethod
    def get_certificate_profile(user) -> Dict[str, Any]:
        """
        Get certificate dashboard data.
        
        Args:
            user: The user
        
        Returns:
            Dictionary with dashboard data
        """
        from apps.core.models import Certificate
        
        cache_key = f"cert_dashboard_{user.id}"
        dashboard_data = cache.get(cache_key)
        
        if dashboard_data is None:
            # Get user's certificates
            certificates = Certificate.objects.filter(content_object=user)
            
            # Calculate metrics
            valid_certs = certificates.filter(status='valid')
            expiring_soon = Certificate.objects.get_expiring_soon(user, 30)
            
            # Get certificates by status
            by_status = {}
            for status in ['valid', 'expired', 'pending', 'revoked']:
                by_status[status] = certificates.filter(status=status).count()
            
            # Get certificates by issuer
            by_issuer = list(
                certificates.values('issuer')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
            
            # Get expiring certificates
            expiring_list = list(
                expiring_soon.values(
                    'name', 'issuer', 'expiry_date'
                ).order_by('expiry_date')[:10]
            )
            
            dashboard_data = {
                'summary': {
                    'total': certificates.count(),
                    'valid': valid_certs.count(),
                    'expiring_soon': expiring_soon.count(),
                    'expired': certificates.filter(status='expired').count(),
                },
                'breakdown': {
                    'by_status': by_status,
                    'by_issuer': by_issuer,
                },
                'expiring_certificates': expiring_list,
                'recent_certificates': list(
                    certificates.order_by('-issue_date')[:5].values()
                ),
            }
            
            cache.set(cache_key, dashboard_data, 300)  # 5 minutes
        
        return dashboard_data
    
    @staticmethod
    def generate_certificate_report(
        content_object,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Generate a certificate report.
        
        Args:
            content_object: Certificate owner
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            Dictionary with report data
        """
        from apps.core.models import Certificate
        
        # Set default dates
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=365)  # Last year
        
        # Get certificates in date range
        certificates = Certificate.objects.filter(
            content_object=content_object,
            issue_date__range=[start_date, end_date]
        )
        
        # Calculate statistics
        total_certificates = certificates.count()
        valid_certificates = certificates.filter(status='valid').count()
        expired_certificates = certificates.filter(status='expired').count()
        
        # Monthly breakdown
        from django.db.models.functions import TruncMonth
        
        monthly_data = list(
            certificates.annotate(month=TruncMonth('issue_date'))
            .values('month')
            .annotate(
                count=Count('id'),
                valid=Count('id', filter=Q(status='valid')),
                expired=Count('id', filter=Q(status='expired'))
            )
            .order_by('month')
        )
        
        # Issuer statistics
        issuer_stats = list(
            certificates.values('issuer')
            .annotate(
                count=Count('id'),
                avg_duration=Avg(
                    F('expiry_date') - F('issue_date')
                )
            )
            .order_by('-count')[:10]
        )
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'summary': {
                'total_certificates': total_certificates,
                'valid_certificates': valid_certificates,
                'expired_certificates': expired_certificates,
                'valid_percentage': round(
                    (valid_certificates / total_certificates * 100) if total_certificates > 0 else 0,
                    2
                ),
            },
            'monthly_breakdown': monthly_data,
            'issuer_statistics': issuer_stats,
            'certificate_list': list(
                certificates.order_by('-issue_date').values(
                    'name', 'issuer', 'issue_date', 'expiry_date', 'status'
                )[:50]
            ),
        }

