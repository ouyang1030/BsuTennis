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

# Loading charted matches

The [Match Charting Project](../Introduction/Intro_to_Tennis_data.md) records every stroke of
a match: serve direction, shot type, wing, direction, return depth and how the point ended.
`load_charting` returns the same `Dataset` as `load_slam`, now with the `shots` table filled.

The source splits points by tour (`'atp'`, `'wta'`) and decade (`'to-2009'`, `'2010s'`,
`'2020s'`). The men's 2020s file is about 60 MB; it is downloaded once and cached.

```{code-cell} ipython3
import bsutennis as bt

charted = bt.load_charting("atp", "2020s")
charted
```

The warning names matches whose format (best of three or five, final-set rule) is missing from
the source's match list. Without the format their points cannot be scored, so they are left out.

## Matches

```{code-cell} ipython3
charted.matches.query("tournament == 'Wimbledon' and round == 'F'")
```

In this source player 1 is always the player who served first, so the scoreline of the 2023
final reads from Djokovic's side.

## Points

The points table has the same columns as for the Grand Slam data. Columns the charting
notation describes are filled from the strokes: serve number and direction, aces, double
faults, outcome and rally length.

```{code-cell} ipython3
final = charted.match("20230716-M-Wimbledon-F-Novak_Djokovic-Carlos_Alcaraz")
columns = ["point_no", "server", "point_score", "side", "serve_no", "serve_direction",
           "outcome", "rally_count", "point_winner"]
final.points[columns].head(8)
```

Serve direction by court side in the final:

```{code-cell} ipython3
(final.points
 .groupby(["server", "side"])
 .serve_direction.value_counts(normalize=True)
 .unstack()
 .round(2))
```

## Shots

One row per stroke, faults included. `shot_no` counts from the serve, so odd strokes belong
to the server. Directions are seen by the hitter (`'left'`, `'middle'`, `'right'`); depth is
charted for returns only.

```{code-cell} ipython3
final.shots.query("point_no == 1")
```

Winners by wing:

```{code-cell} ipython3
(final.shots[final.shots.ending == "winner"]
 .groupby("player")
 .wing.value_counts()
 .unstack())
```

## On the court

Directions and depths are categories, not coordinates, so they are drawn as shaded zones.
`bsutennis.geometry` holds the rectangle behind each category name (`serve_zones(side)`,
`RALLY_LANES`, `RETURN_DEPTHS`, `RETURN_ZONES`), and `TennisCourt.zone_heatmap` shades them by
any value per name:

```{code-cell} ipython3
import matplotlib.pyplot as plt
from bsutennis.geometry import RETURN_ZONES, serve_zones

alcaraz_serves = final.points[final.points.server == "Carlos Alcaraz"]
returns = final.shots[(final.shots.shot_no == 2) & (final.shots.player == "Carlos Alcaraz")]
placed = returns.dropna(subset=["direction", "depth"])

fig, axes = plt.subplots(1, 3, figsize=(15, 7))
for ax, side in zip(axes, ["deuce", "ad"]):
    court = bt.TennisCourt(half=True)
    court.draw(ax=ax)
    shares = alcaraz_serves[alcaraz_serves.side == side].serve_direction.value_counts(normalize=True)
    court.zone_heatmap(ax, shares, serve_zones(side), cmap="bsu_red", vmin=0, fontsize=9)
    ax.set_title(f"Alcaraz's serves, {side} side")

court = bt.TennisCourt(half=True)
court.draw(ax=axes[2])
court.zone_heatmap(axes[2], placed.groupby(["direction", "depth"]).size() / len(placed),
                   RETURN_ZONES, cmap="bsu_blue", vmin=0)
axes[2].set_title("Alcaraz's returns: lane and depth");
```

The court is seen from behind the hitter: the net is at the bottom edge, and the deuce box is
on the server's left.

## Two sources, one match

The same final is in the Grand Slam point-by-point data. The two sources were recorded
independently and number the players differently, yet the replayed points agree:

```{code-cell} ipython3
slam = bt.load_slam(2023, "wimbledon").match("2023-wimbledon-1701")
for column in ["point_winner", "server", "point_score", "break_point"]:
    same = (final.points[column].values == slam.points[column].values).all()
    print(f"{column:13s} identical on all {len(slam.points)} points: {same}")
```

## Data quality

As with the Grand Slam data, the replayed score is checked against the score the charter wrote
before every point (`score_mismatch_at`). In addition, `shots_recorded` is false for points
charted without strokes (the notation allows this) and for the few cells that do not follow
the notation; their stroke columns are missing.

```{code-cell} ipython3
print(f"matches agreeing with the source score: {charted.matches.score_mismatch_at.isna().mean():.2%}")
print(f"points with strokes:                    {charted.points.shots_recorded.mean():.2%}")
```

Totals computed from these tables (aces, double faults, first serves in and won, break points,
winners, unforced errors) match the project's own per-match statistics exactly for 93–99 % of
players and matches, and within one for over 98 %. Most remaining differences come from charts
edited after the statistics were computed.
