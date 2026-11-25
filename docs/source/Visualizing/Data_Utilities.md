# Data Utilities

``bsutennis.geometry`` provides helper functions to preprocess data for visualization.

## Coordinate Transformation

Convert raw data coordinates (e.g., from a specific tracking system with Top-Left origin) to the centered coordinate system used by ``TennisCourt``.

```python
from bsutennis.geometry import transform_coordinate

# x_raw, y_raw: scalars, arrays or pandas Series (the index is kept)
x_trans, y_trans = transform_coordinate(x_raw, y_raw)
```

## Serve Zone Classification

Classify landing points into strategic zones (wide, body, T) based on the service box. The names
are those of the `serve_direction` column of the data tables, so classified tracking data and
charted data can be compared directly.

```python
from bsutennis.geometry import classify_serve_zone

# Returns 'wide', 'body', 'T', or 'out'
zone = classify_serve_zone(x, y)
```
