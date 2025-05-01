class FileNode:
    def __init__(self, name: str):
        self.name = name
        self.children = []
        self.is_file = False

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"FileNode(name={self.name}, is_file={self.is_file})"
    
class DirectoryTree:
    def __init__(self):
        self.root = FileNode("root")
        self.current_node = self.root

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