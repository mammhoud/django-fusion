"""POS Cloud Sidecar — smoke tests.

Verifies the Django ORM bootstrap and the model registry without
starting a network server (Robyn's server is exercised separately).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SIDECAR = Path(__file__).resolve().parent.parent
_BACKEND = _SIDECAR / "backend"
for _p in (str(_SIDECAR), str(_BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(scope="module")
def server_module():
    import server  # noqa: F401

    return server


def test_django_orm_bootstrapped(server_module):
    assert server_module._DJANGO_READY is True


def test_all_models_registered(server_module):
    names = {m.__name__ for m in server_module._ALL_MODELS}
    assert {
        "Organization", "Branch", "Lead", "Contact", "Deal",
        "BranchProduct", "BranchSale", "BranchInventory",
        "SyncConflict", "SyncQueueItem", "DeviceToken",
    } <= names


def test_health_payload_shape(server_module):
    assert server_module.about.__version__ == "0.1.0"
    assert server_module._DJANGO_READY


def test_fusion_routes_registered(server_module):
    """The fusion feature module must import and register cleanly."""
    from routes.fusion import register_fusion_routes  # noqa: F401

    assert callable(register_fusion_routes)
