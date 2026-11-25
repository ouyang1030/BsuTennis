"""
Serves: one row per serve hit, and how predictable a server's directions are.

Needs a ``shots`` table, i.e. charted matches (:func:`~bsutennis.data.load_charting`).
"""

import numpy as np
import pandas as pd

SERVE_COLUMNS = ["match_id", "point_no", "serve_no", "server", "receiver", "receiver_hand", "side",
                 "direction", "serve_in", "ending", "server_won"]


def serves(dataset) -> pd.DataFrame:
    """
    One row per serve hit, faults included, with the point it belongs to.

    Returns
    -------
    DataFrame
        ``match_id``, ``point_no``, ``serve_no`` (1 or 2), ``server``,
        ``receiver``, ``receiver_hand``, ``side``, ``direction`` ('wide',
        'body' or 'T'), ``serve_in``, ``ending`` (of the serve: 'fault', 'ace',
        'service_winner' or missing if play went on) and ``server_won`` (the
        point, so a first serve that misses can still lead to a point won).
    """
    shots = dataset.shots
    hit = shots.loc[shots.shot_no == 1, ["match_id", "point_no", "serve_no", "direction", "ending"]]
    context = dataset.points[["match_id", "point_no", "server", "receiver", "side", "server_won"]]
    hands = dataset.players[["match_id", "player", "hand"]].rename(columns={"player": "receiver", "hand": "receiver_hand"})
    table = hit.merge(context, on=["match_id", "point_no"]).merge(hands, on=["match_id", "receiver"], how="left")
    return table.assign(serve_in=table.ending.ne("fault"))[SERVE_COLUMNS]


def serve_entropy(serves: pd.DataFrame, by: tuple[str, ...] | list[str] = ("server", "side")) -> pd.DataFrame:
    """
    How predictable the serve direction is, per group of ``serves``.

    Entropy in bits of the shares of serves to each direction: 0 when every
    serve goes the same way, ``log2(3) = 1.58`` when each direction gets a third.

    Returns
    -------
    DataFrame
        ``serves`` (with a known direction) and ``entropy`` per group.
    """
    counts = serves.groupby(list(by)).direction.value_counts().unstack(fill_value=0)
    shares = counts.div(counts.sum(axis=1), axis=0)
    entropy = -(shares * np.log2(shares.where(shares > 0))).sum(axis=1)
    return pd.DataFrame({"serves": counts.sum(axis=1), "entropy": entropy})
