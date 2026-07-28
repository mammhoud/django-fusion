"""Course enrollment views."""

import csv
import logging
from io import StringIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.pages.lms.forms import (
    CourseEnrollmentBulkForm,
    CourseEnrollmentForm,
    EnrollmentLeadFilterForm,
)
from apps.pages.lms.models import Course, CourseEnrollmentLead

logger = logging.getLogger(__name__)


class EnrollmentCreateAjaxView(CreateView):
    """AJAX endpoint for creating enrollment leads."""

    model = CourseEnrollmentLead
    form_class = CourseEnrollmentForm
    template_name = 'learning/_enrollment_form.html'

    def get_context_data(self, **kwargs):
        """Add course to context."""
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return context

    def form_valid(self, form):
        """Handle form submission."""
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        
        # Set course on the form instance
        form.instance.course = course
        
        # Save the enrollment lead
        response = super().form_valid(form)
        
        # Send confirmation email
        self._send_confirmation_email(form.instance)
        
        # Log enrollment
        logger.info(
            f"Enrollment lead created: {form.instance.email} for {course.title}",
            extra={'course_id': course.id, 'email': form.instance.email}
        )
        
        return response

    def form_invalid(self, form):
        """Return form errors for HTMX."""
        return render(
            self.request,
            self.template_name,
            {'form': form, 'course': get_object_or_404(Course, id=self.kwargs.get('course_id'))},
            status=400
        )

    def get_success_url(self):
        """Return success message URL."""
        return reverse('course-enrollment-success')

    @staticmethod
    def _send_confirmation_email(enrollment_lead):
        """Send confirmation email to enrollment lead."""
        try:
            subject = _(f"Enrollment Confirmation - {enrollment_lead.course.title}")
            
            context = {
                'full_name': enrollment_lead.full_name,
                'course_title': enrollment_lead.course.title,
                'course_url': settings.SITE_URL + reverse('course-detail', args=[enrollment_lead.course.slug]),
            }
            
            html_message = render_to_string('email/enrollment_confirmation.html', context)
            text_message = render_to_string('email/enrollment_confirmation.txt', context)
            
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [enrollment_lead.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Confirmation email sent to {enrollment_lead.email}")
            
        except Exception as e:
            logger.error(f"Error sending confirmation email to {enrollment_lead.email}: {str(e)}")


@require_POST
def enrollment_create_modal(request, course_id):
    """Return enrollment form modal via HTMX."""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if user already enrolled
    if request.user.is_authenticated:
        existing = CourseEnrollmentLead.objects.filter(
            email=request.user.email,
            course=course,
            status__in=['confirmed', 'enrolled']
        ).exists()
        
        if existing:
            return HttpResponse(
                _("You are already enrolled in this course"),
                status=400
            )
    
    form = CourseEnrollmentForm()
    form.instance.course = course
    
    return render(request, 'learning/_enrollment_modal_form.html', {
        'form': form,
        'course': course,
    })


@login_required
def enrollment_list(request):
    """List enrollment leads for current user or admin."""
    if not request.user.is_staff:
        # Only allow users to see their own leads
        leads = CourseEnrollmentLead.objects.filter(email=request.user.email)
    else:
        # Admin sees all leads
        leads = CourseEnrollmentLead.objects.all()
    
    # Filter form
    form = EnrollmentLeadFilterForm(request.GET or None)
    
    if form.is_valid():
        if form.cleaned_data.get('search'):
            query = form.cleaned_data['search']
            leads = leads.filter(
                models.Q(full_name__icontains=query) |
                models.Q(email__icontains=query)
            )
        
        if form.cleaned_data.get('course'):
            leads = leads.filter(course_id=form.cleaned_data['course'])
        
        if form.cleaned_data.get('status'):
            leads = leads.filter(status=form.cleaned_data['status'])
        
        if form.cleaned_data.get('sort'):
            leads = leads.order_by(form.cleaned_data['sort'])
    
    return render(request, 'learning/enrollment_list.html', {
        'leads': leads,
        'form': form,
    })


@login_required
@require_http_methods(["POST"])
def enrollment_status_update(request, enrollment_id):
    """Update enrollment lead status."""
    enrollment = get_object_or_404(CourseEnrollmentLead, id=enrollment_id)
    
    # Only admin can update
    if not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied')}, status=403)
    
    status = request.POST.get('status')
    if status not in dict(CourseEnrollmentLead.Status.choices):
        return JsonResponse({'error': _('Invalid status')}, status=400)
    
    with transaction.atomic():
        enrollment.status = status
        
        if status == 'enrolled':
            from django.utils import timezone
            enrollment.enrolled_at = timezone.now()
        
        enrollment.save()
        
        # Send update email
        _send_status_update_email(enrollment)
    
    return JsonResponse({
        'success': True,
        'status': status,
        'message': _('Enrollment status updated')
    })


@login_required
def enrollment_export_csv(request):
    """Export enrollment leads as CSV."""
    if not request.user.is_staff:
        return HttpResponse(_('Permission denied'), status=403)
    
    # Get filter parameters
    form = EnrollmentLeadFilterForm(request.GET)
    leads = CourseEnrollmentLead.objects.all()
    
    if form.is_valid():
        if form.cleaned_data.get('course'):
            leads = leads.filter(course_id=form.cleaned_data['course'])
        
        if form.cleaned_data.get('status'):
            leads = leads.filter(status=form.cleaned_data['status'])
    
    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enrollment_leads.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Email', 'Phone', 'Course', 'Status', 'Created At', 'Notes'])
    
    for lead in leads:
        writer.writerow([
            lead.full_name,
            lead.email,
            lead.phone,
            lead.course.title,
            lead.get_status_display(),
            lead.created_at,
            lead.notes,
        ])
    
    logger.info(f"Exported {leads.count()} enrollment leads as CSV")
    
    return response


@login_required
def enrollment_import_csv(request):
    """Import enrollment leads from CSV."""
    if not request.user.is_staff:
        return HttpResponse(_('Permission denied'), status=403)
    
    if request.method == 'POST':
        form = CourseEnrollmentBulkForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = request.FILES['csv_file']
            imported = 0
            skipped = 0
            
            try:
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(StringIO(decoded_file))
                
                for row in reader:
                    try:
                        # Get course
                        course_id = row.get('course_id')
                        if not course_id:
                            skipped += 1
                            continue
                        
                        course = Course.objects.get(id=course_id)
                        
                        # Create or update enrollment lead
                        lead, created = CourseEnrollmentLead.objects.get_or_create(
                            email=row['email'],
                            course=course,
                            defaults={
                                'full_name': row.get('full_name', ''),
                                'phone': row.get('phone', ''),
                                'notes': row.get('notes', ''),
                            }
                        )
                        
                        if created:
                            imported += 1
                        else:
                            skipped += 1
                    
                    except Course.DoesNotExist:
                        skipped += 1
                    except KeyError:
                        skipped += 1
                
                logger.info(f"Imported {imported} enrollment leads, skipped {skipped}")
                
                return render(request, 'learning/enrollment_import_success.html', {
                    'imported': imported,
                    'skipped': skipped,
                })
            
            except Exception as e:
                logger.error(f"Error importing CSV: {str(e)}")
                form.add_error('csv_file', _('Error processing CSV file'))
    
    else:
        form = CourseEnrollmentBulkForm()
    
    return render(request, 'learning/enrollment_import.html', {
        'form': form,
    })


def _send_status_update_email(enrollment_lead):
    """Send status update email."""
    try:
        subject = _(f"Enrollment Status Update - {enrollment_lead.course.title}")
        
        context = {
            'full_name': enrollment_lead.full_name,
            'course_title': enrollment_lead.course.title,
            'status': enrollment_lead.get_status_display(),
        }
        
        html_message = render_to_string('email/enrollment_status_update.html', context)
        text_message = render_to_string('email/enrollment_status_update.txt', context)
        
        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [enrollment_lead.email],
            html_message=html_message,
            fail_silently=True,
        )
    
    except Exception as e:
        logger.error(f"Error sending status update email: {str(e)}")
