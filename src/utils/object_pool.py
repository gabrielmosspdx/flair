"""Object pooling system for efficient resource management."""

from typing import TypeVar, Generic, List, Callable, Optional
from collections import deque


T = TypeVar('T')


class ObjectPool(Generic[T]):
    """Generic object pool for reusable game objects."""
    
    def __init__(
        self,
        factory: Callable[[], T],
        reset_func: Optional[Callable[[T], None]] = None,
        initial_size: int = 10,
        max_size: int = 100
    ):
        """Initialize object pool.
        
        Args:
            factory: Function to create new objects
            reset_func: Optional function to reset objects before reuse
            initial_size: Number of objects to pre-create
            max_size: Maximum pool size
        """
        self.factory = factory
        self.reset_func = reset_func
        self.max_size = max_size
        self.available: deque[T] = deque()
        self.in_use: List[T] = []
        
        # Pre-populate pool
        for _ in range(initial_size):
            obj = self.factory()
            self.available.append(obj)
    
    def acquire(self) -> T:
        """Get an object from the pool.
        
        Returns:
            An available object
        """
        if not self.available:
            # Create new object if pool is empty
            obj = self.factory()
        else:
            obj = self.available.popleft()
            
        self.in_use.append(obj)
        return obj
    
    def release(self, obj: T) -> None:
        """Return an object to the pool.
        
        Args:
            obj: Object to return
        """
        if obj in self.in_use:
            self.in_use.remove(obj)
            
            # Reset object if reset function provided
            if self.reset_func:
                self.reset_func(obj)
            
            # Only add back to pool if under max size
            if len(self.available) < self.max_size:
                self.available.append(obj)
    
    def release_all(self) -> None:
        """Release all objects back to the pool."""
        while self.in_use:
            self.release(self.in_use[0])
    
    def clear(self) -> None:
        """Clear the entire pool."""
        self.available.clear()
        self.in_use.clear()
    
    @property
    def size(self) -> int:
        """Get total pool size.
        
        Returns:
            Number of objects in pool
        """
        return len(self.available) + len(self.in_use)
    
    @property
    def available_count(self) -> int:
        """Get number of available objects.
        
        Returns:
            Number of available objects
        """
        return len(self.available)