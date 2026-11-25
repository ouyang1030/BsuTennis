"""Every dataset has the standard columns and types, whatever its source."""

import warnings

import pandas as pd
import pytest

from bsutennis.data import MATCH_COLUMNS, PLAYER_COLUMNS, POINT_COLUMNS, SHOT_COLUMNS, Dataset

TABLES = {"matches": MATCH_COLUMNS, "players": PLAYER_COLUMNS, "points": POINT_COLUMNS, "shots": SHOT_COLUMNS}

# 'round' is the tennis term; read it as matches["round"] (matches.round is a method).
ACCEPTED = {"round"}


@pytest.mark.parametrize("columns", TABLES.values())
def test_no_column_is_hidden_by_a_dataframe_attribute(columns):
    assert {c for c in columns if hasattr(pd.DataFrame, c)} <= ACCEPTED


def results_like() -> Dataset:
    """A source with matches and players only, and a few columns of each."""
    matches = pd.DataFrame({"tournament": ["Test Open"], "year": [2024], "best_of": [3], "n_points": [0]},
                           index=pd.Index(["m1"], name="match_id"))
    players = pd.DataFrame({"match_id": ["m1", "m1"], "player": ["A", "B"], "won": [True, False], "aces": [3, None]})
    return Dataset.from_tables(matches, players)


def points_like() -> Dataset:
    """A source with points: the columns that are always known, plus a plain-boolean flag."""
    matches = pd.DataFrame({"year": [2024], "best_of": [3], "n_points": [1], "date": [pd.Timestamp("2024-01-01")]},
                           index=pd.Index(["m2"], name="match_id"))
    players = pd.DataFrame({"match_id": ["m2", "m2"], "player": ["C", "D"]})
    always_known = {c: [1 if column.dtype == "int64" else False]
                    for c, column in POINT_COLUMNS.items() if column.dtype in ("int64", "bool")}
    points = pd.DataFrame({"match_id": ["m2"], **always_known, "ace": [True], "serve_no": [1]})
    return Dataset.from_tables(matches, players, points)


@pytest.mark.parametrize("make", [results_like, points_like])
def test_tables_have_the_standard_columns_and_types(make):
    dataset = make()
    for name, columns in TABLES.items():
        table = getattr(dataset, name)
        assert list(table.dtypes.astype(str).items()) == [(c, column.dtype) for c, column in columns.items()]


def test_datasets_of_different_sources_concatenate_cleanly():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        both = Dataset.concat([results_like(), points_like()])
    assert list(both.matches.index) == ["m1", "m2"]
    assert both.players.dtypes["aces"] == "Int64" and both.points.dtypes["ace"] == "boolean"
