"""
The score of a tennis match as an immutable value.

Players are ``0`` and ``1``. A :class:`Score` describes the match *before* a
point is played; :meth:`Score.win_point` returns the score before the next one.
Only the game server, completed sets, games and points are stored; everything
else (server of the point, tiebreak, court side, break / set / match point) is
derived from them, so a score can never be inconsistent.
"""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from itertools import accumulate

from .formats import MatchFormat, SetFormat

POINT_NAMES = ("0", "15", "30", "40")


def _add(pair: tuple[int, int], player: int) -> tuple[int, int]:
    return (pair[0] + 1, pair[1]) if player == 0 else (pair[0], pair[1] + 1)


@dataclass(frozen=True)
class Score:
    match_format: MatchFormat
    game_server: int
    """Player serving the current game (in a tiebreak: the player who serves first)."""
    set_scores: tuple[tuple[int, int], ...] = ()
    """Games of each completed set, e.g. ``((6, 1), (6, 7))``."""
    games: tuple[int, int] = (0, 0)
    points: tuple[int, int] = (0, 0)

    # --- where we are ----------------------------------------------------

    @property
    def sets(self) -> tuple[int, int]:
        won_by_0 = sum(a > b for a, b in self.set_scores)
        return won_by_0, len(self.set_scores) - won_by_0

    @property
    def set_format(self) -> SetFormat:
        return self.match_format.set_format(len(self.set_scores))

    @property
    def in_tiebreak(self) -> bool:
        tiebreak_at = self.set_format.tiebreak_at
        return tiebreak_at is not None and self.games == (tiebreak_at, tiebreak_at)

    @property
    def server(self) -> int:
        """Player serving this point. In a tiebreak service changes after the
        first point and then every two points."""
        if not self.in_tiebreak:
            return self.game_server
        turn = (sum(self.points) + 1) // 2
        return self.game_server if turn % 2 == 0 else 1 - self.game_server

    @property
    def receiver(self) -> int:
        return 1 - self.server

    @property
    def side(self) -> str:
        """Court the serve is hit to: ``'deuce'`` after an even number of points."""
        return "deuce" if sum(self.points) % 2 == 0 else "ad"

    @property
    def is_over(self) -> bool:
        return max(self.sets) == self.match_format.sets_to_win

    @property
    def winner(self) -> int | None:
        if not self.is_over:
            return None
        return 0 if self.sets[0] > self.sets[1] else 1

    # --- what the next point decides ---------------------------------------

    def is_game_point(self, player: int) -> bool:
        """Winning this point wins ``player`` the current game (or tiebreak)."""
        return self._wins_game(_add(self.points, player), player)

    def is_set_point(self, player: int) -> bool:
        return self.is_game_point(player) and self._wins_set(_add(self.games, player), player)

    def is_match_point(self, player: int) -> bool:
        return self.is_set_point(player) and self.sets[player] + 1 == self.match_format.sets_to_win

    @property
    def is_break_point(self) -> bool:
        return not self.in_tiebreak and self.is_game_point(self.receiver)

    # --- playing a point ---------------------------------------------------

    def win_point(self, player: int) -> "Score":
        points = _add(self.points, player)
        if not self._wins_game(points, player):
            return replace(self, points=points)

        games = _add(self.games, player)
        next_server = 1 - self.game_server
        if not self._wins_set(games, player):
            return replace(self, games=games, points=(0, 0), game_server=next_server)

        return replace(
            self,
            set_scores=self.set_scores + (games,),
            games=(0, 0),
            points=(0, 0),
            game_server=next_server,
        )

    def _wins_game(self, points: tuple[int, int], player: int) -> bool:
        mine, theirs = points[player], points[1 - player]
        if self.in_tiebreak:
            return mine >= self.set_format.tiebreak_points and mine - theirs >= 2
        if self.match_format.no_ad:
            return mine >= 4
        return mine >= 4 and mine - theirs >= 2

    def _wins_set(self, games: tuple[int, int], player: int) -> bool:
        if self.in_tiebreak:
            return True
        mine, theirs = games[player], games[1 - player]
        return mine >= self.set_format.games and mine - theirs >= 2

    # --- display -----------------------------------------------------------

    def point_label(self, player: int) -> str:
        """``player``'s point score as written on a scoreboard: 0/15/30/40/AD,
        or the plain count in a tiebreak."""
        mine, theirs = self.points[player], self.points[1 - player]
        if self.in_tiebreak:
            return str(mine)
        if mine >= 3 and theirs >= 3:
            return "AD" if mine > theirs else "40"
        return POINT_NAMES[mine]

    @property
    def scoreline(self) -> str:
        """Games of each set, player 0 first, e.g. ``'1-6 7-6 6-1 3-6 6-4'``.
        While the match is on, the current set is included."""
        sets = self.set_scores if self.is_over else (*self.set_scores, self.games)
        return " ".join(f"{a}-{b}" for a, b in sets)

    def __str__(self) -> str:
        return f"{self.scoreline} {self.point_label(0)}-{self.point_label(1)}"


def replay(point_winners: Iterable[int], match_format: MatchFormat, first_server: int) -> list[Score]:
    """
    Replay a match from the sequence of point winners.

    Returns ``n + 1`` scores for ``n`` points: ``scores[i]`` is the score before
    point ``i`` and ``scores[-1]`` the score after the last point.
    """
    start = Score(match_format=match_format, game_server=first_server)
    return list(accumulate(point_winners, Score.win_point, initial=start))
