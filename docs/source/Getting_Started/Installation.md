# Installation

## Requirements

- Python 3.8+
- matplotlib
- numpy
- scipy

## Install via pip

```bash
pip install bsutennis
```

## Install from source (development)

```bash
git clone https://github.com/ouyang1030/tennis.git
cd tennis
pip install -e .
```

---

# Quick Start

## Draw a Tennis Court

```python
from BsuTennis import TennisCourt
import matplotlib.pyplot as plt

# Create and draw court
court = TennisCourt(theme='bsu', half=True)
fig, ax = plt.subplots(figsize=(6, 8))
court.draw(ax=ax)
plt.show()
```

## Visualize Shot Distribution

```python
from BsuTennis import TennisCourt
import numpy as np

# Generate sample data
x = np.random.normal(0, 2, 100)
y = np.random.uniform(2, 10, 100)

# Create visualization
court = TennisCourt(half=True, theme='bsu')
fig, ax = plt.subplots(figsize=(6, 8))
court.draw(ax=ax)
court.kdeplot(ax, x, y, cmap='bsu_green', alpha=0.6)
court.scatter(ax, x, y, s=20, alpha=0.5)
plt.show()
```
