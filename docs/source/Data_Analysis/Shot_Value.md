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

# Shot value

Counting winners and errors credits only the last shot of a rally. The forehand that pushed the
opponent wide, three shots before the winner, gets nothing. Football analysts faced the same
problem and solved it by valuing every action by how much it changes a team's chance of scoring
(expected threat, VAEP). `bt.metrics.shot_values` does the same for every stroke in a tennis
rally.

- After a stroke that keeps the rally going, the hitter's chance of winning the point is the
  share of points won by everyone who hit a stroke like it. "Like it" means the same rally phase,
  shot type, wing, court position, direction and (for returns) depth.
- After a winner or an ace the chance is 1; after an error or a fault it is 0.
- Before a stroke, the hitter's chance is one minus the opponent's chance after the previous
  stroke.

A stroke's **value** is the change: what it added to, or took from, its hitter's chance.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import pandas as pd

import bsutennis as bt
from bsutennis.geometry import RALLY_LANES

charted = bt.load_charting("atp", "2020s")
values = bt.metrics.shot_values(charted)
columns = ["phase", "player", "shot_type", "wing", "direction", "depth", "ending", "before", "after", "value"]
values[columns].head(6).round(3)
```

## One rally

The longest rally of the 2023 Wimbledon final came on a break point for Alcaraz in the second
set. Djokovic, serving, won it after 30 strokes. His chance of winning the point after each
stroke:

```{code-cell} ipython3
final = "20230716-M-Wimbledon-F-Novak_Djokovic-Carlos_Alcaraz"
rally = values[(values.match_id == final) & (values.point_no == 74)]
djokovic = rally.after.where(rally.player == "Novak Djokovic", 1 - rally.after)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(rally.shot_no, djokovic, color="grey", lw=0.8)
for player, color in [("Novak Djokovic", "#2437ff"), ("Carlos Alcaraz", "#e74c3c")]:
    hit = rally.player == player
    ax.scatter(rally.shot_no[hit], djokovic[hit], color=color, label=f"{player} hits", zorder=3)
ax.axhline(0.5, color="black", lw=0.5)
ax.set(xlabel="stroke", ylabel="Djokovic wins the point", ylim=(0, 1.05))
ax.legend(loc="lower left");
```

The biggest strokes of the rally:

```{code-cell} ipython3
rally.reindex(rally.value.abs().sort_values(ascending=False).index)[["shot_no", *columns]].head(5).round(3)
```

## Returns: depth is what counts

```{code-cell} ipython3
returns = values[(values.phase == "return") & values.depth.notna()]
(returns.groupby(["serve_no", "depth"])
 .agg(returns=("value", "size"), receiver_chance_after=("after", "mean"), value=("value", "mean"))
 .round(3))
```

Once a first serve is in play, the receiver has about a 34 % chance of winning the point. A deep
return lifts that to 50 %, about twice the gain of a medium one, while a short return barely
improves it. (Missed returns have no depth and are
left out here; they lose the point.)

## Rally groundstrokes: aim for the corners

Mean value of forehand and backhand groundstrokes by lane, as seen by the hitter (rallies only):

```{code-cell} ipython3
ground = values[(values.phase == "rally") & (values.shot_type == "groundstroke")]
fig, axes = plt.subplots(1, 2, figsize=(10, 7))
for ax, wing in zip(axes, ["forehand", "backhand"]):
    court = bt.TennisCourt(half=True)
    court.draw(ax=ax)
    by_lane = ground[ground.wing == wing].groupby("direction").value.mean()
    court.zone_heatmap(ax, by_lane, RALLY_LANES, cmap="RdBu", vmin=-0.05, vmax=0.05, fmt="{:+.3f}")
    ax.set_title(f"{wing}s")
```

A groundstroke to either corner gains its hitter a few percent; one down the middle gives it
away. These are averages over every situation. The state does not know how fast or how close to
the line the ball was, so part of a lane's value comes from the strokes players choose to hit
there.

## Shot types

```{code-cell} ipython3
(values[values.phase == "rally"]
 .groupby("shot_type")
 .agg(strokes=("value", "size"), value=("value", "mean"), ends_point=("ending", lambda e: e.notna().mean()))
 .sort_values("strokes", ascending=False)
 .round(3))
```

Volleys, overheads and swinging volleys gain the most: they are usually hit from a strong
position. Slices and lobs lose ground on average, because players often hit them while
defending.

## Who adds most with the forehand?

Value per 100 rally groundstrokes (including the first shot after the serve), for players with
at least 5,000 forehands and 5,000 backhands charted:

```{code-cell} ipython3
strokes = values[values.phase.isin(["serve+1", "rally"]) & (values.shot_type == "groundstroke")]
per_wing = strokes.groupby(["player", "wing"]).value.agg(["size", "mean"]).unstack()
regulars = per_wing[(per_wing["size"] >= 5000).all(axis=1)]
(regulars["mean"] * 100).sort_values("forehand", ascending=False).round(2).head(12)
```

Values from charted matches describe the matches that were charted: strong players, big events,
and opponents of every level. A player's value also depends on the strokes the state cannot
distinguish, which is why these numbers rank shot-making styles more than they measure talent.

## Reference

- Decroos, T., Bransen, L., Van Haaren, J. & Davis, J. (2019). Actions speak louder than goals:
  valuing player actions in soccer. *Proceedings of KDD 2019*, 1851–1861.
