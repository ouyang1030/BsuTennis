"""
Columns every loader derives by replaying a match with :func:`bsutennis.rules.replay`.
Independent of the data source.
"""

from collections.abc import Callable, Sequence

import numpy as np
import pandas as pd

from ..rules import Score


def points_from_replay(
    scores: Sequence[Score],
    winners: Sequence[int],
    players: tuple[str, str],
    mismatch_at: int | None,
) -> pd.DataFrame:
    """
    One row per point: the score before it (server's point of view), the
    point winner, and whether the score is verified against the source.

    ``scores`` is the output of :func:`~bsutennis.rules.replay` (one more than
    the number of points); ``mismatch_at`` the first point where the source
    disagrees, or None.
    """
    points = pd.DataFrame([_score_row(score, players) for score in scores[:-1]])
    points.insert(0, "point_no", np.arange(1, len(winners) + 1))
    points["point_winner"] = [players[w] for w in winners]
    points["server_won"] = points.point_winner == points.server
    verified_until = len(winners) if mismatch_at is None else mismatch_at - 1
    points["score_verified"] = points.point_no <= verified_until
    return points


def summary_from_replay(final: Score, players: tuple[str, str], n_points: int, mismatch_at: int | None) -> dict:
    """The match-level columns that come from the replay. A replay that does not
    reach the end of the match leaves winner and status unknown: the match may
    have been retired, or points may be missing from the source."""
    return {
        "winner": None if final.winner is None else players[final.winner],
        "status": "completed" if final.is_over else None,
        "scoreline": final.scoreline,
        "n_points": n_points,
        "score_mismatch_at": mismatch_at,
    }


def _score_row(s: Score, players: tuple[str, str]) -> dict:
    server, receiver = s.server, s.receiver
    return {
        "set_no": len(s.set_scores) + 1,
        "game_no": sum(s.games) + 1,
        "server": players[server],
        "receiver": players[receiver],
        "server_sets": s.sets[server],
        "receiver_sets": s.sets[receiver],
        "server_games": s.games[server],
        "receiver_games": s.games[receiver],
        "point_score": point_score(s),
        "tiebreak": s.in_tiebreak,
        "side": s.side,
        "break_point": s.is_break_point,
        "set_point": _holder(s, s.is_set_point),
        "match_point": _holder(s, s.is_match_point),
    }


def point_score(s: Score) -> str:
    """Point score with the server first, e.g. ``'30-40'``."""
    return f"{s.point_label(s.server)}-{s.point_label(s.receiver)}"


def _holder(s: Score, has_point: Callable[[int], bool]) -> str | None:
    """Which role, if any, wins the set / match by winning this point.
    Both players can never hold it at once."""
    if has_point(s.server):
        return "server"
    if has_point(s.receiver):
        return "receiver"
    return None
