# Statistical Arbitrage Research

Research into a mean-reversion pairs-trading strategy in Python. Identifies historically cointegrated equity pairs using the Engle-Granger two-step method and Augmented Dickey-Fuller tests on the price spread, then trades the spread based on z-score entry/exit thresholds. Evaluated end-to-end through a custom backtesting framework.

## Status

In progress.

## Roadmap

- [ ] Cointegration screening (Engle-Granger, ADF test)
- [ ] Spread construction and z-score calculation
- [ ] Mean-reversion entry/exit strategy
- [ ] Backtest via the backtesting-framework project
- [ ] Robustness analysis across sector pairs / time windows

## Tech Stack

Python, pandas, NumPy, statsmodels

## Dependencies

Builds on [backtesting-framework](https://github.com/Varish-Sanad/backtesting-framework).
