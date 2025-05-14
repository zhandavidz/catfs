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
import pytest
import random
from datetime import datetime

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from directory import DirectoryTree
from directory import FileNode
from cache import LRUCache
import io
from contextlib import redirect_stdout


class TestFileNode(unittest.TestCase):
    def setUp(self):
        self.parent = FileNode("parent", is_file=False)
        self.file = FileNode("test.txt", is_file=True, parent=self.parent)
        self.dir = FileNode("test_dir", is_file=False, parent=self.parent)

    def test_file_node_creation(self):
        self.assertEqual(self.file.name, "test.txt")
        self.assertTrue(self.file.is_file)
        self.assertEqual(self.dir.name, "test_dir")
        self.assertFalse(self.dir.is_file)

    def test_file_properties(self):
        self.file.set_property("age", "2")
        self.file.set_property("mood", "happy")
        self.assertEqual(self.file.get_property("age"), "2")
        self.assertEqual(self.file.get_property("mood"), "happy")
        self.assertFalse(self.file.set_property("invalid", "value"))

    def test_permissions(self):
        self.file.set_permissions("-r")
        self.assertTrue(self.file.permissions['pet'])
        self.assertFalse(self.file.permissions['feed'])
        self.assertFalse(self.file.permissions['groom'])

        self.file.set_permissions("-rw")
        self.assertTrue(self.file.permissions['pet'])
        self.assertTrue(self.file.permissions['feed'])
        self.assertFalse(self.file.permissions['groom'])

        self.file.set_permissions("-rwx")
        self.assertTrue(self.file.permissions['pet'])
        self.assertTrue(self.file.permissions['feed'])
        self.assertTrue(self.file.permissions['groom'])

    def test_directory_references(self):
        self.assertEqual(self.dir.dot, self.dir)
        self.assertEqual(self.dir.dotdot, self.parent)


class TestDirectoryTree(unittest.TestCase):
    def setUp(self):
        self.tree = DirectoryTree()
        # Set up some test data with proper permissions
        self.tree.rescue("whiskers", "-rwx")
        self.tree.rescue("mittens", "-r")
        self.tree.mkcby("cubby1")
        self.tree.walk("cubby1")
        self.tree.rescue("shadow", "-rw")
        self.tree.walk("root")
        
        # Set user permissions
        self.tree.root.set_permissions("-rwx")  # Give user full permissions

    def test_cat_command(self):
        # Test viewing cat with read permission
        self.tree.meow("whiskers", "age", "2")
        self.tree.meow("whiskers", "mood", "happy")
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.cat("whiskers")
        output = f.getvalue()
        self.assertIn("Cat: whiskers", output)
        self.assertIn("age: 2", output)
        self.assertIn("mood: happy", output)

        # Test viewing cat without read permission
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.cat("mittens")
        self.assertIn("Permission denied", f.getvalue())

    def test_meow_command(self):
        # Test setting cat properties with write permission
        self.tree.meow("whiskers", "age", "3")
        self.assertEqual(self.tree._find_node_in_current("whiskers").get_property("age"), "3")
        
        # Test setting properties without write permission
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.meow("mittens", "age", "3")
        self.assertIn("Permission denied", f.getvalue())

        # Test invalid property
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.meow("whiskers", "invalid", "value")
        self.assertIn("Invalid property", f.getvalue())

    def test_boop_command(self):

        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.boop("whiskers")
        output = f.getvalue()
        self.assertIn("purrs contentedly", output)

        # Test executing cat without execute permission
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.boop("mittens")
        self.assertIn("Permission denied", f.getvalue())

    def test_rescue_command(self):
        # Test creating new cat with valid permissions
        self.tree.rescue("newcat", "-rwx")
        self.assertIsNotNone(self.tree._find_node_in_current("newcat"))
        
        # Test creating duplicate cat
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.rescue("newcat", "-rwx")
        self.assertIn("already exists", f.getvalue())

        # Test creating cat with invalid permissions
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.rescue("invalidcat", "invalid")
        self.assertIn("Invalid permissions", f.getvalue())

    def test_pawprint_command(self):
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.pawprint()
        self.assertIn("/cubby1", f.getvalue())

    def test_copycat_command(self):
        # Test copying cat with proper permissions
        self.tree.meow("whiskers", "age", "2")
        self.tree.copycat("whiskers", "whiskers_copy")
        copy = self.tree._find_node_in_current("whiskers_copy")
        self.assertIsNotNone(copy)
        self.assertEqual(copy.get_property("age"), "2")

        # Test copying non-existent cat
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.copycat("nonexistent", "copy")
        self.assertIn("not found", f.getvalue())

    def test_recollar_command(self):
        # Test renaming cat
        self.tree.recollar("whiskers", "whiskers_new")
        self.assertIsNotNone(self.tree._find_node_in_current("whiskers_new"))
        self.assertIsNone(self.tree._find_node_in_current("whiskers"))

        # Test renaming non-existent cat
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.recollar("nonexistent", "new_name")
        self.assertIn("not found", f.getvalue())

    def test_walk_command(self):
        # Test changing directory
        self.tree.walk("..")
        self.assertEqual(self.tree.current_node.name, "root")
        
        # Test invalid directory
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.walk("nonexistent")
        self.assertIn("not found", f.getvalue())

    def test_adopted_command(self):
        # Test removing cat
        self.tree.adopted("whiskers")
        self.assertIsNone(self.tree._find_node_in_current("whiskers"))

        # Test removing non-existent cat
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.adopted("nonexistent")
        self.assertIn("not found", f.getvalue())

    def test_carry_commands(self):
        # Test carrying cats
        random.seed(42)  # For deterministic testing
        self.tree.carry("whiskers")
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.carrying()
        self.assertIn("whiskers", f.getvalue())
        
        # Test putting down cat
        self.tree.put("whiskers")
        self.assertIsNotNone(self.tree._find_node_in_current("whiskers"))

        # Test carrying non-existent cat
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.carry("nonexistent")
        self.assertIn("not found", f.getvalue())

    def test_mkcby_command(self):
        # Test creating directory
        self.tree.mkcby("new_cubby")
        self.assertIsNotNone(self.tree._find_node_in_current("new_cubby"))
        
        # Test creating duplicate directory
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.mkcby("new_cubby")
        self.assertIn("already exists", f.getvalue())

    def test_prowl_command(self):
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.prowl()
        output = f.getvalue()
        self.assertIn("shadow", output)
        self.assertIn("cubby", output)

class TestLRUCache(unittest.TestCase):
    def setUp(self):
        self.cache = LRUCache(capacity=2)
        self.file1 = FileNode("file1.txt", is_file=True)
        self.file2 = FileNode("file2.txt", is_file=True)
        self.file3 = FileNode("file3.txt", is_file=True)

    def test_cache_operations(self):
        # Test basic put and get
        self.cache.put("/file1", self.file1)
        self.assertEqual(self.cache.get("/file1"), self.file1)
        
        # Test cache miss
        self.assertIsNone(self.cache.get("/nonexistent"))
        
        # Test capacity limit
        self.cache.put("/file2", self.file2)
        self.cache.put("/file3", self.file3)
        self.assertIsNone(self.cache.get("/file1"))  # Should be evicted
        self.assertIsNotNone(self.cache.get("/file2"))
        self.assertIsNotNone(self.cache.get("/file3"))

    def test_lru_eviction(self):
        # Test LRU eviction policy
        self.cache.put("/file1", self.file1)
        self.cache.put("/file2", self.file2)
        self.cache.get("/file1")  # Access file1 to make it more recently used
        self.cache.put("/file3", self.file3)
        self.assertIsNotNone(self.cache.get("/file1"))  # Should still be in cache
        self.assertIsNone(self.cache.get("/file2"))  # Should be evicted

def run_tests():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Record start time and memory
    start_time = time.time()
    start_memory = sys.getsizeof([])  # Simple way to get current memory usage
    
    # Run tests
    unittest.main(exit=False)
    
    # Calculate and log metrics
    end_time = time.time()
    end_memory = sys.getsizeof([])
    
    logger.info(f"Tests completed in {end_time - start_time:.2f} seconds")
    logger.info(f"Memory usage: {end_memory - start_memory} bytes")

if __name__ == '__main__':
    run_tests()

