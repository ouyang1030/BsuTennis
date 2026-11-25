"""The Elo update."""

import pytest

from bsutennis.models import Elo, expected_score


def test_expected_score():
    assert expected_score(1500, 1500) == 0.5
    assert expected_score(1900, 1500) == pytest.approx(10 / 11)   # 400 points: odds of 10 to 1
    assert expected_score(1600, 1500) + expected_score(1500, 1600) == pytest.approx(1)


def test_newcomers_exchange_the_same_points():
    system = Elo()
    assert system.play("Ann", "Bo") == 0.5
    k = 250 / 5 ** 0.4
    assert system.ratings == pytest.approx({"Ann": 1500 + k / 2, "Bo": 1500 - k / 2})


def test_ratings_settle_with_experience():
    system = Elo()
    for _ in range(20):
        system.play("Ann", "Bo")
    assert system.k("Ann") < system.k("Cy")       # Cy has not played yet
    ann = system.rating("Ann")
    system.play("Cy", "Ann")                      # an upset: Cy gains more than Ann loses
    assert system.rating("Cy") - 1500 > ann - system.rating("Ann") > 0
