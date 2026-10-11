from pathlib import Path
from typing import List, Union


def search_by_extension(root_dir: Union[str, Path], extensions: Union[str, List[str]]) -> List[str]:
    """
    Recursively finds files matching specific extensions in a directory.

    Args:
        root_dir (Union[str, Path]): Starting directory path.
        extensions (Union[str, List[str]]): Target extension(s) (e.g., '.txt' or ['txt', '.csv']).

    Returns:
        List[str]: Absolute paths of all matching files.
    """
    root_path = Path(root_dir)
    
    # Return empty list if directory doesn't exist
    if not root_path.is_dir():
        return []

    # Normalize extensions into a list with leading dots
    if isinstance(extensions, str):
        extensions = [extensions]
    valid_exts = {ext if ext.startswith('.') else f'.{ext}' for ext in extensions}

    # Recursively yield matching files using list comprehension
    return [
        str(file.resolve()) 
        for file in root_path.rglob("*") 
        if file.is_file() and file.suffix in valid_exts
    ]

print(find_files_by_extension("./file_management", ".py"))