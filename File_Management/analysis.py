from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

KB = 1024
MB = 1024 * KB

# Upper bounds (inclusive, in bytes) in ascending order; None means no limit.
SIZE_CATEGORIES = (
    (10 * KB, "minuscule"),
    (100 * KB, "petit"),
    (1 * MB, "moyen"),
    (16 * MB, "grand"),
    (128 * MB, "énorme"),
    (None, "gigantesque"),
)


class CopiedEntry(NamedTuple):
    """A file that was successfully copied.

    Attributes:
        source: Path of the original file, which is never modified.
        destination: Final path of the copy, after any collision renaming.
    """

    source: Path
    destination: Path


class FailedEntry(NamedTuple):
    """A file that could not be processed.

    Attributes:
        path: Path of the file that caused the problem.
        reason: Human-readable description of what went wrong.
    """

    path: Path
    reason: str


@dataclass
class ClassifyResult:
    """Outcome of a classification run.

    Each instance owns its own lists, so two results never share state.

    Attributes:
        copied: Files that were copied, as (source, destination) entries.
        skipped: Files left alone because an identical file already exists
            at the destination.
        failed: Files that could not be processed, with the reason.
    """

    copied: list[CopiedEntry] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    failed: list[FailedEntry] = field(default_factory=list)


def by_extension(path: Path) -> str:
    """Return the category name of a file based on its extension.

    The function is pure: it only inspects the name in ``path`` and never
    touches the disk, so the file does not need to exist.

    Args:
        path: Path of the file to categorize.

    Returns:
        The extension in lowercase and without the leading dot (``"pdf"`` for
        ``PHOTO.PDF``). Only the last extension is used, so ``archive.tar.gz``
        gives ``"gz"``. Returns ``"sans_extension"`` when the file has none,
        including dotfiles such as ``.gitignore``.

    Examples:
        >>> by_extension(Path("PHOTO.JPG"))
        'jpg'
        >>> by_extension(Path("README"))
        'sans_extension'
    """
    return path.suffix.lstrip(".").lower() or "sans_extension"


def by_size(path: Path) -> str:
    """Return the size category of an existing file.

    Unlike :func:`by_extension`, this function reads the disk (file size).
    Boundaries are inclusive: a file of exactly 10 KB is ``"minuscule"`` and
    a file of 10 KB + 1 byte is ``"petit"``. 1 KB is 1024 bytes.

    Categories: ``vide`` (0 bytes), ``minuscule`` (up to 10 KB), ``petit``
    (up to 100 KB), ``moyen`` (up to 1 MB), ``grand`` (up to 16 MB),
    ``énorme`` (up to 128 MB) and ``gigantesque`` (anything larger).

    Args:
        path: Path of the file to categorize.

    Returns:
        The name of the size category.

    Raises:
        FileNotFoundError: If ``path`` does not exist. The error is not
            caught here; callers decide how to report it.
    """
    size = path.stat().st_size
    if size == 0:
        return "vide"
    for limit, name in SIZE_CATEGORIES:
        if limit is None or size <= limit:
            return name
