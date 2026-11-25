# Installation

```bash
pip install bsutennis
```

bsutennis needs Python 3.10 or newer; numpy, pandas, matplotlib and scipy are installed with it.

## From source

```bash
git clone https://github.com/ouyang1030/BsuTennis.git
cd BsuTennis
pip install -e ".[dev]"   # package + test and docs dependencies
pytest                    # offline tests
pytest -m network         # tests that download data
```

---

# Quick Start

## Draw a Tennis Court

```python
from bsutennis import TennisCourt
import matplotlib.pyplot as plt

# Create and draw court
court = TennisCourt(theme='bsu', half=True)
fig, ax = plt.subplots(figsize=(6, 8))
court.draw(ax=ax)
plt.show()
```

## Visualize Shot Distribution

```python
from bsutennis import TennisCourt
import matplotlib.pyplot as plt
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
