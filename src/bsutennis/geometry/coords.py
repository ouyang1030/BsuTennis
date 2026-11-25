"""
Coordinate systems.

Standard frame (used everywhere inside bsutennis)
-------------------------------------------------
- Origin ``(0, 0)`` at the centre of the net, units in metres.
- ``x`` runs across the court (sidelines at ``±5.485`` doubles / ``±4.115`` singles).
- ``y`` runs along the court (baselines at ``±11.885``).

Plotting functions only *rotate* this frame for display
(``orientation='horizontal'``); data are never stored in a plot frame.

Raw corner frame
----------------
Some annotation tools record positions from the far-left doubles corner:
``x`` in ``[0, 10.97]`` across the court and ``y`` in ``[0, 23.77]`` along it.
:func:`transform_coordinate` converts that frame to the standard frame.
"""

import numpy as np
import pandas as pd

from .dimensions import HALF_LENGTH, HALF_WIDTH_DOUBLES


def _restore_type(template, values):
    """Return ``values`` as the same kind of object as ``template``."""
    if isinstance(template, pd.Series):
        return pd.Series(values, index=template.index, name=template.name)
    if np.ndim(template) == 0:
        return float(values)
    return values


def transform_coordinate(x, y, fold=True):
    """
    Convert raw corner-frame coordinates to the standard frame.

    Parameters
    ----------
    x, y : float, array-like or pandas.Series
        Positions in the raw corner frame (see module docstring).
    fold : bool, default True
        If True, points on the near half (``y < 0`` after shifting) are
        rotated by 180° onto the far half, so every landing point ends up
        with ``y >= 0``. This is the usual convention for shot-placement
        plots, where the hitter is drawn at the bottom.

    Returns
    -------
    new_x, new_y
        Same type as the inputs (scalar, ``ndarray`` or ``Series``).

    Examples
    --------
    >>> transform_coordinate(5.485, 11.885)
    (0.0, 0.0)
    >>> transform_coordinate([0, 0], [0, 23.77])
    (array([-5.485,  5.485]), array([11.885, 11.885]))
    """
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)

    new_x = xa - HALF_WIDTH_DOUBLES
    new_y = HALF_LENGTH - ya

    if fold:
        near = new_y < 0
        new_x = np.where(near, -new_x, new_x)
        new_y = np.where(near, -new_y, new_y)

    return _restore_type(x, new_x), _restore_type(y, new_y)
