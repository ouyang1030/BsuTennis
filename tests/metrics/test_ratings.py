"""Elo ratings over a hand-made matches table."""

import pandas as pd
import pytest

from bsutennis.metrics import elo
from bsutennis.models import Elo


def match(match_id, date, round_, winner, loser, surface="hard", status="completed"):
    return {"match_id": match_id, "year": 2024, "tournament_date": pd.Timestamp(date), "date": pd.NaT,
            "round": round_, "player1": winner, "player2": loser, "winner": winner,
            "status": status, "surface": surface}


@pytest.fixture
def matches():
    return pd.DataFrame([
        match("final", "2024-01-01", "F", "Ann", "Bo"),
        match("semi", "2024-01-01", "SF", "Bo", "Cy"),
        match("next week", "2024-01-08", "R32", "Cy", "Ann", surface="clay"),
        match("walkover", "2024-01-08", "R16", "Bo", "Cy", status="walkover"),
        match("abandoned", "2024-01-08", "QF", None, "Cy"),
    ]).set_index("match_id")


def test_matches_are_rated_in_order_of_play(matches):
    ratings = elo(matches)
    assert ratings.match_id.unique().tolist() == ["semi", "final", "next week"]  # walkover and no winner left out

    system = Elo()
    system.play("Bo", "Cy")
    final = ratings[ratings.match_id == "final"].set_index("player")
    assert final.loc["Bo", "elo"] == system.rating("Bo")
    assert final.loc["Ann", "win_probability"] == system.play("Ann", "Bo")
    assert final.loc["Ann", "elo_after"] == system.rating("Ann")


def test_one_row_per_player_per_match(matches):
    ratings = elo(matches)
    assert len(ratings) == 6
    per_match = ratings.groupby("match_id").win_probability.sum()
    assert per_match.tolist() == pytest.approx([1, 1, 1])
    assert ratings.groupby("player").elo_after.last().to_dict() == pytest.approx(
        ratings.drop_duplicates("player", keep="last").set_index("player").elo_after.to_dict())


def test_separate_ratings_by_surface(matches):
    clay = elo(matches, by="surface").set_index(["match_id", "player"]).loc["next week"]
    assert clay.elo.tolist() == [1500, 1500]   # first clay match for both
