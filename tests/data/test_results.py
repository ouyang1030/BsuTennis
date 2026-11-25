"""Offline tests of the ATP/WTA results loader on hand-made rows (fictional players)."""

import pandas as pd
import pytest

from bsutennis.data import MATCH_COLUMNS, PLAYER_COLUMNS
from bsutennis.data.sources.results import parse, read_score


@pytest.mark.parametrize(
    "score, scoreline, status",
    [
        ("6-4 7-6(5)", "6-4 7-6", "completed"),
        ("4-6 7-6(0) 6-2 6-4", "4-6 7-6 6-2 6-4", "completed"),
        ("6-3 3-6 [10-7]", "6-3 3-6 1-0", "completed"),   # match tiebreak
        ("12-10 1-2 RET", "12-10 1-2", "retired"),
        ("W/O", None, "walkover"),
        ("6-1 DEF", "6-1", "default"),
        ("3-1 Played and abandoned", "3-1", "abandoned"),
        ("UNK", None, "unknown"),
        ("7-Oct 6-4", None, "unknown"),                    # spreadsheet damage
        ("6-2-6-2", None, "unknown"),
        ("", None, "unknown"),
    ],
)
def test_read_score(score, scoreline, status):
    assert read_score(score) == (scoreline, status)


def source_row(**changes) -> dict:
    row = {
        "tourney_id": "2023-540", "tourney_name": "Wimbledon", "surface": "Grass", "draw_size": "128",
        "tourney_level": "G", "tourney_date": "20230703", "match_num": "701", "round": "F",
        "score": "1-6 7-6(6) 6-1 3-6 6-4", "best_of": "5", "minutes": "282",
        "winner_id": "100001", "winner_seed": "1", "winner_entry": "", "winner_name": "Adam A",
        "winner_hand": "R", "winner_ht": "183", "winner_ioc": "ESP", "winner_age": "20.2",
        "loser_id": "100002", "loser_seed": "2", "loser_entry": "", "loser_name": "Ben B",
        "loser_hand": "R", "loser_ht": "188", "loser_ioc": "SRB", "loser_age": "36.1",
        "w_ace": "9", "w_df": "4", "w_svpt": "172", "w_1stIn": "104", "w_1stWon": "73", "w_2ndWon": "33",
        "w_SvGms": "23", "w_bpSaved": "5", "w_bpFaced": "10",
        "l_ace": "4", "l_df": "1", "l_svpt": "162", "l_1stIn": "111", "l_1stWon": "73", "l_2ndWon": "26",
        "l_SvGms": "24", "l_bpSaved": "5", "l_bpFaced": "10",
        "winner_rank": "1", "winner_rank_points": "9815", "loser_rank": "2", "loser_rank_points": "7595",
    }
    return {**row, **changes}


@pytest.fixture
def dataset():
    walkover = source_row(
        tourney_id="2023-0311", tourney_name="Us Open", surface="", tourney_date="20221226",
        match_num="12", round="R64", score="W/O", minutes="", winner_hand="U", winner_seed="1F",
        winner_entry="Alt", **{f"{p}_{s}": "" for p in "wl" for s in ["ace", "df", "svpt", "1stIn",
                                "1stWon", "2ndWon", "SvGms", "bpSaved", "bpFaced"]},
    )
    return parse(pd.DataFrame([source_row(), walkover]), "MS")


def test_tables_follow_the_schema(dataset):
    assert list(dataset.matches.columns) == list(MATCH_COLUMNS)
    assert list(dataset.players.columns) == list(PLAYER_COLUMNS)
    assert dataset.points.empty and dataset.shots.empty


def test_match(dataset):
    final = dataset.matches.loc["2023-540-F-701"]
    assert (final.tournament, final.level, final.year, final.surface) == ("Wimbledon", "G", 2023, "grass")
    assert final.tournament_date == pd.Timestamp("2023-07-03") and pd.isna(final.date)
    assert (final.player1, final.winner, final.status) == ("Adam A", "Adam A", "completed")
    assert (final.scoreline, final.minutes, final.best_of) == ("1-6 7-6 6-1 3-6 6-4", 282, 5)


def test_players(dataset):
    winner, loser = dataset.players.iloc[0], dataset.players.iloc[1]
    assert (winner.player, winner.opponent, winner.won) == ("Adam A", "Ben B", True)
    assert (loser.player, loser.won, loser.country, loser.age) == ("Ben B", False, "SRB", 36.1)
    assert (winner.player_id, winner.ranking, winner.seed, winner.height_cm) == (100001, 1, 1, 183)
    assert (winner.aces, winner.serve_points, winner.service_games, winner.break_points_saved) == (9, 172, 23, 5)


def test_zero_service_games_with_serve_points_is_not_recorded():
    row = source_row(w_SvGms="0", l_SvGms="0")
    players = parse(pd.DataFrame([row]), "WS").players
    assert players.service_games.isna().all() and (players.serve_points > 0).all()


def test_season_and_cleaned_values(dataset):
    walkover = dataset.matches.loc["2023-0311-R64-12"]
    assert walkover.year == 2023  # the season, although the event starts in December 2022
    assert walkover.tournament == "US Open"  # the source writes 'Us Open'
    assert (walkover.status, walkover.scoreline) == ("walkover", None)
    assert pd.isna(walkover.surface) and pd.isna(walkover.minutes)
    winner = dataset.players.iloc[2]
    assert pd.isna(winner.hand) and pd.isna(winner.seed) and winner.entry == "ALT"
    assert pd.isna(winner.aces)
