# API reference

Names are importable from their subpackage, e.g. `from bsutennis.metrics import shot_values`.
The most used ones are also available from `bsutennis` directly. The columns of the data tables
are described in [Introduction to tennis data](../Introduction/Intro_to_Tennis_data.md).

## Data: `bsutennis.data`

```{eval-rst}
.. autofunction:: bsutennis.data.load_slam
.. autofunction:: bsutennis.data.load_charting
.. autofunction:: bsutennis.data.load_results
.. autoclass:: bsutennis.data.Dataset
   :members:
```

## Rules: `bsutennis.rules`

`ADVANTAGE_SET`, `TEN_POINT_TIEBREAK_SET` and `MATCH_TIEBREAK` are ready-made `SetFormat`s.

```{eval-rst}
.. autoclass:: bsutennis.rules.SetFormat
   :members:
.. autoclass:: bsutennis.rules.MatchFormat
   :members:
.. autofunction:: bsutennis.rules.grand_slam
.. autofunction:: bsutennis.rules.grand_slam_final_set
.. autoclass:: bsutennis.rules.Score
   :members:
.. autofunction:: bsutennis.rules.replay
```

## Models: `bsutennis.models`

```{eval-rst}
.. automodule:: bsutennis.models.markov
.. autofunction:: bsutennis.models.win_probability
.. autofunction:: bsutennis.models.point_importance
.. autofunction:: bsutennis.models.hold_probability
.. autoclass:: bsutennis.models.Elo
   :members:
.. autofunction:: bsutennis.models.expected_score
```

## Metrics: `bsutennis.metrics`

```{eval-rst}
.. autofunction:: bsutennis.metrics.serve_return
.. autofunction:: bsutennis.metrics.serves
.. autofunction:: bsutennis.metrics.serve_entropy
.. autofunction:: bsutennis.metrics.shot_values
.. autofunction:: bsutennis.metrics.serve_shares
.. autofunction:: bsutennis.metrics.point_probabilities
.. autofunction:: bsutennis.metrics.elo
```

## Geometry: `bsutennis.geometry`

`RALLY_LANES`, `RETURN_DEPTHS` and `RETURN_ZONES` map the category names of the data tables to
`Zone` rectangles, for {meth}`TennisCourt.zone_heatmap <bsutennis.viz.TennisCourt.zone_heatmap>`.

```{eval-rst}
.. autofunction:: bsutennis.geometry.transform_coordinate
.. autofunction:: bsutennis.geometry.classify_serve_zone
.. autofunction:: bsutennis.geometry.classify_shot_depth
.. autofunction:: bsutennis.geometry.serve_zones
.. autoclass:: bsutennis.geometry.Zone
```

## Visualisation: `bsutennis.viz`

```{eval-rst}
.. autoclass:: bsutennis.viz.TennisCourt
   :members:
   :inherited-members:
.. autofunction:: bsutennis.viz.create_court_grid
.. autofunction:: bsutennis.viz.create_zone_grid
.. autofunction:: bsutennis.viz.joint_plot
.. autofunction:: bsutennis.viz.pizza
.. autofunction:: bsutennis.viz.pizza_chart
.. autoclass:: bsutennis.viz.Radar
   :members:
.. autofunction:: bsutennis.viz.sonar_chart
.. autofunction:: bsutennis.viz.sonar_from_shots
.. autofunction:: bsutennis.viz.plot_bar
.. autofunction:: bsutennis.viz.plot_bar_comparison
.. autofunction:: bsutennis.viz.plot_horizontal_bar
.. autofunction:: bsutennis.viz.plot_line
.. autofunction:: bsutennis.viz.plot_pie
.. autofunction:: bsutennis.viz.plot_table
```
