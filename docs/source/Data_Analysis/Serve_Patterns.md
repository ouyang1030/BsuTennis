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

# Serve patterns

The serve is the one shot in tennis that a player hits exactly as they choose. Where do
professionals aim it, what does each target earn, and can receivers guess where it will go?
The [Match Charting Project](../Getting_Started/Loading_Charting.md) records the direction of
every serve, faults included, for thousands of matches.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

import bsutennis as bt
from bsutennis.geometry import serve_zones

charted = bt.load_charting("atp", "2020s")
serves = bt.metrics.serves(charted)
first, second = serves[serves.serve_no == 1], serves[serves.serve_no == 2]
serves.head()
```

`serves` has one row per serve hit. A point that starts with a fault has two rows, and
`server_won` is the result of the point.

## First serves: wide or T

```{code-cell} ipython3
first.groupby("side").direction.value_counts(normalize=True).unstack().round(3)
```

Nine first serves in ten go to a corner of the service box: wide or down the T. What does
each target earn? Count every first serve aimed there, faults included, and the points won after
it:

```{code-cell} ipython3
(first.dropna(subset=["direction"])
 .assign(ace=first.ending == "ace")
 .groupby("direction")
 .agg(serves=("serve_in", "size"), serve_in=("serve_in", "mean"), aces=("ace", "mean"),
      points_won=("server_won", "mean"))
 .round(3))
```

Wide and T serves win the same share of points, about 65 %. Serves to the body land in more
often but win fewer points, which is why servers rarely aim there.

## Second serves: to the backhand

```{code-cell} ipython3
second.groupby(["receiver_hand", "side"]).direction.value_counts(normalize=True).unstack().round(3)
```

Second serves follow the receiver's backhand. For a right-handed receiver the backhand is in
the T on the deuce side and out wide on the ad side; against a left-hander the pattern reverses.
On the court, from behind the server:

```{code-cell} ipython3
fig, axes = plt.subplots(2, 2, figsize=(9, 9))
for row, (hand, name) in zip(axes, [("R", "right-handed"), ("L", "left-handed")]):
    for ax, side in zip(row, ["deuce", "ad"]):
        court = bt.TennisCourt(half=True)
        court.draw(ax=ax)
        shares = second[(second.receiver_hand == hand) & (second.side == side)].direction.value_counts(normalize=True)
        court.zone_heatmap(ax, shares, serve_zones(side), cmap="bsu_blue", vmin=0, vmax=0.5, fontsize=8)
        ax.set_title(f"{side} side, {name} receiver", fontsize=10)
fig.suptitle("Where second serves go");
```

## Predictable servers

A receiver who knows where the serve is going can start moving early. *Entropy* measures how
spread a server's choices are: 0 bits if every serve goes the same way, 1.58 if each direction
gets a third.

```{code-cell} ipython3
entropy = bt.metrics.serve_entropy(first).entropy.unstack()
most_charted = first.server.value_counts().index[:15]
entropy.loc[most_charted].sort_values("deuce").round(2)
```

Alcaraz and de Minaur spread their first serves the most. Fritz is the most predictable,
followed by Medvedev, Hurkacz and Rublev. A predictable mix is not necessarily a bad one: the
best mix depends on what each serve earns against the receivers, which the next section tests.

## Are servers mixing optimally?

In game theory, serving is a guessing game. If a server's wide serves won more often than his T
serves, he should hit more of them until receivers adjust. With the best mix (the *minimax*
strategy) every direction used must win equally often. Walker and Wooders (2001) tested this on
ten Wimbledon finals. Here is the same test on every server and side with at least 40 first
serves both wide and to the T:

```{code-cell} ipython3
wide_or_t = first[first.direction.isin(["wide", "T"])]
counts = wide_or_t.groupby(["server", "side", "direction"]).server_won.agg(["sum", "size"]).unstack()
counts = counts[(counts["size"] >= 40).all(axis=1)]

def equal_win_rates(row):
    won, total = row["sum"], row["size"]
    return stats.chi2_contingency([won, total - won], correction=False).pvalue

p_values = counts.apply(equal_win_rates, axis=1)
print(f"{len(p_values)} servers and sides; differences significant at 5 %: {(p_values < 0.05).mean():.1%}")

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.hist(p_values, bins=20, range=(0, 1), density=True)
ax.axhline(1, color="grey", ls="--", lw=0.8)
ax.set(xlabel="p-value: wide and T win equally often", ylabel="density");
```

If every server's two directions really won equally often, 5 % of the tests would come out
significant by chance, and the p-values would spread evenly between 0 and 1 (the dashed line).
The data come close: a few more small p-values than chance would give, otherwise an even spread.
Like Walker and Wooders, we find that professional servers mix their serves about as well as
game theory says they should.

The test is rough. Each server's win rates mix opponents, surfaces and scores, and the same
player appears on both sides. It is still a striking result: nobody tells servers the minimax
strategy, yet their serves earn the same whichever way they go.

## Reference

- Walker, M. & Wooders, J. (2001). Minimax play at Wimbledon. *American Economic Review*,
  91(5), 1521–1538.
