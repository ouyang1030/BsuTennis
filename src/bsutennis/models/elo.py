"""
Elo ratings for tennis.

After every match the winner takes rating points from the loser: more when
the win was unexpected. A player's ratings move fast at first and settle as
they play more, with ``K = 250 / (matches + 5) ** 0.4`` (the variant used by
Jeff Sackmann and FiveThirtyEight).
"""

from dataclasses import dataclass, field


def expected_score(rating: float, opponent: float) -> float:
    """Probability that a player rated ``rating`` beats one rated ``opponent``."""
    return 1 / (1 + 10 ** ((opponent - rating) / 400))


@dataclass
class Elo:
    initial: float = 1500.0
    ratings: dict[str, float] = field(default_factory=dict)
    played: dict[str, int] = field(default_factory=dict)

    def rating(self, player: str) -> float:
        return self.ratings.get(player, self.initial)

    def k(self, player: str) -> float:
        return 250 / (self.played.get(player, 0) + 5) ** 0.4

    def play(self, winner: str, loser: str) -> float:
        """Record a match; return the winner's expected score before it."""
        expected = expected_score(self.rating(winner), self.rating(loser))
        self.ratings[winner] = self.rating(winner) + self.k(winner) * (1 - expected)
        self.ratings[loser] = self.rating(loser) - self.k(loser) * (1 - expected)
        for player in (winner, loser):
            self.played[player] = self.played.get(player, 0) + 1
        return expected
