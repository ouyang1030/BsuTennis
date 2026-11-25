# bsutennis

Load open tennis data into pandas tables, analyse it, and plot it on a court.

```bash
pip install bsutennis
```

Requires Python 3.10 or newer.

## Example

```python
import bsutennis as bt

wimbledon = bt.load_slam(2023, "wimbledon")   # Dataset(254 matches, 48164 points, 0 shots)
final = wimbledon.match("2023-wimbledon-1701")

# Break points in the final, and how many each server saved
final.points[final.points.break_point].groupby("server").server_won.agg(["size", "sum"])

# Win probability and importance of every point
bt.metrics.point_probabilities(final).nlargest(5, "importance")
```

```python
import matplotlib.pyplot as plt

court = bt.TennisCourt(theme="bsu", half=True)
fig, ax = plt.subplots(figsize=(6, 8))
court.draw(ax=ax)
```

## Data

| Loader | Source | Coverage |
|---|---|---|
| `load_slam(year, slam)` | Grand Slam point-by-point | Wimbledon and US Open 2011–2024, Australian Open and Roland Garros 2011–2021 |
| `load_charting(tour, period)` | Match Charting Project | about 11,800 matches, every stroke charted |
| `load_results(tour, year)` | ATP and WTA results | every season since 1968, with rankings and serve statistics |

Each loader returns a `Dataset` of four pandas tables: `matches`, `players`, `points` and
`shots`. A table the source has no data for is empty. Point-by-point matches are replayed with
the scoring rules of their format, and the replayed score is checked against the source.

The data were collected by Jeff Sackmann and are licensed
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), which does not allow
commercial use. The package does not include them: each file is downloaded on first use from a
pinned commit and cached in `~/.cache/bsutennis` (set `BSUTENNIS_CACHE` to change this).

## Contents

- `bsutennis.data`: the loaders and the `Dataset` tables
- `bsutennis.rules`: match formats and the scoring of a match
- `bsutennis.models`: win probability from any score, point importance, Elo
- `bsutennis.metrics`: serve and return statistics, serve direction, shot value, Elo ratings
- `bsutennis.geometry`: court dimensions, coordinates and zones
- `bsutennis.viz`: court plots, zone heatmaps, pizza, radar and sonar charts

The [documentation](https://bsutennis.readthedocs.io/en/latest/) has lessons
on win probability, Elo ratings, player profiles, serve patterns, rally length and shot value.

## Development

```bash
git clone https://github.com/ouyang1030/BsuTennis.git
cd BsuTennis
pip install -e ".[dev]"
pytest              # offline tests
pytest -m network   # tests that download data
```

## License

The code is MIT licensed, see [LICENSE](https://github.com/ouyang1030/BsuTennis/blob/master/LICENSE).
The data keep their own license (see above).
