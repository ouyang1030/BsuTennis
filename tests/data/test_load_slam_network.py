"""
Acceptance tests on real data. They download about 8 MB on first run.

    pytest -m network
"""

import pytest

from bsutennis import load_slam

pytestmark = pytest.mark.network


@pytest.fixture(scope="module")
def wimbledon_2023():
    return load_slam(2023, "wimbledon")


def test_tournament_size(wimbledon_2023):
    assert len(wimbledon_2023.matches) == 254
    assert wimbledon_2023.matches.groupby("event").size().to_dict() == {"MS": 127, "WS": 127}


def test_final(wimbledon_2023):
    info = wimbledon_2023.matches.loc["2023-wimbledon-1701"]
    assert info.winner == "Carlos Alcaraz"
    assert info.scoreline == "1-6 7-6 6-1 3-6 6-4"
    assert info.n_points == 334


def test_every_match_replays_like_the_source(wimbledon_2023):
    assert wimbledon_2023.matches.score_mismatch_at.isna().all()
