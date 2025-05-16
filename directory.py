import os
import pickle
from cache import LRUCache
from enum import Enum

# Role enum and global permissions
class Role(Enum):
    VISITOR = 0
    VOLUNTEER = 1
    STAFF = 2
    ADMIN = 3

global_perms = {
    Role.VISITOR:  {"pet": True,  "feed": False, "groom": False},
    Role.VOLUNTEER: {"pet": True,  "feed": True,  "groom": False},
    Role.STAFF:     {"pet": True,  "feed": True,  "groom": True},
    Role.ADMIN:     {"pet": True,  "feed": True,  "groom": True},
}

class BaseNode:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

class FileNode(BaseNode):
    def __init__(self, name: str, required_role: Role = Role.STAFF, parent=None):
        super().__init__(name, parent)
        self.is_file = True
        self.content = {
            'age': None,
            'mood': None,
            'date_found': None,
            'date_fed': None
        }
        self.required_role = required_role
    def set_property(self, property_name, value):
        if property_name in self.content:
            print(f"Setting {property_name} to {value}")
            self.content[property_name] = value
            return True
        return False
    def get_property(self, property_name):
        return self.content.get(property_name)
    def can_pet(self, user_role: Role):
        if user_role.value >= self.required_role.value:
            return True
        return global_perms[user_role]["pet"]
    def can_feed(self, user_role: Role):
        if user_role.value >= self.required_role.value:
            return True
        return global_perms[user_role]["feed"]
    def can_groom(self, user_role: Role):
        if user_role.value >= self.required_role.value:
            return True
        return global_perms[user_role]["groom"]

class FolderNode(BaseNode):
    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.is_file = False
        self.children = []
        self.dot = self
        self.dotdot = parent
    def add_child(self, child):
        self.children.append(child)
    def remove_child(self, child):
        self.children.remove(child)
    def get_child(self, name):
        if name == ".":
            return self.dot
        elif name == "..":
            return self.dotdot
        for child in self.children:
            if child.name == name:
                return child
        return None

class DirectoryTree:
    def __init__(self, name: str, cache_size: int=0, role: Role = Role.VISITOR):
        self.cache_hits = 0
        self.cache_accesses = 0
        if cache_size > 0:
            self.cache = LRUCache(cache_size)
        else:
            self.cache = None
        self.name = name
        self.role = role
        self.carried_cats = []
        self._pkl_path = os.path.join("cafes", f"{name}.pkl")
        if not os.path.exists("cafes"):
            os.makedirs("cafes")
        if os.path.exists(self._pkl_path):
            raise RuntimeError(f"CatFS {name} already exists, cannot create another CatFS named the same thing")
        self.root = FolderNode("root")
        self.current_node = self.root
        self._save_to_pkl()

    def _save_to_pkl(self):
        with open(self._pkl_path, "wb") as f:
            pickle.dump(self, f)

    def _traverse_to_node(self, path: str):
        if path[0] == "/":
            current = self.root
        else:
            current = self.current_node
        parts = path.strip("/").split("/")
        # current = self.current_node if path.startswith(".") else self.root
        for part in parts:
            if not part:
                continue
            if current.is_file:
                return None
            child = current.get_child(part)
            if child is None:
                return None
            current = child
        return current
    
    def _find_node_in_current(self, name):
        for child in self.current_node.children:
            if child.name == name:
                return child
        return None
    
    def _find_file_in_tree(self, name):
        """takes a file name and returns the file node if it exists in the tree, otherwise None"""
        # FIXME: eventually use cache here if enabled
        def _recursively_find_file(node, name):
            # Recursively search in children
            folders = []
            for child in node.children:
                if not child.is_file:
                    folders.append(child)
                elif child.name == name:
                    return child
            for child in folders:
                found = _recursively_find_file(child, name)
                if found:
                    return found
            return None
        
        self.cache_accesses += 1

        # Check cache first
        if self.cache:
            cached_result = self.cache.get(name)
            if cached_result:
                self.cache_hits += 1
                return cached_result
        
        # If not in cache, search the tree
        result = _recursively_find_file(self.root, name)

        # If found, cache the result
        if self.cache and result:
            self.cache.put(name, result)

        return result
    
    def _get_wd_of_node(self, node):
        """does pwd on that node"""
        path = []
        current = node
        while current is not None and current != self.root:
            path.append(current.name)
            current = getattr(current, 'parent', None)
        return "/" + "/".join(reversed(path))
            
    
    def find(self, name):
        """Finds a cat in the whole tree."""
        node = self._find_file_in_tree(name)
        if node:
            print(f"Found {name} in {self._get_wd_of_node(node)}")
        else:
            print(f"{name} not found in the tree")
    def rescue(self, cat_name, required_role: Role = Role.STAFF):
        """Creates a new cat with a required role"""
        if self._find_node_in_current(cat_name) and self._find_node_in_current(cat_name).is_file: # type: ignore
            print(f"Cat {cat_name} already exists!")
            return
        new_cat = FileNode(cat_name, required_role, parent=self.current_node)
        self.current_node.add_child(new_cat)
        self._save_to_pkl()
        print(f"Rescued new cat: {cat_name} (role required: {required_role.name})")
    def pawprint(self):
        """Prints current working directory (pwd)"""
        print(f"Current cubby: {self._get_wd_of_node(self.current_node)}")
    def cat(self, cat_name):
        """Prints details about a cat."""
        node = self._find_node_in_current(cat_name)
        if not node:
            print(f"Cat {cat_name} not found!")
            return
        if not node.is_file:
            print(f"{cat_name} is not a cat!")
            return
        if not node.can_pet(self.role):
            print("Permission denied: you need petting permission")
            return
        print(f"Cat: {node.name}")
        for prop, value in node.content.items():
            if value is not None:
                print(f"{prop}: {value}")
    def meow(self, cat_name, property_name, value):
        """Write details about a cat."""
        node = self._find_node_in_current(cat_name)
        if not node:
            print(f"Cat {cat_name} not found!")
            return
        if not node.is_file:
            print(f"{cat_name} is not a cat!")
            return
        if not node.can_feed(self.role):
            print("Permission denied: you need feeding permission")
            return
        if not node.set_property(property_name, value):
            print(f"Invalid property: {property_name}, valid properties are: age, mood, date_found, date_fed")
            return
        self._save_to_pkl()
        print(f"Updated {property_name} for {cat_name}")
    def boop(self, cat_name):
        """Executes the cat (if user has groom permission)."""
        node = self._find_node_in_current(cat_name)
        if not node:
            print(f"Cat {cat_name} not found!")
            return
        if not node.is_file:
            print(f"{cat_name} is not a cat!")
            return
        if not node.can_groom(self.role):
            print("Permission denied: you need grooming permission")
            return
        print(f"*{cat_name} purrs contentedly*")
    def copycat(self, cat_name, new_cat_name):
        """Copies a cat."""
        source = self._find_node_in_current(cat_name)
        if source and source.is_file:
            new_cat = FileNode(new_cat_name, required_role=source.required_role, parent=self.current_node)
            new_cat.content = source.content.copy()
            self.current_node.add_child(new_cat)
            self._save_to_pkl()
            print(f"Copied {cat_name} to {new_cat_name}")
        else:
            print(f"Cat {cat_name} not found!")
    def recollar(self, cat_name, new_name):
        """Renames a cat."""
        cat = self._find_node_in_current(cat_name)
        if cat and cat.is_file:
            cat.name = new_name
            self._save_to_pkl()
            print(f"Renamed {cat_name} to {new_name}")
        else:
            print(f"Cat {cat_name} not found!")
    def walk(self, new_location):
        """Changes directory."""
        target = self._traverse_to_node(new_location)
        if target and not target.is_file:
            self.current_node = target
            print(f"Walked to {new_location}")
        else:
            print(f"Location {new_location} not found!")
    def adopted(self, cat_name):
        """Removes a cat."""
        cat = self._find_node_in_current(cat_name)
        if cat and cat.is_file:
            self.current_node.remove_child(cat)
            self._save_to_pkl()
            print(f"{cat_name} has been adopted!")
        else:
            print(f"Cat {cat_name} not found!")
    def carry(self, cat_name):
        """Attempts to carry a cat."""
        import random
        cat = self._find_node_in_current(cat_name)
        if cat and cat.is_file:
            if random.random() < 0.5:  # 50% chance of success
                self.carried_cats.append(cat)
                self.current_node.remove_child(cat)
                self._save_to_pkl()
                print(f"Successfully carrying {cat_name}")
            else:
                print(f"Failed to carry {cat_name} - they're too squirmy!")
        else:
            print(f"Cat {cat_name} not found!")
    def carrying(self):
        """Lists all cats being carried."""
        if self.carried_cats:
            print("Currently carrying:")
            for cat in self.carried_cats:
                print(f"- {cat.name}")
        else:
            print("Not carrying any cats")
    def put(self, cat_name=None):
        """Drops a cat into current directory."""
        if cat_name is None:
            for cat in self.carried_cats[:]:
                self.current_node.add_child(cat)
                self.carried_cats.remove(cat)
            self._save_to_pkl()
            print("Dropped all cats")
        else:
            for cat in self.carried_cats:
                if cat.name == cat_name:
                    self.current_node.add_child(cat)
                    self.carried_cats.remove(cat)
                    self._save_to_pkl()
                    print(f"Dropped {cat_name}")
                    return
            print(f"Not carrying {cat_name}")
    def mkcby(self, cubby_name):
        """Creates a new directory (cubby)."""
        if self._find_node_in_current(cubby_name) and not self._find_node_in_current(cubby_name).is_file: # type: ignore
            print(f"Cubby {cubby_name} already exists!")
        else:
            new_cubby = FolderNode(cubby_name, parent=self.current_node)
            self.current_node.add_child(new_cubby)
            self._save_to_pkl()
            print(f"Created new cubby: {cubby_name}")
    def prowl(self):
        """Lists all cats and sub-cubbies in current directory."""
        if not self.current_node.children or len(self.current_node.children) == 0:
            print("No cats or cubbies in this cubby")
            return
        print("Current cubby contents:")
        for child in self.current_node.children:
            print(f" - {child.name} ({'cubby' if not child.is_file else 'cat'})")
