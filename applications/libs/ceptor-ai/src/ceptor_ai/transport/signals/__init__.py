"""Django signal bindings for the transport layer.

Modules
-------
binding         Connects signal senders to their receivers at app-ready time.
handlers        Core signal handler functions (pure functions, no side effects).
invitations     Invitation-accepted and invitation-expired signal receivers.
notification    User-event notification signal receivers.

Note: ``binding`` imports ``django_structlog`` which is an optional dependency.
Import it only when the app is fully initialised::

    from ceptor_ai.transport.signals.binding import connect_signals
"""
