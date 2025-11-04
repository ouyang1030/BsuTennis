# Tennis Court Plot and Data Analysis

`bsutennis` is a Python package designed to create visualizations of tennis courts and provide tools for tennis-related data analysis. It supports various pitch types and offers a wide range of plotting options.

## Installation

To install `bsutennis`, you can use pip or Anaconda.

### Using pip:

```bash
pip install bsutennis
```
Or install via Anaconda.
```bash
conda install -c conda-forge bsutennis
```
## Quick start
```bash
from bsutennis import Pitch
import matplotlib.pyplot as plt
pitch = Pitch(pitch_color='white', line_color='gray', stripe=True)
fig, ax = pitch.draw()
plt.show()
```
## What is bsutennis
In bsutennis, you can:

- plot tennis courts on nine different pitch types 
- plot radar charts 
- plot Nightingale/pizza charts 
- plot bumpy charts for showing changes over time 
- plot arrows, heatmaps, hexbins, scatter, and (comet) lines 
- load ATP data as a tidy dataframe 
- standardize pitch coordinates into a single format 

## License
```
Copyright (c) 2023 bsutennis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```