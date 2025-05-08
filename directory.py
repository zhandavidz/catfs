class FileNode:
    def __init__(self, name: str):
        self.name = name
        self.children = []
        self.is_file = False

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def __repr__(self):
        return f"FileNode(name={self.name}, is_file={self.is_file})"
    
class DirectoryTree:
    def __init__(self):
        self.root = FileNode("root")
        self.current_node = self.root

    def _traverse_to_node(self, path: str):
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts:
            if not part:
                continue
            found = False
            for child in current.children:
                if child.name == part and not child.is_file:
                    current = child
                    found = True
                    break
            if not found:
                return None
        return current

    def add_file(self, path: str):

        # add a file to the directory tree at specific path
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
                new_dir = FileNode(part)
                current.add_child(new_dir)
                current = new_dir
        file_node = FileNode(parts[-1])
        file_node.is_file = True
        current.add_child(file_node)
    
    def list_directory(self, path: str):
        # list all files and directories in the given path
        # path is a string like "/dir1/dir2"

        current = self._traverse_to_node(path)
        if current is None:
            return []
        return [child.name for child in current.children]
    
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
                return True
        return False