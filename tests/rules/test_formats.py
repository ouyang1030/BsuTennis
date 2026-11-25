"""Format codes: readable, and read back to the same format."""

import pytest

from bsutennis.rules import (
    ADVANTAGE_SET,
    MATCH_TIEBREAK,
    TEN_POINT_TIEBREAK_SET,
    MatchFormat,
    SetFormat,
    grand_slam,
)

CODES = {
    "bo3 6/tb7": MatchFormat(),
    "bo5 6/tb7 final 6/adv": MatchFormat(best_of=5, final_set=ADVANTAGE_SET),
    "bo5 6/tb7 final 6/tb10": MatchFormat(best_of=5, final_set=TEN_POINT_TIEBREAK_SET),
    "bo5 6/tb7 final 6/tb7@12": MatchFormat(best_of=5, final_set=SetFormat(tiebreak_at=12)),
    "bo3 6/tb7 final mtb10": MatchFormat(final_set=MATCH_TIEBREAK),
    "bo5 6/adv": MatchFormat(best_of=5, regular_set=ADVANTAGE_SET, final_set=ADVANTAGE_SET),
    "bo5 4/tb7@3 no-ad": MatchFormat(best_of=5, regular_set=SetFormat(games=4, tiebreak_at=3),
                                     final_set=SetFormat(games=4, tiebreak_at=3), no_ad=True),
}


@pytest.mark.parametrize("code, match_format", CODES.items())
def test_code(code, match_format):
    assert match_format.code == code
    assert MatchFormat.from_code(code) == match_format


@pytest.mark.parametrize("slam", ["ausopen", "frenchopen", "wimbledon", "usopen"])
@pytest.mark.parametrize("year", [2011, 2019, 2023])
def test_every_grand_slam_format_reads_back(slam, year):
    for best_of in (3, 5):
        match_format = grand_slam(slam, year, best_of)
        assert MatchFormat.from_code(match_format.code) == match_format
