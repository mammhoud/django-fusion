"""Long-running process definitions owned by the Precis domain.

Background execution is intentionally implemented in
``plugins.workers``. Campaign onboarding and batch processing are Dramatiq
actors in ``plugins.workers.campaign_tasks``; this package remains the domain
namespace for synchronous workflow/business helpers and contains no worker
runtime.
"""
