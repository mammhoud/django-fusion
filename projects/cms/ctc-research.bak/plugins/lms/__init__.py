"""LMS app for ctc-research.com."""

# Ensure models are imported after Django is initialized
# This prevents "Model class doesn't declare an explicit app_label" errors
# during module load before INSTALLED_APPS is populated.

def ready():
    """Import models when app is ready (after Django setup)."""
    # Models will be imported when first accessed
    pass

default_app_config = "plugins.lms.apps.LmsConfig"
