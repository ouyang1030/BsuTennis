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

# Player profiles

What makes a player good? This lesson profiles a season of ATP players by their serve and
return. It uses the match statistics in the results data and the charts from the
[visualising](../Visualizing/Statistical_Charts.md) chapter.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np

import bsutennis as bt

season = bt.load_results("atp", 2025)
table = bt.metrics.serve_return(season.players)
regulars = table[table.matches >= 25]
len(table), len(regulars)
```

`serve_return` sums each player's points over the season before dividing, so a five-set match
counts more than a retirement after one set. A percentage over a handful of matches is mostly
noise, so the comparisons below keep the regulars: players with at least 25 tour-level matches.

```{code-cell} ipython3
columns = ["matches", "serve_points_won", "return_points_won", "points_won", "dominance_ratio"]
regulars.nlargest(10, "points_won")[columns].round(3)
```

Sinner won 56 % of all the points he played, the best in the tour, while the average regular
is close to 50 %. A few percent of points separate the best from the rest, because winning
slightly more points becomes winning many more matches (see
[Win probability](Win_Probability.md)). The *dominance ratio* says the same thing in another
way: return points won divided by serve points lost.

## Serve and return

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 6.5))
ax.scatter(regulars.serve_points_won, regulars.return_points_won, s=regulars.matches, alpha=0.5)

# Share of all points won, for equal numbers of serve and return points
serve, ret = np.meshgrid(np.linspace(0.55, 0.75, 50), np.linspace(0.30, 0.45, 50))
lines = ax.contour(serve, ret, (serve + ret) / 2, levels=[0.48, 0.50, 0.52, 0.54, 0.56],
                   colors="grey", linewidths=0.6, linestyles="--")
ax.clabel(lines, fmt="{:.0%} of points".format, fontsize=8)

for name, row in regulars.nlargest(8, "points_won").iterrows():
    ax.annotate(name.split(maxsplit=1)[-1], (row.serve_points_won, row.return_points_won),
                xytext=(4, 3), textcoords="offset points", fontsize=8)
ax.set(xlabel="serve points won", ylabel="return points won", ylim=(0.3, 0.45),
       title="ATP 2025, players with 25 or more matches (size: matches)");
```

```{code-cell} ipython3
print(f"correlation: {regulars.serve_points_won.corr(regulars.return_points_won):.2f}")
```

Serving and returning are almost unrelated skills. Taylor Fritz is near the top on serve and
below average on return; Alex de Minaur is the reverse. Both reach the top ten in points won.

## Percentile pizza

A pizza chart shows where a player ranks among the regulars on each statistic: 90 means
better than 90 % of them. For double faults, fewer is better, so that percentile is reversed.

```{code-cell} ipython3
labels = {
    "first_serve_in": "1st serve\nin",
    "first_serve_won": "1st serve\nwon",
    "second_serve_won": "2nd serve\nwon",
    "ace_rate": "Aces",
    "double_fault_rate": "Few double\nfaults",
    "break_points_saved": "Break points\nsaved",
    "return_points_won": "Return\npoints won",
    "break_points_converted": "Break points\nconverted",
}
percentiles = regulars[list(labels)].rank(pct=True) * 100
percentiles["double_fault_rate"] = 100 - percentiles.double_fault_rate
percentiles = percentiles.rename(columns=labels)

fig, ax = bt.pizza("Jannik Sinner", percentiles.loc["Jannik Sinner"].to_dict(),
                   compare_values=percentiles.loc["Carlos Alcaraz"].tolist(),
                   compare_label="Carlos Alcaraz", figsize=(8, 8), title_fontsize=14)
```

Sinner is in the top few percent on everything but first serves in and aces. The narrow white
bars show Alcaraz, who matches him on return but loses more ground on serve.

Percentiles depend on who they are compared with: against the top 20 instead of the regulars,
Sinner's slices would shrink. They also hide how big a gap is: in the 99th percentile, 1 % of
points can be worth many places.

## Radar: the values themselves

A radar chart shows the values, each axis scaled from the 5th to the 95th percentile of the
regulars (values beyond them sit on the edge). Players with different games make different
shapes:

```{code-cell} ipython3
params = ["first_serve_in", "first_serve_won", "second_serve_won", "ace_rate",
          "return_points_won", "break_points_converted"]
radar = bt.Radar([labels[p].replace("\n", " ") for p in params],
                 min_range=regulars[params].quantile(0.05).tolist(),
                 max_range=regulars[params].quantile(0.95).tolist())
fig, ax = radar.setup_axis(figsize=(7, 7))
radar.draw_circles(ax)
for player, color in [("Taylor Fritz", "#e74c3c"), ("Alex De Minaur", "#2ecc71"), ("Jannik Sinner", "#3498db")]:
    radar.draw(ax, regulars.loc[player, params].tolist(), label=player, color=color)
ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1));
```

Fritz wins with his first serve and aces, and de Minaur with his return. Both win an unusual
share of their second-serve points. Sinner is at the edge on everything except first serves in
and aces, where he is average.
