from pathlib import Path

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

