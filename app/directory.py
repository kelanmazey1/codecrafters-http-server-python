"""Module to handle directory structure of servers current session"""
from pathlib import Path


class FileTree:
    def __init__(self):
        self._root = Path("/")

    def __repr__(self):
        return f"FileTree(root={self._root!r})"
    
    def get_root(self) -> Path:
        return self._root
    
    
    def set_root(self, root_path: str | Path, create: bool = False):
        if isinstance(root_path, str):
            root_path = Path(root_path)
        
        if not root_path.exists() and not create:
            raise ValueError(f"{root_path} doesn't exist and was not told to create")
        
        if not root_path.exists():
            root_path.mkdir(parents=True)
        
        self._root = root_path
    

f = FileTree()
def get_file_tree() -> FileTree:
    """Ensure module level singleton"""
    return f