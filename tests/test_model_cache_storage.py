"""Regression tests for model-scoped cache invalidation."""

from concurrent.futures import ThreadPoolExecutor

from django.core.cache import cache
from django_fusion.models.cache_storage import CachingStorage


def _reset() -> None:
    cache.clear()


def test_clear_model_cache_removes_only_registered_model_entries():
    """Invalidating one model leaves unrelated model entries untouched."""
    _reset()
    CachingStorage.cache_set("course", "one", {"title": "One"})
    CachingStorage.cache_set("course", "two", {"title": "Two"})
    CachingStorage.cache_set("article", "one", {"title": "Article"})

    assert CachingStorage.cache_get("course", "one") == {"title": "One"}
    assert CachingStorage.clear_model_cache("course") == 2
    assert CachingStorage.cache_get("course", "one") is None
    assert CachingStorage.cache_get("course", "two") is None
    assert CachingStorage.cache_get("article", "one") == {"title": "Article"}

    _reset()


def test_cache_delete_unregisters_the_entry():
    """Deleting one entry does not make model-wide clearing count it again."""
    _reset()
    CachingStorage.cache_set("course", "one", {"title": "One"})
    CachingStorage.cache_set("course", "two", {"title": "Two"})

    assert CachingStorage.cache_delete("course", "one") is True
    assert CachingStorage.clear_model_cache("course") == 1
    assert CachingStorage.cache_get("course", "two") is None

    _reset()


def test_clear_model_cache_skips_expired_entries():
    """Expired data entries are skipped (not counted) during model clearing."""
    _reset()
    CachingStorage.cache_set("course", "one", {"title": "One"})
    CachingStorage.cache_set("course", "two", {"title": "Two"})

    # Simulate the data entry for "one" expiring before the registry does.
    expired_key = CachingStorage._generate_cache_key("course", "one")
    cache.delete(expired_key)

    assert CachingStorage.clear_model_cache("course") == 1
    assert CachingStorage.cache_get("course", "two") is None

    _reset()


def test_registry_prunes_expired_keys_when_over_cap(monkeypatch):
    """Oversized registries drop entries whose data has already expired."""
    _reset()
    monkeypatch.setattr(CachingStorage, "MAX_REGISTRY_KEYS", 2)

    # Seed the registry with two keys whose data entries no longer exist.
    registry_key = CachingStorage._model_keys_key("course")
    expired = [
        CachingStorage._generate_cache_key("course", f"gone-{i}") for i in range(2)
    ]
    cache.set(registry_key, list(expired), CachingStorage.DEFAULT_TIMEOUT)

    # Registering a live key pushes the registry past the cap (2 expired + 1).
    CachingStorage.cache_set("course", "live", {"title": "Live"})
    live_key = CachingStorage._generate_cache_key("course", "live")

    keys = CachingStorage._registry_for("course")
    assert live_key in keys
    assert all(expired_key not in keys for expired_key in expired)
    assert len(keys) <= CachingStorage.MAX_REGISTRY_KEYS

    _reset()


def test_concurrent_registration_does_not_lose_keys():
    """Concurrent cache_set calls must not drop registrations (lock-guarded)."""
    _reset()
    # Keep the total well under LocMemCache's default max_entries (300) so
    # no eviction occurs and the delete count stays deterministic.
    workers = 4
    keys_per_worker = 10
    total = workers * keys_per_worker

    def register(worker: int) -> None:
        for i in range(keys_per_worker):
            CachingStorage.cache_set("course", f"w{worker}-{i}", {"n": i})

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(register, range(workers)))

    registry = CachingStorage._registry_for("course")
    assert len(registry) == total
    assert len(set(registry)) == total

    # Model-wide invalidation removes every concurrently registered entry.
    assert CachingStorage.clear_model_cache("course") == total
    assert CachingStorage.cache_get("course", "w0-0") is None

    _reset()


def test_model_cache_mixin_invalidate_all_cache():
    """ModelCacheMixin.invalidate_all_cache clears only its own model scope."""
    from django_fusion.models.model_cache import ModelCacheMixin

    class FakeCourse(ModelCacheMixin):
        pass

    _reset()
    CachingStorage.cache_set("fakecourse", "one", {"title": "One"})
    CachingStorage.cache_set("fakecourse", "two", {"title": "Two"})
    CachingStorage.cache_set("othermodel", "one", {"title": "Other"})

    assert FakeCourse().invalidate_all_cache() == 2
    assert CachingStorage.cache_get("fakecourse", "one") is None
    assert CachingStorage.cache_get("fakecourse", "two") is None
    assert CachingStorage.cache_get("othermodel", "one") == {"title": "Other"}

    _reset()
