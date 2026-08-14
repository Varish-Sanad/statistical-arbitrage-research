"""Z-score strategy with some extra guardrails on top, since a cointegrated
pair can stop being cointegrated. Adds three checks around the core
z-score signal: periodic re-cointegration, a beta stability check, and a
rough stop-loss.
"""

import pandas as pd
from statsmodels.tsa.stattools import coint

from src.signals import Signal, SignalGenerator

from .zscore_mean_reversion import ZScoreMeanReversion


class GuardedZScoreStrategy(SignalGenerator):
    def __init__(
        self,
        window: int = 60,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        stop_loss_z: float = 4.0,
        recheck_interval: int = 63,
        elevated_interval: int = 21,
        short_lookback: int = 252,
        long_lookback: int = 756,
        escalation_threshold: int = 2,
        significance: float = 0.05,
        beta_drift_z_threshold: float = 7.0,
    ):
        self._inner = ZScoreMeanReversion(window=window, entry_z=entry_z, exit_z=exit_z)
        self.stop_loss_z = stop_loss_z
        self.recheck_interval = recheck_interval
        self.elevated_interval = elevated_interval
        self.short_lookback = short_lookback
        self.long_lookback = long_lookback
        self.escalation_threshold = escalation_threshold
        self.significance = significance
        self.beta_drift_z_threshold = beta_drift_z_threshold
        self._tradeable = True
        self._elevated_scrutiny = False
        self._consecutive_short_failures = 0
        self._bars_since_recheck = 0

    def generate(self, history: pd.DataFrame) -> Signal:
        self._maybe_recheck_cointegration(history)

        # beta drift is a loose backstop for a sudden break (halt, spinoff,
        # etc) - periodic re-cointegration below is doing the real work
        if self._tradeable and self._beta_has_drifted(history):
            self._tradeable = False

        if not self._tradeable:
            self._inner._position = Signal.FLAT
            return Signal.FLAT

        if self._triggers_stop_loss(history):
            self._inner._position = Signal.FLAT
            return Signal.FLAT

        return self._inner.generate(history)

    def _beta_has_drifted(self, history: pd.DataFrame) -> bool:
        current_beta = history["beta"].iloc[-1]
        reference_beta = history["reference_beta"].iloc[-1]
        reference_std = history["reference_beta_std"].iloc[-1]
        if reference_std == 0:
            return False
        return abs(current_beta - reference_beta) / reference_std > self.beta_drift_z_threshold

    def _triggers_stop_loss(self, history: pd.DataFrame) -> bool:
        # not a real P&L stop, just a price-based proxy - generate() never
        # sees equity or position, only price history
        if len(history) < self._inner.window:
            return False
        recent = history["close"].tail(self._inner.window)
        mu, sigma = recent.mean(), recent.std()
        if sigma == 0:
            return False
        z = (recent.iloc[-1] - mu) / sigma
        return abs(z) > self.stop_loss_z

    def _maybe_recheck_cointegration(self, history: pd.DataFrame) -> None:
        if len(history) < self.long_lookback:
            return

        self._bars_since_recheck += 1
        interval = self.elevated_interval if self._elevated_scrutiny else self.recheck_interval
        if self._bars_since_recheck < interval:
            return
        self._bars_since_recheck = 0

        # long window has more power, short window reacts faster - a short
        # window alone flags too many false alarms on noisy but fine pairs
        long_window = history.tail(self.long_lookback)
        _, long_p, _ = coint(long_window["close_a"], long_window["close_b"])

        if long_p >= self.significance:
            self._tradeable = False
            self._elevated_scrutiny = False
            self._consecutive_short_failures = 0
            return

        short_window = history.tail(self.short_lookback)
        _, short_p, _ = coint(short_window["close_a"], short_window["close_b"])

        if short_p < self.significance:
            self._tradeable = True
            self._elevated_scrutiny = False
            self._consecutive_short_failures = 0
            return

        # long window still ok, short window failed - could be noise, so
        # check again sooner instead of shutting off right away
        self._tradeable = True
        self._elevated_scrutiny = True
        self._consecutive_short_failures += 1
        if self._consecutive_short_failures >= self.escalation_threshold:
            self._tradeable = False
