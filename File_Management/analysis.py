from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

# import shutil


class CopiedEntry(NamedTuple):
    source: Path
    destination: Path


class FailedEntry(NamedTuple):
    path: Path
    reason: str


@dataclass
class ClassifyResult:
    copied: list[CopiedEntry] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    failed: list[FailedEntry] = field(default_factory=list)
