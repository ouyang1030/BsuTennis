"""
Match Charting Project (MCP): crowd-sourced shot-by-shot charts of
professional singles matches, run by Jeff Sackmann.

Every stroke of every point is recorded in a compact notation (see
:mod:`.mcp_notation`), which gives the ``shots`` table. The repository
(github.com/JeffSackmann/tennis_MatchChartingProject) is read at one pinned
commit, so every analysis sees exactly the same data. Set ``BSUTENNIS_MCP_URL``
to read the same files from another copy at that commit.

Data license: CC BY-NC-SA 4.0 (attribution, non-commercial, share-alike).
"""

import os
import warnings
from pathlib import Path

import pandas as pd

from ...rules import ADVANTAGE_SET, MATCH_TIEBREAK, TEN_POINT_TIEBREAK_SET, MatchFormat, Score, SetFormat, replay
from ..cache import fetch, parsed
from ..dataset import Dataset
from ..players import players_table, serve_stats
from ..replayed import point_score, points_from_replay, summary_from_replay
from .mcp_notation import Stroke, parse_point

REPOSITORY = "https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject"
COMMIT = "1813a1309b7ed7ebf1c7e884b32bf675d00e4edf"  # September 2026

PERIODS = ("to-2009", "2010s", "2020s")
POINT_SOURCE_COLUMNS = ["match_id", "Pt", "Svr", "PtWinner", "Set1", "Set2", "Gm1", "Gm2", "Pts", "1st", "2nd"]
FILE_PREFIXES = {"atp": "m", "wta": "w"}
EVENTS = {"atp": "MS", "wta": "WS"}

NEXT_GEN_SET = SetFormat(games=4, tiebreak_at=3)
SET_RULES = {  # 'Final TB?' code: (regular sets, final set, no-ad scoring)
    "1": (SetFormat(), SetFormat(), False),
    "0": (SetFormat(), ADVANTAGE_SET, False),
    "A": (SetFormat(), TEN_POINT_TIEBREAK_SET, False),
    "T": (SetFormat(), SetFormat(tiebreak_at=12), False),
    "S": (SetFormat(), MATCH_TIEBREAK, False),
    "V": (ADVANTAGE_SET, ADVANTAGE_SET, False),
    "W": (SetFormat(tiebreak_at=8), SetFormat(tiebreak_at=8), False),
    "N": (NEXT_GEN_SET, NEXT_GEN_SET, True),
}


def load_charting(tour: str, period: str) -> Dataset:
    """
    Load the charted matches of one tour and period.

    Parameters
    ----------
    tour : {'atp', 'wta'}
        Men's or women's matches, at any level (tour, challenger, ITF, juniors, ...).
    period : {'to-2009', '2010s', '2020s'}
        The source splits the points by decade of the match.

    Examples
    --------
    >>> charted = load_charting("atp", "2020s")
    >>> charted.shots.query("shot_no == 3").wing.value_counts()   # serve +1 forehands
    """
    return parsed(f"mcp-{COMMIT[:7]}-{tour}-{period}", lambda: _load(tour, period))


def _load(tour: str, period: str) -> Dataset:
    prefix = FILE_PREFIXES[tour]
    raw_matches = pd.read_csv(_download(f"charting-{prefix}-matches.csv"), dtype=str, keep_default_na=False)
    raw_points = pd.read_csv(
        _download(f"charting-{prefix}-points-{period}.csv"),
        usecols=POINT_SOURCE_COLUMNS,
        dtype=str,
        keep_default_na=False,
    )
    return parse(raw_matches, raw_points, EVENTS[tour])


def _download(filename: str) -> Path:
    base = os.environ.get("BSUTENNIS_MCP_URL", f"{REPOSITORY}/{COMMIT}")
    return fetch(f"{base}/{filename}", f"mcp/{COMMIT[:7]}/{filename}")


def parse(raw_matches: pd.DataFrame, raw_points: pd.DataFrame, event: str) -> Dataset:
    """Convert the source tables into a :class:`Dataset`.

    Matches whose format cannot be read from the matches file are skipped with a warning.
    """
    raw_matches = raw_matches.apply(lambda column: column.str.strip())
    usable = raw_matches["Best of"].isin(["3", "5"]) & raw_matches["Final TB?"].isin(list(SET_RULES))
    matches = _match_info(raw_matches[usable], event)

    raw_points = _typed_points(raw_points)
    charted = raw_points.match_id.isin(matches.index)
    if not charted.all():
        skipped = raw_points.match_id[~charted].nunique()
        warnings.warn(f"skipped {skipped} matches whose format is missing from the matches file", stacklevel=3)

    point_tables, shot_tables, summaries = [], [], []
    for match_id, rows in raw_points[charted].groupby("match_id", sort=False):
        points, shots, summary = _parse_match(rows, matches.loc[match_id])
        point_tables.append(points)
        shot_tables.append(shots)
        summaries.append(summary)

    summaries = pd.DataFrame(summaries).set_index("match_id").astype({"score_mismatch_at": "Int64"})
    matches = matches.loc[summaries.index].join(summaries)
    points = pd.concat(point_tables, ignore_index=True)
    return Dataset.from_tables(
        matches=matches,
        players=players_table(matches, serve_stats(points)),
        points=points,
        shots=pd.concat(shot_tables, ignore_index=True),
    )


def _match_format(final_tb: str, best_of: int) -> MatchFormat:
    regular, final, no_ad = SET_RULES[final_tb]
    return MatchFormat(best_of=best_of, regular_set=regular, final_set=final, no_ad=no_ad)


def _match_info(raw: pd.DataFrame, event: str) -> pd.DataFrame:
    date = pd.to_datetime(raw.Date, format="%Y%m%d")
    best_of = raw["Best of"].astype(int)
    return pd.DataFrame(
        {
            "tournament": raw.Tournament,
            "year": date.dt.year,
            "date": date,
            "event": event,
            "round": raw.Round,
            "surface": raw.Surface.str.lower(),
            "player1": raw["Player 1"],   # player 1 always serves first
            "player2": raw["Player 2"],
            "player1_hand": raw["Pl 1 hand"],
            "player2_hand": raw["Pl 2 hand"],
            "best_of": best_of,
            "match_format": [_match_format(code, n).code for code, n in zip(raw["Final TB?"], best_of)],
        }
    ).set_index(raw.match_id)


def _typed_points(raw: pd.DataFrame) -> pd.DataFrame:
    """Columns used, with numeric types. The set and game counts only serve to
    check the replay, so a malformed cell becomes missing (and fails the check)."""
    points = raw[POINT_SOURCE_COLUMNS].rename(columns={"1st": "first", "2nd": "second"})
    points = points.astype({"Pt": int, "Svr": int, "PtWinner": int})
    for column in ["Set1", "Set2", "Gm1", "Gm2"]:
        points[column] = pd.to_numeric(points[column], errors="coerce")
    return points.sort_values(["match_id", "Pt"], kind="stable")


def _parse_match(rows: pd.DataFrame, info: pd.Series):
    # The source numbers the players 1 and 2; rules number them 0 and 1.
    # Player 1 always serves first.
    players = (info.player1, info.player2)
    winners = (rows.PtWinner - 1).to_list()
    scores = replay(winners, MatchFormat.from_code(info.match_format), first_server=0)
    mismatch_at = _first_mismatch(scores, rows)

    details, shots = [], []
    for point_no, (score, first, second) in enumerate(zip(scores, rows["first"], rows["second"]), start=1):
        serves = parse_point(first, second)
        details.append(_point_detail(serves))
        shots.extend(_shot_rows(serves or [], point_no, score.server, players))

    points = pd.concat([points_from_replay(scores, winners, players, mismatch_at), _detail_table(details)], axis=1)
    points["match_id"] = info.name
    shots = pd.DataFrame(shots).assign(match_id=info.name)
    summary = {"match_id": info.name, **summary_from_replay(scores[-1], players, len(rows), mismatch_at)}
    return points, shots, summary


def _first_mismatch(scores: list[Score], rows: pd.DataFrame) -> int | None:
    """
    First point (from 1) at which the replay disagrees with the source on the
    server, sets, games or point score. The source writes the score *before*
    each point, sets and games player 1 first, points server first.
    """
    for point_no, (score, row) in enumerate(zip(scores, rows.itertuples()), start=1):
        agrees = (
            score.server == row.Svr - 1
            and score.sets == (row.Set1, row.Set2)
            and score.games == (row.Gm1, row.Gm2)
            and point_score(score) == row.Pts
        )
        if not agrees:
            return point_no
    return None


# --- point details and shots --------------------------------------------------

UNKNOWN_DETAIL = {
    "serve_no": None, "serve_direction": None, "ace": None, "double_fault": None,
    "outcome": None, "rally_count": None, "shots_recorded": False,
}
ERROR_ENDINGS = ("forced_error", "unforced_error")


def _point_detail(serves: list[list[Stroke]] | None) -> dict:
    """Point-level columns from the strokes; unknown if the point has no strokes
    (recorded without shots, or a code that does not follow the notation)."""
    if not serves:
        return UNKNOWN_DETAIL
    rally = serves[-1]
    last = rally[-1]
    double_fault = len(serves) == 2 and last.ending == "fault"
    errors = 1 if last.ending in ERROR_ENDINGS else 0
    return {
        "serve_no": len(serves),
        "serve_direction": rally[0].direction,
        "ace": last.ending == "ace",
        "double_fault": double_fault,
        "outcome": "double_fault" if double_fault else last.ending,
        "rally_count": 0 if double_fault else len(rally) - errors,
        "shots_recorded": True,
    }


def _detail_table(details: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(details).astype(
        {"serve_no": "Int64", "ace": "boolean", "double_fault": "boolean", "rally_count": "Int64"}
    )


def _shot_rows(serves: list[list[Stroke]], point_no: int, server: int, players: tuple[str, str]) -> list[dict]:
    rows = []
    for serve_no, strokes in enumerate(serves, start=1):
        for shot_no, stroke in enumerate(strokes, start=1):
            hitter = server if shot_no % 2 == 1 else 1 - server
            rows.append({
                "point_no": point_no,
                "serve_no": serve_no,
                "shot_no": shot_no,
                "player": players[hitter],
                "role": "server" if hitter == server else "receiver",
                **vars(stroke),
            })
    return rows
