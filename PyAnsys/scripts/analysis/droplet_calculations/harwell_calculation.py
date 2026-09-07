"""
Harwell Droplet Size Calculation
=================================
Calculates DPM injection diameters and mass flows for the Harwell enthalpy
cases used in Bangma and spiral-inlet separator calculations.

Reference:
    Purnanto, M.H., Zarrouk, S.J. and Cater, J.E. (2013).
    CFD Modelling of Two-Phase Flow inside Geothermal Steam-Water Separators.
    IPENZ Transactions, Volume 40.

Harwell Equation (Eq. 3, Purnanto et al., 2013):
    (x)_sa = 1.91 * Dt * (Re^0.1 / We^0.6) * (rho_g / rho_l)^0.6
    (x)_med = 1.42 * (x)_sa

    Re = rho_g * vt * Dt / mu_g
    We = rho_g * vt^2 * Dt / sigma
    vt = m_gas / (rho_g * A_inlet)
"""

import csv
import os
from droplet_distribution import x_xmed_points, mass_fracs, best_model

# ─── Fixed Fluid Properties (Table 1, Purnanto et al. 2013, Psep = 11.2 bara) ──
rho_g   = 5.73          # Gas density [kg/m3]
rho_l   = 881.77        # Liquid density [kg/m3]
mu_g    = 15.188e-6     # Gas dynamic viscosity [kg/m.s]
sigma   = 0.0411        # Surface tension [N/m]

# ─── Inlet Designs ─────────────────────────────────────────────────────────
inlet_designs = [
    {
        "name": "Bangma Separator",
        "diameter_m": 0.724,
        "area_m2": 0.4115,
        "output_csv": "harwell_results.csv",
        "use_case_velocity_overrides": True,
    },
    {
        "name": "Spiral Inlet",
        "diameter_m": 0.724,
        "area_m2": 0.724**2,
        "output_csv": "spiral_harwell_results.csv",
        "use_case_velocity_overrides": False,
    },
]

# ─── Enthalpy Cases (Table 2, Purnanto et al. 2013) ────────────────────────
cases = [
    {"name": "Case 1",  "label": "h = 1600 kJ/kg -25%",  "m_gas": 60.52,  "m_liq": 87.69},
    {"name": "Case 2",  "label": "h = 1440 kJ/kg",       "m_gas": 64.85,  "m_liq": 132.76},
    {"name": "Case 3",  "label": "h = 1520 kJ/kg",       "m_gas": 72.77,  "m_liq": 124.84},
    {"name": "Case 4",  "label": "h = 1600 kJ/kg",       "m_gas": 80.69,  "m_liq": 116.92},
    {"name": "Case 5",  "label": "h = 1680 kJ/kg",       "m_gas": 88.61,  "m_liq": 109.00},
    {"name": "Case 6",  "label": "h = 1760 kJ/kg",       "m_gas": 96.52,  "m_liq": 101.09},
    {"name": "Case 7",  "label": "h = 1976 kJ/kg",       "m_gas": 117.91, "m_liq": 79.70, "vt": 50.0},
    {"name": "Case 8",  "label": "h = 2214 kJ/kg",       "m_gas": 141.47, "m_liq": 56.14, "vt": 60.0},
]

# ─── Droplet Size Distribution (Figure 5, Hoffmann 2007 / Purnanto 2013) ───
# Fractions from active Purnanto/Fluent distribution in droplet_distribution.py.
injections = [
    {"index": i + 1, "x_xmed": float(x), "mass_frac": float(f)}
    for i, (x, f) in enumerate(zip(x_xmed_points, mass_fracs))
]

# ─── Harwell Calculation Function ───────────────────────────────────────────
def harwell(m_gas, m_liq, diameter_m, area_m2, vt=None):
    """
    Calculate Harwell droplet sizes and injection parameters.

    Parameters:
        m_gas : float - gas mass flow rate [kg/s]
        m_liq : float - liquid mass flow rate [kg/s]
        diameter_m : float - inlet hydraulic/equivalent diameter [m]
        area_m2 : float - inlet flow area [m2]
        vt    : float | None - optional inlet gas velocity [m/s]

    Returns:
        dict with all intermediate values and injection parameters
    """
    # Mean gas velocity at inlet
    if vt is None:
        vt = m_gas / (rho_g * area_m2)

    # Reynolds and Weber numbers
    Re = rho_g * vt * diameter_m / mu_g
    We = rho_g * vt**2 * diameter_m / sigma

    # Exponent terms (calculated with full floating point precision)
    Re_exp  = Re**0.1
    We_exp  = We**0.6
    rho_exp = (rho_g / rho_l)**0.6

    # Sauter mean diameter
    x_sa = 1.91 * diameter_m * (Re_exp / We_exp) * rho_exp  # [m]

    # Median diameter
    x_med = 1.42 * x_sa  # [m]

    # Injection diameters and mass flows
    inj_results = []
    for inj in injections:
        diameter = inj["x_xmed"] * x_med  # [m]
        mass_flow = inj["mass_frac"] * m_liq  # [kg/s]
        inj_results.append({
            "index":     inj["index"],
            "x_xmed":    inj["x_xmed"],
            "diameter_m":  diameter,
            "diameter_mm": diameter * 1000,
            "mass_flow": mass_flow,
        })

    return {
        "vt":       vt,
        "Re":       Re,
        "We":       We,
        "Re_exp":   Re_exp,
        "We_exp":   We_exp,
        "rho_exp":  rho_exp,
        "x_sa_mm":  x_sa * 1000,
        "x_med_mm": x_med * 1000,
        "injections": inj_results,
    }

# ─── Print Results ───────────────────────────────────────────────────────────
def print_separator(char="-", width=90):
    print(char * width)

def case_velocity(case, design):
    if design["use_case_velocity_overrides"]:
        return case.get("vt")
    return None

def calculate_design_results(design):
    all_results = []
    for case in cases:
        result = harwell(
            case["m_gas"],
            case["m_liq"],
            design["diameter_m"],
            design["area_m2"],
            case_velocity(case, design),
        )
        all_results.append((case, result))
    return all_results

def print_results(design):
    print()
    print_separator("=")
    print(f"  HARWELL DROPLET SIZE CALCULATION — {design['name']} (Purnanto et al., 2013)")
    print_separator("=")
    print(f"  Fixed properties: rho_g={rho_g} kg/m3, rho_l={rho_l} kg/m3")
    print(f"                    mu_g={mu_g:.3e} kg/m.s, sigma={sigma} N/m")
    print(f"  Geometry:         Dh={design['diameter_m']} m, A={design['area_m2']} m2")
    print_separator("=")

    all_results = calculate_design_results(design)
    for case, result in all_results:
        print()
        print(f"  {case['name']} — {case['label']}")
        print(f"  m_gas = {case['m_gas']} kg/s | m_liq = {case['m_liq']} kg/s")
        print_separator()

        # Intermediate values
        print(f"  {'Parameter':<30} {'Value':>20}")
        print_separator()
        print(f"  {'Inlet velocity vt':<30} {result['vt']:>20.4f}  m/s")
        print(f"  {'Reynolds number Re':<30} {result['Re']:>20.1f}")
        print(f"  {'Weber number We':<30} {result['We']:>20.1f}")
        print(f"  {'Re^0.1':<30} {result['Re_exp']:>20.6f}")
        print(f"  {'We^0.6':<30} {result['We_exp']:>20.4f}")
        print(f"  {'(rho_g/rho_l)^0.6':<30} {result['rho_exp']:>20.6f}")
        print(f"  {'Sauter mean (x)_sa':<30} {result['x_sa_mm']:>20.4f}  mm")
        print(f"  {'Median (x)_med':<30} {result['x_med_mm']:>20.4f}  mm")
        print_separator()

        # Injection table
        print(f"  {'Inj':>4}  {'x/x_med':>8}  {'Diameter (mm)':>14}  {'Diameter (m)':>14}  {'Mass Flow (kg/s)':>16}")
        print_separator()
        total_mass = 0
        for inj in result["injections"]:
            marker = " *" if inj["x_xmed"] == 1.0 else "  "
            print(f"  {inj['index']:>4}  {inj['x_xmed']:>8.2f}  "
                  f"{inj['diameter_mm']:>14.4f}  "
                  f"{inj['diameter_m']:>14.4e}  "
                  f"{inj['mass_flow']:>16.4f}{marker}")
            total_mass += inj["mass_flow"]
        print_separator()
        print(f"  {'Total':>4}  {'':>8}  {'':>14}  {'':>14}  {total_mass:>16.4f}")
        print(f"  * = median diameter injection")
        print()

    # ── Summary table across all cases ──────────────────────────────────────
    print()
    print_separator("=")
    print("  SUMMARY — Harwell Parameters Across All Cases")
    print_separator("=")
    header = f"  {'Case':<10} {'h (kJ/kg)':<14} {'vt (m/s)':>10} {'Re':>12} {'We':>10} {'x_sa (mm)':>10} {'x_med (mm)':>11}"
    print(header)
    print_separator()
    for case, result in all_results:
        label = case["label"].replace("h = ", "").replace(" kJ/kg", "").replace("-25%", "(-25%)")
        print(f"  {case['name']:<10} {label:<14} "
              f"{result['vt']:>10.4f} "
              f"{result['Re']:>12.0f} "
              f"{result['We']:>10.0f} "
              f"{result['x_sa_mm']:>10.4f} "
              f"{result['x_med_mm']:>11.4f}")
    print_separator("=")

    # ── Velocity comparison table ────────────────────────────────────────────
    print()
    print_separator("=")
    print("  INJECTION Z-VELOCITY PER CASE (for Fluent DPM setup)")
    print_separator("=")
    print(f"  {'Case':<10} {'h (kJ/kg)':<20} {'vt (m/s)':>10}  {'Z-velocity':>12}")
    print_separator()
    for case, result in all_results:
        print(f"  {case['name']:<10} {case['label']:<20} "
              f"{result['vt']:>10.4f}  "
              f"{-result['vt']:>12.4f} m/s")
    print_separator("=")
    print()
    print("  Note: Z-velocity is negative (flow directed in -Z direction into vessel)")
    print(f"  Note: Injection mass fractions from {best_model} (Figure 5, Hoffmann 2007 / Purnanto 2013)")
    print("  Note: All calculations performed with full floating point precision — no intermediate rounding")
    print()

def save_csv(design):
    output = os.path.join(os.path.dirname(__file__), design["output_csv"])
    fieldnames = [
        "case", "enthalpy_kJkg", "vt_ms", "z_velocity_ms",
        "inj", "x_xmed", "diameter_mm", "diameter_m", "mass_flow_kgs",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for case, result in calculate_design_results(design):
            enthalpy = case["label"].replace("h = ", "").replace(" kJ/kg", "")
            for inj in result["injections"]:
                writer.writerow({
                    "case":           case["name"],
                    "enthalpy_kJkg":  enthalpy,
                    "vt_ms":          round(result["vt"], 6),
                    "z_velocity_ms":  round(-result["vt"], 6),
                    "inj":            inj["index"],
                    "x_xmed":         inj["x_xmed"],
                    "diameter_mm":    round(inj["diameter_mm"], 6),
                    "diameter_m":     f"{inj['diameter_m']:.6e}",
                    "mass_flow_kgs":  round(inj["mass_flow"], 6),
                })
    print(f"  Saved: {output}")

if __name__ == "__main__":
    for design in inlet_designs:
        print_results(design)
        save_csv(design)
