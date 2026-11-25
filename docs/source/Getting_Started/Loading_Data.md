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

# Loading a Grand Slam

`load_slam` downloads one tournament of [Grand Slam point-by-point data](../Introduction/Intro_to_Tennis_data.md)
(about 8 MB, cached after the first call) and returns a `Dataset` of long tables: matches,
players (one row per player per match), points, and shots (empty for this source).

```{code-cell} ipython3
import bsutennis as bt

wimbledon = bt.load_slam(2023, "wimbledon")
wimbledon
```

## Matches

One row per match, indexed by `match_id`. The winner and scoreline are not read from the
source: they come from replaying every point with the scoring rules of that year.

```{code-cell} ipython3
wimbledon.matches.query("round == 'F'")
```

## Players

Two rows per match. The serve statistics are counted from the points, with the same
definitions as the official ATP and WTA statistics, so they can be compared across sources
(see [Loading results](Loading_Results.md)).

```{code-cell} ipython3
final = wimbledon.match("2023-wimbledon-1701")
final.players[["player", "won", "aces", "double_faults", "serve_points", "first_serves_in",
               "first_serve_points_won", "break_points_faced", "break_points_saved"]]
```

## Points

One row per point. The score columns describe the score *before* the point, from the
server's point of view, as a scoreboard shows it.

```{code-cell} ipython3
columns = ["point_no", "set_no", "game_no", "server", "point_score", "side",
           "break_point", "serve_no", "rally_count", "point_winner"]
final.points[columns].head(10)
```

Because every point is a row, questions become one line of pandas. Break points faced and
saved in the final:

```{code-cell} ipython3
(final.points[final.points.break_point]
 .groupby("server")
 .server_won.agg(faced="size", saved="sum"))
```

The same line works on the whole tournament, or on several tournaments combined with
`bt.Dataset.concat([...])`.

## Data quality

While loading, the replayed score is compared with the score written in the source after
every point. `score_mismatch_at` is the first point where they disagree (usually a point
missing from the source), and `score_verified` marks the points before it.

```{code-cell} ipython3
n_bad = wimbledon.matches.score_mismatch_at.notna().sum()
print(f"{n_bad} of {len(wimbledon.matches)} matches disagree with the source")
```

All 254 matches of Wimbledon 2023 agree with the source. Older files are noisier: in the
Australian Open 2019 about 40 % of matches contain a missing or duplicated point, so
filter with `points.score_verified` when the score matters.
