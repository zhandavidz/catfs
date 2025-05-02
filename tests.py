# // test create_file return code 1 for success
# // test remove_file return code 0 for failure
# calculate the time taken to run the test
# calculate the memory used to run the test
# eviction behavior test
# test for all the commands 
# test for LRU algorithm

import os
import unittest
import sys
import time
import logging

from cache import LRUCache

cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))  # Output: 1
cache.put(3, 3)       # Evicts key 2
print(cache.get(2))  # Output: -1 (not found)
