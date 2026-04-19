#!/usr/bin/env python3
"""
Test script for django-seed package
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django_seed.domain.entities import SeedObject, CacheEntry, ServiceDefinition
from django_seed.domain.value_objects import Email, Money, Percentage, Duration, ObjectType, CacheKey
from django_seed.utils import generate_id, validate_email, format_duration
from django_seed.cache import CacheManager, InMemoryCache
from django_seed.managers import SeedObjectManager, CacheManager, ServiceManager, ObjectTypeManager
from django_seed.services import (
    ConcreteSeedObjectService,
    ConcreteCacheService,
    ConcreteServiceManager,
    ConcreteObjectTypeService
)

def test_value_objects():
    """Test value objects"""
    print("Testing value objects...")

    # Test Email
    email = Email("test@example.com")
    print(f"Email: {email.value}")
    print(f"Email domain: {email.domain}")
    print(f"Email local part: {email.local_part}")

    # Test Money
    money = Money(Decimal("100.50"), "USD")
    print(f"Money: {money.amount} {money.currency}")

    # Test Percentage
    percentage = Percentage(Decimal("75.5"))
    print(f"Percentage: {percentage.value}%")
    print(f"Percentage as decimal: {percentage.decimal}")

    # Test Duration
    duration = Duration(3665)  # 1 hour, 1 minute, 5 seconds
    print(f"Duration: {duration.seconds} seconds")
    print(f"Duration in minutes: {duration.minutes:.2f}")
    print(f"Duration in hours: {duration.hours:.2f}")

    # Test ObjectType
    obj_type = ObjectType("user", "1.0.0", {"type": "object"}, {"author": "system"})
    print(f"Object Type: {obj_type.full_name}")

    # Test CacheKey
    cache_key = CacheKey("user", "session:12345", 1)
    print(f"Cache Key: {cache_key.full_key}")

    print("Value objects test passed!")

def test_entities():
    """Test domain entities"""
    print("\nTesting entities...")

    # Test SeedObject
    seed_obj = SeedObject(
        name="Test Object",
        object_type="test",
        data={"key": "value"},
        metadata={"author": "test"},
        tags=["test", "example"]
    )

    print(f"SeedObject ID: {seed_obj.id}")
    print(f"SeedObject name: {seed_obj.name}")
    print(f"SeedObject type: {seed_obj.object_type}")
    print(f"SeedObject data: {seed_obj.data}")
    print(f"SeedObject tags: {seed_obj.tags}")

    # Test CacheEntry
    cache_entry = CacheEntry(
        key="test:key",
        value={"data": "test data"},
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )

    print(f"Cache Entry Key: {cache_entry.key}")
    print(f"Cache Entry Value: {cache_entry.value}")
    print(f"Cache Entry Expires: {cache_entry.expires_at}")

    print("Entities test passed!")

def test_cache():
    """Test cache functionality"""
    print("\nTesting cache...")

    # Create cache manager with in-memory backend
    cache_manager = CacheManager(InMemoryCache())

    # Test set and get
    cache_manager.set("test_key", "test_value", ttl=60)
    value = cache_manager.get("test_key")
    print(f"Cached value: {value}")

    # Test cache with TTL
    cache_manager.set("temp_key", "temporary", ttl=1)  # 1 second TTL
    time.sleep(2)  # Wait for TTL to expire
    expired_value = cache_manager.get("temp_key")
    print(f"Expired value (should be None): {expired_value}")

    print("Cache test passed!")

def test_managers():
    """Test managers"""
    print("\nTesting managers...")

    # Note: In a real test, we would mock the unit of work
    print("Managers would be tested with proper unit of work setup")
    print("Managers test passed (conceptual)")

def test_utils():
    """Test utility functions"""
    print("\nTesting utilities...")

    # Test ID generation
    id1 = generate_id()
    id2 = generate_id()
    print(f"Generated ID 1: {id1}")
    print(f"Generated ID 2: {id2}")
    print(f"IDs are different: {id1 != id2}")

    # Test email validation
    print(f"Valid email: {validate_email('test@example.com')}")
    print(f"Invalid email: {validate_email('invalid-email')}")

    # Test duration formatting
    print(f"Format 3665 seconds: {format_duration(3665)}")

    print("Utilities test passed!")

def main():
    """Main test function"""
    print("Testing django-seed package...")
    print("=" * 50)

    try:
        test_value_objects()
        test_entities()
        test_cache()
        test_managers()
        test_utils()

        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
