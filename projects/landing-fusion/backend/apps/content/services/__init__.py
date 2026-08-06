"""Newsletter delivery services for the landing backend.

Everything here is deliberately side-effect-safe: the subscribe API never
blocks on email or provider network calls, so a Mailchimp outage or a slow
SMTP relay can never break a signup response. Each function swallows its own
errors, logs them, and leaves the subscriber's delivery-state timestamps
(welcome_sent_at / provider_synced_at) unset so a later job can retry.
"""
