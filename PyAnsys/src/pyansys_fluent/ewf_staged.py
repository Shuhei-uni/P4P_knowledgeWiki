"""Offline decision and evidence checks for the continuous EWF step ladder.

No Fluent imports: command order and gates can be tested before execution.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import re
import statistics

FILM = re.compile(r"Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)")
FATAL = re.compile(r"floating point exception|received signal|fatal error|Divergence detected", re.I)
INNER = re.compile(r"sub-iteration:\s*(\d+) residual - h:\s*([^;]+); u:\s*([^;]+); v:\s*(\S+)")
BULK = ["v2-total-liquid-mass", "v2-lower-liquid-mass", "v2-total-vapor-mass",
        "v2-flux-phase2-steamoutlet", "v2-flux-phase1-steamoutlet",
        "p72-contact-removal", "p72-contact-inventory", "v2-applied-absorber",
        "p72s3-pressure-inlet", "p72s3-pressure-outlet"]
FILM_REPORTS = ["p72d-" + name for name in [
    "total-mass", "upper-mass", "lower-mass", "total-outflow", "total-stripped",
    "total-separated", "total-secondary", "total-dpm", "drain-rate",
    "total-courant", "total-thickness"]] + ["p72r-film-speed-max"]


@dataclass(frozen=True)
class LadderBlock:
    dt: float
    count: int

    @property
    def duration(self):
        return self.dt * self.count


LADDER = [LadderBlock(1e-6, 2000), LadderBlock(2e-6, 1000),
          LadderBlock(5e-6, 1000), LadderBlock(10e-6, 1000)]


def refresh_plan(dt, physical_dpm_interval=20e-6):
    """One film update between flow/profile refreshes; same DPM physical span."""
    if not math.isfinite(dt) or dt <= 0 or dt > 15e-6:
        raise ValueError("Step violates the declared 1% drain depletion bound")
    n = max(1, round(physical_dpm_interval / dt))
    if not math.isclose(n * dt, physical_dpm_interval, abs_tol=1e-12):
        raise ValueError("Candidate does not retain the selected physical DPM interval")
    return {"timestep-max": dt, "film-per-flow-iters": 1,
            "sub-time-steps": 1, "iters-per-dpm-step": n}


def history(text):
    result = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit():
            key, value = int(parts[0]), float(parts[1])
            if key in result:
                raise ValueError("Duplicate report coordinate")
            result[key] = value
    return result


def residuals(text):
    names, result = [], {}
    for line in text.splitlines():
        tokens = line.split()
        if tokens and tokens[0] == "iter" and "continuity" in tokens:
            names = tokens[1:tokens.index("time/iter")] if "time/iter" in tokens else tokens[1:]
        elif names and tokens and tokens[0].isdigit() and len(tokens) > len(names):
            try:
                values = list(map(float, tokens[1:len(names) + 1]))
            except ValueError:
                continue
            result[int(tokens[0])] = dict(zip(names, values))
    return result


def bulk_gate(windows, liquid_feed, pressure_floor):
    """Three nonoverlapping 1000-row windows; never use source-inclusive outlet."""
    if len(windows) < 3:
        return {"pass": False, "reason": "THREE_WINDOWS_REQUIRED"}
    windows = windows[-3:]
    floor = liquid_feed * .001
    limits = {"v2-total-liquid-mass": (.005, .01, 1e-12),
              "v2-flux-phase2-steamoutlet": (.02, .05, floor),
              "p72-contact-removal": (.02, .05, floor),
              "pressure-drop": (.02, .05, pressure_floor)}
    checks = {}
    for name, (mean_limit, span_limit, characteristic_floor) in limits.items():
        arrays = []
        for w in windows:
            h = w["histories"]
            if name == "pressure-drop":
                a = [x-y for x, y in zip(h["p72s3-pressure-inlet"], h["p72s3-pressure-outlet"])]
            else:
                a = h[name]
            if len(a) != 1000 or not all(math.isfinite(x) for x in a):
                return {"pass": False, "reason": "MISSING_OR_NONFINITE_BULK_WINDOW"}
            arrays.append(a)
        means = [statistics.fmean(a) for a in arrays]
        ranges = [(max(a)-min(a))/max(abs(m), characteristic_floor) for a, m in zip(arrays, means)]
        changes = [abs(b-a)/max(abs(a), abs(b), characteristic_floor) for a, b in zip(means, means[1:])]
        checks[name] = {"pass": max(ranges) <= span_limit and max(changes) <= mean_limit,
                        "means": means, "range_fractions": ranges, "mean_change_fractions": changes}
    discrepancies = []
    for w in windows:
        h = w["histories"]
        discrepancies.extend(abs(a+b) for a, b in zip(h["p72-contact-removal"], h["v2-applied-absorber"]))
    checks["collector_expression_agreement"] = {"pass": max(discrepancies) <= max(1e-8, liquid_feed*1e-7),
                                                 "max_discrepancy_kg_s": max(discrepancies)}
    # Residuals are supporting evidence, but incomplete/nonfinite rows forbid a gate.
    residual_arrays = [w.get("residuals", {}) for w in windows]
    finite = all(len(w) == 1000 and all(math.isfinite(x) and x >= 0 for row in w.values() for x in row.values())
                 for w in residual_arrays)
    checks["residuals_finite_complete"] = {"pass": finite}
    if finite:
        growth = {}
        names = set.intersection(*(set(next(iter(w.values()))) for w in residual_arrays))
        for n in sorted(names):
            means = [statistics.fmean(row[n] for row in w.values()) for w in residual_arrays]
            growth[n] = means[-1] <= 1.25*max(means[-2], 1e-8)
        checks["residual_late_growth"] = {"pass": all(growth.values()), "equations": growth}
    return {"pass": all(v["pass"] for v in checks.values()), "checks": checks}


def assess_block(text, histories, initial, start, count, dt, initial_clock, film=True,
                 ledger_basis="gross-reported-sources", require_all_inner=False):
    if ledger_basis not in {"gross-reported-sources", "verified-v252-net-secondary"}:
        raise ValueError("Unknown film ledger basis")
    ids = list(range(start+1, start+count+1))
    for name, h in histories.items():
        if not set(ids).issubset(h) or not all(math.isfinite(h[i]) for i in ids):
            raise ValueError("Missing/nonfinite history: " + name)
    clocks = [tuple(map(float, m.groups())) for m in FILM.finditer(text)]
    if len(clocks) != count or any(not all(math.isfinite(x) for x in row) for row in clocks):
        raise ValueError("Missing/nonfinite accepted film clocks")
    previous = initial_clock
    for clock, step, cfl in clocks:
        if cfl < 0 or not math.isclose(step, dt, rel_tol=1e-7, abs_tol=1e-12) or not math.isclose(clock-previous, dt, rel_tol=1e-6, abs_tol=1e-11):
            raise ValueError("Accepted film step/clock differs from declared block")
        previous = clock
    result = {"peak_courant": max(x[2] for x in clocks), "accepted_steps": count,
              "added_film_time_s": clocks[-1][0]-initial_clock,
              "fatal_solver_event": bool(FATAL.search(text)), "histories": {n: [h[i] for i in ids] for n, h in histories.items()},
              "residuals": {i: row for i, row in residuals(text).items() if i in ids}}
    failures = []
    if result["fatal_solver_event"]: failures.append("FATAL_SOLVER_EVENT")
    if result["peak_courant"] > .1: failures.append("COURANT_OPERATING_CEILING")
    if film:
        h = result["histories"]
        for n in ["p72d-total-mass", "p72d-lower-mass", "p72d-total-thickness"]:
            if min(h[n]) < -1e-12: failures.append("NEGATIVE_FILM_FIELD")
        if max(h["p72d-total-thickness"]) >= .3: failures.append("THICKNESS_LIMIT")
        departure = sum(histories[n][ids[-1]]-initial[n] for n in
                        ["p72d-total-mass", "p72d-total-outflow", "p72d-total-stripped", "p72d-total-separated"])
        supply = {n: sum(h[n])*dt for n in ["p72d-total-secondary", "p72d-total-dpm"]}
        drain = sum(h["p72d-drain-rate"])*dt
        ledger = departure + drain - sum(supply.values())
        original_ledger = ledger
        separated = histories["p72d-total-separated"][ids[-1]]-initial["p72d-total-separated"]
        # Case-specific native source probes must establish this overlap before
        # the caller selects it. Keep the original calculation in the receipt.
        # This is a net-source consistency check, not whole-system closure.
        if ledger_basis == "verified-v252-net-secondary":
            ledger -= separated
        denominator = sum(abs(v) for v in supply.values())
        fraction = abs(ledger)/max(denominator, 1e-12)
        if fraction > .01 and abs(ledger) > 1e-10: failures.append("FILM_LEDGER_OPERATING_LIMIT")
        result.update(direct_removal_kg=drain, integrated_sources_kg=supply,
                      ledger_residual_kg=ledger, ledger_fraction=fraction,
                      ledger_basis=ledger_basis,
                      original_ledger_residual_kg=original_ledger,
                      separated_mass_increment_kg=separated,
                      peak_thickness_m=max(h["p72d-total-thickness"]),
                      peak_speed_m_s=max(h["p72r-film-speed-max"]))
    inner = list(INNER.finditer(text))
    result["achieved_inner_residual_rows"] = len(inner)
    achieved = []
    left = 0
    for accepted in FILM.finditer(text):
        matches = list(INNER.finditer(text[left:accepted.start()]))
        if matches:
            try:
                last = matches[-1]
                achieved.append([float(last[k].strip()) for k in [2,3,4]])
            except ValueError:
                failures.append('INVALID_INNER_RESIDUAL')
        left = accepted.end()
    good = sum(all(math.isfinite(x) and 0 <= x <= 1e-5 for x in row) for row in achieved)
    if achieved and good < .99*len(achieved):
        failures.append('ACHIEVED_INNER_RESIDUAL_LIMIT')
    if require_all_inner and (len(achieved) != count or good != count):
        failures.append('ALL_INNER_STEPS_REQUIRED')
    result['inner_steps_observed'] = len(achieved)
    result['inner_steps_passed'] = good
    result['all_inner_steps_required'] = require_all_inner
    if require_all_inner:
        result['inner_convergence'] = 'PASS_ALL_RECORDED_STEPS' if len(achieved)==count and good==count else 'FAILED_OR_MISSING_REQUIRED_STEP'
    else:
        result["inner_convergence"] = 'PASS_RECORDED_STEPS' if len(achieved)==count and good >= .99*count else 'UNAVAILABLE_OR_INCOMPLETE_CLAIM_LIMIT'
    result["failures"] = failures
    result["pass"] = not failures
    return result


def journal(work, count, end, token="block"):
    """One fixed native solve; save before the terminal marker; no GUI exit."""
    if count < 1 or end < count:
        raise ValueError("Invalid native horizon")
    root = str(work).replace("\\", "/")
    if any(x in root for x in ['"', '\n', '\r']):
        raise ValueError("Unsafe journal path")
    lines = [f'/file/start-transcript "{root}/native-run.trn"',
             f'/solve/iterate {count}',
             f'/file/write-case-data "{root}/final-N{end}.cas.h5"']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', token):
        raise ValueError('Unsafe terminal token')
    lines.append('/file/stop-transcript')
    lines.append(f'(with-output-to-file "{root}/returned.txt" (lambda () (display "NATIVE_COMMAND_RETURNED") (newline)))')
    lines.append(f'(display "P72STAGED_RETURNED_{token}") (newline)')
    return '\n'.join(lines) + '\n'
