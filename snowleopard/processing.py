import numpy as np
import pandas as pd
import pathlib
from typing import List, Optional, Union

PathLike = Union[str, pathlib.Path]


def SUMDROP(k, *column_names):
    """ SUMDROP(k; column_name_1, column_name_2, ...)
    Add a sequence of values while dropping the k lowest scores. Use SUMDROP(0; ...) to sum all values.
    """
    pass


def BOUND(lower, upper, value):
    """ BOUND(lower, upper; value)
    Limit the value between the two bounds. More formally: BOUND(a, b; v) returns a if v <= a, b if v >= b, and v itself if a <= v <= b.
    """
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def get_column_headers(path_to_csv: PathLike) -> List[str]:
    df = pd.read_csv(path_to_csv)
    return df.columns


def clean_column(df: pd.DataFrame, column: str, fillna = 0):
    """ Convert a column to numeric values, filling na/errors with the fillvalue. """
    return pd.to_numeric(df[column], errors='coerce').fillna(fillna)


def sum_highest(*values: float, drop: int = 0, weights: Optional[float] = None) -> float:
    """ Add the given values, dropping the lowest `drop` of them. """
    vals = np.sort(np.array(values).astype(np.float))[drop:]
    if weights is None:
        weights = np.ones(vals.shape)
    return np.dot(vals, weights).sum()
