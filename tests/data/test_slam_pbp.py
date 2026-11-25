"""Offline tests of the slam PBP parser on a small hand-made tournament."""

import pandas as pd
import pytest

from bsutennis.data import MATCH_COLUMNS, PLAYER_COLUMNS, POINT_COLUMNS, Dataset
from bsutennis.data.sources.slam_pbp import parse

MATCH_ID = "2023-wimbledon-2101"  # women's singles, first round


def love_match_rows() -> pd.DataFrame:
    """Player 1 wins all 48 points (6-0 6-0); player 2 serves first.

    Rows are written the way the source writes them: score *after* each point,
    flags per player, two placeholder rows at the start. Serve placement
    columns are absent, as in older files.
    """
    rows = [
        {"match_id": MATCH_ID, "SetNo": 1, "PointWinner": 0, "PointServer": 0, "P1Score": "0", "P2Score": "0"},
        {"match_id": MATCH_ID, "SetNo": 1, "PointWinner": 0, "PointServer": 0, "P1Score": "0", "P2Score": "0"},
    ]
    for game in range(12):
        server = 2 if game % 2 == 0 else 1
        for label in ["15", "30", "40", "0"]:
            rows.append({
                "match_id": MATCH_ID, "SetNo": 1 + game // 6,
                "PointWinner": 1, "PointServer": server, "P1Score": label, "P2Score": "0",
                "ServeNumber": 1, "RallyCount": 3, "Speed_KMH": 0,
            })
    raw = pd.DataFrame(rows)
    flags = ["P1Ace", "P2Ace", "P1DoubleFault", "P2DoubleFault", "P1Winner", "P2Winner", "P1UnfErr", "P2UnfErr"]
    raw[flags] = 0

    def point(n):  # row label of point n (the two placeholders come first)
        return n + 1

    raw.loc[point(1), ["P2DoubleFault", "ServeNumber", "RallyCount"]] = [1, 0, 0]
    raw.loc[point(5), ["P1Ace", "P1Winner", "RallyCount", "Speed_KMH"]] = [1, 1, 1, 190]
    raw.loc[point(6), ["P1Winner", "RallyCount"]] = [1, 5]
    raw.loc[point(9), ["P2UnfErr", "RallyCount"]] = [1, 0]
    return raw


RAW_MATCHES = pd.DataFrame({"match_id": [MATCH_ID], "match_num": [2101], "player1": ["Anna"], "player2": ["Bea"]})


@pytest.fixture
def dataset() -> Dataset:
    return parse(RAW_MATCHES, love_match_rows(), "wimbledon", 2023)


def point(ds: Dataset, n: int) -> pd.Series:
    return ds.points.set_index("point_no").loc[n]


def test_tables_follow_the_schema(dataset):
    assert list(dataset.matches.columns) == list(MATCH_COLUMNS)
    assert list(dataset.players.columns) == list(PLAYER_COLUMNS)
    assert list(dataset.points.columns) == list(POINT_COLUMNS)


def test_match_summary(dataset):
    info = dataset.matches.loc[MATCH_ID]
    assert (info.tournament, info.level, info["event"], info["round"], info.best_of) == ("Wimbledon", "G", "WS", "R128", 3)
    assert (info.winner, info.status) == ("Anna", "completed")
    assert info.match_format == "bo3 6/tb7 final 6/tb10"  # women's Wimbledon 2023
    assert info.scoreline == "6-0 6-0"
    assert info.n_points == 48
    assert pd.isna(info.score_mismatch_at)
    assert dataset.points.score_verified.all()


def test_score_columns_are_from_the_servers_view(dataset):
    p = point(dataset, 4)  # Bea serves at 0-40
    assert (p.server, p.receiver, p.point_score) == ("Bea", "Anna", "0-40")
    assert p.break_point and pd.isna(p.set_point)
    assert point(dataset, 24).set_point == "server"   # Anna serves for the first set
    assert pd.isna(point(dataset, 24).match_point)
    assert point(dataset, 48).match_point == "server"


def test_serve_statistics_are_counted_from_the_points(dataset):
    players = dataset.players.set_index("player")
    assert players.loc["Anna", ["opponent", "won"]].tolist() == ["Bea", True]
    anna, bea = players.loc["Anna"], players.loc["Bea"]
    assert (anna.serve_points, anna.service_games, anna.aces, anna.first_serves_in) == (24, 6, 1, 24)
    assert (anna.first_serve_points_won, anna.break_points_faced) == (24, 0)
    assert (bea.serve_points, bea.double_faults, bea.first_serves_in, bea.first_serve_points_won) == (24, 1, 23, 0)
    assert (bea.break_points_faced, bea.break_points_saved) == (6, 0)


def test_point_details(dataset):
    df = point(dataset, 1)
    assert (df.outcome, df.double_fault, df.serve_no, df.rally_count) == ("double_fault", True, 2, 0)
    ace = point(dataset, 5)
    assert (ace.outcome, ace.serve_no, ace.rally_count, ace.serve_speed_kmh) == ("ace", 1, 1, 190)
    assert point(dataset, 6).outcome == "winner"
    error = point(dataset, 9)
    assert error.outcome == "unforced_error" and pd.isna(error.rally_count)  # 0 = not recorded
    assert pd.isna(point(dataset, 2).serve_speed_kmh)                         # 0 = not recorded
    assert dataset.points.serve_width.isna().all()                            # column absent


def test_missing_point_is_reported():
    raw = love_match_rows().drop(index=4)  # drop point 3 (score 40-0)
    ds = parse(RAW_MATCHES, raw, "wimbledon", 2023)
    assert ds.matches.loc[MATCH_ID, "score_mismatch_at"] == 3
    assert ds.points.score_verified.tolist()[:4] == [True, True, False, False]


def test_select_and_concat(dataset):
    both = Dataset.concat([dataset, dataset.match(MATCH_ID)])
    assert (len(both.matches), len(both.players), len(both.points)) == (2, 4, 96)
    assert repr(dataset) == "Dataset(1 matches, 48 points, 0 shots)"
