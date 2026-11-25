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

# Loading results

`load_results` reads one season of [ATP or WTA results](../Introduction/Intro_to_Tennis_data.md):
every singles match with its score, and for each player the ranking, age, seed, entry and,
where the tours publish them, serve statistics. A season of tour-level matches is about 1 MB.

```{code-cell} ipython3
import bsutennis as bt

season = bt.load_results("atp", 2023)
season
```

There are no points or shots, so the work is done on `matches` and `players`.

## Matches

Player 1 is the winner. `status` says how the match ended; walkovers and retirements matter for
anything that rates players.

```{code-cell} ipython3
season.matches.query("level == 'G' and round == 'F'")
```

```{code-cell} ipython3
season.matches.status.value_counts()
```

## Players

Two rows per match, so per-player questions need no reshaping. Most match wins of the season,
and how often those players won a point on their first serve when it went in:

```{code-cell} ipython3
totals = season.players.groupby("player")[["won", "first_serves_in", "first_serve_points_won"]].sum()
totals["first_serve_won"] = (totals.first_serve_points_won / totals.first_serves_in).round(3)
totals.nlargest(8, "won")[["won", "first_serve_won"]]
```

Several seasons combine with `bt.Dataset.concat`, and `level` selects the qualifying and
challenger (`'qual_chall'`), futures (`'futures'`, ATP) or ITF (`'qual_itf'`, WTA) files.

## One statistic, two sources

The official statistics are compiled by the tours. The Grand Slam point-by-point data was
recorded separately, and bsutennis counts the same statistics from its points. For Wimbledon
2023 the two agree match by match:

```{code-cell} ipython3
wimbledon = bt.load_slam(2023, "wimbledon")
verified = wimbledon.matches.index[wimbledon.matches.score_mismatch_at.isna()]
counted = wimbledon.players[wimbledon.players.match_id.isin(verified)]
official = season.players[season.players.match_id.str.startswith("2023-540-")]
both = counted.merge(official, on=["player", "opponent"], suffixes=("", "_official"))

statistics = ["aces", "double_faults", "serve_points", "first_serves_in", "first_serve_points_won",
              "second_serve_points_won", "service_games", "break_points_faced", "break_points_saved"]
agreement = {s: (both[s] == both[f"{s}_official"]).mean() for s in statistics}
print(f"{len(both)} player-matches")
for statistic, share in agreement.items():
    print(f"{statistic:24s} {share:.1%} identical")
```

`service_games` follows the official convention: a game counts for the player who served its
last point, so each tiebreak counts for one of the two players. Official statistics before
2018 credit tiebreaks inconsistently, so for older seasons this column can be off by one per
tiebreak.
