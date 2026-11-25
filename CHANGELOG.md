# Changelog

## 0.1.0

First release on PyPI.

### Data

- `load_slam`, `load_charting` and `load_results` read Grand Slam point-by-point data, the Match
  Charting Project and ATP/WTA results into a `Dataset` of four tables: `matches`, `players`,
  `points` and `shots`.
- Files are downloaded on first use from pinned commits and cached; parsed tables are cached too.
  `BSUTENNIS_ARCHIVE_URL` and `BSUTENNIS_MCP_URL` read the files from another copy.
- Point-by-point matches are replayed with the scoring rules of their format and checked
  against the source score.

### Analysis

- `bsutennis.rules`: match formats (with short codes such as `'bo5 6/tb7 final 6/tb10'`) and
  the scoring of a match.
- `bsutennis.models`: win probability from any score, point importance, hold probability, Elo.
- `bsutennis.metrics`: serve and return statistics, a table of serves, serve entropy, shot
  value, win probability of every point, Elo ratings.
- `TennisCourt.zone_heatmap` and zone maps in `bsutennis.geometry` shade the court by the
  category names of the data tables.

### Changes from the earlier BsuTennis code on GitHub

- The package is now `bsutennis` (lowercase), in a `src/` layout with the subpackages
  `geometry`, `rules`, `data`, `models`, `metrics` and `viz`.
- The old data modules (`BsuTennis/data/ao.py`, `atp.py`, `rg.py`) are replaced by the loaders.
- `classify_serve_zone` and `classify_shot_depth` return lowercase names (`'wide'`, `'deep'`,
  ...), and the medium/deep boundary is 9.14 m (was 9.0 m), as in the data tables. The unused
  `max_length` argument of `classify_shot_depth` is removed.
- `TennisCourt.draw_service_zones` is removed; use `draw_guides`.
- `pizza_chart` scales slices to the outer edge; values above about 80 used to be cut off.
