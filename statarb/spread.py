"""Builds the rolling-beta spread and reshapes it into a single open/close
series so the existing backtesting engine can trade a two-leg pair without
any changes to the engine itself.
"""

import pandas as pd


def build_synthetic_spread(
    aligned: pd.DataFrame,
    window: int = 252,
    calibration_bars: int = 252,
) -> pd.DataFrame:
    """aligned comes from data.load_aligned_pair. Returns open/close columns
    shaped for BacktestEngine:

    close[t] = close_a[t] - beta(t) * close_b[t] + offset
    open[t]  = open_a[t] - beta(t-1) * open_b[t] + offset

    beta is a rolling OLS slope (cov/var closed form, no need to fit OLS
    per bar). open uses the previous bar's beta since that is the hedge
    ratio the signal was actually generated under at t-1.

    offset shifts the spread so it stays comfortably positive - the engine
    sizes positions as equity / price, and a spread near zero blows that
    up into a huge position. Has to be a fixed number, not something that
    moves bar to bar, or the offset's own drift gets counted as fake P&L.
    Size matters too, not just sign - it should be close to the real
    notional cost of the position (price_a + beta * price_b), not just
    "bigger than the spread's swings," otherwise the strategy ends up
    trading at a much higher effective leverage than intended.

    offset (and reference_beta/reference_beta_std, used by a beta
    stability check downstream) gets calibrated once from the bars right
    after beta first becomes valid, then held fixed for the rest of the
    series. Those calibration bars get dropped from the tradable output.
    """
    close_a, close_b = aligned["close_a"], aligned["close_b"]

    rolling_cov = close_a.rolling(window).cov(close_b)
    rolling_var = close_b.rolling(window).var()
    beta = rolling_cov / rolling_var

    raw_close_spread = close_a - beta * close_b
    raw_open_spread = aligned["open_a"] - beta.shift(1) * aligned["open_b"]
    gross_notional = close_a + beta * close_b

    valid_start = beta.first_valid_index()
    calibration_slice = slice(valid_start, valid_start + calibration_bars)
    offset = gross_notional.iloc[calibration_slice].mean()
    reference_beta = beta.iloc[calibration_slice].mean()
    reference_beta_std = beta.iloc[calibration_slice].std()

    close_spread = raw_close_spread + offset
    open_spread = raw_open_spread + offset

    result = pd.DataFrame({
        "date": aligned["date"],
        "open": open_spread,
        "close": close_spread,
        "beta": beta,
        # raw leg prices, kept around for the periodic re-cointegration
        # check downstream - the engine itself ignores extra columns
        "close_a": close_a,
        "close_b": close_b,
        # constant reference values from the calibration window, used to
        # detect the hedge ratio drifting away from what the offset was
        # built for
        "reference_beta": reference_beta,
        "reference_beta_std": reference_beta_std,
    })
    return result.iloc[valid_start + calibration_bars:].dropna().reset_index(drop=True)
