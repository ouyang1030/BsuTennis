"""
Grand Slam point-by-point data, collected by Jeff Sackmann.

Coverage: Wimbledon and US Open 2011-2024 (no Wimbledon 2020), Australian Open
and Roland Garros 2011-2021. Older files do not record serve number, rally
length or serve placement; those columns are then missing. There is no
shot-level data, so ``Dataset.shots`` is empty.

The original repository (github.com/JeffSackmann/tennis_slam_pointbypoint) was
withdrawn in 2026; files are read from an archival mirror (see :mod:`.archive`).

Data license: CC BY-NC-SA 4.0 (attribution, non-commercial, share-alike).
"""

import numpy as np
import pandas as pd

from ...rules import MatchFormat, Score, grand_slam, replay
from ..cache import parsed
from ..dataset import Dataset
from ..players import players_table, serve_stats
from ..replayed import points_from_replay, summary_from_replay
from .archive import COMMIT, download

NAMES = {"ausopen": "Australian Open", "frenchopen": "Roland Garros", "wimbledon": "Wimbledon", "usopen": "US Open"}
SURFACES = {"ausopen": "hard", "frenchopen": "clay", "wimbledon": "grass", "usopen": "hard"}

# match_num is EGNN: E event (1 men, 2 women), G round, NN match in round
EVENTS = {1: "MS", 2: "WS"}
BEST_OF = {1: 5, 2: 3}
ROUNDS = {1: "R128", 2: "R64", 3: "R32", 4: "R16", 5: "QF", 6: "SF", 7: "F"}

# Five serve lanes coarsened to the standard three: the three body lanes are 'body'.
SERVE_DIRECTIONS = {"W": "wide", "BW": "body", "B": "body", "BC": "body", "C": "T"}

# Source columns used. Older files lack some of them; they are read as missing.
SOURCE_COLUMNS = [
    "match_id", "SetNo", "PointWinner", "PointServer", "P1Score", "P2Score",
    "ServeNumber", "RallyCount", "Speed_KMH", "ServeWidth", "ServeDepth", "ReturnDepth",
    "P1Ace", "P2Ace", "P1DoubleFault", "P2DoubleFault",
    "P1Winner", "P2Winner", "P1UnfErr", "P2UnfErr",
]


def load_slam(year: int, slam: str) -> Dataset:
    """
    Load all singles matches of one Grand Slam.

    Parameters
    ----------
    year : int
    slam : {'ausopen', 'frenchopen', 'wimbledon', 'usopen'}

    Examples
    --------
    >>> wimbledon = load_slam(2023, "wimbledon")
    >>> final = wimbledon.match("2023-wimbledon-1701")
    """
    return parsed(f"slam-{COMMIT[:7]}-{year}-{slam}", lambda: _load(year, slam))


def _load(year: int, slam: str) -> Dataset:
    raw_matches = pd.read_csv(download(f"slam_pointbypoint/{year}-{slam}-matches.csv"))
    raw_points = pd.read_csv(
        download(f"slam_pointbypoint/{year}-{slam}-points.csv"),
        dtype={"P1Score": str, "P2Score": str},
        low_memory=False,
    )
    return parse(raw_matches, raw_points, slam, year)


def parse(raw_matches: pd.DataFrame, raw_points: pd.DataFrame, slam: str, year: int) -> Dataset:
    """Convert the two source tables of one tournament into a :class:`Dataset`."""
    matches = _match_info(raw_matches, slam, year)
    raw_points = raw_points.reindex(columns=SOURCE_COLUMNS)
    raw_points = raw_points[raw_points.PointWinner != 0]  # '0X' / '0Y' placeholder rows

    point_tables, summaries = [], []
    for match_id, rows in raw_points.groupby("match_id", sort=False):
        points, summary = _parse_match(rows, matches.loc[match_id])
        point_tables.append(points)
        summaries.append(summary)

    summaries = pd.DataFrame(summaries).set_index("match_id").astype({"score_mismatch_at": "Int64"})
    matches = matches.join(summaries)
    points = pd.concat(point_tables, ignore_index=True)
    return Dataset.from_tables(
        matches=matches,
        players=players_table(matches, serve_stats(points)),
        points=points,
    )


def _match_info(raw_matches: pd.DataFrame, slam: str, year: int) -> pd.DataFrame:
    event = raw_matches.match_num // 1000
    best_of = event.map(BEST_OF)
    return pd.DataFrame(
        {
            "tournament": NAMES[slam],
            "level": "G",
            "year": year,
            "event": event.map(EVENTS),
            "round": (raw_matches.match_num // 100 % 10).map(ROUNDS),
            "surface": SURFACES[slam],
            "player1": raw_matches.player1,
            "player2": raw_matches.player2,
            "best_of": best_of,
            "match_format": [grand_slam(slam, year, n).code for n in best_of],
        }
    ).set_index(raw_matches.match_id)


def _parse_match(rows: pd.DataFrame, info: pd.Series) -> tuple[pd.DataFrame, dict]:
    # The source numbers the players 1 and 2; rules number them 0 and 1.
    players = (info.player1, info.player2)
    winners = (rows.PointWinner - 1).to_list()
    first_server = rows.PointServer.iloc[0] - 1
    scores = replay(winners, MatchFormat.from_code(info.match_format), first_server)
    mismatch_at = _first_mismatch(scores, rows)

    points = pd.concat(
        [points_from_replay(scores, winners, players, mismatch_at), _point_details(rows)],
        axis=1,
    )
    points["match_id"] = info.name
    summary = {"match_id": info.name, **summary_from_replay(scores[-1], players, len(rows), mismatch_at)}
    return points, summary


def _first_mismatch(scores: list[Score], rows: pd.DataFrame) -> int | None:
    """
    First point (from 1) at which the replay disagrees with the source on the
    server, the set number, or the point score after the point.

    The source writes the score *after* each point. The score after the last
    point is not compared: some files do not reset it after match point. Game
    numbers are not compared: some files count games per set, others per match.
    """
    pairs = zip(scores, scores[1:-1], rows.itertuples())
    for point_no, (before, after, row) in enumerate(pairs, start=1):
        agrees = (
            before.server == row.PointServer - 1
            and len(before.set_scores) + 1 == row.SetNo
            and (after.point_label(0), after.point_label(1)) == (row.P1Score, row.P2Score)
        )
        if not agrees:
            return point_no
    return None


def _point_details(rows: pd.DataFrame) -> pd.DataFrame:
    server, winner = rows.PointServer, rows.PointWinner
    ace = _flag(rows, "Ace", server)
    double_fault = _flag(rows, "DoubleFault", server)
    outcome = np.select(
        [double_fault, ace, _flag(rows, "Winner", winner), _flag(rows, "UnfErr", 3 - winner)],
        ["double_fault", "ace", "winner", "unforced_error"],
        default=None,
    )
    details = pd.DataFrame(
        {
            "serve_no": rows.ServeNumber.replace({0: 2}).astype("Int64"),  # 0 marks a double fault
            "serve_direction": rows.ServeWidth.map(SERVE_DIRECTIONS),
            "ace": ace,
            "double_fault": double_fault,
            "outcome": outcome,
            # 0 means "not recorded", except on a double fault
            "rally_count": rows.RallyCount.where((rows.RallyCount > 0) | double_fault).astype("Int64"),
            "shots_recorded": False,
            "serve_speed_kmh": rows.Speed_KMH.where(rows.Speed_KMH > 0),  # 0 means "not recorded"
            "serve_width": rows.ServeWidth,
            "serve_depth": rows.ServeDepth,
            "return_depth": rows.ReturnDepth,
        }
    )
    return details.reset_index(drop=True)


def _flag(rows: pd.DataFrame, name: str, player: pd.Series) -> np.ndarray:
    """The ``P1<name>`` / ``P2<name>`` flag of ``player`` (1 or 2) on each point."""
    return rows[f"P1{name}"].where(player == 1, rows[f"P2{name}"]).eq(1).to_numpy()
