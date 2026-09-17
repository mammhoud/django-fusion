"""Wagtail admin views for the content app — the newsletter broadcast page.

Registered in ``urls.py`` as ``/admin/newsletter/broadcast/`` (before the
wagtail admin include) and linked from the NewsletterSubscriber snippet index
header button. Only staff users can open it; it batch-emails subscribers
through the branded broadcast shell.
"""

from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView

from apps.content.models.newsletter import NewsletterSubscriber


class BroadcastEmailForm(forms.Form):
    """Compose a newsletter broadcast: subject + plain-text message."""

    subject = forms.CharField(
        label=_("Subject"),
        max_length=150,
        widget=forms.TextInput(attrs={"class": "input"}),
    )
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={"class": "input", "rows": 12}),
        help_text=_("Plain text — it is rendered as paragraphs in the branded "
                    "HTML shell and used verbatim for the plain-text part."),
    )
    include_inactive = forms.BooleanField(
        label=_("Include paused subscribers"),
        required=False,
        help_text=_("By default only active subscribers are emailed."),
    )


class BroadcastEmailView(FormView):
    """Staff-only page that emails every (active) subscriber."""

    form_class = BroadcastEmailForm
    template_name = "newsletter/broadcast_email.html"

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return HttpResponseRedirect(reverse("wagtailadmin_login"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_count"] = NewsletterSubscriber.objects.filter(is_active=True).count()
        context["total_count"] = NewsletterSubscriber.objects.count()
        return context

    def form_valid(self, form):
        from apps.content.services.newsletter import send_newsletter_broadcast

        sent = send_newsletter_broadcast(
            subject=form.cleaned_data["subject"],
            message=form.cleaned_data["message"],
            include_inactive=form.cleaned_data["include_inactive"],
        )
        messages.success(
            self.request,
            _("Broadcast sent — %(count)d subscriber(s) emailed.") % {"count": sent},
        )
        return HttpResponseRedirect(reverse("wagtailadmin_newsletter_broadcast"))
