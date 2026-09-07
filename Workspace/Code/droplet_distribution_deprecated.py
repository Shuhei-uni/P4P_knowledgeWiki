"""
droplet_distribution_deprecated.py
==================================
Deprecated version of the droplet distribution module.

This keeps the earlier fitted/digitized Figure 5 workflow for reference only.
It uses the old injection ratios:

    0.30, 0.50, 0.70, 0.90, 1.00, 1.30, 1.70, 2.30, 2.90

Do not use this module for the current DPM setup. Use droplet_distribution.py,
which uses the Purnanto/Fluent-style lower-tail discretisation.

Exports
-------
x_xmed_points : np.ndarray  - 9 x/x_med injection ratios
mass_fracs    : np.ndarray  - corresponding interval mass fractions
best_model    : str         - name of the selected fitted model
"""

import os
import warnings

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import curve_fit
from scipy.special import erf

warnings.warn(
    "droplet_distribution_deprecated.py is deprecated. "
    "Use droplet_distribution.py for the current DPM setup.",
    DeprecationWarning,
    stacklevel=2,
)
warnings.filterwarnings("ignore")

# ─── Load digitized data ─────────────────────────────────────────────────────
_csv = os.path.join(os.path.dirname(__file__), "Digitized_Figure5_(Purnanto 2013)).csv")
_data = np.loadtxt(_csv, delimiter=",")
_dx = _data[:, 0]
_dy = _data[:, 1]

# Merge with anchor points, sort, deduplicate.
_ax = np.array([0.3, 2.9])
_ay = np.array([0.05, 1.0])
_fx = np.concatenate([_ax, _dx])
_fy = np.concatenate([_ay, _dy])
_fx, _fy = zip(*sorted(zip(_fx, _fy)))
_fx, _fy = np.array(_fx), np.array(_fy)
_, _ui = np.unique(_fx, return_index=True)
_fx, _fy = _fx[_ui], _fy[_ui]

# ─── Distribution models ─────────────────────────────────────────────────────
def _rosin_rammler(x, n, xp):
    return 1 - np.exp(-(x / xp) ** n)


def _log_normal(x, mu, sigma):
    return 0.5 * (1 + erf((np.log(x + 1e-10) - mu) / (sigma * np.sqrt(2))))


# ─── Fit ─────────────────────────────────────────────────────────────────────
try:
    _popt_rr, _ = curve_fit(
        _rosin_rammler,
        _fx,
        _fy,
        p0=[1.5, 1.2],
        bounds=([0.1, 0.1], [10, 10]),
        maxfev=10000,
    )
    _rr_fitted = True
except Exception:
    _rr_fitted = False

try:
    _popt_ln, _ = curve_fit(
        _log_normal,
        _fx,
        _fy,
        p0=[0.0, 0.8],
        bounds=([-3, 0.1], [3, 5]),
        maxfev=10000,
    )
    _ln_fitted = True
except Exception:
    _ln_fitted = False

_ix = np.concatenate([[0.0], _fx, [2.9]])
_iy = np.concatenate([[0.0], _fy, [1.0]])
_, _ui2 = np.unique(_ix, return_index=True)
_pchip = PchipInterpolator(_ix[_ui2], _iy[_ui2])

# ─── R² and best model ───────────────────────────────────────────────────────
def _r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot


_r2s = {"PCHIP": _r2(_fy, _pchip(_fx))}
if _rr_fitted:
    _r2s["Rosin-Rammler"] = _r2(_fy, _rosin_rammler(_fx, *_popt_rr))
if _ln_fitted:
    _r2s["Log-Normal"] = _r2(_fy, _log_normal(_fx, *_popt_ln))
best_model = max(_r2s, key=_r2s.get)

# ─── Interval mass fractions ─────────────────────────────────────────────────
x_xmed_points = np.array([0.3, 0.5, 0.7, 0.9, 1.0, 1.3, 1.7, 2.3, 2.9])


def _cdf(x):
    if best_model == "Rosin-Rammler":
        return float(_rosin_rammler(x, *_popt_rr))
    if best_model == "Log-Normal":
        return float(_log_normal(x, *_popt_ln))
    return float(_pchip(x))


_cumulative = np.clip([_cdf(x) for x in x_xmed_points], 0, 1)
_diffs = np.diff(np.concatenate([[0.0], _cumulative]))
mass_fracs = _diffs / _diffs.sum()
