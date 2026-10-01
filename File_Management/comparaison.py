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

if __name__ == '__main__':
    find_added_files(r"C:\Document\3A\Open Source\Projet Collectif\Zone de test\old", r"C:\Document\3A\Open Source\Projet Collectif\Zone de test\new")