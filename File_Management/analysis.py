from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

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
