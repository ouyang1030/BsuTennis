"""
Acceptance tests on real Match Charting Project data (about 7 MB on first run).

    pytest -m network
"""

import pytest

from bsutennis import load_charting

pytestmark = pytest.mark.network


@pytest.fixture(scope="module")
def charted():
    return load_charting("wta", "to-2009")


def test_size_is_fixed_by_the_pinned_commit(charted):
    assert (len(charted.matches), len(charted.points)) == (416, 61068)


def test_replayed_score_agrees_with_the_source(charted):
    assert charted.matches.score_mismatch_at.isna().mean() > 0.99


def test_almost_every_point_has_shots(charted):
    assert charted.points.shots_recorded.mean() > 0.97


def test_last_stroke_agrees_with_the_point_winner(charted):
    last = charted.shots.groupby(["match_id", "point_no"]).tail(1)
    last = last.merge(charted.points[["match_id", "point_no", "point_winner"]])
    won = last.ending.isin(["ace", "service_winner", "winner"])
    lost = last.ending.isin(["fault", "forced_error", "unforced_error"])
    agrees = (won & (last.player == last.point_winner)) | (lost & (last.player != last.point_winner))
    assert agrees[won | lost].mean() > 0.99
