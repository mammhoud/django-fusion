"""Django template tags for ceptor-ai.

Tag libraries
-------------
rseal_chat          ``{% chat_bubble %}`` inclusion tag (uses components/chat/bubble.html).
components/         Sub-package with additional tag libraries:
  breadcrumbs       ``{% breadcrumbs %}`` tag with Wagtail page ancestry support.
  gallary           ``{% media_gallery %}`` tag for rendering gallery blocks.

Usage (in settings TEMPLATES builtins or via {% load %})::

    {% load rseal_chat %}
    {% chat_bubble config=chat_config %}
"""
