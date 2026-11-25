"""
Jeff Sackmann's Grand Slam point-by-point, ATP and WTA repositories were
withdrawn from GitHub in 2026. They are read from an archival mirror, pinned to
one commit so that every analysis sees exactly the same files.

Set ``BSUTENNIS_ARCHIVE_URL`` to read the same files from another copy of the
mirror at that commit, e.g. a clone: ``file:///home/me/tennis-sackmann-archive``.
"""

import os
from pathlib import Path

from ..cache import fetch

REPOSITORY = "https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive"
COMMIT = "83733587353df8a41f2fd4f516147d5aa83f5a8d"  # slam_pointbypoint = upstream 6febb77 (Oct 2024)


def download(path: str) -> Path:
    """Local copy of ``path`` in the mirror, e.g. ``'atp/atp_matches_2023.csv'``."""
    base = os.environ.get("BSUTENNIS_ARCHIVE_URL", f"{REPOSITORY}/{COMMIT}")
    return fetch(f"{base}/{path}", f"archive/{COMMIT[:7]}/{path}")
