"""Offline tests of the MCP loader on a small hand-made match."""

import pandas as pd
import pytest

from bsutennis.data import MATCH_COLUMNS, PLAYER_COLUMNS, POINT_COLUMNS, SHOT_COLUMNS
from bsutennis.data.sources.mcp import parse

MATCH_ID = "20240101-M-Test_Open-F-Anna_A-Bea_B"
NO_FORMAT_ID = "20240102-M-Test_Open-SF-Anna_A-Cleo_C"

# Codes of particular points; every other point is an ace (Anna serving) or a
# return winner (Bea serving), so Anna wins 6-0 6-0.
SPECIAL = {
    1: ("5n", "4*"),       # 2nd-serve ace
    5: ("6d", "5w"),       # double fault by Bea
    6: ("S", ""),          # recorded without shots
    7: ("6f12b*", ""),     # does not follow the notation
}


def raw_matches() -> pd.DataFrame:
    row = {"Pl 1 hand": "R", "Pl 2 hand": "L ", "Date": "20240101", "Tournament": "Test Open",
           "Round": "F", "Surface": "Hard", "Best of": "3", "Final TB?": "1"}
    return pd.DataFrame([
        {"match_id": MATCH_ID, "Player 1": "Anna A", "Player 2": "Bea B", **row},
        {"match_id": NO_FORMAT_ID, "Player 1": "Anna A", "Player 2": "Cleo C", **row, "Best of": ""},
    ])


def raw_points(match_id=MATCH_ID) -> pd.DataFrame:
    """Rows as the source writes them: the score *before* each point, points server first."""
    rows = []
    for game in range(12):
        anna_serves = game % 2 == 0
        for i, label in enumerate(["0", "15", "30", "40"]):
            pt = len(rows) + 1
            first, second = SPECIAL.get(pt, ("4*", "") if anna_serves else ("6f1*", ""))
            rows.append({
                "match_id": match_id, "Pt": str(pt), "Svr": "1" if anna_serves else "2", "PtWinner": "1",
                "Set1": str(game // 6), "Set2": "0", "Gm1": str(game % 6), "Gm2": "0",
                "Pts": f"{label}-0" if anna_serves else f"0-{label}",
                "1st": first, "2nd": second,
            })
    return pd.DataFrame(rows)


@pytest.fixture
def dataset():
    points = pd.concat([raw_points(), raw_points(NO_FORMAT_ID)])
    with pytest.warns(UserWarning, match="skipped 1 matches"):
        return parse(raw_matches(), points, "MS")


def point(ds, n):
    return ds.points.set_index("point_no").loc[n]


def test_tables_follow_the_schema(dataset):
    assert list(dataset.matches.columns) == list(MATCH_COLUMNS)
    assert list(dataset.players.columns) == list(PLAYER_COLUMNS)
    assert list(dataset.points.columns) == list(POINT_COLUMNS)
    assert list(dataset.shots.columns) == list(SHOT_COLUMNS)


def test_match_info(dataset):
    assert list(dataset.matches.index) == [MATCH_ID]  # the match without a format is skipped
    info = dataset.matches.loc[MATCH_ID]
    assert (info.tournament, info.surface, info.best_of) == ("Test Open", "hard", 3)
    assert info.date == pd.Timestamp("2024-01-01")
    assert (info.winner, info.status, info.scoreline) == ("Anna A", "completed", "6-0 6-0")
    assert info.match_format == "bo3 6/tb7"
    assert pd.isna(info.score_mismatch_at)


def test_players(dataset):
    players = dataset.players.set_index("player")
    assert players.loc["Bea B", ["opponent", "won", "hand"]].tolist() == ["Anna A", False, "L"]
    # Anna serves points 1-4, 9-12, ...: all aces, point 1 on the second serve
    anna = players.loc["Anna A"]
    assert (anna.serve_points, anna.service_games, anna.aces) == (24, 6, 24)
    assert (anna.first_serves_in, anna.first_serve_points_won, anna.second_serve_points_won) == (23, 23, 1)
    # Bea serves points 5-8, ...: a double fault at 5; 6 and 7 have no strokes, so no serve number
    bea = players.loc["Bea B"]
    assert (bea.double_faults, bea.first_serves_in, bea.break_points_faced, bea.break_points_saved) == (1, 21, 6, 0)


def test_second_serve_ace(dataset):
    p = point(dataset, 1)
    assert (p.serve_no, p.ace, p.outcome, p.rally_count, p.serve_direction) == (2, True, "ace", 1, "wide")
    shots = dataset.shots[dataset.shots.point_no == 1]
    assert shots[["serve_no", "shot_no", "ending"]].values.tolist() == [[1, 1, "fault"], [2, 1, "ace"]]
    assert shots.error.iloc[0] == "net" and pd.isna(shots.error.iloc[1])  # None or NaN, by pandas version


def test_double_fault(dataset):
    p = point(dataset, 5)
    assert (p.server, p.double_fault, p.outcome, p.rally_count) == ("Bea B", True, "double_fault", 0)


def test_return_winner(dataset):
    p = point(dataset, 8)
    assert (p.outcome, p.rally_count) == ("winner", 2)
    shots = dataset.shots[dataset.shots.point_no == 8]
    assert shots[["player", "role", "shot_type"]].values.tolist() == [
        ["Bea B", "server", "serve"],
        ["Anna A", "receiver", "groundstroke"],
    ]


@pytest.mark.parametrize("n", [6, 7])
def test_points_without_shots(dataset, n):
    p = point(dataset, n)
    assert not p.shots_recorded and pd.isna(p.outcome) and pd.isna(p.ace)
    assert n not in set(dataset.shots.point_no)


def test_wrong_source_score_is_reported():
    points = raw_points()
    points.loc[9, "Pts"] = "15-15"  # point 10 is really 15-0
    ds = parse(raw_matches().iloc[:1], points, "MS")
    assert ds.matches.loc[MATCH_ID, "score_mismatch_at"] == 10
