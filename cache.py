# implement caching algorithm
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Move the key to the end to mark it as recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update and mark as recently used
            self.cache.move_to_end(key)
        self.cache[key] = value
        # Remove least recently used item if over capacity
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Pop from the beginning (LRU)
