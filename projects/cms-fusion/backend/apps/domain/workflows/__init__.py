"""Workflow definitions for long-running async processes.

Sub-packages
------------
workflows.temporal  Temporal.io workflow and activity definitions for:
                    - Email campaign execution
                    - Certificate generation pipeline
                    - Bulk enrollment processing

Usage::

    from apps.domain.workflows.temporal.workflows import EmailCampaignWorkflow
    from apps.domain.workflows.temporal.activities import send_batch_activity
"""
