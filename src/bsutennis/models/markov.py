"""
Win probabilities under the independent-points model.

Each player wins a fixed share of the points they serve, ``p_serve[0]`` and
``p_serve[1]``, whatever the score (Barnett & Clarke 2005; Newton & Keller
2005; O'Malley 2008). The probability of winning the match from any score then
follows from the scoring rules alone. The rules are those of
:class:`~bsutennis.rules.Score`, so every format it plays (tiebreak and
advantage sets, match tiebreaks, no-ad games) is covered.

Some situations can repeat without end: deuce, a tie late in a tiebreak, a
tie late in an advantage set. From such a tie the next two points (or games)
decide unless they are split, which leads to an equivalent tie. With ``u`` and
``v`` the chances of winning both and losing both,

    P(tie) = (u · P(after winning both) + v · P(after losing both)) / (u + v).
"""

from functools import lru_cache

from ..rules import MatchFormat, Score


def win_probability(score: Score, p_serve: tuple[float, float]) -> float:
    """
    Probability that player 0 wins the match from ``score``.

    Parameters
    ----------
    score : Score
    p_serve : (float, float)
        Probability that player 0, and player 1, wins a point on their own serve.

    Examples
    --------
    >>> from bsutennis.rules import MatchFormat, Score
    >>> start = Score(MatchFormat(best_of=5), game_server=0)
    >>> round(win_probability(start, (0.65, 0.62)), 3)
    0.681
    """
    return _model(score.match_format, tuple(p_serve)).match(score)


def point_importance(score: Score, p_serve: tuple[float, float]) -> float:
    """
    How much the next point matters: player 0's chance of winning the match
    after winning it minus after losing it (Morris 1977). The same for both
    players, between 0 and 1.
    """
    return win_probability(score.win_point(0), p_serve) - win_probability(score.win_point(1), p_serve)


def hold_probability(p: float, no_ad: bool = False) -> float:
    """Probability that the server wins a game, winning each point with probability ``p``."""
    start = Score(MatchFormat(no_ad=no_ad), game_server=0)
    return _model(start.match_format, (p, p)).unit(start)


@lru_cache(maxsize=256)
def _model(match_format: MatchFormat, p_serve: tuple[float, float]) -> "_Model":
    return _Model(p_serve)


class _Model:
    """Memoised probabilities for one match format and one pair of serve probabilities.

    A *unit* is a game or a tiebreak: the stretch of points between two
    changes of the games score.
    """

    def __init__(self, p_serve: tuple[float, float]):
        self.p_serve = p_serve
        self._units: dict = {}
        self._matches: dict = {}

    def point(self, s: Score) -> float:
        """P(player 0 wins the next point)."""
        return self.p_serve[0] if s.server == 0 else 1 - self.p_serve[1]

    # --- within a unit ----------------------------------------------------------

    def unit(self, s: Score) -> float:
        """P(player 0 wins the game or tiebreak in progress)."""
        key = (s.points, s.game_server, s.in_tiebreak, s.set_format.tiebreak_points)
        if key not in self._units:
            self._units[key] = self._unit(s)
        return self._units[key]

    def _unit(self, s: Score) -> float:
        if _point_tie(s):
            first, second = self.point(s), self.point(s.win_point(0))
            return _decide(first * second, (1 - first) * (1 - second), 1.0, 0.0)
        p = self.point(s)
        return p * self._after_point(s.win_point(0), 0) + (1 - p) * self._after_point(s.win_point(1), 1)

    def _after_point(self, s: Score, winner: int) -> float:
        if s.points == (0, 0):  # the point ended the unit
            return 1.0 if winner == 0 else 0.0
        return self.unit(s)

    # --- the match ---------------------------------------------------------------

    def match(self, s: Score) -> float:
        """P(player 0 wins the match)."""
        if s.is_over:
            return 1.0 if s.winner == 0 else 0.0
        if s.points != (0, 0):
            return self._by_unit(s)
        key = (s.sets, s.games, s.game_server)
        if key not in self._matches:
            self._matches[key] = self._match_at_unit_start(s)
        return self._matches[key]

    def _match_at_unit_start(self, s: Score) -> float:
        if not _game_tie(s):
            return self._by_unit(s)
        first = self.unit(s)
        second = self.unit(_finish_unit(s, 0))  # the other player serves the next game
        return _decide(
            first * second,
            (1 - first) * (1 - second),
            self.match(_finish_unit(_finish_unit(s, 0), 0)),
            self.match(_finish_unit(_finish_unit(s, 1), 1)),
        )

    def _by_unit(self, s: Score) -> float:
        q = self.unit(s)
        return q * self.match(_finish_unit(s, 0)) + (1 - q) * self.match(_finish_unit(s, 1))


def _point_tie(s: Score) -> bool:
    """Deuce, or a tie late in a tiebreak: the next two points decide unless split."""
    a, b = s.points
    if a != b:
        return False
    if s.in_tiebreak:
        return a >= s.set_format.tiebreak_points - 1
    return not s.match_format.no_ad and a >= 3


def _game_tie(s: Score) -> bool:
    """A tie late in an advantage set: the next two games decide unless split."""
    a, b = s.games
    return s.set_format.tiebreak_at is None and a == b and a >= s.set_format.games - 1


def _decide(u: float, v: float, after_winning_both: float, after_losing_both: float) -> float:
    return (u * after_winning_both + v * after_losing_both) / (u + v)


def _finish_unit(s: Score, winner: int) -> Score:
    """The score after ``winner`` takes the game or tiebreak in progress."""
    while True:
        s = s.win_point(winner)
        if s.points == (0, 0):
            return s
