"""Serve and return percentages, pooled over matches."""

import pandas as pd
import pytest

from bsutennis.metrics import serve_return


def player_row(match_id, player, opponent, serve_points, first_in, first_won, second_won, faced=4, saved=2):
    return {"match_id": match_id, "player": player, "opponent": opponent, "aces": 5, "double_faults": 2,
            "serve_points": serve_points, "first_serves_in": first_in, "first_serve_points_won": first_won,
            "second_serve_points_won": second_won, "break_points_faced": faced, "break_points_saved": saved}


@pytest.fixture
def players():
    return pd.DataFrame([
        player_row("long", "Ann", "Bo", 100, 60, 45, 20),
        player_row("long", "Bo", "Ann", 100, 50, 35, 25),
        player_row("short", "Ann", "Cy", 20, 10, 10, 10, faced=0, saved=0),   # won every serve point
        player_row("short", "Cy", "Ann", 20, 10, 5, 5),
        {"match_id": "no stats", "player": "Ann", "opponent": "Di"},
        {"match_id": "no stats", "player": "Di", "opponent": "Ann"},
    ])


def test_percentages_are_pooled_over_matches(players):
    ann = serve_return(players).loc["Ann"]
    assert ann.matches == 2  # the match without statistics is left out
    assert ann.serve_points_won == pytest.approx((65 + 20) / 120)       # not the mean of 0.65 and 1.0
    assert ann.first_serve_won == pytest.approx(55 / 70)
    assert ann.second_serve_won == pytest.approx(30 / 50)


def test_return_comes_from_the_opponents_serve(players):
    ann = serve_return(players).loc["Ann"]
    assert ann.return_points == 120
    assert ann.return_points_won == pytest.approx((40 + 10) / 120)
    assert ann.points_won == pytest.approx((85 + 50) / 240)
    assert ann.dominance_ratio == pytest.approx((50 / 120) / (35 / 120))
    assert ann.break_points_converted == pytest.approx(1 - 4 / 8)


def test_group_by_any_column(players):
    by_match = serve_return(players, by=["match_id", "player"])
    assert by_match.loc[("short", "Ann"), "serve_points_won"] == 1.0
