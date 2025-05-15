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
import random
from datetime import datetime
import io
from contextlib import redirect_stdout

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from directory import DirectoryTree, FileNode, FolderNode, Role
from cache import LRUCache

class TestFileNode(unittest.TestCase):
    def setUp(self):
        self.parent = FolderNode("parent")
        self.file = FileNode("test.txt", parent=self.parent)
        self.dir = FolderNode("test_dir", parent=self.parent)

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
        # Test can_pet/can_feed/can_groom logic
        self.file.required_role = Role.VISITOR
        self.assertTrue(self.file.can_pet(Role.VISITOR))
        self.assertTrue(self.file.can_feed(Role.STAFF))
        self.assertFalse(self.file.can_groom(Role.VISITOR))
        self.file.required_role = Role.STAFF
        self.assertFalse(self.file.can_feed(Role.VISITOR))
        self.assertTrue(self.file.can_feed(Role.ADMIN))

    def test_directory_references(self):
        self.assertEqual(self.dir.dot, self.dir)
        self.assertEqual(self.dir.dotdot, self.parent)

class TestDirectoryTree(unittest.TestCase):
    def setUp(self):
        # Use a unique name for each test to avoid pickle conflicts
        self.cafe_name = f"testcafe_{random.randint(0, int(1e9))}"
        self.tree = DirectoryTree(name=self.cafe_name, role=Role.ADMIN)
        self.tree.rescue("whiskers", Role.ADMIN)
        self.tree.rescue("mittens", Role.VISITOR)
        self.tree.mkcby("cubby1")
        self.tree.walk("cubby1")
        self.tree.rescue("shadow", Role.VOLUNTEER)
        self.tree.walk("/")

    def tearDown(self):
        # Clean up the pickle file after each test
        pkl_path = os.path.join("cafes", f"{self.cafe_name}.pkl")
        if os.path.exists(pkl_path):
            os.remove(pkl_path)

    def test_cat_command(self):
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
        self.tree.role = Role.VISITOR
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.cat("whiskers")
        self.assertIn("Permission denied", f.getvalue())

    def test_meow_command(self):
        # Test setting cat properties with write permission
        self.tree.meow("whiskers", "age", "3")
        whiskers = self.tree._find_node_in_current("whiskers")
        self.assertIsNotNone(whiskers)
        if whiskers is not None:
            self.assertEqual(whiskers.get_property("age"), "3")
        self.tree.role = Role.VISITOR
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.meow("whiskers", "age", "4")
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
        self.tree.role = Role.VISITOR
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.boop("whiskers")
        self.assertIn("Permission denied", f.getvalue())

    def test_rescue_command(self):
        self.tree.rescue("newcat", Role.ADMIN)
        self.assertIsNotNone(self.tree._find_node_in_current("newcat"))
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.rescue("newcat", Role.ADMIN)
        self.assertIn("already exists", f.getvalue())

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
        if copy is not None:
            self.assertEqual(copy.get_property("age"), "2")
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
        self.tree.walk("cubby1")
        self.assertEqual(self.tree.current_node.name, "cubby1")
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.walk("nonexistent")
        self.assertIn("not found", f.getvalue())

    def test_adopted_command(self):
        self.tree.adopted("whiskers")
        self.assertIsNone(self.tree._find_node_in_current("whiskers"))
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.adopted("nonexistent")
        self.assertIn("not found", f.getvalue())

    def test_carry_commands(self):
        random.seed(42)
        success_detected = False
        failure_detected = False
        # Loop until both success and failure have been detected
        while not (success_detected and failure_detected):
            f = io.StringIO()
            with redirect_stdout(f):
                self.tree.carry("whiskers")
            output = f.getvalue()
            if "Successfully carrying whiskers" in output:
                success_detected = True
                # Test putting down cat only after a success
                f2 = io.StringIO()
                with redirect_stdout(f2):
                    self.tree.carrying()
                self.assertIn("whiskers", f2.getvalue())
                self.tree.put("whiskers")
                self.assertIsNotNone(self.tree._find_node_in_current("whiskers"))
            if "Failed to carry whiskers" in output:
                failure_detected = True
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

    def test_find_command(self):
        # Test finding a cat in the current cubby
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.find("whiskers")
        output = f.getvalue()
        self.assertIn("Found whiskers", output)
        # Test finding a cat in a different cubby
        self.tree.walk("cubby1")
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.find("shadow")
        output = f.getvalue()
        self.assertIn("Found shadow", output)
        # Test not finding a cat
        f = io.StringIO()
        with redirect_stdout(f):
            self.tree.find("notacat")
        output = f.getvalue()
        self.assertIn("notacat not found", output)

class TestLRUCache(unittest.TestCase):
    def setUp(self):
        self.cache = LRUCache(capacity=2)
        self.file1 = FileNode("file1.txt")
        self.file2 = FileNode("file2.txt")
        self.file3 = FileNode("file3.txt")

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

