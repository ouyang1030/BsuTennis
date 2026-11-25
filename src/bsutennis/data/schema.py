"""
The standard tables.

Every loader returns a :class:`~bsutennis.data.Dataset` whose tables have
exactly these columns, in this order, with these types (see :func:`conform`).
Columns a source does not record are missing values, never guesses.

Score columns in ``points`` describe the score *before* the point, from the
server's point of view, as a scoreboard shows it.
"""

from dataclasses import dataclass

import pandas as pd

# Column types. The nullable ones hold <NA> where a source does not record a value.
TEXT = "object"          # str, or missing
INT = "int64"            # always known
COUNT = "Int64"          # integer, or missing
REAL = "float64"         # float, or NaN
BOOL = "bool"            # always known
FLAG = "boolean"         # True, False, or missing
DATE = "datetime64[ns]"  # date, or NaT


@dataclass(frozen=True)
class Column:
    dtype: str
    description: str


def conform(table: pd.DataFrame, columns: dict[str, Column]) -> pd.DataFrame:
    """``table`` with exactly ``columns``, in order and with their types; columns
    it lacks become missing values."""
    return table.reindex(columns=list(columns)).astype({name: c.dtype for name, c in columns.items()})


MATCH_COLUMNS = {
    # index: match_id
    "tournament": Column(TEXT, "Tournament name as the source writes it, e.g. 'Wimbledon' or 'Rome Masters'; "
                               "the four Grand Slams are named alike in every source"),
    "level": Column(TEXT, "Tournament level, source code: 'G' Grand Slam, 'M' Masters 1000, 'A' other "
                          "tour events, 'F' tour finals, 'D' Davis Cup / Billie Jean King Cup; the WTA "
                          "uses further codes ('PM', 'P', 'I', 'T1'-'T5', ...)"),
    "year": Column(INT, "Season"),
    "tournament_date": Column(DATE, "First day of the tournament week, usually a Monday (ATP/WTA results)"),
    "date": Column(DATE, "Day the match was played (Match Charting Project)"),
    "event": Column(TEXT, "'MS' men's singles or 'WS' women's singles"),
    "round": Column(TEXT, "e.g. 'R128', 'R16', 'QF', 'SF', 'F', 'RR', 'BR' (bronze medal), 'Q1'"),
    "surface": Column(TEXT, "'hard', 'clay', 'grass' or 'carpet'"),
    "player1": Column(TEXT, "Name of player 1 (results: the winner; charting: the first server)"),
    "player2": Column(TEXT, "Name of player 2"),
    "best_of": Column(INT, "Number of sets, 3 or 5 (rarely 1)"),
    "match_format": Column(TEXT, "Scoring format, e.g. 'bo5 6/tb7 final 6/tb10': best of five, "
                                 "7-point tiebreaks at 6-6, a 10-point tiebreak in the final set "
                                 "(MatchFormat.from_code reads it); missing for ATP/WTA results"),
    "winner": Column(TEXT, "Name of the winner; missing if not known (a replay that does not reach "
                           "the end of the match)"),
    "status": Column(TEXT, "'completed', 'retired', 'walkover', 'default', 'abandoned' or 'unknown'"),
    "scoreline": Column(TEXT, "Games per set, player 1 first, e.g. '1-6 7-6 6-1 3-6 6-4'; a match "
                              "tiebreak counts as a set won 1-0"),
    "minutes": Column(COUNT, "Length of the match in minutes (ATP/WTA results)"),
    "n_points": Column(INT, "Number of points in the points table"),
    "score_mismatch_at": Column(COUNT, "First point_no at which the replayed score disagrees "
                                       "with the source; missing if they agree throughout"),
}

PLAYER_COLUMNS = {
    # one row per player per match
    "match_id": Column(TEXT, "Match identifier, index of the matches table"),
    "player": Column(TEXT, "Name of the player"),
    "opponent": Column(TEXT, "Name of the opponent"),
    "won": Column(FLAG, "True if the player won the match; missing if the winner is not known"),
    # who, as of the tournament (ATP/WTA results unless noted)
    "player_id": Column(COUNT, "Player identifier of the ATP/WTA files"),
    "hand": Column(TEXT, "'R', 'L' or 'A' (ambidextrous) (results and charting)"),
    "height_cm": Column(COUNT, "Height in centimetres"),
    "country": Column(TEXT, "Three-letter IOC country code"),
    "age": Column(REAL, "Age in years at the start of the tournament"),
    "ranking": Column(COUNT, "ATP/WTA ranking at the start of the tournament"),
    "ranking_points": Column(COUNT, "Ranking points at the start of the tournament"),
    "seed": Column(COUNT, "Seed number"),
    "entry": Column(TEXT, "How the player entered the draw: 'Q' qualifier, 'WC' wild card, "
                          "'LL' lucky loser, 'PR' protected ranking, ..."),
    # serve statistics: reported by ATP/WTA results, counted from the points otherwise
    "aces": Column(COUNT, "Aces"),
    "double_faults": Column(COUNT, "Double faults"),
    "serve_points": Column(COUNT, "Points served"),
    "first_serves_in": Column(COUNT, "First serves in"),
    "first_serve_points_won": Column(COUNT, "Points won after a first serve in"),
    "second_serve_points_won": Column(COUNT, "Points won after a second serve (double faults included as lost)"),
    "service_games": Column(COUNT, "Games in which the player served the last point, so a tiebreak "
                                   "counts for one player, as in the official statistics since 2018 "
                                   "(earlier official statistics credit tiebreaks inconsistently)"),
    "break_points_faced": Column(COUNT, "Break points faced on serve"),
    "break_points_saved": Column(COUNT, "Break points faced and won"),
}

POINT_COLUMNS = {
    # where in the match
    "match_id": Column(TEXT, "Match identifier, index of the matches table"),
    "point_no": Column(INT, "Point number within the match, from 1"),
    "set_no": Column(INT, "Set number, from 1"),
    "game_no": Column(INT, "Game number within the set, from 1 (a tiebreak is game 13)"),
    # who
    "server": Column(TEXT, "Name of the server"),
    "receiver": Column(TEXT, "Name of the receiver"),
    "point_winner": Column(TEXT, "Name of the player who won the point"),
    "server_won": Column(BOOL, "True if the server won the point"),
    # score before the point, server first
    "server_sets": Column(INT, "Sets won by the server"),
    "receiver_sets": Column(INT, "Sets won by the receiver"),
    "server_games": Column(INT, "Games won by the server in the current set"),
    "receiver_games": Column(INT, "Games won by the receiver in the current set"),
    "point_score": Column(TEXT, "Point score, server first: '30-40', 'AD-40', or '5-6' in a tiebreak"),
    "tiebreak": Column(BOOL, "True during a tiebreak"),
    "side": Column(TEXT, "'deuce' or 'ad': the court the serve is hit to"),
    "break_point": Column(BOOL, "True if the receiver wins the game by winning this point"),
    "set_point": Column(TEXT, "'server' or 'receiver' if that player wins the set by winning "
                              "this point, otherwise missing"),
    "match_point": Column(TEXT, "Same as set_point, for the match"),
    "score_verified": Column(BOOL, "False from the first point where the replayed score "
                                   "disagrees with the source"),
    # how the point was played
    "serve_no": Column(COUNT, "1 or 2: the serve that started the rally (2 on a double fault)"),
    "serve_direction": Column(TEXT, "'wide', 'body' or 'T' for that serve"),
    "ace": Column(FLAG, "True if the serve was an ace"),
    "double_fault": Column(FLAG, "True if the point was a double fault"),
    "outcome": Column(TEXT, "'ace', 'service_winner', 'double_fault', 'winner', 'forced_error' "
                            "or 'unforced_error'; missing when the source does not record it"),
    "rally_count": Column(COUNT, "Shots in the point, serve included and errors excluded "
                                 "(an ace is 1, a double fault 0)"),
    "shots_recorded": Column(BOOL, "True if the point's shots are in the shots table"),
    # Grand Slam point-by-point only
    "serve_speed_kmh": Column(REAL, "Speed of the serve that started the rally, km/h"),
    "serve_width": Column(TEXT, "Slam PBP code: 'W' wide, 'BW' body-wide, 'B' body, "
                                "'BC' body-centre, 'C' centre (T)"),
    "serve_depth": Column(TEXT, "Slam PBP code: 'CTL' close to the service line, 'NCTL' not"),
    "return_depth": Column(TEXT, "Slam PBP code: 'D' deep, 'ND' not deep"),
}

SHOT_COLUMNS = {
    # one row per stroke, serves included (a faulted first serve is a row too)
    "match_id": Column(TEXT, "Match identifier"),
    "point_no": Column(INT, "Point number within the match"),
    "serve_no": Column(INT, "1 or 2: the serve this stroke follows"),
    "shot_no": Column(INT, "Stroke number after that serve: 1 serve, 2 return, 3 serve +1, ..."),
    "player": Column(TEXT, "Name of the player who hit the stroke"),
    "role": Column(TEXT, "'server' or 'receiver'"),
    "shot_type": Column(TEXT, "'serve', 'groundstroke', 'slice', 'volley', 'half_volley', "
                              "'swinging_volley', 'overhead', 'drop_shot', 'lob' or 'trick'"),
    "wing": Column(TEXT, "'forehand' or 'backhand'"),
    "direction": Column(TEXT, "Serve: 'wide', 'body' or 'T'. Other strokes: 'left', 'middle' or "
                              "'right' lane as seen by the hitter (outer 30 % / middle 40 % of the court)"),
    "depth": Column(TEXT, "Returns only: 'short' (in the service box), 'medium' or 'deep' "
                          "(closer to the baseline than to the service line)"),
    "position": Column(TEXT, "'baseline' or 'net': where the stroke was hit"),
    "approach": Column(BOOL, "True for an approach shot or a serve-and-volley serve"),
    "ending": Column(TEXT, "Missing if play continued; otherwise 'fault', 'ace', 'service_winner', "
                           "'winner', 'forced_error' or 'unforced_error'"),
    "error": Column(TEXT, "For faults and errors: 'net', 'wide', 'deep', 'wide_deep', "
                          "'foot_fault', 'shank', 'time_violation' or 'unknown'"),
}
