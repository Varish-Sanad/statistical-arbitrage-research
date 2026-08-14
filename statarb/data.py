"""Fetches and caches daily OHLCV history via yfinance."""

from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent.parent / "data"


def fetch_ohlcv(ticker: str, start: str, end: str, cache_dir: Path = CACHE_DIR) -> pd.DataFrame:
    """Downloads daily bars for ticker over [start, end), caches to CSV so
    repeat runs don't hit the network again. Close is already split/dividend
    adjusted by default in yfinance.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{ticker}_{start}_{end}.csv"

    if cache_path.exists():
        return pd.read_csv(cache_path, parse_dates=["date"])

    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if raw.empty:
        raise ValueError(f"no data returned for {ticker} in [{start}, {end})")

    # yfinance gives back a multiindex column (price type, ticker) even
    # for a single ticker, so drop the ticker level
    raw = raw.droplevel("Ticker", axis=1)
    raw = raw.reset_index().rename(columns={"Date": "date"})
    raw.columns = [c.lower() for c in raw.columns]
    raw = raw.sort_values("date").reset_index(drop=True)

    raw.to_csv(cache_path, index=False)
    return raw


def load_aligned_pair(ticker_a: str, ticker_b: str, start: str, end: str) -> pd.DataFrame:
    """Merges both tickers on the dates they both traded, columns become
    open_a/close_a/open_b/close_b.
    """
    df_a = fetch_ohlcv(ticker_a, start, end)[["date", "open", "close"]]
    df_b = fetch_ohlcv(ticker_b, start, end)[["date", "open", "close"]]

    merged = df_a.merge(df_b, on="date", suffixes=("_a", "_b"), how="inner")
    return merged.sort_values("date").reset_index(drop=True)
