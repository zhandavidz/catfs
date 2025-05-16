# implement caching algorithm
from collections import OrderedDict
from typing import Optional, TypeVar, Generic

T = TypeVar('T')

class LRUCache(Generic[T]):
    """
    A Least Recently Used (LRU) cache implementation for storing generic objects.
    Uses OrderedDict to maintain the order of access and automatically evict least recently used items.
    """
    def __init__(self, capacity: int):
        """
            Args:
            capacity (int): Maximum number of items the cache can hold
        """
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, path: str) -> Optional[T]:
        """        
        Args:
            path (str): The path to look up in the cache
        Returns:
            Optional[T]: The cached object if found, None otherwise
        """
        if path not in self.cache:
            return None
        # Move the path to the end to mark it as recently used
        self.cache.move_to_end(path)
        return self.cache[path]

    def put(self, path: str, content: T) -> None:
        """        
        Args:
            path (str): The path to store in the cache
            content (T): The object to cache
        """
        if path in self.cache:
            # Update and mark as recently used
            self.cache.move_to_end(path)
        self.cache[path] = content
        # Remove least recently used item if over capacity
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Pop from the beginning (LRU)
