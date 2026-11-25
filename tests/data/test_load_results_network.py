"""
Acceptance tests on real ATP results (about 1 MB, plus 8 MB of Wimbledon points).

    pytest -m network
"""

import pytest

from bsutennis import load_results, load_slam

pytestmark = pytest.mark.network

STATISTICS = [
    "aces", "double_faults", "serve_points", "first_serves_in", "first_serve_points_won",
    "second_serve_points_won", "service_games", "break_points_faced", "break_points_saved",
]


@pytest.fixture(scope="module")
def season():
    return load_results("atp", 2023)


def test_size_is_fixed_by_the_pinned_commit(season):
    assert (len(season.matches), len(season.players)) == (2986, 5972)


def test_wimbledon_final(season):
    [final] = season.matches.query("tournament == 'Wimbledon' and round == 'F'").itertuples()
    assert (final.winner, final.scoreline, final.minutes) == ("Carlos Alcaraz", "1-6 7-6 6-1 3-6 6-4", 283)


def test_serve_statistics_agree_with_the_points_of_another_source(season):
    """Counted from the Grand Slam points, the statistics of each verified match
    equal the official ones."""
    wimbledon = load_slam(2023, "wimbledon")
    verified = wimbledon.matches.index[wimbledon.matches.score_mismatch_at.isna()]
    counted = wimbledon.players[wimbledon.players.match_id.isin(verified)]
    official = season.players[season.players.match_id.str.startswith("2023-540-")]
    both = counted.merge(official, on=["player", "opponent"], suffixes=("", "_official"))
    assert len(both) > 230
    for column in STATISTICS:
        assert (both[column] == both[f"{column}_official"]).mean() > 0.99, column
