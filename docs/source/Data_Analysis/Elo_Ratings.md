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

# Elo ratings

The ATP ranking adds up points won at tournaments over the last twelve months. It rewards
playing a lot and going deep in big events, but it ignores *whom* a player beat. An Elo rating
does the opposite. After every match the winner takes rating points from the loser, and takes
more when the win was unexpected. Ratings that predict well are therefore a good measure of
current strength.

`bt.metrics.elo` rates every match in a `matches` table, in the order the matches were played.
It uses the tennis variant of Elo popularised by Jeff Sackmann and FiveThirtyEight, in which a
player's rating moves fast at first and settles as they play more matches.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import bsutennis as bt

seasons = bt.Dataset.concat(bt.load_results("atp", year) for year in range(2000, 2026))
ratings = bt.metrics.elo(seasons.matches)
ratings.tail()
```

There is one row per player per match: the rating before the match (`elo`), the rating after it,
and the player's chance of winning before it was played.

## The best players now

A player's current rating is the one after their last match. The table below lists players who
played in 2025, with their ranking at that last tournament:

```{code-cell} ipython3
year = ratings.match_id.map(seasons.matches.year)
latest = (ratings[year == 2025]
          .drop_duplicates("player", keep="last")
          .merge(seasons.players[["match_id", "player", "ranking"]]))
latest.nlargest(10, "elo_after")[["player", "elo_after", "ranking"]].round(0)
```

## Careers

```{code-cell} ipython3
dates = seasons.matches.tournament_date
fig, ax = plt.subplots(figsize=(11, 4.5))
for player in ["Roger Federer", "Rafael Nadal", "Novak Djokovic", "Carlos Alcaraz", "Jannik Sinner"]:
    history = ratings[ratings.player == player]
    ax.plot(history.match_id.map(dates), history.elo_after, lw=1, label=player)
ax.set(ylabel="Elo rating", title="ATP tour-level Elo ratings")
ax.legend(loc="lower center", ncols=2);
```

All players start at 1500 in 2000, so the first seasons are a warm-up. Federer's early curve, for
example, does not yet reflect his strength in 1999. The ratings also use tour-level main-draw
matches only. A newcomer's Challenger wins do not count, so newcomers start lower than they
should.

## How well do ratings predict?

Every `win_probability` is computed *before* the match, so comparing it with the result tests
real predictions. Ratings by surface (`by="surface"`) know that clay specialists exist but rest
on fewer matches. Averaging the two is a common compromise.

```{code-cell} ipython3
surface = bt.metrics.elo(seasons.matches, by="surface")
players = seasons.players[["match_id", "player", "won", "ranking"]]
rated = (ratings
         .merge(surface[["match_id", "player", "win_probability"]], on=["match_id", "player"],
                suffixes=("", "_surface"))
         .merge(players, on=["match_id", "player"])
         .merge(players[["match_id", "player", "ranking"]]
                .rename(columns={"player": "opponent", "ranking": "opponent_ranking"})))
rated["blend"] = (rated.win_probability + rated.win_probability_surface) / 2

# From 2015 on, with both players ranked; one row per match, from the winner's side
winners = rated[rated.won & (rated.match_id.map(seasons.matches.year) >= 2015)
                & rated.ranking.notna() & rated.opponent_ranking.notna()]
pd.DataFrame({
    "favourite won": [(winners[c] > 0.5).mean() for c in ["win_probability", "win_probability_surface", "blend"]]
                     + [(winners.ranking < winners.opponent_ranking).mean()],
    "log loss": [-np.log(winners[c]).mean() for c in ["win_probability", "win_probability_surface", "blend"]]
                + [np.nan],
}, index=["Elo", "surface Elo", "blend", "ranking"]).round(3)
```

Elo picks the winner a little more often than the ranking does, and the blend does best (lower
log loss is better). Still, neither the ranking nor any rating gets far beyond two winners in
three: matches between tour players are hard to call from strength alone.

Are the probabilities right as well as the picks? Group the predictions and compare each group
with how often its players actually won:

```{code-cell} ipython3
recent = rated[rated.match_id.map(seasons.matches.year) >= 2015]
bins = pd.cut(recent.blend, np.linspace(0, 1, 11))
calibration = recent.groupby(bins, observed=True).agg(predicted=("blend", "mean"), won=("won", "mean"))

fig, ax = plt.subplots(figsize=(4.5, 4.5))
ax.plot([0, 1], [0, 1], color="grey", lw=0.8, ls="--")
ax.plot(calibration.predicted, calibration.won, marker="o")
ax.set(xlabel="predicted chance of winning", ylabel="share of matches won",
       title="Calibration, 2015-2025");
```

The points lie close to the diagonal, but the curve is a little flatter than it. The ratings are
slightly overconfident: players given about a 75 % chance won about 70 % of their matches. Two
likely reasons: Elo treats a rating as known exactly, and these ratings miss the Challenger results
of newcomers, who then start too low.

## From ratings to matches

An Elo difference gives the chance of winning a match, while the
[independent-points model](Win_Probability.md) gives the chance from serve and return
percentages. The two answer the same question from different data, so each can check the other.
Each also suits a different task: Elo handles players' whole histories, and the point model
handles the score of a match in progress.
