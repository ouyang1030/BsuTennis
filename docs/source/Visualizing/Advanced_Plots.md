# Advanced Visualizations

Advanced density plots, statistical charts, and joint distributions for in-depth tennis analysis.

---

## Density Analysis

### KDE (Kernel Density Estimation)

Smooth contour plots showing shot concentration areas.

````carousel
![Green KDE](../_static/test_kde_green.png)
<!-- slide -->
![Red KDE](../_static/test_kde_red.png)
<!-- slide -->
![Blue KDE](../_static/test_kde_blue.png)
````

```python
court.kdeplot(ax, x, y, cmap='bsu_green', levels=50, alpha=0.6)
```

**Colormaps**: `bsu_green`, `bsu_red`, `bsu_blue`

---

### Heatmap (Grid)

Frequency distribution across defined grid cells.

![Heatmap](../_static/test_heatmap_freq.png)

```python
court.heatmap(ax, x, y, gridsize=8, statistic='frequency', half=True)
```

---

### Hexbin

Honeycomb-style density visualization.

````carousel
![Full Hexbin](../_static/test_heatmap_hex.png)
<!-- slide -->
![Half Hexbin](../_static/test_heatmap_hex_half.png)
````

```python
court.hexbin(ax, x, y, gridsize=20, cmap='bsu_green', half=True)
```

---

## Statistical Charts

### Pizza Chart

Radial bar charts for player performance metrics.

````carousel
![BSU Pizza](../_static/test_pizza_bsu.png)
<!-- slide -->
![Comparison Pizza](../_static/test_pizza_compare.png)
````

```python
from BsuTennis import pizza

stats = {'Aces': 85, 'Winners': 72, '1st Serve %': 68}
fig, ax = pizza('Player Name', stats, theme='bsu')
```

---

### Sonar Chart

Directional distribution from court zones.

````carousel
![6-Direction Sonar](../_static/test_sonar_6dir.png)
<!-- slide -->
![8-Direction Sonar](../_static/test_sonar_8dir.png)
<!-- slide -->
![Custom Sonar](../_static/test_sonar_custom.png)
````

```python
from BsuTennis import sonar_from_shots

sonar_from_shots(ax, shot_x, shot_y, shot_dx, shot_dy,
                 n_zones_x=3, n_zones_y=2, n_directions=6)
```

---

### Radar Chart

![Radar](../_static/test_radar.png)

```python
from BsuTennis import Radar

radar = Radar(params=['Speed', 'Power', 'Accuracy', 'Stamina', 'Mental'])
fig, ax = radar.setup_axis()
radar.draw_radar(ax, values=[85, 78, 92, 80, 88])
```

---

## Joint Plots

Court visualization with marginal distributions.

### Full Court (Two Players)

![Joint KDE](../_static/test_joint_kde.png)

```python
from BsuTennis import joint_plot

fig, ax = joint_plot(p1_x, p1_y, p2_x, p2_y, kind='kde', half=False)
```

### Half Court (Single Player)

````carousel
![Half Scatter](../_static/test_joint_half_scatter.png)
<!-- slide -->
![Half KDE](../_static/test_joint_half_kde.png)
<!-- slide -->
![Half Grid](../_static/test_joint_grid.png)
````

```python
fig, ax = joint_plot(x, y, kind='scatter', half=True)
```

**Visualization Types**: `scatter`, `kde`, `grid`
