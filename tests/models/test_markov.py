"""
The independent-points model, checked three ways: against closed forms,
against known theorems, and against the rules engine itself (the exact
distribution of outcomes, propagated point by point with Score.win_point).
"""

from collections import defaultdict
from math import comb

import pytest

from bsutennis.models import hold_probability, point_importance, win_probability
from bsutennis.rules import ADVANTAGE_SET, MATCH_TIEBREAK, TEN_POINT_TIEBREAK_SET, MatchFormat, Score, SetFormat

FORMATS = {
    "best of 3": MatchFormat(),
    "best of 5, advantage final set": MatchFormat(best_of=5, final_set=ADVANTAGE_SET),
    "match tiebreak": MatchFormat(final_set=MATCH_TIEBREAK),
    "10-point final-set tiebreak": MatchFormat(best_of=5, final_set=TEN_POINT_TIEBREAK_SET),
    "no-ad short sets": MatchFormat(regular_set=SetFormat(games=4, tiebreak_at=3),
                                    final_set=SetFormat(games=4, tiebreak_at=3), no_ad=True),
}


def start(match_format, first_server=0):
    return Score(match_format=match_format, game_server=first_server)


# --- closed forms -----------------------------------------------------------------

@pytest.mark.parametrize("p", [0.5, 0.6, 0.75])
def test_hold_probability_matches_the_closed_form(p):
    q = 1 - p
    closed = p**4 * (1 + 4 * q + 10 * q**2) + 20 * p**3 * q**3 * p**2 / (1 - 2 * p * q)
    assert hold_probability(p) == pytest.approx(closed, abs=1e-12)


def test_no_ad_hold_is_winning_four_of_seven_points():
    p = 0.62
    closed = sum(comb(7, k) * p**k * (1 - p) ** (7 - k) for k in range(4, 8))
    assert hold_probability(p, no_ad=True) == pytest.approx(closed, abs=1e-12)


# --- theorems -----------------------------------------------------------------------

@pytest.mark.parametrize("match_format", FORMATS.values(), ids=FORMATS.keys())
def test_equal_players_have_equal_chances(match_format):
    assert win_probability(start(match_format), (0.63, 0.63)) == pytest.approx(0.5, abs=1e-12)


@pytest.mark.parametrize("match_format", FORMATS.values(), ids=FORMATS.keys())
def test_serving_first_does_not_matter(match_format):
    """Newton & Keller (2005): under independent points, who serves first does not
    change the probability of winning a set or a match."""
    p_serve = (0.66, 0.6)
    assert win_probability(start(match_format, 0), p_serve) == pytest.approx(
        win_probability(start(match_format, 1), p_serve), abs=1e-12)


# --- the rules engine ----------------------------------------------------------------

def propagate(score, p_serve, n_points):
    """Exact chance that player 0 has won after ``n_points`` points, and the chance
    that the match is still on, by pushing the distribution of scores forward."""
    states, won = {score: 1.0}, 0.0
    for _ in range(n_points):
        following = defaultdict(float)
        for s, chance in states.items():
            p = p_serve[0] if s.server == 0 else 1 - p_serve[1]
            for winner, q in [(0, p), (1, 1 - p)]:
                t = s.win_point(winner)
                if t.is_over:
                    won += chance * q * (t.winner == 0)
                else:
                    following[t] += chance * q
        states = following
    return won, sum(states.values())


@pytest.mark.parametrize(
    "set_format, n_points",
    [
        (SetFormat(games=4, tiebreak_at=4), 140),
        (SetFormat(games=4, tiebreak_at=6), 160),   # tiebreak only after a longer advantage phase
        (MATCH_TIEBREAK, 80),
        (SetFormat(games=2, tiebreak_at=None), 150),
    ],
    ids=["tiebreak set", "late tiebreak", "match tiebreak", "advantage set"],
)
def test_one_set_agrees_with_the_rules_engine(set_format, n_points):
    """Short sets keep the exact propagation fast; the model code is the same for any length."""
    one_set = MatchFormat(best_of=1, final_set=set_format)
    p_serve = (0.6, 0.55)
    won, unfinished = propagate(start(one_set), p_serve, n_points)
    # Sets with a tiebreak are all but finished; advantage sets have a long tail of
    # deuces, which the exact check below then brackets less tightly.
    assert unfinished < 1e-2
    assert won - 1e-12 <= win_probability(start(one_set), p_serve) <= won + unfinished + 1e-12


def test_every_score_is_the_average_of_the_next_two():
    """P(score) = p * P(after winning the point) + (1 - p) * P(after losing it), at
    every score of a long, close match."""
    match_format, p_serve = FORMATS["best of 5, advantage final set"], (0.7, 0.68)
    score, rng_state = start(match_format), 12345
    while not score.is_over:
        p = p_serve[0] if score.server == 0 else 1 - p_serve[1]
        expected = p * win_probability(score.win_point(0), p_serve) + (1 - p) * win_probability(score.win_point(1), p_serve)
        assert win_probability(score, p_serve) == pytest.approx(expected, abs=1e-12)
        rng_state = (1103515245 * rng_state + 12345) % 2**31   # deterministic sequence of winners
        score = score.win_point(0 if rng_state / 2**31 < p else 1)


# --- importance ---------------------------------------------------------------------

def test_a_break_point_matters_more_than_a_point_at_40_0():
    score = start(MatchFormat())
    for _ in range(3):
        score = score.win_point(1)          # 0-40 on player 0's serve
    break_point = score
    game_point = start(MatchFormat()).win_point(0).win_point(0).win_point(0)   # 40-0
    p_serve = (0.64, 0.64)
    assert point_importance(break_point, p_serve) > 3 * point_importance(game_point, p_serve) > 0


def test_finished_match():
    score = start(MatchFormat(best_of=1, final_set=MATCH_TIEBREAK))
    for _ in range(10):
        score = score.win_point(1)
    assert score.is_over and win_probability(score, (0.9, 0.1)) == 0.0
