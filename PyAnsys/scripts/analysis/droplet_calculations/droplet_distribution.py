"""
droplet_distribution.py
=======================
Shared module exposing the nine DPM injection size ratios and liquid mass
fractions used for the Purnanto/Fluent droplet distribution.

Exports
-------
x_xmed_points : list[float]  - 9 x/x_med injection ratios
mass_fracs    : list[float]  - corresponding interval mass fractions
best_model    : str          - label used by harwell_calculation.py output
"""

import numpy as np

# Purnanto/Fluent representative droplet-size points. These are upper-bin
# representative ratios relative to the Harwell median diameter.
x_xmed_points = np.array([0.01, 0.05, 0.10, 0.20, 0.30, 0.62, 1.00, 1.50, 2.90])

# Monotonic cumulative liquid mass fractions at the points above. The first
# five points split the lower 5% tail below x/x_med = 0.30; the remaining
# points follow the main cumulative levels in Figure 5.
cumulative_fracs = np.array([0.001625, 0.008300, 0.016600, 0.033300, 0.050000,
                             0.250000, 0.500000, 0.750000, 1.000000])

_diffs = np.diff(np.concatenate([[0.0], cumulative_fracs]))

if np.any(_diffs < 0):
    raise ValueError("Droplet cumulative fractions must be monotonic.")

mass_fracs = _diffs / _diffs.sum()

best_model = "Purnanto/Fluent fixed cumulative distribution"
