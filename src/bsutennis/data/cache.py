"""
Local cache for downloaded open data and the tables parsed from it.

Files are stored under ``$BSUTENNIS_CACHE`` (default ``~/.cache/bsutennis``)
and downloaded only once. Loaders put the source commit in the cache path,
so a cached file never changes.

Parsing a source (replaying every match) takes seconds to minutes, so the
parsed tables are cached too, keyed by the code that parses them and the
pandas and numpy versions: an upgrade never returns stale tables. The whole
cache can be deleted at any time.
"""

import gzip
import hashlib
import os
import pickle
import urllib.request
import warnings
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import TypeVar

import numpy as np
import pandas as pd

T = TypeVar("T")


def cache_dir() -> Path:
    return Path(os.environ.get("BSUTENNIS_CACHE", Path.home() / ".cache" / "bsutennis"))


def fetch(url: str, name: str) -> Path:
    """Path of the cached copy of ``url`` (stored as ``cache_dir() / name``),
    downloading it on first use."""
    path = cache_dir() / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_name(path.name + ".part")
        urllib.request.urlretrieve(url, partial)
        partial.rename(path)  # an interrupted download never looks complete
    return path


def parsed(name: str, build: Callable[[], T]) -> T:
    """
    The result of ``build()``, from the cache when an earlier call stored it.

    Warnings raised by ``build`` are stored with the result and raised again on
    every load, so a cached load reports the same data problems.
    """
    path = cache_dir() / "parsed" / _parser_version() / f"{name}.pkl.gz"
    if path.exists():
        with gzip.open(path, "rb") as file:
            result, raised = pickle.load(file)
    else:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = build()
        raised = [(str(w.message), w.category) for w in caught]
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_name(path.name + ".part")
        with gzip.open(partial, "wb", compresslevel=1) as file:
            pickle.dump((result, raised), file, protocol=pickle.HIGHEST_PROTOCOL)
        partial.rename(path)
    for message, category in raised:
        warnings.warn(message, category, stacklevel=3)
    return result


@cache
def _parser_version() -> str:
    """Hash of the code that parses the sources, with the pandas and numpy versions."""
    package = Path(__file__).parents[1]
    digest = hashlib.sha256(f"{pd.__version__} {np.__version__}".encode())
    for path in sorted([*(package / "data").rglob("*.py"), *(package / "rules").rglob("*.py")]):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]
