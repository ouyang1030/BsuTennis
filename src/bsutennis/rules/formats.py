"""
Match formats: how many sets, how a set is won, how tiebreaks work.

A tiebreak is played when both players reach ``tiebreak_at`` games in a set.
Two special cases fall out of the same definition:

- ``tiebreak_at=None`` is an advantage set (play on until a two-game lead);
- ``tiebreak_at=0`` is a match tiebreak (the "set" is a single tiebreak).

Formats have a short code, used in the ``match_format`` column of the data
tables: ``'bo5 6/tb7 final 6/tb10'`` is best of five sets, sets of six games
with a 7-point tiebreak at 6-6, and a 10-point tiebreak in the final set.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SetFormat:
    games: int = 6
    tiebreak_at: int | None = 6
    tiebreak_points: int = 7

    @property
    def code(self) -> str:
        """``'6/tb7'`` (7-point tiebreak at 6-6), ``'6/tb7@12'`` (at 12-12),
        ``'6/adv'`` (advantage set) or ``'mtb10'`` (10-point match tiebreak)."""
        if self.tiebreak_at is None:
            return f"{self.games}/adv"
        if self.tiebreak_at == 0:
            return f"mtb{self.tiebreak_points}"
        at = "" if self.tiebreak_at == self.games else f"@{self.tiebreak_at}"
        return f"{self.games}/tb{self.tiebreak_points}{at}"

    @classmethod
    def from_code(cls, code: str) -> "SetFormat":
        if match := re.fullmatch(r"mtb(\d+)", code):
            return cls(tiebreak_at=0, tiebreak_points=int(match[1]))
        match = re.fullmatch(r"(\d+)/(?:adv|tb(\d+)(?:@(\d+))?)", code)
        games = int(match[1])
        if match[2] is None:
            return cls(games=games, tiebreak_at=None)
        return cls(games=games, tiebreak_at=int(match[3] or games), tiebreak_points=int(match[2]))


@dataclass(frozen=True)
class MatchFormat:
    best_of: int = 3
    regular_set: SetFormat = SetFormat()
    final_set: SetFormat = SetFormat()
    no_ad: bool = False

    @property
    def sets_to_win(self) -> int:
        return self.best_of // 2 + 1

    def set_format(self, sets_played: int) -> SetFormat:
        """Format of the set that starts after ``sets_played`` completed sets."""
        if sets_played == self.best_of - 1:
            return self.final_set
        return self.regular_set

    @property
    def code(self) -> str:
        """e.g. ``'bo3 6/tb7'``, ``'bo5 6/tb7 final 6/adv'``, ``'bo3 6/tb7 final mtb10'``,
        ``'bo5 4/tb7@3 no-ad'``; the final set is named only when it differs."""
        words = [f"bo{self.best_of}", self.regular_set.code]
        if self.final_set != self.regular_set:
            words += ["final", self.final_set.code]
        if self.no_ad:
            words.append("no-ad")
        return " ".join(words)

    @classmethod
    def from_code(cls, code: str) -> "MatchFormat":
        words = code.split()
        regular = SetFormat.from_code(words[1])
        final = SetFormat.from_code(words[words.index("final") + 1]) if "final" in words else regular
        return cls(best_of=int(words[0].removeprefix("bo")), regular_set=regular, final_set=final,
                   no_ad="no-ad" in words)


ADVANTAGE_SET = SetFormat(tiebreak_at=None)
TEN_POINT_TIEBREAK_SET = SetFormat(tiebreak_points=10)
MATCH_TIEBREAK = SetFormat(tiebreak_at=0, tiebreak_points=10)  # replaces the final set


def grand_slam_final_set(slam: str, year: int) -> SetFormat:
    """
    Final-set rule of a Grand Slam singles event.

    Since 2022 all four Slams play a 10-point tiebreak at 6-6. Before that:
    the US Open used a 7-point tiebreak at 6-6; Wimbledon (2019-2021) a 7-point
    tiebreak at 12-12; the Australian Open (2019-2021) a 10-point tiebreak at 6-6;
    otherwise the final set was an advantage set.

    ``slam`` uses the dataset spelling: ``'ausopen'``, ``'frenchopen'``,
    ``'wimbledon'``, ``'usopen'``.
    """
    if year >= 2022:
        return TEN_POINT_TIEBREAK_SET
    if slam == "usopen":
        return SetFormat()
    if slam == "wimbledon" and year >= 2019:
        return SetFormat(tiebreak_at=12)
    if slam == "ausopen" and year >= 2019:
        return TEN_POINT_TIEBREAK_SET
    return ADVANTAGE_SET


def grand_slam(slam: str, year: int, best_of: int) -> MatchFormat:
    """Format of a Grand Slam singles match (``best_of`` 5 for men, 3 for women)."""
    return MatchFormat(best_of=best_of, final_set=grand_slam_final_set(slam, year))
