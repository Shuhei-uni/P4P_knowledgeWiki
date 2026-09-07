"""
Droplet Size Distribution Fitting — Figure 5 (Hoffmann, 2007 / Purnanto et al., 2013)
=======================================================================================
Fits a cumulative distribution to digitized data points from Figure 5 of
Purnanto et al. (2013), which shows the standard size distribution for
droplets in pipelines (Hoffmann, 2007).

The fitted distribution is then used to calculate precise interval mass
fractions for each of the 9 DPM injections used in the Harwell calculation.

Reference:
    Purnanto, M.H., Zarrouk, S.J. and Cater, J.E. (2013).
    CFD Modelling of Two-Phase Flow inside Geothermal Steam-Water Separators.
    IPENZ Transactions, Volume 40.

    Hoffmann, A.C. and Stein, L.E. (2007).
    Gas Cyclones and Swirl Tubes: Principles, Design and Operation, 2nd Ed.
    Springer, New York.
"""

import os
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─── Digitized Data Points from Figure 5 ────────────────────────────────────
# Format: (x/x_med, cumulative weight fraction)
_csv_path = "Digitized_Figure5_(Purnanto 2013)).csv"
_data = np.loadtxt(
    os.path.join(os.path.dirname(__file__), _csv_path),
    delimiter=","
)
digitized_x = _data[:, 0]
digitized_y = _data[:, 1]

# ─── Anchor points from paper text ──────────────────────────────────────────
# Paper states: ~5% at x/x_med = 0.3, 100% at x/x_med = 2.9
# Add these as constraints alongside digitized points
anchor_x = np.array([0.0, 0.3, 2.9])
anchor_y = np.array([0.0, 0.05, 1.0])

# ─── Distribution Models ─────────────────────────────────────────────────────

def rosin_rammler_cdf(x, n, x_prime):
    """
    Rosin-Rammler cumulative distribution (commonly used for droplet sizing).
    F(x) = 1 - exp(-(x/x_prime)^n)
    """
    return 1 - np.exp(-(x / x_prime)**n)

def log_normal_cdf(x, mu, sigma):
    """
    Log-normal cumulative distribution.
    F(x) = 0.5 * (1 + erf((ln(x) - mu) / (sigma * sqrt(2))))
    """
    from scipy.special import erf
    return 0.5 * (1 + erf((np.log(x + 1e-10) - mu) / (sigma * np.sqrt(2))))

def modified_log_normal_cdf(x, mu, sigma, scale):
    """Modified log-normal with scale parameter"""
    from scipy.special import erf
    return scale * 0.5 * (1 + erf((np.log(x + 1e-10) - mu) / (sigma * np.sqrt(2))))

# ─── Fit distributions ───────────────────────────────────────────────────────

# Combine digitized and anchor points for fitting
fit_x = np.concatenate([anchor_x[1:], digitized_x])  # exclude x=0 for log models
fit_y = np.concatenate([anchor_y[1:], digitized_y])

# Sort by x
sort_idx = np.argsort(fit_x)
fit_x = fit_x[sort_idx]
fit_y = fit_y[sort_idx]

# Remove duplicates
_, unique_idx = np.unique(fit_x, return_index=True)
fit_x = fit_x[unique_idx]
fit_y = fit_y[unique_idx]

# Fit Rosin-Rammler
try:
    popt_rr, _ = curve_fit(rosin_rammler_cdf, fit_x, fit_y,
                           p0=[1.5, 1.2], bounds=([0.1, 0.1], [10, 10]),
                           maxfev=10000)
    rr_n, rr_xp = popt_rr
    rr_fitted = True
except:
    rr_fitted = False

# Fit Log-normal
try:
    popt_ln, _ = curve_fit(log_normal_cdf, fit_x, fit_y,
                           p0=[0.0, 0.8], bounds=([-3, 0.1], [3, 5]),
                           maxfev=10000)
    ln_mu, ln_sigma = popt_ln
    ln_fitted = True
except:
    ln_fitted = False

# PCHIP interpolation (exact through data points, monotone)
# Add (0,0) and (2.9, 1.0) as boundary constraints
interp_x = np.concatenate([[0.0], fit_x, [2.9]])
interp_y = np.concatenate([[0.0], fit_y, [1.0]])
_, unique_idx2 = np.unique(interp_x, return_index=True)
interp_x = interp_x[unique_idx2]
interp_y = interp_y[unique_idx2]
pchip = PchipInterpolator(interp_x, interp_y)

# ─── Calculate R-squared for each model ─────────────────────────────────────
def r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred)**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    return 1 - ss_res / ss_tot

x_eval = fit_x
rr_r2 = r_squared(fit_y, rosin_rammler_cdf(x_eval, *popt_rr)) if rr_fitted else None
ln_r2 = r_squared(fit_y, log_normal_cdf(x_eval, *popt_ln)) if ln_fitted else None
pchip_r2 = r_squared(fit_y, pchip(x_eval))

# ─── x/x_med points for 9 injections ────────────────────────────────────────
# Using the same points as harwell_calculation.py
x_xmed_points = np.array([0.3, 0.5, 0.7, 0.9, 1.0, 1.3, 1.7, 2.3, 2.9])

def get_interval_fractions(x_points, cdf_func):
    """
    Calculate interval mass fractions from cumulative distribution.
    Interval fraction(i) = CDF(x_i) - CDF(x_{i-1})
    with CDF(0) = 0 as the lower boundary.
    """
    cumulative = np.array([cdf_func(x) for x in x_points])
    cumulative = np.clip(cumulative, 0, 1)

    # Prepend 0 for the lower boundary
    cumulative_with_zero = np.concatenate([[0.0], cumulative])

    # Interval fractions = differences between consecutive cumulative values
    interval_fracs = np.diff(cumulative_with_zero)

    # Normalise to ensure they sum to exactly 1
    interval_fracs = interval_fracs / interval_fracs.sum()

    return cumulative, interval_fracs

# Get fractions from each model
rr_cum, rr_fracs = get_interval_fractions(x_xmed_points,
    lambda x: rosin_rammler_cdf(x, *popt_rr)) if rr_fitted else (None, None)
ln_cum, ln_fracs = get_interval_fractions(x_xmed_points,
    lambda x: log_normal_cdf(x, *popt_ln)) if ln_fitted else (None, None)
pchip_cum, pchip_fracs = get_interval_fractions(x_xmed_points, pchip)

# ─── Print Results ───────────────────────────────────────────────────────────
def print_sep(char="-", width=95):
    print(char * width)

print()
print_sep("=")
print("  DROPLET SIZE DISTRIBUTION FITTING — Figure 5 (Hoffmann, 2007 / Purnanto et al., 2013)")
print_sep("=")

print()
print("  Digitized data points:")
print_sep()
print(f"  {'x/x_med':>10}  {'Cumulative weight fraction':>28}")
print_sep()
for x, y in zip(digitized_x, digitized_y):
    print(f"  {x:>10.4f}  {y:>28.6f}")
print_sep()

print()
print("  Paper anchor points (from text):")
print(f"    x/x_med = 0.3  → cumulative fraction ≈ 0.05 (5%)")
print(f"    x/x_med = 2.9  → cumulative fraction = 1.00 (100%)")

print()
print_sep("=")
print("  MODEL FIT RESULTS")
print_sep("=")

if rr_fitted:
    print(f"\n  Rosin-Rammler:  F(x) = 1 - exp(-(x/x')^n)")
    print(f"    n      = {rr_n:.6f}")
    print(f"    x'     = {rr_xp:.6f}")
    print(f"    R²     = {rr_r2:.8f}")

if ln_fitted:
    print(f"\n  Log-Normal:     F(x) = 0.5*(1 + erf((ln(x) - mu) / (sigma*sqrt(2))))")
    print(f"    mu     = {ln_mu:.6f}")
    print(f"    sigma  = {ln_sigma:.6f}")
    print(f"    R²     = {ln_r2:.8f}")

print(f"\n  PCHIP Interpolation (monotone cubic, exact through data points)")
print(f"    R²     = {pchip_r2:.8f}")

r2_values = {}
if rr_fitted: r2_values["Rosin-Rammler"] = rr_r2
if ln_fitted: r2_values["Log-Normal"] = ln_r2
r2_values["PCHIP"] = pchip_r2
best_model = max(r2_values, key=r2_values.get)
print(f"\n  Best fit: {best_model} (R² = {r2_values[best_model]:.8f})")

print()
print_sep("=")
print("  CUMULATIVE FRACTIONS AND INTERVAL MASS FRACTIONS AT 9 INJECTION POINTS")
print_sep("=")

# Header
print(f"\n  {'Inj':>4}  {'x/x_med':>8}  ", end="")
if rr_fitted:
    print(f"{'RR Cum':>8}  {'RR Frac':>8}  ", end="")
if ln_fitted:
    print(f"{'LN Cum':>8}  {'LN Frac':>8}  ", end="")
print(f"{'PCHIP Cum':>10}  {'PCHIP Frac':>10}  {'Previous':>10}")
print_sep()

prev_fracs = [0.05, 0.10, 0.15, 0.15, 0.10, 0.15, 0.10, 0.10, 0.10]

for i, (x, pf) in enumerate(zip(x_xmed_points, prev_fracs)):
    print(f"  {i+1:>4}  {x:>8.1f}  ", end="")
    if rr_fitted:
        print(f"{rr_cum[i]:>8.4f}  {rr_fracs[i]:>8.4f}  ", end="")
    if ln_fitted:
        print(f"{ln_cum[i]:>8.4f}  {ln_fracs[i]:>8.4f}  ", end="")
    print(f"{pchip_cum[i]:>10.4f}  {pchip_fracs[i]:>10.4f}  {pf:>10.4f}")

print_sep()
print(f"  {'Total':>4}  {'':>8}  ", end="")
if rr_fitted:
    print(f"{'':>8}  {sum(rr_fracs):>8.4f}  ", end="")
if ln_fitted:
    print(f"{'':>8}  {sum(ln_fracs):>8.4f}  ", end="")
print(f"{'':>10}  {sum(pchip_fracs):>10.4f}  {sum(prev_fracs):>10.4f}")

print()
print_sep("=")
print(f"  RECOMMENDED INTERVAL FRACTIONS — Using {best_model}")
print_sep("=")

if best_model == "Rosin-Rammler":
    best_fracs = rr_fracs
elif best_model == "Log-Normal":
    best_fracs = ln_fracs
else:
    best_fracs = pchip_fracs

print(f"\n  {'Inj':>4}  {'x/x_med':>8}  {'Interval Fraction':>18}  {'As Percentage':>14}")
print_sep()
for i, (x, f) in enumerate(zip(x_xmed_points, best_fracs)):
    marker = " *" if i == 4 else "  "
    print(f"  {i+1:>4}  {x:>8.1f}  {f:>18.6f}  {f*100:>13.4f}%{marker}")
print_sep()
print(f"  {'Total':>4}  {'':>8}  {sum(best_fracs):>18.6f}  {sum(best_fracs)*100:>13.4f}%")
print(f"  * = median diameter injection (x/x_med = 1.0)")

print()
print_sep("=")
print("  VALIDATION AGAINST PAPER TEXT")
print_sep("=")
cum_at_03 = (rosin_rammler_cdf(0.3, *popt_rr) if best_model == "Rosin-Rammler" else
             log_normal_cdf(0.3, *popt_ln) if best_model == "Log-Normal" else
             float(pchip(0.3)))
cum_at_29 = (rosin_rammler_cdf(2.9, *popt_rr) if best_model == "Rosin-Rammler" else
             log_normal_cdf(2.9, *popt_ln) if best_model == "Log-Normal" else
             float(pchip(2.9)))

print(f"\n  Paper states: ~5% at x/x_med = 0.3")
print(f"  Model gives:  {cum_at_03*100:.2f}% at x/x_med = 0.3  {'✓' if abs(cum_at_03 - 0.05) < 0.02 else '✗ (check digitization)'}")
print(f"\n  Paper states: 100% at x/x_med = 2.9")
print(f"  Model gives:  {cum_at_29*100:.2f}% at x/x_med = 2.9  {'✓' if abs(cum_at_29 - 1.0) < 0.02 else '✗ (check digitization)'}")

print()
print("  Notes:")
print("  - PCHIP: monotone cubic interpolation, exact through digitized points")
print("  - Rosin-Rammler: standard model for droplet/particle size distributions")
print("  - Log-Normal: alternative standard model for droplet distributions")
print("  - 'Previous' column shows approximate fractions used before digitization")
print("  - All interval fractions normalised to sum to exactly 1.0")
print()

# ─── Plot ────────────────────────────────────────────────────────────────────
x_smooth = np.linspace(0.001, 3.0, 500)

fig, ax = plt.subplots(figsize=(8, 5))

plot_styles = {
    "Rosin-Rammler": ('#E74C3C', lambda x: rosin_rammler_cdf(x, *popt_rr) if rr_fitted else None),
    "Log-Normal":    ('#3498DB', lambda x: log_normal_cdf(x, *popt_ln) if ln_fitted else None),
    "PCHIP":         ('#2ECC71', lambda x: np.clip(pchip(x), 0, 1)),
}
r2_labels = {"Rosin-Rammler": rr_r2 if rr_fitted else None,
             "Log-Normal": ln_r2 if ln_fitted else None,
             "PCHIP": pchip_r2}

for name, (color, fn) in plot_styles.items():
    y = fn(x_smooth)
    if y is None:
        continue
    is_best = (name == best_model)
    ax.plot(x_smooth, y,
            color=color,
            linewidth=2.5 if is_best else 1.5,
            linestyle='-' if is_best else '--',
            alpha=1.0 if is_best else 0.4,
            label=f'{name} (R²={r2_labels[name]:.4f})' + (' ← best' if is_best else ''))

ax.scatter(digitized_x, digitized_y,
           color='black', s=80, zorder=5, label='Digitized points (6)')

ax.set_xlabel('x / x$_{med}$', fontsize=12)
ax.set_ylabel('Cumulative weight fraction', fontsize=12)
ax.set_title('Droplet Size Distribution — Figure 5\n(Hoffmann, 2007 / Purnanto et al., 2013)',
             fontsize=12, fontweight='bold')
ax.set_xlim(0, 3.0)
ax.set_ylim(0, 1.05)
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()
