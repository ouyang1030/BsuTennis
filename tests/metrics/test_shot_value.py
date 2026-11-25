"""Shot values on hand-made rallies."""

import pandas as pd
import pytest

from bsutennis.data import Dataset
from bsutennis.metrics import shot_values


def stroke(point, serve_no, shot_no, player, shot_type="groundstroke", ending=None):
    return {"match_id": "m", "point_no": point, "serve_no": serve_no, "shot_no": shot_no, "player": player,
            "shot_type": shot_type, "wing": None, "position": "baseline", "direction": None, "depth": None,
            "ending": ending}


@pytest.fixture
def dataset():
    shots = pd.DataFrame([
        # 1: Ann serves in, Bo returns, Ann hits a winner
        stroke(1, 1, 1, "Ann", "serve"), stroke(1, 1, 2, "Bo"), stroke(1, 1, 3, "Ann", ending="winner"),
        # 2: first serve fault (not part of the rally), second serve in, Bo misses the return
        stroke(2, 1, 1, "Ann", "serve", "fault"), stroke(2, 2, 1, "Ann", "serve"),
        stroke(2, 2, 2, "Bo", ending="unforced_error"),
        # 3: Ann serves in, Bo returns, Ann misses
        stroke(3, 1, 1, "Ann", "serve"), stroke(3, 1, 2, "Bo"), stroke(3, 1, 3, "Ann", ending="unforced_error"),
        # 4: an ace
        stroke(4, 1, 1, "Ann", "serve", "ace"),
    ])
    points = pd.DataFrame({"match_id": "m", "point_no": [1, 2, 3, 4], "serve_no": [1, 2, 1, 1],
                           "server": "Ann", "server_won": [True, True, False, True],
                           "point_winner": ["Ann", "Ann", "Bo", "Ann"]})
    return Dataset(matches=pd.DataFrame(), players=pd.DataFrame(), points=points, shots=shots)


def test_faults_before_the_rally_are_left_out(dataset):
    values = shot_values(dataset)
    assert len(values) == 9
    assert values.query("point_no == 2").serve_no.tolist() == [2, 2]


def test_chances(dataset):
    values = shot_values(dataset).set_index(["point_no", "shot_no"])
    # first serves that started a rally: Ann won points 1 and 4 of 1, 3, 4
    assert values.loc[(1, 1), "before"] == pytest.approx(2 / 3)
    # first serves in play (points 1 and 3): Ann won one of the two
    assert values.loc[(1, 1), "after"] == pytest.approx(1 / 2)
    # Bo's returns in play (points 1 and 3): Bo won one of the two
    assert values.loc[(1, 2), ["before", "after"]].tolist() == pytest.approx([1 / 2, 1 / 2])
    assert values.loc[(1, 3), ["before", "after", "value"]].tolist() == pytest.approx([1 / 2, 1, 1 / 2])
    assert values.loc[(4, 1), "value"] == pytest.approx(1 / 3)       # the ace


def test_values_add_up_to_the_result(dataset):
    values = shot_values(dataset).merge(dataset.points[["point_no", "server", "server_won"]], on="point_no")
    signed = values.value.where(values.player == values.server, -values.value)
    start = values[values.shot_no == 1].set_index("point_no").before
    total = signed.groupby(values.point_no).sum()
    result = dataset.points.set_index("point_no").server_won.astype(float)
    assert total.tolist() == pytest.approx((result - start).tolist())
