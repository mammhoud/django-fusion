"""Newsletter subscription view (auth/accounts URL group)."""

from django.http import JsonResponse
from django.views import View


class NewsletterSubscribeView(View):
    """Newsletter subscription — creates a pending Subscriber and triggers confirmation email."""

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."}, status=400)

        from apps.domain.models.newsletter.subscriber import Subscriber

        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={
                "name": request.POST.get("name", "").strip(),
                "status": "pending",
                "source": "website_footer",
            },
        )

        if not created and subscriber.status == "confirmed":
            return JsonResponse({
                "status": "ok",
                "message": "You are already subscribed!",
            })

        # If previously unsubscribed, reactivate
        if not created and subscriber.status == "unsubscribed":
            subscriber.regenerate_tokens()
            subscriber.status = "pending"
            subscriber.save(update_fields=["status", "confirmation_token", "unsubscribe_token", "updated_at"])

        # Send confirmation email (best-effort)
        try:
            from apps.domain.services.communication.newsletter import send_confirmation_email
            send_confirmation_email(subscriber.id)
        except Exception:
            pass  # Non-blocking — subscription is still saved

        return JsonResponse({
            "status": "ok",
            "message": "Thank you! Please check your email to confirm your subscription.",
        })
