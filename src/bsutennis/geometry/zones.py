"""
Court zones in the standard frame (see :mod:`bsutennis.geometry.coords`).

Two kinds of helpers:

- *classifiers* turn landing coordinates into zone names (scalars or arrays
  in, a scalar or an object ``ndarray`` out);
- *zone maps* give the rectangle of each zone name used in the data tables
  (serve ``direction``, rally lanes, return ``depth``), so that counts per
  category can be drawn on the court.

Zones lie on the far half (``y >= 0``): the ball is hit from the near side.
"""

from typing import NamedTuple

import numpy as np

from .dimensions import HALF_LENGTH, HALF_WIDTH_SINGLES, SERVICE_LINE_DISTANCE, WIDTH_SINGLES

# Each service box is split into three equal-width lanes.
_THIRD = HALF_WIDTH_SINGLES / 3

# Depth (metres from the net): 'short' inside the service box, then 'medium' or 'deep'
# by whether the ball lands closer to the service line or to the baseline, the way the
# Match Charting Project charts return depth.
DEPTH_EDGE = (SERVICE_LINE_DISTANCE + HALF_LENGTH) / 2


def _finish(scalar_input, result):
    return result[0] if scalar_input else result


def classify_serve_zone(x, y):
    """
    Classify a serve landing point as ``'wide'``, ``'body'``, ``'T'`` or ``'out'``,
    the names of the ``serve_direction`` column of the data tables.

    Coordinates must be in the standard frame with the landing point on the
    far half (``y > 0``), e.g. after :func:`~bsutennis.geometry.coords.transform_coordinate`.
    Each service box is split into three equal lanes across its width.

    Parameters
    ----------
    x, y : float or array-like

    Returns
    -------
    str or numpy.ndarray of str
    """
    xa = np.atleast_1d(np.asarray(x, dtype=float))
    ya = np.atleast_1d(np.asarray(y, dtype=float))
    scalar_input = np.ndim(x) == 0 and np.ndim(y) == 0

    in_depth = (ya > 0) & (ya <= SERVICE_LINE_DISTANCE)
    H, T = HALF_WIDTH_SINGLES, _THIRD

    conditions = [
        ~in_depth,
        (xa >= -H) & (xa < -2 * T),   # left box, wide
        (xa >= -2 * T) & (xa < -T),   # left box, body
        (xa >= -T) & (xa <= 0),       # left box, T
        (xa > 0) & (xa < T),          # right box, T
        (xa >= T) & (xa < 2 * T),     # right box, body
        (xa >= 2 * T) & (xa <= H),    # right box, wide
    ]
    choices = ['out', 'wide', 'body', 'T', 'T', 'body', 'wide']
    result = np.select(conditions, choices, default='out').astype(object)
    return _finish(scalar_input, result)


def classify_shot_depth(y):
    """
    Classify shot depth from the landing ``y`` coordinate (``y > 0``).

    - ``'short'``: inside the service box (``y <= 6.40``)
    - ``'medium'``: closer to the service line than to the baseline (``y <= 9.14``)
    - ``'deep'``: closer to the baseline

    The same bands as the ``depth`` column of the data tables and :data:`RETURN_DEPTHS`.

    Parameters
    ----------
    y : float or array-like

    Returns
    -------
    str or numpy.ndarray of str
    """
    ya = np.atleast_1d(np.asarray(y, dtype=float))
    scalar_input = np.ndim(y) == 0

    conditions = [
        ya <= SERVICE_LINE_DISTANCE,
        (ya > SERVICE_LINE_DISTANCE) & (ya <= DEPTH_EDGE),
        ya > DEPTH_EDGE,
    ]
    result = np.select(conditions, ['short', 'medium', 'deep'], default=None).astype(object)
    return _finish(scalar_input, result)


# --- zone maps --------------------------------------------------------------------

class Zone(NamedTuple):
    """A rectangle in the standard frame."""
    x0: float
    x1: float
    y0: float
    y1: float


def serve_zones(side: str) -> dict[str, Zone]:
    """
    The ``'wide'``, ``'body'`` and ``'T'`` thirds of the service box a serve
    from the ``side`` (``'deuce'`` or ``'ad'``) lands in, as in
    :func:`classify_serve_zone`.

    The server stands at the near baseline facing ``+y``; the deuce box is on
    the server's left (``x < 0``).
    """
    sign = -1 if side == "deuce" else 1
    lanes = {"T": (0, _THIRD), "body": (_THIRD, 2 * _THIRD), "wide": (2 * _THIRD, HALF_WIDTH_SINGLES)}
    return {name: _zone(sign * a, sign * b, 0, SERVICE_LINE_DISTANCE) for name, (a, b) in lanes.items()}


# Rally lanes as seen by the hitter at the near baseline: the outer 30 % and the
# middle 40 % of the singles width, where the ball crosses the far baseline.
LANE_EDGE = 0.2 * WIDTH_SINGLES
RALLY_LANES = {
    "left": Zone(-HALF_WIDTH_SINGLES, -LANE_EDGE, 0, HALF_LENGTH),
    "middle": Zone(-LANE_EDGE, LANE_EDGE, 0, HALF_LENGTH),
    "right": Zone(LANE_EDGE, HALF_WIDTH_SINGLES, 0, HALF_LENGTH),
}

# Depth bands as rectangles, as in classify_shot_depth.
RETURN_DEPTHS = {
    "short": Zone(-HALF_WIDTH_SINGLES, HALF_WIDTH_SINGLES, 0, SERVICE_LINE_DISTANCE),
    "medium": Zone(-HALF_WIDTH_SINGLES, HALF_WIDTH_SINGLES, SERVICE_LINE_DISTANCE, DEPTH_EDGE),
    "deep": Zone(-HALF_WIDTH_SINGLES, HALF_WIDTH_SINGLES, DEPTH_EDGE, HALF_LENGTH),
}

# Returns by lane and depth, keyed like ``shots.groupby(["direction", "depth"])``.
RETURN_ZONES = {
    (lane, depth): Zone(across.x0, across.x1, along.y0, along.y1)
    for lane, across in RALLY_LANES.items()
    for depth, along in RETURN_DEPTHS.items()
}


def _zone(xa: float, xb: float, y0: float, y1: float) -> Zone:
    return Zone(min(xa, xb), max(xa, xb), y0, y1)
