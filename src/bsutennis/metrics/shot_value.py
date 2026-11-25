"""
Shot value: how much each stroke changed its hitter's chance of winning the point.

The chance after a stroke that keeps the rally going is the share of points
won by the hitters of all such strokes in the same *state* (rally phase, shot
type, wing, position, direction, ...). A stroke that ends the point leaves a
chance of 1 (ace, service winner, winner) or 0 (fault, error). The chance
before a stroke is one minus the opponent's chance after the previous one, so
a stroke's value is what it added to, or took from, its hitter's chance.

Over one point the server's values (receiver's counted negatively) add up to
the result minus the server's chance at the start of the rally. The exceptions
are points whose charted ending is missing or disagrees with the recorded
winner (0.1 % of the men's 2020s charts).

The chances are estimated from the data passed in, so values describe that
data: use many matches.
"""

import pandas as pd

TERMINAL_CHANCE = {"ace": 1.0, "service_winner": 1.0, "winner": 1.0,
                   "fault": 0.0, "forced_error": 0.0, "unforced_error": 0.0}
PHASES = {1: "serve", 2: "return", 3: "serve+1"}   # later strokes: "rally"
STATE = ("phase", "shot_type", "wing", "position", "direction", "depth")


def shot_values(dataset, state: tuple[str, ...] | list[str] = STATE) -> pd.DataFrame:
    """
    Every stroke of the rallies in ``dataset.shots``, with its value.

    Strokes of a first serve that missed are left out: the rally starts with
    the serve that went in (or with the double fault).

    Parameters
    ----------
    dataset : Dataset
        Charted matches.
    state : sequence of str
        Shot columns that describe a stroke, plus ``'phase'`` ('serve',
        'return', 'serve+1' or 'rally'). The serve number is always part of
        the state. Finer states separate more situations but rest on fewer
        strokes each.

    Returns
    -------
    DataFrame
        The shot columns, ``phase``, and ``before`` / ``after`` (the hitter's
        chance of winning the point) and ``value`` (``after - before``).
    """
    winners = dataset.points[["match_id", "point_no", "serve_no", "point_winner"]].rename(columns={"serve_no": "rally_serve"})
    rally = dataset.shots.merge(winners, on=["match_id", "point_no"])
    rally = rally[rally.serve_no == rally.rally_serve].drop(columns="rally_serve")
    rally["phase"] = rally.shot_no.map(PHASES).fillna("rally")
    hitter_won = (rally.player == rally.point_winner).astype(float)

    in_play = rally.ending.isna()
    after = rally.ending.map(TERMINAL_CHANCE)
    after[in_play] = hitter_won[in_play].groupby([rally.loc[in_play, c] for c in ["serve_no", *state]], dropna=False).transform("mean")

    before = 1 - after.groupby([rally.match_id, rally.point_no]).shift()
    serve = rally.shot_no == 1
    before[serve] = hitter_won[serve].groupby(rally.serve_no[serve]).transform("mean")
    return rally.drop(columns="point_winner").assign(before=before, after=after, value=after - before)
