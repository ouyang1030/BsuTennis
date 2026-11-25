"""
Parser for the shot notation of the Match Charting Project.

A point is charted in one cell per serve. A cell holds the serve and, if the
serve went in, the whole rally::

    6f29b1*       serve down the T; deep forehand return down the middle;
                  backhand to the hitter's left lane, a winner
    5d            body serve, long: a fault, the next cell holds the 2nd serve

The notation is defined in the 'Instructions' sheet of the MCP spreadsheet.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Stroke:
    shot_type: str | None
    wing: str | None
    direction: str | None
    depth: str | None
    position: str
    approach: bool
    ending: str | None
    error: str | None


# --- codes -------------------------------------------------------------------

STROKES = {  # letter: (wing, shot type); 'q' is an unknown shot
    "f": ("forehand", "groundstroke"), "b": ("backhand", "groundstroke"),
    "r": ("forehand", "slice"), "s": ("backhand", "slice"),
    "v": ("forehand", "volley"), "z": ("backhand", "volley"),
    "o": ("forehand", "overhead"), "p": ("backhand", "overhead"),
    "u": ("forehand", "drop_shot"), "y": ("backhand", "drop_shot"),
    "l": ("forehand", "lob"), "m": ("backhand", "lob"),
    "h": ("forehand", "half_volley"), "i": ("backhand", "half_volley"),
    "j": ("forehand", "swinging_volley"), "k": ("backhand", "swinging_volley"),
    "t": (None, "trick"), "q": (None, None),
}
HIT_AT_NET = {"volley", "overhead", "half_volley", "swinging_volley"}
SERVE_DIRECTIONS = {"4": "wide", "5": "body", "6": "T"}
# "1 = to a right-hander's forehand side" is the left lane as seen by the hitter.
RALLY_DIRECTIONS = {"1": "left", "2": "middle", "3": "right"}
RETURN_DEPTHS = {"7": "short", "8": "medium", "9": "deep"}
ERRORS = {
    "n": "net", "w": "wide", "d": "deep", "x": "wide_deep",
    "g": "foot_fault", "!": "shank", "e": "unknown",
}
SERVE_ENDINGS = {"*": "ace", "#": "service_winner"}
RALLY_ENDINGS = {"*": "winner", "#": "forced_error", "@": "unforced_error"}

# Whole-point codes: the point is recorded without shots. Value: True if the server won.
UNCHARTED = {"S": True, "R": False, "P": False, "Q": True}  # P / Q: point penalty
TIME_VIOLATION = "V"  # the server loses the serve

SERVE = re.compile(
    r"c*"                               # lets
    r"(?P<direction>[0456])?"
    r"(?P<marks>[+;]*)"                 # + serve-and-volley, ; net cord
    r"(?:(?P<fault>[nwdxge!]);*|(?P<end>[*#]))?"
)
SHOT = re.compile(
    r"(?P<letter>[fbrsvzopuylmhijktq])"
    r"(?P<marks>[+\-=;^!]*)"            # + approach, - at net, = at baseline, ; ^ !
    r"(?P<direction>[0-3])?"
    r"(?P<depth>[0789])?"
    r"(?P<marks_after>[+\-=;^!]*)"
    r"(?P<error>[nwdxe!])?"
    r"(?P<end>[*#@])?"
)
CHALLENGE_STOP = "C"  # play stopped by a wrong challenge; ends the rally


# --- parsing -----------------------------------------------------------------

def parse_point(first: str, second: str) -> list[list[Stroke]] | None:
    """
    The strokes of a point: one list per serve (one or two lists).

    Returns ``[]`` for points recorded without shots (codes S, R, P, Q) and
    None if a cell does not follow the notation.
    """
    if first in UNCHARTED:
        return []
    serves = [parse_cell(first)]
    if serves[0] is not None and serves[0][0].ending == "fault":
        serves.append(parse_cell(second))
    return None if None in serves else serves


def parse_cell(code: str) -> list[Stroke] | None:
    """Strokes of one serve cell, or None if ``code`` does not follow the notation."""
    if code == TIME_VIOLATION:
        return [_serve(direction=None, marks="", fault="V", end=None)]

    serve = SERVE.match(code)
    strokes = [_serve(serve["direction"], serve["marks"], serve["fault"], serve["end"])]
    pos = serve.end()
    if pos == 0:
        return None  # nothing recognisable as a serve
    if strokes[0].ending is not None:
        return strokes if pos == len(code) else None

    while pos < len(code) and code[pos:] != CHALLENGE_STOP:
        shot = SHOT.match(code, pos)
        if shot is None or strokes[-1].ending is not None:
            return None  # unknown code, or strokes after the rally ended
        strokes.append(_rally_stroke(shot, is_return=len(strokes) == 1))
        pos = shot.end()
    return strokes


def _serve(direction, marks, fault, end) -> Stroke:
    error = "time_violation" if fault == "V" else ERRORS.get(fault)
    return Stroke(
        shot_type="serve",
        wing=None,
        direction=SERVE_DIRECTIONS.get(direction),
        depth=None,
        position="baseline",
        approach="+" in marks,
        ending="fault" if fault else SERVE_ENDINGS.get(end),
        error=error,
    )


def _rally_stroke(shot: re.Match, is_return: bool) -> Stroke:
    wing, shot_type = STROKES[shot["letter"]]
    marks = shot["marks"] + shot["marks_after"]
    if "-" in marks:
        position = "net"
    elif "=" in marks:
        position = "baseline"
    else:
        position = "net" if shot_type in HIT_AT_NET else "baseline"
    ending = RALLY_ENDINGS.get(shot["end"])
    error = ERRORS.get(shot["error"])
    if error is None and "!" in marks and ending in ("forced_error", "unforced_error"):
        error = "shank"
    return Stroke(
        shot_type=shot_type,
        wing=wing,
        direction=RALLY_DIRECTIONS.get(shot["direction"]),
        depth=RETURN_DEPTHS.get(shot["depth"]) if is_return else None,
        position=position,
        approach="+" in marks,
        ending=ending,
        error=error,
    )
