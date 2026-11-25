"""Elo ratings over the ``matches`` table."""

import pandas as pd

from ..models import Elo

# Order of the rounds within a tournament.
ROUNDS = ["Q1", "Q2", "Q3", "Q4", "ER", "R128", "R64", "R32", "R16", "RR", "QF", "SF", "BR", "F"]


def elo(matches: pd.DataFrame, by: str | None = None, initial: float = 1500.0) -> pd.DataFrame:
    """
    Elo ratings of both players before and after every match.

    Matches are rated in the order they were played: by season, tournament date
    (or match date) and round. Walkovers and matches without a known winner are
    left out.

    Parameters
    ----------
    matches : DataFrame
        The ``matches`` table, usually of many seasons of results combined.
    by : str, optional
        A column whose values get separate ratings, e.g. ``'surface'``.
        Matches with no value in it are left out.
    initial : float
        Rating of a player's first match.

    Returns
    -------
    DataFrame
        One row per player per match, like the ``players`` table, in the order
        the matches were rated: ``match_id``, ``player``, ``opponent``, ``elo``
        (before the match), ``elo_after`` and ``win_probability`` (the player's
        chance before the match).

    Examples
    --------
    Current ratings: ``ratings.groupby("player").elo_after.last()``.
    """
    played = matches[matches.winner.notna() & (matches.status != "walkover")]
    if by is not None:
        played = played[played[by].notna()]
    order = pd.DataFrame({
        "year": played.year,
        "start": played.tournament_date.fillna(played.date),
        "round": played["round"].map({name: i for i, name in enumerate(ROUNDS)}),
    })
    played = played.loc[order.sort_values(["year", "start", "round"], kind="stable").index]

    systems: dict = {}
    rows = []
    for match in played.itertuples():
        system = systems.setdefault(None if by is None else getattr(match, by), Elo(initial))
        players = (match.player1, match.player2)
        before = [system.rating(player) for player in players]
        loser = match.player2 if match.winner == match.player1 else match.player1
        expected = system.play(match.winner, loser)
        p1 = expected if match.winner == match.player1 else 1 - expected
        for player, opponent, rating, p in zip(players, players[::-1], before, (p1, 1 - p1)):
            rows.append((match.Index, player, opponent, rating, system.rating(player), p))
    return pd.DataFrame(rows, columns=["match_id", "player", "opponent", "elo", "elo_after", "win_probability"])
