"""
ATP and WTA match results, collected by Jeff Sackmann: every singles match
since 1968, with rankings and (since 1991 for the ATP, 2003 for the WTA, with
gaps) per-player serve statistics.

There are no point- or shot-level data, so ``Dataset.points`` and
``Dataset.shots`` are empty. Player 1 is the winner.

The original repositories (github.com/JeffSackmann/tennis_atp, tennis_wta)
were withdrawn in 2026; files are read from an archival mirror (see :mod:`.archive`).

Data license: CC BY-NC-SA 4.0 (attribution, non-commercial, share-alike).
"""

import re

import pandas as pd

from ..dataset import Dataset
from ..players import players_table
from .archive import download

EVENTS = {"atp": "MS", "wta": "WS"}
RENAMED_TOURNAMENTS = {"Us Open": "US Open"}  # source spelling since 2019 (WTA) / 2021 (ATP)
LEVELS = {  # level: file name suffix
    "tour": "",
    "qual_chall": "_qual_chall",  # ATP: tour-level qualifying and challenger main draws
    "futures": "_futures",        # ATP: ITF futures
    "qual_itf": "_qual_itf",      # WTA: tour-level qualifying and ITF events
}

# Per-player source columns: winner / loser prefix, then the standard name.
PLAYER_SOURCE = {
    "id": "player_id", "hand": "hand", "ht": "height_cm", "ioc": "country", "age": "age",
    "rank": "ranking", "rank_points": "ranking_points", "seed": "seed", "entry": "entry",
}
STAT_SOURCE = {  # w_ / l_ prefix
    "ace": "aces", "df": "double_faults", "svpt": "serve_points", "1stIn": "first_serves_in",
    "1stWon": "first_serve_points_won", "2ndWon": "second_serve_points_won",
    "SvGms": "service_games", "bpFaced": "break_points_faced", "bpSaved": "break_points_saved",
}
INTEGER_COLUMNS = ["player_id", "height_cm", "ranking", "ranking_points", "seed", *STAT_SOURCE.values()]


def load_results(tour: str, year: int, level: str = "tour") -> Dataset:
    """
    Load one season of singles results.

    Parameters
    ----------
    tour : {'atp', 'wta'}
    year : int
        1968 to the current season.
    level : {'tour', 'qual_chall', 'futures', 'qual_itf'}
        'tour' is the main draw of tour-level events, Grand Slams and team
        events included. 'qual_chall' and 'futures' exist for the ATP,
        'qual_itf' for the WTA.

    Examples
    --------
    >>> season = load_results("atp", 2023)
    >>> season.players.groupby("player").won.sum().nlargest(5)
    """
    path = download(f"{tour}/{tour}_matches{LEVELS[level]}_{year}.csv")
    return parse(pd.read_csv(path, dtype=str, keep_default_na=False), EVENTS[tour])


def parse(raw: pd.DataFrame, event: str) -> Dataset:
    """Convert one source file into a :class:`Dataset`."""
    raw = raw.set_axis(raw.tourney_id + "-" + raw["round"] + "-" + raw.match_num).rename_axis("match_id")
    scorelines, statuses = zip(*raw.score.map(read_score))
    tournament_date = pd.to_datetime(raw.tourney_date, format="%Y%m%d")
    matches = pd.DataFrame(
        {
            "tournament": raw.tourney_name.replace(RENAMED_TOURNAMENTS),
            "level": raw.tourney_level,
            "year": raw.tourney_id.str[:4].astype(int),  # the season; some events start in December
            "tournament_date": tournament_date,
            "event": event,
            "round": raw["round"],
            "surface": raw.surface.str.lower().replace({"": None}),
            "player1": raw.winner_name,
            "player2": raw.loser_name,
            "best_of": raw.best_of.astype(int),
            "winner": raw.winner_name,
            "status": statuses,
            "scoreline": scorelines,
            "minutes": pd.to_numeric(raw.minutes).astype("Int64"),
            "n_points": 0,
        },
        index=raw.index,
    )
    paired = matches[["player1", "player2", "winner"]].join(_paired_player_columns(raw))
    return Dataset.from_tables(matches=matches, players=players_table(paired))


def _paired_player_columns(raw: pd.DataFrame) -> pd.DataFrame:
    """Winner and loser columns renamed to player1_<x> and player2_<x>."""
    columns = {}
    for source, player in [("winner", "player1"), ("loser", "player2")]:
        for name, standard in PLAYER_SOURCE.items():
            columns[f"{player}_{standard}"] = raw[f"{source}_{name}"]
        for name, standard in STAT_SOURCE.items():
            columns[f"{player}_{standard}"] = raw[f"{source[0]}_{name}"]
    paired = pd.DataFrame(columns).replace({"": None})
    for player in ["player1", "player2"]:
        paired[f"{player}_hand"] = paired[f"{player}_hand"].replace({"U": None})  # unknown
        paired[f"{player}_entry"] = paired[f"{player}_entry"].str.upper()
        paired[f"{player}_age"] = pd.to_numeric(paired[f"{player}_age"])
        for standard in INTEGER_COLUMNS:
            # A few seeds are codes such as '1F' (WTA, 1970s); they become missing.
            column = f"{player}_{standard}"
            paired[column] = pd.to_numeric(paired[column], errors="coerce").astype("Int64")
        # No service game although the player served points means "not recorded"
        # (the WTA Grand Slams of 2017 write 0 for every match).
        games = paired[f"{player}_service_games"]
        paired[f"{player}_service_games"] = games.mask(games.eq(0) & paired[f"{player}_serve_points"].gt(0))
    return paired


# --- the score string -----------------------------------------------------------

SET = re.compile(r"(\d+)-(\d+)(?:\(\d+\))?")        # 7-6(4): tiebreak points dropped
MATCH_TIEBREAK = re.compile(r"\[(\d+)-(\d+)\]")     # [10-7]: a set won 1-0
STATUS_WORDS = {
    "RET": "retired",
    "W/O": "walkover", "Walkover": "walkover",
    "DEF": "default", "Def.": "default", "Default": "default",
    "ABD": "abandoned", "abandoned": "abandoned", "unfinished": "abandoned",
}
FILLER_WORDS = {"Played", "and"}  # 'Played and abandoned', 'Played and unfinished'


def read_score(score: str) -> tuple[str | None, str]:
    """
    Scoreline (winner first, standard format) and match status of a source score.

    >>> read_score("7-6(4) 3-6 6-4")
    ('7-6 3-6 6-4', 'completed')
    >>> read_score("6-2 0-0 RET")
    ('6-2 0-0', 'retired')

    A score with anything else in it (typos, 'UNK', spreadsheet damage such as
    '7-Oct') gives ``(None, 'unknown')``.
    """
    sets, status = [], "completed"
    for token in score.split():
        if match := SET.fullmatch(token):
            sets.append(f"{match[1]}-{match[2]}")
        elif match := MATCH_TIEBREAK.fullmatch(token):
            sets.append("1-0" if int(match[1]) > int(match[2]) else "0-1")
        elif token in STATUS_WORDS:
            status = STATUS_WORDS[token]
        elif token not in FILLER_WORDS:
            return None, "unknown"
    if not sets and status == "completed":
        return None, "unknown"
    return " ".join(sets) or None, status
