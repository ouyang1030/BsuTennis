# Installation

To install `bsutennis`, you can use pip or Anaconda.

## Using pip:

```bash
pip install bsutennis
```
Or install via Anaconda.
```bash
conda install -c conda-forge bsutennis
```
# Quick start
```bash
from bsutennis import Pitch
import matplotlib.pyplot as plt
pitch = Pitch(pitch_color='white', line_color='gray', stripe=True)
fig, ax = pitch.draw()
plt.show()
```