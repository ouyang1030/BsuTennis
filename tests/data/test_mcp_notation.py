"""The examples of the MCP 'Instructions' sheet, and a few real-world variants."""

import pytest

from bsutennis.data.sources.mcp_notation import parse_cell, parse_point


def endings(strokes):
    return [s.ending for s in strokes]


# --- serves ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "code, direction, ending, error",
    [
        ("6", "T", None, None),
        ("5*", "body", "ace", None),
        ("6#", "T", "service_winner", None),
        ("6x", "T", "fault", "wide_deep"),
        ("5d", "body", "fault", "deep"),
        ("cc4e", "wide", "fault", "unknown"),   # two lets, then an unseen fault
        ("4x;", "wide", "fault", "wide_deep"),  # fault off the net cord
        ("n", None, "fault", "net"),            # direction not recorded
        ("V", None, "fault", "time_violation"),
    ],
)
def test_serve(code, direction, ending, error):
    [serve] = parse_cell(code)
    assert (serve.shot_type, serve.direction, serve.ending, serve.error) == ("serve", direction, ending, error)


def test_serve_and_volley():
    serve, ret, volley = parse_cell("4+b27v1*")
    assert serve.approach and serve.direction == "wide"
    assert (ret.wing, ret.direction, ret.depth) == ("backhand", "middle", "short")
    assert (volley.shot_type, volley.position, volley.ending) == ("volley", "net", "winner")


# --- rallies --------------------------------------------------------------------

def test_rally_after_second_serve():
    first, second = parse_point("5d", "4s39b3b1w@")
    assert endings(first) == ["fault"]
    serve, ret, b3, b1 = second
    assert (ret.shot_type, ret.wing, ret.direction, ret.depth) == ("slice", "backhand", "right", "deep")
    assert b3.depth is None  # depth is only charted on returns
    assert (b1.direction, b1.ending, b1.error) == ("left", "unforced_error", "wide")


@pytest.mark.parametrize(
    "code, ending, error",
    [("6f#", "forced_error", None), ("6f2d@", "unforced_error", "deep"), ("6b3n#", "forced_error", "net")],
)
def test_return_errors(code, ending, error):
    _, ret = parse_cell(code)
    assert (ret.ending, ret.error) == (ending, error)


@pytest.mark.parametrize(
    "code, position, approach",
    [
        ("6f-1", "net", False),       # groundstroke hit at the net
        ("6o=2", "baseline", False),  # smash from the baseline
        ("6b+2", "baseline", True),   # approach shot
        ("6z^2*", "net", False),      # stop volley
        ("6f;1*", "baseline", False), # net cord
    ],
)
def test_position_and_approach(code, position, approach):
    stroke = parse_cell(code)[-1]
    assert (stroke.position, stroke.approach) == (position, approach)


def test_shank_written_as_a_mark():
    assert parse_cell("6f1!@")[-1].error == "shank"


def test_rally_stopped_by_a_wrong_challenge():
    assert endings(parse_cell("6b29C")) == [None, None]


# --- whole points -----------------------------------------------------------------

def test_double_fault():
    first, second = parse_point("6n", "4w")
    assert endings(first) == endings(second) == ["fault"]


def test_time_violation_then_second_serve():
    first, second = parse_point("V", "4*")
    assert first[0].error == "time_violation" and second[0].ending == "ace"


@pytest.mark.parametrize("code", ["S", "R", "P", "Q"])
def test_points_recorded_without_shots(code):
    assert parse_point(code, "") == []


@pytest.mark.parametrize(
    "first, second",
    [
        ("6f12b3*", ""),   # 2 is not a return depth
        ("2m2j2n@", ""),   # 2 is not a serve direction
        ("4*f1", ""),      # strokes after an ace
        ("6d", ""),        # fault with no second serve recorded
    ],
)
def test_codes_outside_the_notation(first, second):
    assert parse_point(first, second) is None
