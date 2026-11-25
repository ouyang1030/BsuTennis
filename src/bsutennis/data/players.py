"""
The players table: one row per player per match.

Every source describes a match in one row with paired columns: ``player1`` /
``player2`` and ``player1_<x>`` / ``player2_<x>``. :func:`players_table` turns
each pair into one column ``<x>`` with two rows per match. For point-level
sources, :func:`serve_stats` counts the serve statistics from the points.
"""

import numpy as np
import pandas as pd

PAIRS = [("player1", "player2"), ("player2", "player1")]


def players_table(paired: pd.DataFrame, stats: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Parameters
    ----------
    paired : DataFrame
        Indexed by ``match_id``, with columns ``player1``, ``player2``,
        ``winner`` and any ``player1_<x>`` / ``player2_<x>`` pairs.
    stats : DataFrame, optional
        Further columns indexed by ``(match_id, player)``, e.g. :func:`serve_stats`.
    """
    sides = []
    for me, other in PAIRS:
        side = paired.filter(regex=f"^{me}_").rename(columns=lambda c: c.removeprefix(f"{me}_"))
        side["player"] = paired[me]
        side["opponent"] = paired[other]
        side["won"] = (paired[me] == paired.winner).astype("boolean").mask(paired.winner.isna())
        sides.append(side)
    # the two rows of a match next to each other, matches in their original order
    order = np.argsort(np.tile(np.arange(len(paired)), 2), kind="stable")
    players = pd.concat(sides).iloc[order].rename_axis("match_id").reset_index()
    if stats is not None:
        players = players.join(stats, on=["match_id", "player"])
    return players


def serve_stats(points: pd.DataFrame) -> pd.DataFrame:
    """
    Serve statistics of each player in each match, indexed by ``(match_id, player)``.

    A point counts towards a statistic only if the columns it needs are recorded
    (e.g. ``serve_no``); the statistic is missing if they are recorded on none of
    the player's serve points.
    """
    won = points.server_won
    first = points.serve_no.eq(1)
    second = points.serve_no.eq(2)
    counts = pd.DataFrame(
        {
            "match_id": points.match_id,
            "player": points.server,
            "aces": points.ace,
            "double_faults": points.double_fault,
            "serve_points": True,
            "first_serves_in": first,
            "first_serve_points_won": first & won,
            "second_serve_points_won": second & won,
            "break_points_faced": points.break_point,
            "break_points_saved": points.break_point & won,
        }
    )
    stats = counts.groupby(["match_id", "player"], sort=False).sum(min_count=1)
    # As in the official statistics, a game counts for whoever served its last
    # point; a tiebreak therefore counts for one of the two players.
    last_points = points.drop_duplicates(["match_id", "set_no", "game_no"], keep="last")
    stats["service_games"] = last_points.groupby(["match_id", "server"]).size()
    return stats.astype("Int64")
