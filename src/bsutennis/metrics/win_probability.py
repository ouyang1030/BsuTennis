"""
Win probability and importance of every point, from the independent-points
model (:mod:`bsutennis.models.markov`) and the replayed score.
"""

import pandas as pd

from ..models import point_importance, win_probability
from ..rules import MatchFormat, replay


def serve_shares(players: pd.DataFrame) -> pd.DataFrame:
    """
    Share of serve points each player won in each match, indexed by
    ``match_id`` with columns ``player`` and ``serve_points_won``.
    """
    won = players.first_serve_points_won + players.second_serve_points_won
    return players[["match_id", "player"]].assign(serve_points_won=won / players.serve_points).set_index("match_id")


def point_probabilities(dataset, p_serve: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Before every point: player 1's probability of winning the match, and the
    importance of the point (how much that probability moves between winning
    and losing it).

    Parameters
    ----------
    dataset : Dataset
        Matches need a ``match_format`` (point-level sources have one).
    p_serve : DataFrame, optional
        Probability of winning a point on serve, in the shape of
        :func:`serve_shares`. By default the shares each player achieved in the
        match itself, which describes how the match went rather than predicting it.

    Returns
    -------
    DataFrame
        ``match_id``, ``point_no``, ``player1_win_probability``, ``importance``;
        in the order of ``dataset.points``.
    """
    p_serve = serve_shares(dataset.players) if p_serve is None else p_serve
    tables = [
        _match_probabilities(dataset.matches.loc[match_id], points, p_serve.loc[[match_id]])
        for match_id, points in dataset.points.groupby("match_id", sort=False)
    ]
    return pd.concat(tables, ignore_index=True)


def _match_probabilities(info: pd.Series, points: pd.DataFrame, shares: pd.DataFrame) -> pd.DataFrame:
    # Player 1 of the matches table is player 0 of the rules.
    shares = shares.set_index("player").serve_points_won
    p = (shares[info.player1], shares[info.player2])
    winners = (points.point_winner == info.player2).astype(int)
    first_server = 0 if points.server.iloc[0] == info.player1 else 1
    scores = replay(winners, MatchFormat.from_code(info.match_format), first_server)[:-1]
    return pd.DataFrame(
        {
            "match_id": info.name,
            "point_no": points.point_no.to_numpy(),
            "player1_win_probability": [win_probability(s, p) for s in scores],
            "importance": [point_importance(s, p) for s in scores],
        }
    )
