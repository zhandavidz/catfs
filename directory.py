import os
import pickle
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
    def __init__(self, name: str, role: Role = Role.VISITOR):
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
        parts = path.strip("/").split("/")
        current = self.current_node if path.startswith(".") else self.root
        for part in parts:
            if not part:
                continue
            child = current.get_child(part)
            if child is None:
                return None
            current = child
        return current
    def add_node(self, path: str, is_file: bool, required_role: Role = Role.STAFF):
        # add a file/dir to the directory tree at specific path
        # path is a string like "/dir1/dir2/file.txt"
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts[:-1]:
            found = False
            for child in current.children:
                if child.name == part and not child.is_file:
                    current = child
                    found = True
                    break
            if not found:
                new_dir = FolderNode(part, current)
                current.add_child(new_dir)
                current = new_dir
        if is_file:
            file_node = FileNode(parts[-1], required_role, current)
            current.add_child(file_node)
        else:
            folder_node = FolderNode(parts[-1], current)
            current.add_child(folder_node)
        self._save_to_pkl()
    def remove_file(self, path: str):
        # remove a file from the directory tree at specific path
        # path is a string like "/dir1/dir2/file.txt"
        parts = path.strip("/").split("/")
        dir_path = "/".join(parts[:-1])
        file_name = parts[-1]
        current = self._traverse_to_node(dir_path)
        if current is None:
            return False
        for child in current.children:
            if child.name == file_name and child.is_file:
                current.remove_child(child)
                self._save_to_pkl()
                return True
        return False
    def remove_directory(self, path: str):
        # remove a directory from the directory tree at specific path
        # path is a string like "/dir1/dir2"
        parts = path.strip("/").split("/")
        dir_path = "/".join(parts[:-1])
        dir_name = parts[-1]
        current = self._traverse_to_node(dir_path)
        if current is None:
            return False
        for child in current.children:
            if child.name == dir_name and not child.is_file:
                if len(child.children) > 0:
                    return False
                current.remove_child(child)
                self._save_to_pkl()
                return True
        return False
    def rescue(self, cat_name, required_role: Role = Role.STAFF):
        # Creates a new cat with a required role
        if self._find_node_in_current(cat_name):
            print(f"Cat {cat_name} already exists!")
            return
        new_cat = FileNode(cat_name, required_role, parent=self.current_node)
        self.current_node.add_child(new_cat)
        self._save_to_pkl()
        print(f"Rescued new cat: {cat_name} (role required: {required_role.name})")
    def _find_node_in_current(self, name):
        for child in self.current_node.children:
            if child.name == name:
                return child
        return None
    def pawprint(self):
        # Prints current working directory
        path = []
        current = self.current_node
        while current is not None and current != self.root:
            path.append(current.name)
            current = getattr(current, 'parent', None)
        print("/" + "/".join(reversed(path)))
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
            print(f"Invalid property: {property_name}")
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
    def put(self, cat_name):
        """Drops a cat into current directory."""
        if cat_name == "all":
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
        if not self._find_node_in_current(cubby_name):
            new_cubby = FolderNode(cubby_name, parent=self.current_node)
            self.current_node.add_child(new_cubby)
            self._save_to_pkl()
            print(f"Created new cubby: {cubby_name}")
        else:
            print(f"Cubby {cubby_name} already exists!")
    def prowl(self):
        """Lists all cats and sub-cubbies in current directory."""
        print("Current directory contents:")
        for child in self.current_node.children:
            if child.name not in [".", ".."]:
                print(f"- {child.name} ({'cubby' if not child.is_file else 'cat'})")
