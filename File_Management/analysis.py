import filecmp
import shutil
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
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


def by_date(path: Path) -> str:
    """Return the modification month of an existing file as ``YYYY-MM``.

    The date read is the last modification time (``st_mtime``). It is
    converted using UTC, not the local time zone, so the result is the same
    on every machine: a file modified on January 31st at 23:30 UTC is always
    ``"2024-01"``, wherever the code runs.

    Args:
        path: Path of the file to categorize.

    Returns:
        The month of the last modification, such as ``"2024-03"``.

    Raises:
        FileNotFoundError: If ``path`` does not exist. The error is not
            caught here; callers decide how to report it.
    """
    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m")


def resolve_destination(source: Path, directory: Path) -> Path | None:
    """Choose the path where ``source`` should be copied in ``directory``.

    Candidates are tried in order: ``name.ext``, ``name_1.ext``,
    ``name_2.ext``, and so on. The first candidate that does not exist is
    returned. If a candidate already exists with the same content as
    ``source``, nothing needs to be copied and ``None`` is returned.

    Args:
        source: Path of the existing file to copy.
        directory: Folder that will receive the copy.

    Returns:
        A free destination path, or ``None`` if an identical file is already
        present in ``directory``.
    """
    candidate = directory / source.name
    counter = 0
    while candidate.exists():
        if filecmp.cmp(source, candidate, shallow=False):
            return None
        counter += 1
        candidate = directory / f"{source.stem}_{counter}{source.suffix}"
    return candidate


CRITERIA: dict[str, Callable[[Path], str]] = {
    "extension": by_extension,
    "size": by_size,
    "date": by_date,
}

DEFAULT_DEST_NAME = "classified"


def File_classify(
    fichiers: Iterable[Path],
    critère: str,
    dest_root: Path | None = None,
) -> ClassifyResult:
    """Copy each file into ``dest_root/<category>/`` according to a criterion.

    Files are copied with their metadata (``shutil.copy2``). The originals
    are never modified. Category folders are created when missing and reused
    otherwise.

    Collisions: if a file with the same name but different content already
    exists, the copy is renamed with a numeric suffix (``rapport_1.pdf``).
    If an identical file is already present, the file is skipped.

    Args:
        fichiers: Paths of the files to classify.
        critère: ``"extension"``, ``"size"`` or ``"date"``.
        dest_root: Root folder receiving the category folders. Defaults to a
            ``classified`` folder in the current directory.

    Returns:
        A :class:`ClassifyResult` with ``copied`` (source and final path),
        ``skipped`` (already present) and ``failed`` (path and reason).

    Raises:
        ValueError: If ``critère`` is unknown. Raised before any file or
            folder is touched.

    A problem on one file (missing file, permission error...) is recorded in
    ``failed`` and processing continues with the next file.
    """
    try:
        categorize = CRITERIA[critère]
    except KeyError:
        valid = ", ".join(sorted(CRITERIA))
        raise ValueError(f"Unknown criterion {critère!r}; expected one of: {valid}") from None

    root = Path(dest_root) if dest_root is not None else Path.cwd() / DEFAULT_DEST_NAME
    result = ClassifyResult()

    for source in map(Path, fichiers):
        try:
            directory = root / categorize(source)
            directory.mkdir(parents=True, exist_ok=True)
            destination = resolve_destination(source, directory)
            if destination is None:
                result.skipped.append(source)
                continue
            shutil.copy2(source, destination)
            result.copied.append(CopiedEntry(source, destination))
        except OSError as error:
            result.failed.append(FailedEntry(source, str(error)))

    return result
