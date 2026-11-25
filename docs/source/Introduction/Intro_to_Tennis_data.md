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

# Tennis Data

## Sources

| Source | Level | Coverage | Status in bsutennis |
|---|---|---|---|
| Grand Slam point-by-point | one row per point | Wimbledon and US Open 2011–2024 (no Wimbledon 2020); Australian Open and Roland Garros 2011–2021 | `load_slam` |
| Match Charting Project | one row per shot | about 7,500 men's and 4,200 women's tour matches, 1960–2026 | `load_charting` |
| ATP / WTA match results | one row per match, with per-player rankings and serve statistics | every tour-level season since 1968; challengers, qualifying, futures and ITF events | `load_results` |

All three were collected by Jeff Sackmann and are licensed
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): credit him, do not use
the data commercially, and share derived data under the same license. bsutennis does not ship
any data; files are downloaded on first use and cached under `~/.cache/bsutennis`
(override with the `BSUTENNIS_CACHE` environment variable). The tables parsed from them are
cached as well, so only the first load of a source replays its matches. The cache can be
deleted at any time.

The Match Charting Project is read from
[its own repository](https://github.com/JeffSackmann/tennis_MatchChartingProject). The original
Grand Slam and ATP/WTA repositories were withdrawn from GitHub in 2026; bsutennis reads them from
the archival mirror
[Aneeshers/tennis-sackmann-archive](https://github.com/Aneeshers/tennis-sackmann-archive).
Every source is pinned to one commit, so every analysis sees exactly the same files. To read
the same files from another copy, for example a local clone, set `BSUTENNIS_ARCHIVE_URL` (Grand
Slam and ATP/WTA) or `BSUTENNIS_MCP_URL` (Match Charting Project) to its location, such as
`file:///home/me/tennis-sackmann-archive`.

## Conventions

- **Players** are named as written in the source. Some files abbreviate first names
  (`'R. Nadal'` at Roland Garros 2018), so names are not yet comparable across tournaments.
  Which player is `player1` is also the source's choice: the winner in ATP/WTA results, the
  first server in the Match Charting Project. Tournament names are also kept, except that the
  four Grand Slams are named alike in every source.
- **Score columns** describe the score *before* the point, server first, as on a scoreboard
  (`'30-40'`, `'AD-40'`, `'5-6'` in a tiebreak).
- **Derived, not copied**: set and game numbers, the score, break / set / match points and
  the match winner are computed by replaying the point winners with the scoring rules of
  that tournament and year (see `bsutennis.rules`). The source score is used only to
  check the replay.
- **Missing means not recorded**: values a source writes as `0` when it did not measure
  them (serve speed, rally length) become missing values.
- **Serve statistics** in `players` are the official ones for ATP/WTA results and are counted
  from the points for the other sources, with the same definitions.
- **Attribute access** works for every column (`points.server`) except `round`, which is a
  DataFrame method: write `matches["round"]`, or use it inside `query`.
- **Shot directions** are seen by the hitter: the `'left'`, `'middle'` or `'right'` lane
  (outer 30 %, middle 40 %, outer 30 % of the court width) in which the ball crosses, or would
  cross, the opponent's baseline, whatever either player's handedness.
- **Court positions** use the standard frame of `bsutennis.geometry`: metres, origin at
  the centre of the net.

## The standard tables

Every column has a fixed type. Where a source does not record a value, the column holds a
missing value (`<NA>`, `NaN` or `NaT`); columns marked "always known" never do.

```{code-cell} ipython3
:tags: [remove-input]
import pandas as pd
from bsutennis.data import MATCH_COLUMNS, PLAYER_COLUMNS, POINT_COLUMNS, SHOT_COLUMNS

pd.set_option("display.max_colwidth", None)
TYPE_NAMES = {"object": "text", "int64": "integer, always known", "Int64": "integer",
              "float64": "number", "bool": "True / False, always known",
              "boolean": "True / False", "datetime64[ns]": "date"}

def schema_table(columns):
    return pd.DataFrame(
        {"type": [TYPE_NAMES[c.dtype] for c in columns.values()],
         "description": [c.description for c in columns.values()]},
        index=pd.Index(list(columns), name="column"),
    )
```

`Dataset.matches`, one row per match (index `match_id`):

```{code-cell} ipython3
:tags: [remove-input]
schema_table(MATCH_COLUMNS)
```

`Dataset.players`, one row per player per match:

```{code-cell} ipython3
:tags: [remove-input]
schema_table(PLAYER_COLUMNS)
```

`Dataset.points`, one row per point:

```{code-cell} ipython3
:tags: [remove-input]
schema_table(POINT_COLUMNS)
```

`Dataset.shots`, one row per stroke (Match Charting Project only):

```{code-cell} ipython3
:tags: [remove-input]
schema_table(SHOT_COLUMNS)
```
