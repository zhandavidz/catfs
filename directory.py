class FileNode:
    def __init__(self, name: str, is_file: bool = False, parent = None):
        self.name = name
        self.children = [] # list to store child nodes (files or directories)
        self.is_file = is_file
        self.content = {
            'age': None,
            'mood': None,
            'date_found': None,
            'date_fed': None
        }
        self.parent = parent
        self.permissions = {
            'pet': False,  # read
            'feed': False, # write
            'groom': False # execute
        }

        # Only add . and .. references for directories
        if not is_file:
            # Create special nodes for . and .. without adding them to children
            # to avoid recursion
            self.dot = self  # self-reference
            self.dotdot = parent  # parent reference

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def get_child(self, name):
        """Get a child node by name, handling . and .. specially."""
        if name == ".":
            return self.dot
        elif name == "..":
            return self.dotdot
        for child in self.children:
            if child.name == name:
                return child
        return None

    def set_property(self, property_name, value):
        if property_name in self.content:
            print(f"Setting {property_name} to {value}")
            self.content[property_name] = value
            return True
        return False

    def get_property(self, property_name):
        return self.content.get(property_name)

    def __repr__(self):
        return f"FileNode(name={self.name}, is_file={self.is_file})"
    
    def set_permissions(self, permissions):
        if permissions == "-r":
            self.permissions['pet'] = True
        elif permissions == "-rw":
            self.permissions['pet'] = True
            self.permissions['feed'] = True
        elif permissions == "-rwx":
            self.permissions['pet'] = True
            self.permissions['feed'] = True
            self.permissions['groom'] = True


class DirectoryTree:
    def __init__(self):
        # initialize the dir with root
        self.root = FileNode("root")
        self.current_node = self.root # points to current working dir
        self.carried_cats = [] # cats being carried
        self.permissions = {
            'pet': False,
            'feed': False,
            'groom': False
        }

    def set_permissions(self, role):
        if role == "Visitor":
            self.permissions['pet'] = True
        elif role == "Volunteer":
            self.permissions['pet'] = True
            self.permissions['feed'] = True
        elif role == "Staff":
            self.permissions['pet'] = True
            self.permissions['feed'] = True
            self.permissions['groom'] = True
        elif role == "Admin":
            self.permissions['pet'] = True
            self.permissions['feed'] = True
            self.permissions['groom'] = True

    def _traverse_to_node(self, path: str):
        parts = path.strip("/").split("/")
        current = self.current_node if path.startswith(".") else self.root # traversal starting point
        for part in parts:
            if not part: # skip empty parts
                continue
            child = current.get_child(part)
            if child is None:
                return None
            current = child
        return current

    def add_node(self, path: str, is_file: bool): #when u add a node, make sure to specify it's a dir or file

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
            if not found: # doesn't exist, make new dir or file
                new_dir = FileNode(part, is_file)
                current.add_child(new_dir)
                current = new_dir
        # make + add the node
        file_node = FileNode(parts[-1])
        file_node.is_file = True
        current.add_child(file_node)
    
    def list_directory(self, path: str):
        # list all files and directories in the given path
        # path is a string like "/dir1/dir2"

        current = self._traverse_to_node(path)
        if current is None:
            return []
        # return names of children
        return [child.name for child in current.children]
    
    def remove_file(self, path: str):

        # remove a file from the directory tree at specific path
        # path is a string like "/dir1/dir2/file.txt"
        
        parts = path.strip("/").split("/")
        dir_path = "/".join(parts[:-1]) # get path
        file_name = parts[-1] # get the file name

        current = self._traverse_to_node(dir_path)
        if current is None:
            return False
        
        for child in current.children:
            if child.name == file_name and child.is_file:
                current.remove_child(child)
                return True
        return False
    
    def remove_directory(self, path: str):

        # remove a directory from the directory tree at specific path
        # path is a string like "/dir1/dir2"

        parts = path.strip("/").split("/")
        dir_path = "/".join(parts[:-1]) # get path
        dir_name = parts[-1] # dir name

        current = self._traverse_to_node(dir_path)
        if current is None:
            return False
        
        for child in current.children:
            if child.name == dir_name and not child.is_file:
                if len(child.children) > 0: # itself
                    current.remove_child(child) # remove dir if empty
                    return False
                current.remove_child(child) # remove dir if empty
                return True
        return False

    def cat(self, cat_name):
        """Prints details about a cat."""
        node = self._find_node_in_current(cat_name)
        if not node:
            print(f"Cat {cat_name} not found!")
            return
        if not node.is_file:
            print(f"{cat_name} is not a cat!")
            return
        if not node.permissions['pet']:
            print("Permission denied: cat needs petting permission")
            return
        if not self.permissions['pet']:
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
        if not node.permissions['feed']:
            print("Permission denied: cat needs feeding permission")
            return
        if not self.permissions['feed']:
            print("Permission denied: you need feeding permission")
            return
        if not node.set_property(property_name, value):
            print(f"Invalid property: {property_name}")
            return
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
        if not node.permissions['groom'] and not self.permissions['groom']:
            print("Permission denied: cat needs grooming permission")
            return
        if not self.permissions['groom']:
            print("Permission denied: you need grooming permission")
            return
        print(f"*{cat_name} purrs contentedly*")

    def rescue(self, cat_name, permissions):
        """Creates a new cat."""
        if self._find_node_in_current(cat_name):
            print(f"Cat {cat_name} already exists!")
            return
        if permissions not in ["-r", "-rw", "-rwx"]:
            print("Invalid permissions. Must be '-r', '-rw', or '-rwx'")
            return
            
        new_cat = FileNode(cat_name, is_file=True, parent=self.current_node)
        new_cat.permissions = {
            'pet': '-r' in permissions,
            'feed': '-rw' in permissions,
            'groom': '-rwx' in permissions
        }
        self.current_node.add_child(new_cat)
        print(f"Rescued new cat: {cat_name}")

    def pawprint(self):
        """Prints current working directory."""
        path = []
        current = self.current_node
        while current != self.root:
            path.append(current.name)
            current = current.parent
        print("/" + "/".join(reversed(path)))

    def copycat(self, cat_name, new_cat_name):
        """Copies a cat."""
        source = self._find_node_in_current(cat_name)
        if source and source.is_file:
            new_cat = FileNode(new_cat_name, is_file=True, parent=self.current_node)
            new_cat.content = source.content.copy()
            new_cat.permissions = source.permissions.copy()
            self.current_node.add_child(new_cat)
            print(f"Copied {cat_name} to {new_cat_name}")
        else:
            print(f"Cat {cat_name} not found!")

    def recollar(self, cat_name, new_name):
        """Renames a cat."""
        cat = self._find_node_in_current(cat_name)
        if cat and cat.is_file:
            cat.name = new_name
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
            print("Dropped all cats")
        else:
            for cat in self.carried_cats:
                if cat.name == cat_name:
                    self.current_node.add_child(cat)
                    self.carried_cats.remove(cat)
                    print(f"Dropped {cat_name}")
                    return
            print(f"Not carrying {cat_name}")

    def mkcby(self, cubby_name):
        """Creates a new directory (cubby)."""
        if not self._find_node_in_current(cubby_name):
            new_cubby = FileNode(cubby_name, is_file=False, parent=self.current_node)
            self.current_node.add_child(new_cubby)
            print(f"Created new cubby: {cubby_name}")
        else:
            print(f"Cubby {cubby_name} already exists!")

    def prowl(self):
        """Lists all cats and sub-cubbies in current directory."""
        print("Current directory contents:")
        for child in self.current_node.children:
            if child.name not in [".", ".."]:
                print(f"- {child.name} ({'cubby' if not child.is_file else 'cat'})")

    def _find_node_in_current(self, name):
        """Helper method to find a node in current directory."""
        for child in self.current_node.children:
            if child.name == name:
                return child
        return None
