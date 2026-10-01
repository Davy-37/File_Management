import hashlib

def verify_file_integrity(path_file, original_sha256):
    """
    Check if a file has been modified based on its SHA-256 hash.

    Args:
        path_file (str): Path to the file to check.
        original_sha256 (str): Original SHA-256 hash of the file.

    Returns:
        bool: True if the file has been modified, False otherwise.
    """
    
    with open(path_file, "rb") as file:
        content = file.read()
        file_hash = hashlib.sha256(content).hexdigest()
    

    if file_hash != original_sha256 :
            return True
            
    return False
        