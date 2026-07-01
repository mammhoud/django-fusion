"""Workflow definitions for long-running async processes.

Sub-packages
------------
workflows.temporal  Temporal.io workflow and activity definitions for:
                    - Email campaign execution
                    - Certificate generation pipeline
                    - Bulk enrollment processing

Usage::

    from ceptor_ai.workflows.temporal.workflows import EmailCampaignWorkflow
    from ceptor_ai.workflows.temporal.activities import send_batch_activity
"""
