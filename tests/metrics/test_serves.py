"""Serves table and serve entropy, from a hand-made charted match."""

import math

import pandas as pd
import pytest

from bsutennis.data import Dataset
from bsutennis.metrics import serve_entropy, serves


@pytest.fixture
def dataset():
    # Point 1: first serve wide is a fault, second serve to the body, Bo wins the rally.
    # Point 2: an ace down the T.
    shots = pd.DataFrame({
        "match_id": "m", "point_no": [1, 1, 1, 2], "serve_no": [1, 2, 2, 1], "shot_no": [1, 1, 2, 1],
        "direction": ["wide", "body", "left", "T"], "ending": ["fault", None, "winner", "ace"],
    })
    points = pd.DataFrame({"match_id": "m", "point_no": [1, 2], "server": "Ann", "receiver": "Bo",
                           "side": ["deuce", "ad"], "server_won": [False, True]})
    players = pd.DataFrame({"match_id": "m", "player": ["Ann", "Bo"], "hand": ["R", "L"]})
    return Dataset(matches=pd.DataFrame(), players=players, points=points, shots=shots)


def test_one_row_per_serve_hit(dataset):
    table = serves(dataset)
    assert table[["point_no", "serve_no", "direction", "serve_in", "server_won"]].values.tolist() == [
        [1, 1, "wide", False, False],
        [1, 2, "body", True, False],
        [2, 1, "T", True, True],
    ]
    assert set(table.receiver_hand) == {"L"}
    assert table.side.tolist() == ["deuce", "deuce", "ad"]


def test_entropy_in_bits():
    table = pd.DataFrame({"server": ["Ann"] * 3 + ["Bo"] * 4,
                          "direction": ["wide", "body", "T", "T", "T", "T", None]})
    entropy = serve_entropy(table, by=["server"])
    assert entropy.loc["Ann", "entropy"] == pytest.approx(math.log2(3))   # one serve each way
    assert entropy.loc["Bo", "entropy"] == 0                              # always the T
    assert entropy.serves.tolist() == [3, 3]                              # unknown directions left out
