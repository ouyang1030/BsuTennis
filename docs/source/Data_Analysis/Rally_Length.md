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

# Rally length

Most tennis points are over in a few shots. This lesson looks at how long rallies are, how the
server's advantage fades as a rally goes on, how points end, and who wins the long ones. It uses
the charted men's matches of the 2020s.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import bsutennis as bt

charted = bt.load_charting("atp", "2020s")
points = (charted.points
          .dropna(subset=["rally_count"])
          .join(charted.matches.surface, on="match_id"))
points["rally"] = pd.cut(points.rally_count, [-1, 4, 8, np.inf], labels=["0-4", "5-8", "9+"])
len(points)
```

`rally_count` counts the shots that landed in, serve included: an ace is 1 and a double fault 0.
The bands 0–4, 5–8 and 9+ shots are the ones the ATP uses.

## How long are rallies?

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9, 4))
for surface in ["grass", "hard", "clay"]:
    counts = points[points.surface == surface].rally_count.clip(upper=20)
    ax.hist(counts, bins=np.arange(-0.5, 21.5), density=True, histtype="step", lw=1.5, label=surface)
ax.set(xlabel="shots in the rally (20 = 20 or more)", ylabel="share of points")
ax.legend();
```

```{code-cell} ipython3
points.groupby("surface").rally.value_counts(normalize=True).unstack().round(3)
```

The most common rally is a single shot, a serve that does not come back. Grass keeps points
shortest and clay makes them longest, but even on clay most points last four shots or fewer.

In short rallies, odd lengths are more common than the even lengths next to them. The player
who hit the last ball in wins the point, because the next shot was either missed or never
reached. Odd rallies end with the server's shot, so they are the server's points, and servers
win most points:

```{code-cell} ipython3
print(f"odd rally <=> server won: {((points.rally_count % 2 == 1) == points.server_won).mean():.2%}")
```

(The few exceptions are points the charter recorded oddly.) This is why the server's success is
measured over bands of lengths and not single lengths.

## The serve's advantage fades

```{code-cell} ipython3
won = points.groupby(["serve_no", "rally"], observed=True).server_won.mean().unstack(0)
ax = won.plot(marker="o", figsize=(6, 4))
ax.axhline(0.5, color="grey", lw=0.8, ls="--")
ax.set(xlabel="shots in the rally", ylabel="points won by the server", ylim=(0.4, 0.8))
ax.legend(["first serve", "second serve"]);
```

On first serve the server wins 77 % of short points, a share that drops to 57 % in long rallies.
It falls but does not vanish: the server's opening still counts after eight shots. On second
serve, short points include double faults, so the server does better in longer rallies once the
ball is in play.

## How points end

```{code-cell} ipython3
endings = points.groupby("rally", observed=True).outcome.value_counts(normalize=True).unstack()
endings = endings[["ace", "service_winner", "double_fault", "winner", "forced_error", "unforced_error"]]
ax = endings.plot.barh(stacked=True, figsize=(9, 3), width=0.7)
ax.set(xlabel="share of points", ylabel="shots in the rally")
ax.legend(ncols=3, loc="upper center", bbox_to_anchor=(0.5, -0.3));
```

Short points end with the serve itself (aces, unreturned serves, double faults) or a quick winner
or error. In longer rallies, about two points in five end with an unforced error, as the
pressure of hitting yet another ball builds.

## Who wins the long rallies?

Each point is played by two players, so turn every point into two rows, one per player:

```{code-cell} ipython3
both = pd.concat([points.assign(player=points.server), points.assign(player=points.receiver)])
both["won"] = both.point_winner == both.player
profile = pd.DataFrame({
    "long_rallies": both[both.rally == "9+"].groupby("player").size(),
    "won_long": both[both.rally == "9+"].groupby("player").won.mean(),
    "won_all": both.groupby("player").won.mean(),
})
profile = profile[profile.long_rallies >= 1500]
profile.sort_values("won_long", ascending=False).round(3)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(6.5, 6))
ax.scatter(profile.won_all, profile.won_long)
ax.axline((0.5, 0.5), slope=1, color="grey", lw=0.8, ls="--")
for name, row in profile.iterrows():
    ax.annotate(name.split(maxsplit=1)[-1], (row.won_all, row.won_long),
                xytext=(4, 2), textcoords="offset points", fontsize=8)
ax.set(xlabel="all points won", ylabel="rallies of 9+ shots won",
       title="Charted ATP matches, 2020s");
```

Players above the diagonal do better in long rallies than overall, de Minaur most of all.
Sinner, Alcaraz and Djokovic win the most points, both overall and in long rallies. Big servers such as Hurkacz and Fritz sit far below
the line: they earn their points early. Charted matches over-represent the best players and
the biggest matches, so these shares compare players in the matches someone chose to chart.
