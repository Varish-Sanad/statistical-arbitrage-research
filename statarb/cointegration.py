"""Engle-Granger cointegration screening using statsmodels' coint(), which
handles the OLS hedge ratio step and the ADF test on the residual, with
the MacKinnon-adjusted critical values that plain ADF wouldn't have.
"""

from dataclasses import dataclass

import pandas as pd
from statsmodels.tsa.stattools import coint

from .data import load_aligned_pair
from .universe import CandidatePair


@dataclass(frozen=True)
class CointegrationResult:
    pair: CandidatePair
    test_statistic: float
    p_value: float
    is_cointegrated: bool


def test_pair(pair: CandidatePair, aligned: pd.DataFrame, significance: float = 0.05) -> CointegrationResult:
    test_statistic, p_value, _critical_values = coint(aligned["close_a"], aligned["close_b"])
    return CointegrationResult(
        pair=pair,
        test_statistic=test_statistic,
        p_value=p_value,
        is_cointegrated=p_value < significance,
    )


def screen_universe(
    pairs: list[CandidatePair], start: str, end: str, significance: float = 0.05
) -> list[CointegrationResult]:
    results = []
    for pair in pairs:
        try:
            aligned = load_aligned_pair(pair.ticker_a, pair.ticker_b, start, end)
        except ValueError as e:
            # ticker might not have existed yet in this form (spinoff,
            # merger, etc) - skip instead of failing the whole screen
            print(f"  skipping {pair.ticker_a}/{pair.ticker_b}: {e}")
            continue
        results.append(test_pair(pair, aligned, significance))
    return results
