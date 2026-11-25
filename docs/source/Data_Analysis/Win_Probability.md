---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Win probability and important points

Suppose each player wins a fixed share of the points on their own serve, whatever the score.
Then the rules of tennis settle everything else: the chance to hold serve, to win a set, and
to win the match from any score. This *independent-points model* (Barnett & Clarke 2005;
O'Malley 2008) is to tennis roughly what expected goals is to football: a simple baseline that
turns a match into probabilities. `bsutennis.models` computes it for any match format.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np

import bsutennis as bt
from bsutennis.models import hold_probability, win_probability
from bsutennis.rules import MatchFormat, Score
```

## Small edges grow

Holding serve amplifies a player's edge on serve points, and a match amplifies it again:

```{code-cell} ipython3
p = np.linspace(0.5, 0.8, 61)
fig, (games, matches) = plt.subplots(1, 2, figsize=(11, 4))

games.plot(p, [hold_probability(x) for x in p])
games.set(xlabel="serve points won", ylabel="games held", title="From points to games")

for best_of in (3, 5):
    start = Score(MatchFormat(best_of=best_of), game_server=0)
    matches.plot(p, [win_probability(start, (x, 0.62)) for x in p], label=f"best of {best_of}")
matches.axvline(0.62, color="grey", lw=0.8, ls="--")
matches.set(xlabel="serve points won (opponent: 0.62)", ylabel="match won", title="From points to matches")
matches.legend();
```

A player who wins 60 % of their serve points holds 74 % of their service games. Against an
opponent who wins 62 %, winning 66 % instead gives a 73 % chance of winning a best-of-five match
(69 % over best of three): longer matches favour the better player.

## A match, point by point

The 2023 Wimbledon final went to five sets. Using each player's share of serve points won in
the match, `point_probabilities` gives Alcaraz's chance of winning (he is player 1 in this
source) before every point, and how much each point mattered.

```{code-cell} ipython3
final = bt.load_slam(2023, "wimbledon").match("2023-wimbledon-1701")
bt.metrics.serve_shares(final.players)
```

```{code-cell} ipython3
probabilities = bt.metrics.point_probabilities(final)
points = final.points.merge(probabilities, on=["match_id", "point_no"])

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(points.point_no, points.player1_win_probability, color="#2437ff")
for _, first_point in points.groupby("set_no").point_no.min().items():
    ax.axvline(first_point, color="grey", lw=0.8, ls="--")
ax.axhline(0.5, color="black", lw=0.5)
ax.set(xlabel="point", ylabel="Alcaraz wins the match", ylim=(0, 1),
       title="2023 Wimbledon final: win probability before each point");
```

The shares are measured in the final itself, so the curve describes how the match went, not
what could have been predicted before it. For a prediction, estimate the shares from earlier
matches, for example with `bt.metrics.serve_return` over the previous season.

## The points that mattered

A point's *importance* is the difference between the player's chances after winning it and
after losing it (Morris 1977). Most points barely move the match; a few move it a lot:

```{code-cell} ipython3
columns = ["point_no", "set_no", "server", "server_games", "receiver_games", "point_score",
           "point_winner", "importance"]
points.nlargest(6, "importance")[columns]
```

The biggest points of the final were in the second-set tiebreak, which Alcaraz won from a set
point down, and on break points early in the fifth set.

## Who won the big points?

Compare each player's share of points won on the most important tenth of the points with
their share overall:

```{code-cell} ipython3
big = points.importance >= points.importance.quantile(0.9)
for player in [final.matches.player1.iloc[0], final.matches.player2.iloc[0]]:
    won = points.point_winner == player
    print(f"{player:15s} all points {won.mean():.1%}   big points {won[big].mean():.1%}  ({big.sum()} points)")
```

With about 34 big points, the standard error of each share is about 8 percentage points, so a
single match cannot show that a player is "clutch". Across many matches, the same comparison is
the classic test of whether some players raise their game on important points (Klaassen & Magnus
2001).

## References

- Barnett, T. & Clarke, S. R. (2005). Combining player statistics to predict outcomes of tennis
  matches. *IMA Journal of Management Mathematics*, 16(2), 113–120.
- Klaassen, F. & Magnus, J. R. (2001). Are points in tennis independent and identically
  distributed? *Journal of the American Statistical Association*, 96(454), 500–509.
- Morris, C. (1977). The most important points in tennis. In *Optimal Strategies in Sports*.
- Newton, P. K. & Keller, J. B. (2005). Probability of winning at tennis I. *Studies in Applied
  Mathematics*, 114(3), 241–269.
- O'Malley, A. J. (2008). Probability formulas and statistical analysis in tennis. *Journal of
  Quantitative Analysis in Sports*, 4(2).
