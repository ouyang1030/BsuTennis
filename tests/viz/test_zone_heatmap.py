"""zone_heatmap shades the zones of categorical data."""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from bsutennis import TennisCourt
from bsutennis.geometry import RETURN_ZONES, serve_zones


def zone_patches(ax):
    return [p for p in ax.patches if isinstance(p, Rectangle) and p.get_zorder() == 1]


def test_one_shaded_rectangle_per_value():
    court = TennisCourt(half=True)
    fig, ax = plt.subplots()
    court.draw(ax=ax)
    shares = pd.Series({"wide": 0.5, "T": 0.3, "body": 0.2})
    mappable = court.zone_heatmap(ax, shares, serve_zones("deuce"), cmap="bsu_red")
    patches = zone_patches(ax)
    assert len(patches) == 3
    assert sorted(t.get_text() for t in ax.texts) == ["20%", "30%", "50%"]
    assert (mappable.norm.vmin, mappable.norm.vmax) == (0.2, 0.5)
    darkest = min(patches, key=lambda p: sum(p.get_facecolor()[:3]))
    assert darkest.get_x() < -2.7  # the wide lane, where half the serves went


def test_zones_without_a_value_stay_blank_and_keys_can_be_pairs():
    court = TennisCourt(half=True)
    fig, ax = plt.subplots()
    returns = pd.Series({("left", "deep"): 12, ("middle", "short"): 3})  # like groupby(["direction", "depth"]).size()
    court.zone_heatmap(ax, returns, RETURN_ZONES, annot=False)
    assert len(zone_patches(ax)) == 2 and not ax.texts


def test_horizontal_court_swaps_the_axes():
    court = TennisCourt(half=True, orientation="horizontal")
    fig, ax = plt.subplots()
    court.zone_heatmap(ax, {"T": 1.0}, serve_zones("ad"))
    [patch] = zone_patches(ax)
    assert (patch.get_x(), patch.get_y()) == (0, 0)  # T lane of the ad box starts at the net and the centre line
    assert patch.get_width() > patch.get_height()
