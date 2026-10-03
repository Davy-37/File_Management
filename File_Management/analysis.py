from pathlib import Path
import hashlib

def duplicates(path_folder, delete=False):
    """
    Detect and display duplicate files in a folder.

    Args:
        path_folder (str): Path to the folder to analyze.
        delete (bool): If True, delete duplicate files while keeping one copy.
    
    Returns:
        None
    """

    folder = Path(path_folder)
    
    files_by_hash = {}
    
    for file in folder.iterdir():
        if file.is_file():
            with open(file, "rb") as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
            if file_hash in files_by_hash:
                files_by_hash[file_hash].append(file.name)
            else:
                files_by_hash[file_hash] = []
                files_by_hash[file_hash].append(file.name)
     
    for file_hash in files_by_hash:
        if len(files_by_hash[file_hash]) > 1:
            print("=")
            for file in files_by_hash[file_hash]:
                print(file)
            print("\n")
            
    if delete:        
        for file_hash in files_by_hash:
            if len(files_by_hash[file_hash]) > 1:
                print("delete :")
                for i in range(1, len(files_by_hash[file_hash])):
                    file_to_delete = folder / files_by_hash[file_hash][i]
                    file_to_delete.unlink()
                    print("-",files_by_hash[file_hash][i])
                print("\n")
    

