import re
from pathlib import Path
from collections import deque
from typing import List, Tuple, Dict, Union, Optional

def _build_pattern(keyword: str, ignore_case: bool, whole_word: bool) -> re.Pattern:
    """
    Build the regular expression pattern for the search.

    Parameters
    ----------
    keyword : str
        The word or phrase to search for.
    ignore_case : bool
        If True, the search will be case-insensitive.
    whole_word : bool
        If True, the keyword is treated as a whole word, preventing partial matches.

    Returns
    -------
    re.Pattern
        The compiled regular expression object.
    """
    flags = re.IGNORECASE if ignore_case else 0
    pattern_str = rf"\b{re.escape(keyword)}\b" if whole_word else re.escape(keyword)
    return re.compile(pattern_str, flags)


def search_by_extension(root_dir: Union[str, Path], extensions: Union[str, List[str], None] = None, recursive: bool = True) -> List[Path]:
    """
    Find files matching specific extensions in a directory.

    Parameters
    ----------
    root_dir : Union[str, Path]
        Starting directory path.
    extensions : Union[str, List[str], None], optional
        Target extension(s) (e.g., '.txt' or ['txt', '.csv']). If None, returns all files.
    recursive : bool, optional
        If True (default), searches in all subdirectories recursively.

    Returns
    -------
    List[Path]
        List of Path objects for all matching files.
    """
    root_path = Path(root_dir)
    if not root_path.is_dir():
        return []

    file_iterator = root_path.rglob("*") if recursive else root_path.glob("*")

    if not extensions:
        return [file for file in file_iterator if file.is_file()]

    if isinstance(extensions, str):
        extensions = [extensions]
    
    valid_exts = {ext if ext.startswith('.') else f'.{ext}' for ext in extensions}

    return [
        file for file in file_iterator 
        if file.is_file() and file.suffix in valid_exts
    ]


def contains_word(filepath: Union[str, Path], keyword: str, ignore_case: bool = True, whole_word: bool = False) -> bool:
    """
    Check as quickly as possible if a file contains the specified keyword.

    This function stops reading the file and returns True at the first occurrence 
    found, making it highly efficient for checking large files.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the file to be searched.
    keyword : str
        The word or phrase to search for.
    ignore_case : bool, optional
        If True (default), the search is case-insensitive.
    whole_word : bool, optional
        If True, prevents partial matches (default is False).

    Returns
    -------
    bool
        True if the keyword is found in the file, False otherwise.
    """
    pattern = _build_pattern(keyword, ignore_case, whole_word)
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if pattern.search(line):
                return True
    return False


def find_lines(filepath: Union[str, Path], keyword: str, ignore_case: bool = True, whole_word: bool = False) -> List[Tuple[int, str]]:
    """
    Find all lines in a file that contain a specific keyword.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the file to be searched.
    keyword : str
        The word or phrase to search for.
    ignore_case : bool, optional
        If True (default), the search is case-insensitive.
    whole_word : bool, optional
        If True, prevents partial matches (default is False).

    Returns
    -------
    List[Tuple[int, str]]
        A list of tuples, where each tuple contains the line number (1-indexed) 
        and the exact content of the line (without trailing newlines).
    """
    pattern = _build_pattern(keyword, ignore_case, whole_word)
    results = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, start=1):
            if pattern.search(line):
                results.append((line_num, line.rstrip('\n')))
                
    return results


def count_occurrences(filepath: Union[str, Path], keyword: str, ignore_case: bool = True, whole_word: bool = False) -> int:
    """
    Count the total number of times a keyword appears in a file.

    Multiple occurrences on a single line are counted individually.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the file to be searched.
    keyword : str
        The word or phrase to search for.
    ignore_case : bool, optional
        If True (default), the search is case-insensitive.
    whole_word : bool, optional
        If True, prevents partial matches (default is False).

    Returns
    -------
    int
        The total count of the keyword found in the file.
    """
    pattern = _build_pattern(keyword, ignore_case, whole_word)
    total = 0
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total += len(pattern.findall(line))
            
    return total


def get_context(filepath: Union[str, Path], keyword: str, lines_around: int = 2, ignore_case: bool = True, whole_word: bool = False) -> List[Dict[str, Union[int, List[str]]]]:
    """
    Find keyword occurrences and return them along with surrounding context lines.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the file to be searched.
    keyword : str
        The word or phrase to search for.
    lines_around : int, optional
        The number of lines to capture before and after the matched line (default is 2).
    ignore_case : bool, optional
        If True (default), the search is case-insensitive.
    whole_word : bool, optional
        If True, prevents partial matches (default is False).

    Returns
    -------
    List[Dict[str, Union[int, List[str]]]]
        A list of dictionaries. Each dictionary represents a match and contains:
        - 'line_num': the integer line number where the match occurred.
        - 'context': a list of strings representing the matched line and its surrounding context lines.
    """
    pattern = _build_pattern(keyword, ignore_case, whole_word)
    contexts = []
    
    before_buffer = deque(maxlen=lines_around)
    lines_after_needed = 0
    current_match_context = []
    current_match_line = 0
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, start=1):
            clean_line = line.rstrip('\n')
            
            if lines_after_needed > 0:
                current_match_context.append(clean_line)
                lines_after_needed -= 1
                if lines_after_needed == 0:
                    contexts.append({"line_num": current_match_line, "context": current_match_context.copy()})
                    current_match_context = []
                    
            elif pattern.search(line):
                current_match_line = line_num
                current_match_context = list(before_buffer) + [clean_line]
                lines_after_needed = lines_around
                
                if lines_around == 0:
                    contexts.append({"line_num": current_match_line, "context": current_match_context.copy()})
                    current_match_context = []
            else:
                before_buffer.append(clean_line)

        if lines_after_needed > 0:
            contexts.append({"line_num": current_match_line, "context": current_match_context.copy()})

    return contexts


def search_in_folder(folder_path: Union[str, Path], keyword: str, extensions: Union[str, List[str], None] = None, recursive: bool = True, ignore_case: bool = True, whole_word: bool = False) -> List[Path]:
    """
    Scan a directory to find all files containing a specific keyword.

    Parameters
    ----------
    folder_path : Union[str, Path]
        The path to the target directory.
    keyword : str
        The word or phrase to search for.
    extensions : Union[str, List[str], None], optional
        Target extension(s) (e.g., '.txt' or ['txt', '.csv']). If None, searches all files.
    recursive : bool, optional
        If True (default), searches in all subdirectories recursively.
    ignore_case : bool, optional
        If True (default), the search is case-insensitive.
    whole_word : bool, optional
        If True, prevents partial matches (default is False).

    Returns
    -------
    List[Path]
        A list of Path objects for every file that contains the keyword.
    """
    files_to_check = search_by_extension(folder_path, extensions, recursive)
    matching_files = []
    
    for file in files_to_check:
        if contains_word(file, keyword, ignore_case, whole_word):
            matching_files.append(file)
            
    return matching_files