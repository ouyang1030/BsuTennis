# Data Utilities

``BsuTennis.stats`` provides helper functions to preprocess data for visualization.

## Coordinate Transformation

Convert raw data coordinates (e.g., from a specific tracking system with Top-Left origin) to the centered coordinate system used by ``TennisCourt``.

```python
from BsuTennis.stats import transform_coordinate

# Assume x, y are raw data lists
x_trans, y_trans = transform_coordinate(x_raw, y_raw)
```

## Serve Zone Classification

Classify landing points into strategic zones (Wide, Body, T) based on the service box.

```python
from BsuTennis.stats import classify_serve_zone

# Returns 'Wide', 'Body', 'T', or 'Out'
zone = classify_serve_zone(x, y)
```
