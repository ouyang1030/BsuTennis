"""
Serve and return percentages from the ``players`` table.

Percentages over several matches are *pooled*: the counts are summed first
and divided afterwards, so a five-set match weighs more than a retirement
after three games.
"""

import pandas as pd

SERVE_COUNTS = [
    "aces", "double_faults", "serve_points", "first_serves_in", "first_serve_points_won",
    "second_serve_points_won", "break_points_faced", "break_points_saved",
]


def serve_return(players: pd.DataFrame, by: str | list[str] = "player") -> pd.DataFrame:
    """
    Serve and return percentages of each group of rows of ``players``.

    Rows without serve statistics (for the player or the opponent) are left out.
    To group by a match column, join it first::

        players.join(dataset.matches[["surface"]], on="match_id")

    Returns
    -------
    DataFrame
        One row per group: ``matches``, ``serve_points``, ``return_points`` and the
        shares ``first_serve_in``, ``first_serve_won``, ``second_serve_won``,
        ``serve_points_won``, ``return_points_won``, ``points_won``, ``ace_rate``,
        ``double_fault_rate``, ``break_points_saved``, ``break_points_converted``,
        plus the ``dominance_ratio`` (return points won / serve points lost).
    """
    rows = _with_opponent_counts(players).dropna(subset=["serve_points", "opp_serve_points"])
    totals = rows.groupby(by)[SERVE_COUNTS + [f"opp_{c}" for c in SERVE_COUNTS]].sum()
    serve_won = totals.first_serve_points_won + totals.second_serve_points_won
    return_won = totals.opp_serve_points - totals.opp_first_serve_points_won - totals.opp_second_serve_points_won
    return pd.DataFrame(
        {
            "matches": rows.groupby(by).size(),
            "serve_points": totals.serve_points,
            "return_points": totals.opp_serve_points,
            "first_serve_in": totals.first_serves_in / totals.serve_points,
            "first_serve_won": totals.first_serve_points_won / totals.first_serves_in,
            "second_serve_won": totals.second_serve_points_won / (totals.serve_points - totals.first_serves_in),
            "serve_points_won": serve_won / totals.serve_points,
            "return_points_won": return_won / totals.opp_serve_points,
            "points_won": (serve_won + return_won) / (totals.serve_points + totals.opp_serve_points),
            "ace_rate": totals.aces / totals.serve_points,
            "double_fault_rate": totals.double_faults / totals.serve_points,
            "break_points_saved": totals.break_points_saved / totals.break_points_faced,
            "break_points_converted": 1 - totals.opp_break_points_saved / totals.opp_break_points_faced,
            "dominance_ratio": (return_won / totals.opp_serve_points) / (1 - serve_won / totals.serve_points),
        }
    ).astype(float)


def _with_opponent_counts(players: pd.DataFrame) -> pd.DataFrame:
    """Each row with the opponent's serve counts as ``opp_<count>``."""
    opponent = players[["match_id", "player", *SERVE_COUNTS]].rename(
        columns={"player": "opponent", **{c: f"opp_{c}" for c in SERVE_COUNTS}}
    )
    return players.merge(opponent, on=["match_id", "opponent"], how="left")
