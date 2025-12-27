# Statistical Charts

Beyond court plotting, ``BsuTennis.chart`` provides functions for general statistical visualization with a consistent aesthetic.

## Standard Charts

Import these functions from ``BsuTennis.chart``:

### Bar Charts
```python
from BsuTennis.chart import plot_bar

plot_bar(
    data=[10, 20, 15], 
    labels=['A', 'B', 'C'], 
    title="Simple Bar Chart"
)
```

![Bar Chart](../_static/test_chart_bar.png)

### Horizontal Bar Comparison (Moving Bar)
Visualize head-to-head stats.

```python
from BsuTennis.chart import plot_bar_comparison

plot_bar_comparison(
    values_left=[70, 5], 
    values_right=[65, 8], 
    labels=['1st Serve %', 'Aces'], 
    names=['Player A', 'Player B']
)
```

### Pie Charts
```python
from BsuTennis.chart import plot_pie

plot_pie(
    sizes=[60, 40], 
    labels=['In', 'Out']
)
```

### Line Charts
```python
from BsuTennis.chart import plot_line

plot_line(
    x_data=[1, 2, 3],
    y_data=[10, 15, 12]
)
```

## Radar Charts

Use the ``Radar`` class to compare multivariate data.

```python
from BsuTennis import Radar
import matplotlib.pyplot as plt

radar = Radar(
    params=['Serve', 'Return', 'Forehand', 'Backhand', 'Volley', 'Mental'],
    range_min=[0]*6,
    range_max=[100]*6
)

fig, ax = plt.subplots(figsize=(6, 6))
radar.setup_axis(ax)
radar.draw(ax, values=[80, 70, 90, 60, 50, 85], color='blue', alpha=0.3)
```

![Radar Chart](../_static/test_radar.png)
