"""
Steam quality calculator from DPM injection outcomes.

This script follows the outlet steam-quality approach described by
Purnanto, Zarrouk, and Cater (2013):

- Outlet steam quality is the mass-flow ratio of steam leaving the top outlet
  to the total two-phase mass flow leaving that outlet.
- Trapped particles are treated as separated liquid.
- By default, incomplete particles are also treated as separated liquid,
  matching the paper's preferred interpretation.

Expected CSV columns
--------------------
Minimum:
    inj,trapped,escaped,incomplete

Also supported:
    case,inj,trapped,escaped,incomplete

Optional explicit flow columns if you do not want to rely on the built-in
Harwell cases:
    m_gas
    liquid_mass_flow_kgs

If `case` is omitted, the script treats the whole file as one case and expects
`m_gas` plus either `liquid_mass_flow_kgs` or a single built-in case selected
via `--case`.
"""

"python3 Code/steam_quality_calculation.py Code/steam_quality_input_template.csv"



import argparse
import csv
import os
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class InjectionOutcome:
    case_name: str
    inj: int
    trapped: float
    escaped: float
    incomplete: float
    particle_total: float
    liquid_mass_flow_kgs: float
    escaped_fraction: float
    separated_fraction: float
    liquid_to_outlet_kgs: float
    liquid_separated_kgs: float


CASES = [
    {"name": "Case 1", "label": "h = 1600 kJ/kg -25%", "m_gas": 60.52, "m_liq": 87.69},
    {"name": "Case 2", "label": "h = 1440 kJ/kg", "m_gas": 64.85, "m_liq": 132.76},
    {"name": "Case 3", "label": "h = 1520 kJ/kg", "m_gas": 72.77, "m_liq": 124.84},
    {"name": "Case 4", "label": "h = 1600 kJ/kg", "m_gas": 80.69, "m_liq": 116.92},
    {"name": "Case 5", "label": "h = 1680 kJ/kg", "m_gas": 88.61, "m_liq": 109.00},
    {"name": "Case 6", "label": "h = 1760 kJ/kg", "m_gas": 96.52, "m_liq": 101.09},
    {"name": "Case 7", "label": "h = 1976 kJ/kg", "m_gas": 117.91, "m_liq": 79.70},
    {"name": "Case 8", "label": "h = 2214 kJ/kg", "m_gas": 141.47, "m_liq": 56.14},
]

CASE_LOOKUP = {case["name"]: case for case in CASES}
CASE_LABEL_LOOKUP = {case["label"]: case for case in CASES}


def normalize_case_name(value: str) -> str:
    value = value.strip()
    if value in CASE_LOOKUP:
        return value
    if value in CASE_LABEL_LOOKUP:
        return CASE_LABEL_LOOKUP[value]["name"]

    lowered = value.lower()
    for case in CASES:
        if lowered == case["name"].lower() or lowered == case["label"].lower():
            return case["name"]

    raise ValueError(
        f"Unknown case '{value}'. Use one of: "
        + ", ".join(case["name"] for case in CASES)
    )


def built_in_liquid_mass_flows(case_name: str) -> dict[int, float]:
    output_csv = os.path.join(os.path.dirname(__file__), "harwell_results.csv")
    mass_flows: dict[int, float] = {}

    with open(output_csv, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["case"] == case_name:
                mass_flows[int(row["inj"])] = float(row["mass_flow_kgs"])

    if not mass_flows:
        raise ValueError(
            f"No built-in injection mass flows found for {case_name} in {output_csv}."
        )

    return mass_flows


def built_in_m_gas(case_name: str) -> float:
    return CASE_LOOKUP[case_name]["m_gas"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate outlet steam quality from DPM injection results."
    )
    parser.add_argument(
        "input_csv",
        help="CSV containing injection outcomes.",
    )
    parser.add_argument(
        "--case",
        dest="default_case",
        help="Built-in case name to use when the CSV does not include a 'case' column.",
    )
    parser.add_argument(
        "--incomplete",
        choices=("separated", "escaped", "ignore"),
        default="separated",
        help=(
            "How to treat incomplete particles. Default is 'separated' to match "
            "the paper's preferred assumption."
        ),
    )
    parser.add_argument(
        "--output-csv",
        help="Optional path for a per-case summary CSV.",
    )
    return parser.parse_args()


def parse_float(row: dict[str, str], field: str, default: float | None = None) -> float:
    value = row.get(field, "")
    if value is None or value == "":
        if default is None:
            raise ValueError(f"Missing required field '{field}'.")
        return default
    return float(value)


def parse_int(row: dict[str, str], field: str) -> int:
    value = row.get(field, "")
    if value is None or value == "":
        raise ValueError(f"Missing required field '{field}'.")
    return int(float(value))


def fractions_from_counts(
    trapped: float,
    escaped: float,
    incomplete: float,
    incomplete_policy: str,
) -> tuple[float, float, float]:
    particle_total = trapped + escaped + incomplete
    if particle_total <= 0:
        raise ValueError("Each injection row must have a positive particle total.")

    if incomplete_policy == "separated":
        separated = trapped + incomplete
        escaped_eff = escaped
    elif incomplete_policy == "escaped":
        separated = trapped
        escaped_eff = escaped + incomplete
    else:
        separated = trapped
        escaped_eff = escaped
        particle_total = trapped + escaped
        if particle_total <= 0:
            raise ValueError(
                "With '--incomplete ignore', trapped + escaped must be positive."
            )

    return particle_total, escaped_eff / particle_total, separated / particle_total


def load_rows(
    path: str,
    default_case: str | None,
    incomplete_policy: str,
) -> list[InjectionOutcome]:
    outcomes: list[InjectionOutcome] = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV is empty or missing a header row.")

        has_case_col = "case" in reader.fieldnames
        mass_flow_cache: dict[str, dict[int, float]] = {}

        for row_number, row in enumerate(reader, start=2):
            try:
                if has_case_col:
                    case_name = normalize_case_name(row["case"])
                elif default_case:
                    case_name = normalize_case_name(default_case)
                elif row.get("m_gas", "") and row.get("liquid_mass_flow_kgs", ""):
                    case_name = "Input Case"
                else:
                    raise ValueError(
                        "CSV without a 'case' column must provide '--case' or "
                        "explicit 'm_gas' and 'liquid_mass_flow_kgs' columns."
                    )

                inj = parse_int(row, "inj")
                trapped = parse_float(row, "trapped", 0.0)
                escaped = parse_float(row, "escaped", 0.0)
                incomplete = parse_float(row, "incomplete", 0.0)

                particle_total, escaped_fraction, separated_fraction = fractions_from_counts(
                    trapped,
                    escaped,
                    incomplete,
                    incomplete_policy,
                )

                if row.get("liquid_mass_flow_kgs", ""):
                    liquid_mass_flow_kgs = parse_float(row, "liquid_mass_flow_kgs")
                else:
                    if case_name not in mass_flow_cache:
                        mass_flow_cache[case_name] = built_in_liquid_mass_flows(case_name)
                    try:
                        liquid_mass_flow_kgs = mass_flow_cache[case_name][inj]
                    except KeyError as exc:
                        raise ValueError(
                            f"Injection {inj} is not valid for {case_name}. "
                            "Expected injections 1-9."
                        ) from exc

                outcomes.append(
                    InjectionOutcome(
                        case_name=case_name,
                        inj=inj,
                        trapped=trapped,
                        escaped=escaped,
                        incomplete=incomplete,
                        particle_total=particle_total,
                        liquid_mass_flow_kgs=liquid_mass_flow_kgs,
                        escaped_fraction=escaped_fraction,
                        separated_fraction=separated_fraction,
                        liquid_to_outlet_kgs=liquid_mass_flow_kgs * escaped_fraction,
                        liquid_separated_kgs=liquid_mass_flow_kgs * separated_fraction,
                    )
                )
            except ValueError as exc:
                raise ValueError(f"Row {row_number}: {exc}") from exc

    if not outcomes:
        raise ValueError("Input CSV contains no data rows.")

    return outcomes


def determine_case_m_gas(case_name: str, raw_rows: list[dict[str, str]]) -> float:
    m_gas_values: set[float] = set()

    for row in raw_rows:
        m_gas_raw = row.get("m_gas", "")
        if not m_gas_raw:
            continue

        if row.get("case", ""):
            row_case_name = normalize_case_name(row["case"])
        else:
            row_case_name = "Input Case"

        if row_case_name == case_name:
            m_gas_values.add(float(m_gas_raw))

    if len(m_gas_values) > 1:
        raise ValueError(f"Multiple m_gas values supplied for {case_name}.")
    if len(m_gas_values) == 1:
        return next(iter(m_gas_values))
    if case_name == "Input Case":
        raise ValueError(
            "Could not determine m_gas for Input Case. Supply an 'm_gas' column."
        )
    return built_in_m_gas(case_name)


def load_raw_rows(path: str) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def summarize_by_case(
    outcomes: list[InjectionOutcome],
    raw_rows: list[dict[str, str]],
) -> list[dict[str, float | str]]:
    grouped: dict[str, list[InjectionOutcome]] = defaultdict(list)
    for outcome in outcomes:
        grouped[outcome.case_name].append(outcome)

    summaries: list[dict[str, float | str]] = []
    for case_name, case_rows in grouped.items():
        m_gas = determine_case_m_gas(case_name, raw_rows)
        liquid_to_outlet = sum(row.liquid_to_outlet_kgs for row in case_rows)
        liquid_separated = sum(row.liquid_separated_kgs for row in case_rows)
        liquid_total = sum(row.liquid_mass_flow_kgs for row in case_rows)
        total_top_outlet = m_gas + liquid_to_outlet

        quality = m_gas / total_top_outlet
        collection_efficiency = liquid_separated / liquid_total
        carryover_fraction = liquid_to_outlet / liquid_total

        summaries.append(
            {
                "case": case_name,
                "m_gas_kgs": m_gas,
                "liquid_inlet_kgs": liquid_total,
                "liquid_to_top_outlet_kgs": liquid_to_outlet,
                "liquid_separated_kgs": liquid_separated,
                "top_outlet_total_kgs": total_top_outlet,
                "steam_quality": quality,
                "steam_quality_percent": quality * 100.0,
                "collection_efficiency": collection_efficiency,
                "collection_efficiency_percent": collection_efficiency * 100.0,
                "liquid_carryover_fraction": carryover_fraction,
                "liquid_carryover_percent": carryover_fraction * 100.0,
            }
        )

    return sorted(summaries, key=lambda row: row["case"])


def print_summary(summaries: list[dict[str, float | str]], incomplete_policy: str) -> None:
    print()
    print("=" * 92)
    print("STEAM QUALITY FROM DPM INJECTION RESULTS")
    print("=" * 92)
    print(f"Incomplete-particle treatment: {incomplete_policy}")
    print(
        "Paper basis: outlet steam quality = steam mass at top outlet / "
        "total mass at top outlet"
    )
    print("=" * 92)

    header = (
        f"{'Case':<10} {'m_gas':>10} {'m_liq':>10} {'liq->top':>12} "
        f"{'quality':>10} {'quality %':>11} {'collect %':>11}"
    )
    print(header)
    print("-" * len(header))

    for row in summaries:
        print(
            f"{row['case']:<10} "
            f"{row['m_gas_kgs']:>10.4f} "
            f"{row['liquid_inlet_kgs']:>10.4f} "
            f"{row['liquid_to_top_outlet_kgs']:>12.4f} "
            f"{row['steam_quality']:>10.6f} "
            f"{row['steam_quality_percent']:>10.4f}% "
            f"{row['collection_efficiency_percent']:>10.4f}%"
        )

    print("=" * 92)
    print()


def write_summary_csv(path: str, summaries: list[dict[str, float | str]]) -> None:
    fieldnames = [
        "case",
        "m_gas_kgs",
        "liquid_inlet_kgs",
        "liquid_to_top_outlet_kgs",
        "liquid_separated_kgs",
        "top_outlet_total_kgs",
        "steam_quality",
        "steam_quality_percent",
        "collection_efficiency",
        "collection_efficiency_percent",
        "liquid_carryover_fraction",
        "liquid_carryover_percent",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)


def main() -> None:
    args = parse_args()
    input_csv = os.path.abspath(args.input_csv)

    raw_rows = load_raw_rows(input_csv)
    outcomes = load_rows(input_csv, args.default_case, args.incomplete)
    summaries = summarize_by_case(outcomes, raw_rows)
    print_summary(summaries, args.incomplete)

    if args.output_csv:
        output_path = os.path.abspath(args.output_csv)
        write_summary_csv(output_path, summaries)
        print(f"Saved summary CSV: {output_path}")


if __name__ == "__main__":
    main()
