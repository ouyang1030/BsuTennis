"""
A dataset is four tables, from coarse to fine: one row per match, one row per
player per match, one row per point, and one row per stroke. A source without
points or strokes leaves those tables empty.

Analyses work on the long tables across many matches; selecting a single
match gives the same kind of object.
"""

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd

from .schema import MATCH_COLUMNS, PLAYER_COLUMNS, POINT_COLUMNS, SHOT_COLUMNS, conform


@dataclass
class Dataset:
    matches: pd.DataFrame
    """One row per match, indexed by ``match_id``. Columns: :data:`~bsutennis.data.schema.MATCH_COLUMNS`."""
    players: pd.DataFrame
    """One row per player per match. Columns: :data:`~bsutennis.data.schema.PLAYER_COLUMNS`."""
    points: pd.DataFrame
    """One row per point. Columns: :data:`~bsutennis.data.schema.POINT_COLUMNS`."""
    shots: pd.DataFrame
    """One row per stroke. Columns: :data:`~bsutennis.data.schema.SHOT_COLUMNS`."""

    @classmethod
    def from_tables(
        cls,
        matches: pd.DataFrame,
        players: pd.DataFrame,
        points: pd.DataFrame | None = None,
        shots: pd.DataFrame | None = None,
    ) -> "Dataset":
        """
        A dataset whose tables follow the schema: loaders pass the columns their
        source has, and get exactly the standard columns and types back
        (:func:`~bsutennis.data.schema.conform`). A table not given is empty.
        """
        return cls(
            matches=conform(matches, MATCH_COLUMNS),
            players=conform(players, PLAYER_COLUMNS),
            points=conform(pd.DataFrame(points), POINT_COLUMNS),
            shots=conform(pd.DataFrame(shots), SHOT_COLUMNS),
        )

    def select(self, match_ids: Iterable[str]) -> "Dataset":
        match_ids = list(match_ids)
        return Dataset(
            matches=self.matches.loc[match_ids],
            players=_rows_of(self.players, match_ids),
            points=_rows_of(self.points, match_ids),
            shots=_rows_of(self.shots, match_ids),
        )

    def match(self, match_id: str) -> "Dataset":
        return self.select([match_id])

    @staticmethod
    def concat(datasets: Iterable["Dataset"]) -> "Dataset":
        datasets = list(datasets)
        return Dataset(
            matches=pd.concat([d.matches for d in datasets]),
            players=pd.concat([d.players for d in datasets], ignore_index=True),
            points=pd.concat([d.points for d in datasets], ignore_index=True),
            shots=pd.concat([d.shots for d in datasets], ignore_index=True),
        )

    def __repr__(self) -> str:
        return f"Dataset({len(self.matches)} matches, {len(self.points)} points, {len(self.shots)} shots)"


def _rows_of(table: pd.DataFrame, match_ids: list[str]) -> pd.DataFrame:
    return table[table.match_id.isin(match_ids)].reset_index(drop=True)
