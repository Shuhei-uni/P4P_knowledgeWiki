#!/usr/bin/env python3
"""Build an exploratory F4 EWF child using the recorded E2.7 controls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.common import safe_get_state
from build_09cV2_student_velocity_adaptation import FILM_MATERIAL, set_leaf_readback
from run_phase8_parity_carrier import dump, load_pair, pair, require, save_pair, sha256

OUTPUT_ROOT = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\EWF\F4")
E27_CONTROLS = {
    "solve-momentum?": True,
    "mom-equation?": True,
    "mom-gravity?": True,
    "mom-aero-drive?": True,
    "mom-pressure?": False,
    "solve-energy?": False,
    "solve-scalar?": False,
    "secondary-phase-mode": 1,
    "film-vof-coupling?": False,
    "film-coupled-solution?": True,
    "ewf-adaptive?": False,
    "timestep-max": 1e-5,
    "adapt-init-dt": 1e-5,
    "courant-number": 0.05,
    "sub-iter-nums": 10,
    "thickness-limit": 0.3,
    "surface-tension?": False,
    "surface-tension": 0.07194,
    "dpm-collection?": True,
    "dpm-splashing?": True,
    "film-stripping?": True,
    "film-separation?": False,
}


def inspect(solver) -> dict:
    parameters = dict(solver.rp_vars().get("wall-film/model-parameters"))
    for name, target in E27_CONTROLS.items():
        actual = parameters.get(name)
        if isinstance(target, float):
            require(actual is not None and abs(float(actual) - target) <=
                    max(1e-12, abs(target) * 1e-8), f"EWF {name} mismatch: {actual}")
        else:
            require(actual == target, f"EWF {name} mismatch: {actual}")
    wall = solver.settings.setup.boundary_conditions.wall
    film = safe_get_state(wall["wall"].phase["mixture"].wall_film, "film wall")
    bottom = safe_get_state(wall["bottom"].phase["mixture"].wall_film, "bottom film")
    require(film.get("eulerian_film_wall") is True and
            film.get("enable_flow_momentum_coupling") is False and
            film.get("enable_dpm_wall_splash") is True,
            "Film wall or wall splash mismatch")
    require(bottom.get("eulerian_film_wall") is not True, "Bottom became a film wall")
    wall_dpm = safe_get_state(wall["wall"].phase["mixture"].discrete_phase,
                              "film wall DPM")
    bottom_dpm = safe_get_state(wall["bottom"].phase["mixture"].discrete_phase,
                                "bottom DPM")
    require(wall_dpm["bc_type"] == "reflect", "Inherited main-wall DPM BC changed")
    require(bottom_dpm["bc_type"] == "trap", "Bottom DPM fate changed")
    dpm = safe_get_state(solver.settings.setup.models.discrete_phase, "F4 DPM")
    injections = set(dpm.get("injections", {}))
    original = {name for name in injections if name.startswith("09cv3-finemist-")}
    require(len(original) == 7, "Original seven inlet bins changed")
    interaction = dpm["general_settings"]["interaction"]
    require(interaction["enabled"] is True and interaction["iteration_interval"] == 100,
            "F4 DPM source cadence changed")
    return {"model_parameters": parameters, "film_wall": film,
            "bottom_wall_film": bottom, "wall_dpm": wall_dpm,
            "bottom_dpm": bottom_dpm, "injections": dpm["injections"],
            "added_injections": sorted(injections - original),
            "interaction": interaction,
            "methods": safe_get_state(solver.settings.solution.methods, "F4 methods")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("f3_child_receipt", type=Path)
    args = parser.parse_args()
    parent = json.loads(args.f3_child_receipt.read_text(encoding="utf-8"))
    require(parent["status"] == "CASE_DATA_VERIFIED" and parent["mode"] == "allocated" and
            parent["family"] == "F2" and parent["fraction"] == 0.05 and
            parent.get("source_interval") == 100, "F4 parent must match the 5% F3 recovery")
    source = Path(parent["child_base"])
    for kind, path in zip(("case", "data"), pair(source)):
        require(path.is_file() and sha256(path) == parent["child_pair"][f"{kind}_sha256"],
                f"F3 parent {kind} changed")
    label = f"F4-26p81-5pct-E27-provisional-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    child = OUTPUT_ROOT / label
    receipt_path = ROOT / "output" / "phase8-ewf" / label / "build.json"
    require(not any(path.exists() for path in pair(child)) and not receipt_path.exists(),
            "F4 child collision")
    receipt = {"status": "BUILDING", "basis": "Phase 7.2A E2.7 provisional",
               "parent_receipt": str(args.f3_child_receipt), "child_base": str(child),
               "parent_case_sha256": parent["child_pair"]["case_sha256"],
               "controls": E27_CONTROLS,
               "claim_limit": "Exploratory F4 setup; Phase 7.2A final EWF basis is not established."}
    dump(receipt_path, receipt)
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double",
                           processor_count=4, ui_mode="gui", start_timeout=240,
                           cleanup_on_exit=False, start_transcript=True)
    try:
        load_pair(solver, source)
        receipt["parent_methods"] = safe_get_state(solver.settings.solution.methods,
                                                   "F3 parent methods")
        receipt["parent_injections"] = list(
            safe_get_state(solver.settings.setup.models.discrete_phase.injections,
                           "F3 inlet bins"))
        require(len(receipt["parent_injections"]) == 7, "F3 parent injection count changed")
        ewf = solver.tui.define.models.eulerian_wallfilm
        ewf.enable_wallfilm_model("yes")
        solver.execute_tui(
            '/define/models/eulerian-wallfilm/film-material yes '
            f'"{FILM_MATERIAL}"\n')
        parameters = solver.rp_vars().get("wall-film/model-parameters")
        require(isinstance(parameters, list), "Live EWF controls unavailable")
        missing = set(E27_CONTROLS) - set(dict(parameters))
        require(not missing, f"EWF controls missing: {sorted(missing)}")
        solver.rp_vars("wall-film/model-parameters", [
            (name, E27_CONTROLS.get(str(name), value)) for name, value in parameters])
        solver.tui.define.models.eulerian_wallfilm.solve_wallfilm_equation("yes")
        wall = solver.settings.setup.boundary_conditions.wall
        film = wall["wall"].phase["mixture"].wall_film
        set_leaf_readback(film.eulerian_film_wall, True, "F4 EWF wall")
        set_leaf_readback(film.film_condition_type, "film-wall-boundary", "F4 film condition")
        set_leaf_readback(film.enable_flow_momentum_coupling, False,
                          "F4 wall flow momentum coupling")
        set_leaf_readback(film.enable_dpm_wall_splash, True,
                          "F4 EWF wall DPM splash")
        # EWF collection is controlled by the EWF DPM Coupling option and its
        # film-wall DPM Interaction tab. Fluent 2025 R2 removes the DPM
        # ``wall-film`` BC while EWF is active: that BC belongs to the
        # incompatible Lagrangian Wall Film model. Preserve the parent BC.
        require(safe_get_state(wall["wall"].phase["mixture"].discrete_phase,
                               "F4 inherited wall DPM")["bc_type"] == "reflect",
                "F4 inherited main-wall DPM BC changed")
        require(safe_get_state(wall["bottom"].phase["mixture"].wall_film,
                               "F4 bottom film").get("eulerian_film_wall") is not True,
                "F4 bottom unexpectedly became EWF")
        solver.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        receipt["configured"] = inspect(solver)
        solver.settings.mesh.check()
        receipt["child_pair"] = save_pair(solver, child)
        load_pair(solver, child)
        receipt["reopened"] = inspect(solver)
        require(receipt["reopened"]["methods"] == receipt["parent_methods"],
                "F4 EWF setup changed carrier methods")
        receipt["status"] = "CASE_DATA_VERIFIED"
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        raise
    finally:
        dump(receipt_path, receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(receipt_path)}, indent=2))


if __name__ == "__main__":
    main()
