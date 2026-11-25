"""Zone maps: the rectangles behind the category names of the data tables."""

import numpy as np
import pytest

from bsutennis.geometry import (
    RALLY_LANES,
    RETURN_DEPTHS,
    RETURN_ZONES,
    classify_serve_zone,
    classify_shot_depth,
    serve_zones,
)
from bsutennis.geometry.dimensions import HALF_LENGTH, HALF_WIDTH_SINGLES, SERVICE_LINE_DISTANCE, WIDTH_SINGLES


def centre(zone):
    return (zone.x0 + zone.x1) / 2, (zone.y0 + zone.y1) / 2


@pytest.mark.parametrize("side", ["deuce", "ad"])
def test_serve_zones_agree_with_the_classifier(side):
    for name, zone in serve_zones(side).items():
        assert classify_serve_zone(*centre(zone)) == name


def test_depth_bands_agree_with_the_classifier():
    for name, zone in RETURN_DEPTHS.items():
        assert classify_shot_depth(centre(zone)[1]) == name


def test_deuce_box_is_on_the_servers_left():
    assert all(z.x1 <= 0 for z in serve_zones("deuce").values())
    assert all(z.x0 >= 0 for z in serve_zones("ad").values())
    assert serve_zones("deuce")["wide"].x0 == -HALF_WIDTH_SINGLES


def test_rally_lanes_are_30_40_30_percent_of_the_width():
    widths = [(z.x1 - z.x0) / WIDTH_SINGLES for z in RALLY_LANES.values()]
    assert np.allclose(widths, [0.3, 0.4, 0.3])
    assert RALLY_LANES["left"].x0 == -HALF_WIDTH_SINGLES  # left as seen by the hitter facing +y


def test_return_depths_split_at_the_service_line_and_halfway_to_the_baseline():
    short, medium, deep = RETURN_DEPTHS.values()
    assert (short.y0, short.y1, deep.y1) == (0, SERVICE_LINE_DISTANCE, HALF_LENGTH)
    assert medium.y1 - SERVICE_LINE_DISTANCE == pytest.approx(HALF_LENGTH - deep.y0)


def test_return_zones_cross_lanes_and_depths():
    assert set(RETURN_ZONES) == {(lane, depth) for lane in RALLY_LANES for depth in RETURN_DEPTHS}
    assert RETURN_ZONES["right", "deep"] == (RALLY_LANES["right"].x0, HALF_WIDTH_SINGLES,
                                              RETURN_DEPTHS["deep"].y0, HALF_LENGTH)
