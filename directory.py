class FileNode:
    def __init__(self, name: str, is_file: bool = False, parent = None):
        self.name = name
        self.children = [] # list to store child nodes (files or directories)
        self.is_file = is_file
        self.content = {}
        self.parent = parent

        if not is_file:
            self.children.append(".", is_file = False, parent = self) # '.' self reference
            if parent:
                self.children.append("..", is_file = False, parent = parent) # '..' parent reference

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def __repr__(self):
        return f"FileNode(name={self.name}, is_file={self.is_file})"
    
class DirectoryTree:
    def __init__(self):

        # initialize the dir with root
        self.root = FileNode("root")
        self.current_node = self.root # points to current working dir

    def _traverse_to_node(self, path: str):
        parts = path.strip("/").split("/")
        current = self.current_node if path.startswith(".") else self.root # traversal starting point
        for part in parts:
            if not part or part == ".": # skip empty parts or "."
                continue
            if part == "..":
                current = current.parent # go another level
            found = False
            for child in current.children:
                if child.name == part and not child.is_file: # child match current path
                    current = child 
                    found = True
                    break
            if not found:
                return None
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
                if len(child.children) > 2: # itself
                    current.remove_child(child) # remove dir if empty
                    return False
                current.remove_child(child) # remove dir if empty
                return True
        return False
