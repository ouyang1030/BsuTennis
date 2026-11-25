"""Parsed tables are cached, with the warnings raised while parsing."""

import warnings

import pytest

from bsutennis.data.cache import parsed


@pytest.fixture(autouse=True)
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("BSUTENNIS_CACHE", str(tmp_path))


def test_built_once():
    calls = []

    def build():
        calls.append(1)
        return {"rows": 3}

    assert parsed("table", build) == {"rows": 3}
    assert parsed("table", build) == {"rows": 3}
    assert len(calls) == 1


def test_warnings_are_raised_on_every_load():
    def build():
        warnings.warn("skipped 2 matches", UserWarning)
        return 1

    for _ in range(2):
        with pytest.warns(UserWarning, match="skipped 2 matches"):
            parsed("with warning", build)
