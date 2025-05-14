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

from directory import DirectoryTree
from directory import FileNode
from cache import LRUCache

def test_file_node_creation():
    # Test file node creation
    file_node = FileNode("test.txt", is_file=True)
    assert file_node.name == "test.txt"
    assert file_node.is_file == True
    assert len(file_node.children) == 0

    # Test directory node creation
    dir_node = FileNode("test_dir", is_file=False, parent=None)
    assert dir_node.name == "test_dir"
    assert dir_node.is_file == False
    assert len(dir_node.children) == 2  # Should have . and .. references

def test_directory_tree_basic_operations():
    tree = DirectoryTree()
    
    # Test adding files and directories
    tree.add_node("/dir1/file1.txt", is_file=True)
    tree.add_node("/dir1/dir2/file2.txt", is_file=True)
    
    # Test listing directory
    assert "file1.txt" in tree.list_directory("/dir1")
    assert "dir2" in tree.list_directory("/dir1")
    assert "file2.txt" in tree.list_directory("/dir1/dir2")
    
    # Test removing file
    assert tree.remove_file("/dir1/file1.txt") == True
    assert "file1.txt" not in tree.list_directory("/dir1")
    
    # Test removing directory
    assert tree.remove_directory("/dir1/dir2") == True
    assert "dir2" not in tree.list_directory("/dir1")

def test_directory_tree_path_traversal():
    tree = DirectoryTree()
    tree.add_node("/dir1/dir2/dir3", is_file=False)
    tree.add_node("/dir1/dir2/file.txt", is_file=True)
    
    # Test relative path traversal
    assert tree._traverse_to_node(".") == tree.current_node
    assert tree._traverse_to_node("..") == tree.root
    
    # Test absolute path traversal
    node = tree._traverse_to_node("/dir1/dir2")
    assert node is not None
    assert node.name == "dir2"
    
    # Test invalid path
    assert tree._traverse_to_node("/nonexistent/path") is None

def test_lru_cache():
    cache = LRUCache(capacity=2)
    
    # Create test nodes
    file1 = FileNode("file1.txt", is_file=True)
    file2 = FileNode("file2.txt", is_file=True)
    file3 = FileNode("file3.txt", is_file=True)
    
    # Test cache operations
    cache.put("/file1", file1)
    cache.put("/file2", file2)
    
    # Test cache hit
    assert cache.get("/file1") == file1
    
    # Test cache miss
    assert cache.get("/nonexistent") is None
    
    # Test LRU eviction
    cache.put("/file3", file3)  # Should evict file1 as it's least recently used
    assert cache.get("/file1") is None
    assert cache.get("/file2") == file2
    assert cache.get("/file3") == file3

def test_directory_with_cache():
    tree = DirectoryTree()
    cache = LRUCache(capacity=3)
    
    # Add some files
    tree.add_node("/dir1/file1.txt", is_file=True)
    tree.add_node("/dir1/file2.txt", is_file=True)
    
    # Cache the directory nodes
    dir1_node = tree._traverse_to_node("/dir1")
    cache.put("/dir1", dir1_node)
    
    # Test cache hit
    cached_dir = cache.get("/dir1")
    assert cached_dir is not None
    assert cached_dir.name == "dir1"
    assert "file1.txt" in [child.name for child in cached_dir.children]
    
    # Test cache invalidation
    tree.remove_file("/dir1/file1.txt")
    cached_dir = cache.get("/dir1")
    assert "file1.txt" not in [child.name for child in cached_dir.children]


