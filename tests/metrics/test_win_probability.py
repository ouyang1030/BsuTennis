"""Point-by-point win probabilities from a hand-made match."""

import pandas as pd
import pytest

from bsutennis.data import Dataset
from bsutennis.metrics import point_probabilities, serve_shares
from bsutennis.models import win_probability
from bsutennis.rules import MatchFormat, Score, replay

MATCH_FORMAT = MatchFormat(best_of=3)
# Ann serves first and wins 6-4 6-4: every game is held, except one break per set
GAMES = (["Ann", "Bo"] * 4 + ["Ann", "Ann"]) * 2   # winner of each game; the 10th game is Bo's serve
SERVE_POINTS_WON = {"Ann": 33, "Bo": 31}              # of 50 each: a close match


def dataset(player1="Ann", player2="Bo") -> Dataset:
    names = ("Ann", "Bo")
    winners = [names.index(w) for w in GAMES for _ in range(4)]
    scores = replay(winners, MATCH_FORMAT, first_server=0)
    points = pd.DataFrame({
        "match_id": "m", "point_no": range(1, len(winners) + 1),
        "server": [names[s.server] for s in scores[:-1]], "point_winner": [names[w] for w in winners],
    })
    matches = pd.DataFrame({"player1": [player1], "player2": [player2], "match_format": [MATCH_FORMAT.code]},
                           index=pd.Index(["m"], name="match_id"))
    players = pd.DataFrame({"match_id": "m", "player": [player1, player2], "serve_points": 50,
                            "first_serves_in": 50, "second_serve_points_won": 0,
                            "first_serve_points_won": [SERVE_POINTS_WON[player1], SERVE_POINTS_WON[player2]]})
    return Dataset(matches=matches, players=players, points=points, shots=pd.DataFrame())


def test_serve_shares_come_from_the_players_table():
    shares = serve_shares(dataset().players)
    assert shares.set_index("player").serve_points_won.to_dict() == {"Ann": 0.66, "Bo": 0.62}


def test_first_point_is_the_pre_match_probability():
    probabilities = point_probabilities(dataset())
    start = Score(MATCH_FORMAT, game_server=0)
    assert probabilities.player1_win_probability.iloc[0] == pytest.approx(win_probability(start, (0.66, 0.62)))
    assert len(probabilities) == len(dataset().points)


def test_probability_rises_towards_the_end_and_match_point_matters():
    probabilities = point_probabilities(dataset())
    first, last = probabilities.iloc[0], probabilities.iloc[-1]   # last: 40-0, match point for Ann
    assert first.player1_win_probability < 0.7 < 0.95 < last.player1_win_probability
    assert probabilities.importance.max() > 10 * probabilities.importance.min() > 0


def test_player_order_only_mirrors_the_probability():
    as_listed = point_probabilities(dataset())
    swapped = point_probabilities(dataset(player1="Bo", player2="Ann"))
    assert (as_listed.player1_win_probability + swapped.player1_win_probability).tolist() == pytest.approx([1.0] * len(as_listed))
    assert swapped.importance.tolist() == pytest.approx(as_listed.importance.tolist())
