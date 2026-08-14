"""Z-score mean reversion signal, meant to run on the spread series from
spread.py rather than a raw price.

Entry and exit use separate thresholds (enter past entry_z, exit only once
back under exit_z), so this keeps state on which side of the trade it's
on. A single symmetric threshold would exit the moment z ticks back under
entry_z, which just causes whipsaw trades near the boundary instead of
riding the reversion back to the mean.
"""

import pandas as pd

from src.signals import Signal, SignalGenerator


class ZScoreMeanReversion(SignalGenerator):
    def __init__(self, window: int = 60, entry_z: float = 2.0, exit_z: float = 0.5):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z
        self._position = Signal.FLAT

    def generate(self, history: pd.DataFrame) -> Signal:
        if len(history) < self.window:
            return Signal.FLAT

        recent = history["close"].tail(self.window)
        mu, sigma = recent.mean(), recent.std()
        if sigma == 0:
            return Signal.FLAT

        z = (recent.iloc[-1] - mu) / sigma

        if self._position == Signal.FLAT:
            if z > self.entry_z:
                self._position = Signal.SHORT
            elif z < -self.entry_z:
                self._position = Signal.LONG
        elif abs(z) < self.exit_z:
            self._position = Signal.FLAT

        return self._position
