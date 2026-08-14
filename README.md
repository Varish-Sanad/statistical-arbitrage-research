# Statistical Arbitrage Research

Pairs trading research project. Looks for pairs of stocks whose prices stay tethered together over time (cointegration), builds a mean reversion strategy around the spread between them, and runs it through a backtesting engine.

## What it does

1. Screens a list of candidate pairs, stocks in similar sectors with a plausible reason to move together, for cointegration using the Engle-Granger two step method.
2. For pairs that pass, builds a rolling hedge ratio (beta) and constructs the spread between the two prices.
3. Reshapes that spread into a single price series so it can be fed into a single instrument backtesting engine as if it were one asset.
4. Runs a z-score based mean reversion strategy on the spread: enter when the spread is unusually wide or narrow, exit once it reverts back toward its average.
5. Adds some guardrails on top: periodic re-testing of cointegration since a pair can stop being cointegrated, a check on the hedge ratio drifting too far from where it started, and a rough stop-loss.

## Concepts

- Cointegration: two individually random walk like prices can still have a stable, mean reverting relationship between them even though neither price alone is mean reverting.
- Correlation is not the same as cointegration. Two stocks can move together day to day and still drift apart in price level over time.
- Engle-Granger two step test: regress one price on the other (OLS) to get the hedge ratio, then run an Augmented Dickey-Fuller test on the residual to check if it is stationary.
- Z-score mean reversion: once a spread is confirmed to mean revert, measure how many standard deviations away from its rolling average it currently is, and trade on the expectation that it reverts.
- Multiple testing: testing many candidate pairs at once means some will look statistically significant just by chance, so the significance threshold needs to be corrected for the number of pairs tested.

## Stack

Python, pandas, NumPy, statsmodels, yfinance

## Structure

- statarb/universe.py, candidate pairs and the reasoning behind each one
- statarb/data.py, pulls and caches price history
- statarb/cointegration.py, Engle-Granger screening
- statarb/spread.py, rolling beta and spread construction
- statarb/strategies/, the z-score signal and a guarded version with the extra checks
- examples/run_pairs_backtest.py, runs the pipeline end to end

## Dependencies

Builds on backtesting-framework for the backtest engine itself.
