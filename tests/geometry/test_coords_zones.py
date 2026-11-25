import numpy as np
import pandas as pd
import pytest

from bsutennis import classify_serve_zone, classify_shot_depth, transform_coordinate


# --- transform_coordinate -------------------------------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ((5.485, 11.885), (0.0, 0.0)),        # net centre
        ((0.0, 0.0), (-5.485, 11.885)),       # far-left corner, no fold
        ((0.0, 23.77), (5.485, 11.885)),      # near-left corner, folded to far half
    ],
)
def test_transform_scalar(raw, expected):
    x, y = transform_coordinate(*raw)
    assert isinstance(x, float) and isinstance(y, float)
    assert (x, y) == pytest.approx(expected)


def test_transform_array_matches_scalar():
    rng = np.random.default_rng(0)
    xs = rng.uniform(0, 10.97, 50)
    ys = rng.uniform(0, 23.77, 50)
    vx, vy = transform_coordinate(xs, ys)
    for i in range(len(xs)):
        sx, sy = transform_coordinate(float(xs[i]), float(ys[i]))
        assert (vx[i], vy[i]) == pytest.approx((sx, sy))
    assert np.all(vy >= 0)


def test_transform_series_keeps_index():
    df = pd.DataFrame({"x": [0.0, 5.485], "y": [23.77, 11.885]}, index=["a", "b"])
    x, y = transform_coordinate(df["x"], df["y"])
    assert isinstance(x, pd.Series)
    assert list(x.index) == ["a", "b"]
    assert x["a"] == pytest.approx(5.485)


def test_transform_no_fold():
    _, y = transform_coordinate(0.0, 23.77, fold=False)
    assert y == pytest.approx(-11.885)


# --- classify_serve_zone --------------------------------------------------

@pytest.mark.parametrize(
    "x, y, zone",
    [
        (0.1, 5.0, "T"),
        (-0.1, 5.0, "T"),
        (2.0, 5.0, "body"),
        (-2.0, 5.0, "body"),
        (4.0, 5.0, "wide"),
        (-4.0, 5.0, "wide"),
        (1.0, 7.0, "out"),     # long
        (4.5, 5.0, "out"),     # wide of singles line
        (1.0, 0.0, "out"),     # at the net
    ],
)
def test_serve_zone_scalar(x, y, zone):
    assert classify_serve_zone(x, y) == zone


def test_serve_zone_vectorised():
    x = np.array([0.1, 2.0, 4.0, 1.0])
    y = np.array([5.0, 5.0, 5.0, 7.0])
    assert list(classify_serve_zone(x, y)) == ["T", "body", "wide", "out"]


# --- classify_shot_depth --------------------------------------------------

def test_shot_depth():
    assert classify_shot_depth(3.0) == "short"
    assert classify_shot_depth(8.0) == "medium"
    assert classify_shot_depth(10.0) == "deep"
    assert list(classify_shot_depth([3.0, 8.0, 10.0])) == ["short", "medium", "deep"]
    # halfway between the service line (6.40 m) and the baseline (11.885 m)
    assert list(classify_shot_depth([9.14, 9.15])) == ["medium", "deep"]
