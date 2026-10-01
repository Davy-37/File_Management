from pathlib import Path
import hashlib

def find_added_files(path_old_folder, path_new_folder):
    """
    Display the files added to the new folder.

    Args:
        path_old_folder (str): Path to the old folder.
        path_new_folder (str): Path to the new folder.
    """
    
    old_folder = Path(path_old_folder)
    new_folder = Path(path_new_folder)
    
    old_set = set()
    new_set = set()
    
    for file in old_folder.iterdir():
        if file.is_file():
            old_set.add(file.name)
            
    for file in new_folder.iterdir():
        if file.is_file():
            new_set.add(file.name)
    
    diff = new_set - old_set
    
    for diff_file in diff:
        print("+",diff_file)


def find_deleted_files(path_old_folder, path_new_folder):
    """
    Display files that are present in the old folder but not in the new folder.

    Args:
        path_old_folder (str): Path to the old folder.
        path_new_folder (str): Path to the new folder.
    """
    
    old_folder = Path(path_old_folder)
    new_folder = Path(path_new_folder)
    
    old_set = set()
    new_set = set()
    
    for file in old_folder.iterdir():
        if file.is_file():
            old_set.add(file.name)
            
    for file in new_folder.iterdir():
        if file.is_file():
            new_set.add(file.name)
    
    diff = old_set - new_set
    
    for diff_file in diff:
        print("-",diff_file)


def find_modified_files(path_old_folder, path_new_folder):
    """
    Display files that are modified between the old and new folder.

    Args:
        path_old_folder (str): Path to the old folder.
        path_new_folder (str): Path to the new folder.
    """
    
    old_folder = Path(path_old_folder)
    new_folder = Path(path_new_folder)
    
    old_set = set()
    new_set = set()
    
    for file in old_folder.iterdir():
        if file.is_file():
            old_set.add(file.name)
            
    for file in new_folder.iterdir():
        if file.is_file():
            new_set.add(file.name)
            
    common_files = set.intersection(old_set, new_set)
    
    modified = set()
    
    for file in common_files:
        path_old_file = old_folder / file
        path_new_file = new_folder / file
        
        with open(path_old_file, "rb") as old_file:
            old_content = old_file.read()
            old_file_hash = hashlib.sha256(old_content).hexdigest()
            
        with open(path_new_file, "rb") as new_file:
            new_content = new_file.read()
            new_file_hash = hashlib.sha256(new_content).hexdigest()
        
        if old_file_hash != new_file_hash:
            modified.add(file)
            
    for modified_file in modified:
        print("~",modified_file)
            