"""Screens the candidate universe for cointegration, then backtests the
guarded z-score strategy on every pair that clears the threshold, not
just the best one.
"""

from src.engine import BacktestEngine
from src.metrics import summarize

from statarb.cointegration import screen_universe
from statarb.data import load_aligned_pair
from statarb.spread import build_synthetic_spread
from statarb.strategies.guarded_zscore import GuardedZScoreStrategy
from statarb.universe import UNIVERSE

START, END = "2012-01-01", "2024-01-01"

# testing this many pairs at alpha=0.05 means some "significant" results
# are expected just from chance, so correct for that (bonferroni)
SIGNIFICANCE = 0.05 / len(UNIVERSE)


if __name__ == "__main__":
    print(f"Screening {len(UNIVERSE)} candidate pairs for cointegration ({START} to {END})...")
    print(f"Bonferroni-corrected significance: 0.05 / {len(UNIVERSE)} = {SIGNIFICANCE:.5f}\n")
    results = screen_universe(UNIVERSE, START, END, significance=SIGNIFICANCE)
    for r in sorted(results, key=lambda r: r.p_value):
        status = "COINTEGRATED" if r.is_cointegrated else "not cointegrated"
        print(f"  {r.pair.ticker_a}/{r.pair.ticker_b}: p={r.p_value:.4f}  ({status})")

    passing = [r for r in results if r.is_cointegrated]
    if not passing:
        raise SystemExit("\nNo pair in the universe cleared the cointegration threshold.")

    print(f"\n{len(passing)} pair(s) cleared the threshold, backtesting each with the guarded strategy:\n")

    for r in sorted(passing, key=lambda r: r.p_value):
        pair = r.pair
        aligned = load_aligned_pair(pair.ticker_a, pair.ticker_b, START, END)
        synthetic = build_synthetic_spread(aligned, window=252)

        engine = BacktestEngine(synthetic, GuardedZScoreStrategy())
        result = engine.run()
        stats = summarize(result["equity"])

        print(f"--- {pair.ticker_a}/{pair.ticker_b} (screen p={r.p_value:.4f}) ---")
        for key, value in stats.items():
            print(f"  {key}: {value:.4f}")
        print()
