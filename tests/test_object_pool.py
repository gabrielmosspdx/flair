"""Tests for object pooling system."""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.object_pool import ObjectPool  # noqa: E402


class MockObject:
    """Simple test object for pooling."""

    def __init__(self):
        self.value = 0
        self.active = True

    def reset(self):
        """Reset object state."""
        self.value = 0
        self.active = True


class TestObjectPool(unittest.TestCase):
    """Test object pooling functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.pool = ObjectPool(
            factory=MockObject, reset_func=lambda obj: obj.reset(), initial_size=5, max_size=10
        )

    def test_initial_pool_size(self):
        """Test that pool is pre-populated."""
        self.assertEqual(self.pool.available_count, 5)
        self.assertEqual(self.pool.size, 5)

    def test_acquire_object(self):
        """Test acquiring objects from pool."""
        obj = self.pool.acquire()
        self.assertIsInstance(obj, MockObject)
        self.assertEqual(self.pool.available_count, 4)
        self.assertEqual(len(self.pool.in_use), 1)

    def test_release_object(self):
        """Test releasing objects back to pool."""
        obj = self.pool.acquire()
        obj.value = 42

        self.pool.release(obj)
        self.assertEqual(self.pool.available_count, 5)
        self.assertEqual(len(self.pool.in_use), 0)

        # Object should be reset
        next_obj = self.pool.acquire()
        self.assertEqual(next_obj.value, 0)

    def test_acquire_when_empty(self):
        """Test acquiring when pool is empty."""
        # Acquire all pre-created objects
        [self.pool.acquire() for _ in range(5)]
        self.assertEqual(self.pool.available_count, 0)

        # Should create new object
        new_obj = self.pool.acquire()
        self.assertIsInstance(new_obj, MockObject)
        self.assertEqual(len(self.pool.in_use), 6)

    def test_max_pool_size(self):
        """Test that pool respects max size."""
        # Acquire and release many objects
        objects = [self.pool.acquire() for _ in range(15)]
        for obj in objects:
            self.pool.release(obj)

        # Pool should not exceed max size
        self.assertLessEqual(self.pool.available_count, 10)

    def test_release_all(self):
        """Test releasing all objects."""
        [self.pool.acquire() for _ in range(3)]
        self.assertEqual(len(self.pool.in_use), 3)

        self.pool.release_all()
        self.assertEqual(len(self.pool.in_use), 0)
        self.assertEqual(self.pool.available_count, 5)

    def test_clear_pool(self):
        """Test clearing the pool."""
        self.pool.acquire()
        self.pool.clear()

        self.assertEqual(self.pool.size, 0)
        self.assertEqual(self.pool.available_count, 0)
        self.assertEqual(len(self.pool.in_use), 0)


if __name__ == "__main__":
    unittest.main()
