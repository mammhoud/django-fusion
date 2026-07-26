from django import template

from ..models import Enrollment

register = template.Library()

@register.filter
def is_enrolled(course, user):
    if not user or user.is_anonymous:
        return False
    return Enrollment.objects.filter(student=user, course=course).exists()
