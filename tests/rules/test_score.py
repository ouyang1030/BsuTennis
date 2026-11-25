from functools import reduce

import pytest

from bsutennis.rules import (
    ADVANTAGE_SET,
    TEN_POINT_TIEBREAK_SET,
    MatchFormat,
    Score,
    SetFormat,
    grand_slam_final_set,
    replay,
)

BEST_OF_3 = MatchFormat(best_of=3)
BEST_OF_5 = MatchFormat(best_of=5)


def start(match_format=BEST_OF_3, server=0) -> Score:
    return Score(match_format=match_format, game_server=server)


def play(score: Score, winners) -> Score:
    return reduce(Score.win_point, winners, score)


def win_games(score: Score, player: int, n: int = 1) -> Score:
    """``player`` wins ``n`` games to love (outside a tiebreak)."""
    return play(score, [player] * 4 * n)


def level_games(score: Score, n: int) -> Score:
    """Players win games alternately, so the set reaches n-n without ending."""
    for _ in range(n):
        score = win_games(win_games(score, 0), 1)
    return score


# --- games ------------------------------------------------------------------

def test_love_game():
    s = play(start(), [0, 0, 0])
    assert (s.point_label(0), s.point_label(1)) == ("40", "0")
    assert s.is_game_point(0) and not s.is_break_point
    s = s.win_point(0)
    assert s.games == (1, 0) and s.points == (0, 0)
    assert s.server == 1


def test_deuce_and_advantage():
    s = play(start(), [0, 1, 0, 1, 0, 1])
    assert (s.point_label(0), s.point_label(1)) == ("40", "40")
    s = s.win_point(1)
    assert (s.point_label(0), s.point_label(1)) == ("40", "AD")
    assert s.is_break_point
    s = s.win_point(0)
    assert (s.point_label(0), s.point_label(1)) == ("40", "40")
    assert play(s, [1, 1]).games == (0, 1)


def test_no_ad_deciding_point():
    s = play(start(MatchFormat(no_ad=True)), [0, 1, 0, 1, 0, 1])
    assert s.is_game_point(0) and s.is_game_point(1)
    assert s.win_point(1).games == (0, 1)


def test_side_alternates_each_point():
    s = start()
    sides = []
    for winner in [0, 1, 0, 1, 1]:
        sides.append(s.side)
        s = s.win_point(winner)
    assert sides == ["deuce", "ad", "deuce", "ad", "deuce"]


# --- sets -------------------------------------------------------------------

def test_six_four_wins_set():
    s = win_games(level_games(start(), 4), 0, 2)
    assert s.set_scores == ((6, 4),) and s.sets == (1, 0)


def test_six_five_does_not_win_set():
    s = win_games(level_games(start(), 5), 0)
    assert s.games == (6, 5) and s.set_scores == ()
    assert win_games(s, 0).set_scores == ((7, 5),)


def test_tiebreak_at_six_all():
    s = level_games(start(), 6)
    assert s.in_tiebreak
    first = s.server
    servers = []
    for _ in range(6):
        servers.append(s.server)
        s = s.win_point(0)
    assert servers == [first, 1 - first, 1 - first, first, first, 1 - first]
    assert s.is_set_point(0)
    s = s.win_point(0)
    assert s.set_scores == ((7, 6),)
    assert s.server == 1 - first  # the tiebreak's first receiver serves next


def test_tiebreak_needs_two_point_lead():
    s = play(level_games(start(), 6), [0, 1] * 6)  # 6-6 in the tiebreak
    assert not s.is_set_point(0)
    s = s.win_point(0)
    assert s.is_set_point(0)
    assert s.win_point(0).set_scores == ((7, 6),)


def test_advantage_final_set():
    fmt = MatchFormat(best_of=3, final_set=ADVANTAGE_SET)
    s = win_games(win_games(start(fmt), 0, 6), 1, 6)  # 6-0 0-6
    s = level_games(s, 6)
    assert not s.in_tiebreak
    s = win_games(level_games(s, 2), 0, 2)
    assert s.set_scores[-1] == (10, 8) and s.winner == 0


def test_ten_point_final_set_tiebreak():
    fmt = MatchFormat(best_of=3, final_set=TEN_POINT_TIEBREAK_SET)
    s = level_games(win_games(win_games(start(fmt), 0, 6), 1, 6), 6)
    assert s.in_tiebreak
    s = play(s, [0] * 9)
    assert not s.is_over
    s = s.win_point(0)
    assert s.is_over and s.set_scores[-1] == (7, 6)


def test_tiebreak_at_twelve_all():
    fmt = MatchFormat(best_of=3, final_set=SetFormat(tiebreak_at=12))
    s = level_games(win_games(win_games(start(fmt), 0, 6), 1, 6), 6)
    assert not s.in_tiebreak
    assert level_games(s, 6).in_tiebreak


def test_match_tiebreak_instead_of_final_set():
    fmt = MatchFormat(best_of=3, final_set=SetFormat(tiebreak_at=0, tiebreak_points=10))
    s = win_games(win_games(start(fmt), 0, 6), 1, 6)
    assert s.in_tiebreak
    s = play(s, [1] * 10)
    assert s.is_over and s.winner == 1 and s.set_scores[-1] == (0, 1)


# --- big points -------------------------------------------------------------

def test_break_set_and_match_point():
    s = win_games(win_games(start(BEST_OF_3), 0, 6), 0, 5)  # 6-0 5-0
    assert s.server == 1                                     # 11 games played
    s = play(s, [0, 0, 0])                                   # 0-40 on player 1's serve
    assert s.is_break_point
    assert s.is_set_point(0) and s.is_match_point(0)
    assert not s.is_set_point(1)


def test_set_point_is_not_match_point_in_first_set():
    s = play(win_games(start(BEST_OF_5), 0, 5), [0, 0, 0])
    assert s.is_set_point(0) and not s.is_match_point(0)


def test_no_break_point_in_tiebreak():
    s = play(level_games(start(), 6), [1] * 6)
    assert s.in_tiebreak and s.is_game_point(1) and not s.is_break_point


# --- replay -----------------------------------------------------------------

def test_replay_returns_score_before_each_point_and_final():
    scores = replay([0] * 48, BEST_OF_3, first_server=1)
    assert len(scores) == 49
    assert scores[0].server == 1
    assert scores[-1].is_over and str(scores[-1]).startswith("6-0 6-0")


# --- formats ----------------------------------------------------------------

@pytest.mark.parametrize(
    "slam, year, expected",
    [
        ("wimbledon", 2018, ADVANTAGE_SET),
        ("wimbledon", 2019, SetFormat(tiebreak_at=12)),
        ("ausopen", 2019, TEN_POINT_TIEBREAK_SET),
        ("frenchopen", 2021, ADVANTAGE_SET),
        ("usopen", 2015, SetFormat()),
        ("frenchopen", 2022, TEN_POINT_TIEBREAK_SET),
    ],
)
def test_grand_slam_final_set(slam, year, expected):
    assert grand_slam_final_set(slam, year) == expected
