# Statistical Charts

Beyond court plotting, `BsuTennis` provides functions for general statistical visualization with a consistent aesthetic.

## Standard Charts

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

## Radar Chart (Player Comparison)

The `Radar` class creates spider/radar charts for comparing player statistics across multiple dimensions.

```python
from BsuTennis import Radar
import matplotlib.pyplot as plt

# Define parameters and ranges
params = ['Serve Speed\n(km/h)', 'First Serve\n(%)', 'Aces\n(per match)', 
          'Winners\n(per match)', 'Break Points\nWon (%)', 'Rally\nLength']
min_range = [150, 50, 0, 20, 30, 3]
max_range = [220, 80, 15, 60, 70, 8]

# Create radar instance
radar = Radar(params, min_range=min_range, max_range=max_range)

# Setup axis
fig, ax = radar.setup_axis(figsize=(10, 10))

# Draw background grid
radar.draw_circles(ax, num_rings=5)

# Draw player data
radar.draw(ax, [205, 68, 12, 48, 55, 6.5], label='Player A', color='#e74c3c')
radar.draw(ax, [195, 72, 8, 52, 62, 5.8], label='Player B', color='#3498db')

# Add legend and title
plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1))
plt.title('Player Performance Comparison', size=16, weight='bold')
plt.show()
```

![Radar Chart](../_static/test_radar.png)
