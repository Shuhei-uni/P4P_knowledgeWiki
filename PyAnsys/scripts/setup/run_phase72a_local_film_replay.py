"""Replay an unavailable remote checkpoint in a caller-owned local Fluent session.

No launch, attach, exit, or continuous status polling. Native autosave owns
intermediate checkpoints; two large TUI commands own the requested horizon.
"""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import traceback

import run_phase72a_contact_absorber as contact
import run_phase72a_r3_ewf_absorber_direct as prior


def readback(s):
    bc = s.settings.setup.boundary_conditions
    return {
        "fields": contact.snapshot(s),
        "hooks": s.settings.setup.cell_zone_conditions.fluid[contact.LOWER_ZONE].get_state(),
        "lower_film_wall": bc.wall["wall:004"].get_state(),
        "entry_faces": {z: bc.porous_jump[z].get_state() for z in contact.ENTRY_FACES},
        "dpm": s.settings.setup.models.discrete_phase.get_state(),
        "film_parameters": dict(s.rp_vars("wall-film/model-parameters")),
        "controls": s.settings.solution.controls.get_state(),
    }


def require_match(actual, expected):
    checks = {}
    for group in expected:
        if group == "pair":
            continue
        if group == "fields":
            checks[group] = actual[group].keys() == expected[group].keys() and all(
                math.isclose(actual[group][k][0], v[0], rel_tol=1e-9, abs_tol=1e-10)
                and actual[group][k][1:] == v[1:]
                for k, v in expected[group].items()
            )
        else:
            checks[group] = actual[group] == expected[group]
    if not all(checks.values()):
        raise RuntimeError(f"Local parent/readback mismatch: {checks}")
    return checks


def prepare(s, work, out, reference, manifest):
    """Validate the exact local N17586 input without changing scientific settings."""
    for kind in ("case", "data"):
        path = Path(reference["pair"][kind])
        if prior.sha(path) != reference["pair"][kind + "_sha256"]:
            raise RuntimeError(f"Parent {kind} hash mismatch")
    s.settings.file.read_case(file_name=reference["pair"]["case"])
    s.settings.file.read_data(file_name=reference["pair"]["data"])
    assert prior.native_iteration(s) == 17586
    loaded = readback(s)
    prior.dump(out / "loaded-parent.json", loaded)
    checks = require_match(loaded, reference)
    prior.validate_roughness(s)
    assert loaded["film_parameters"]["timestep-max"] == 1e-6
    assert not loaded["film_parameters"]["ewf-adaptive?"]
    assert loaded["film_parameters"]["thickness-limit"] == 1.0
    paths = contact.instrument(s, work / "monitors")
    autosave = prior.configure_autosave(s, str(work), data_frequency=1000)
    s.settings.file.auto_save.retain_most_recent_files = False
    assert not s.settings.file.auto_save.retain_most_recent_files()
    autosave = s.settings.file.auto_save.get_state()
    prepared = prior.save_pair(s, work / "prepared-N17586.cas.h5", 17586)
    s.settings.file.read_case(file_name=prepared["case"])
    s.settings.file.read_data(file_name=prepared["data"])
    assert prior.native_iteration(s) == 17586
    reopened = readback(s)
    reopen_checks = require_match(reopened, loaded)
    prior.dump(out / "prepared-reopen.json", {"pair": prepared, "readback": reopened,
                                               "checks": reopen_checks})
    manifest.update(status="PREPARED_VERIFIED", parent_checks=checks,
                    prepared_pair=prepared, autosave=autosave,
                    report_paths={k: str(v) for k, v in paths.items()},
                    scientific_settings_changed=False)
    prior.dump(out / "run-manifest.json", manifest)
    return paths


def run(s, work, out, manifest, paths, remote_reference):
    """Replay 6000, preserve that local endpoint, then issue one iterate 10000."""
    try:
        for label, steps, endpoint in (("LOCAL_REPLAY_RUNNING", 6000, 23586),
                                        ("LOCAL_EXTENSION_RUNNING", 10000, 33586)):
            manifest.update(status=label, active_tui_command=f"/solve/iterate {steps}",
                            command_started_utc=datetime.now(timezone.utc).isoformat())
            prior.dump(out / "run-manifest.json", manifest)
            print(label, manifest["active_tui_command"], flush=True)
            s.tui.solve.iterate(steps)
            actual = prior.native_iteration(s)
            if actual != endpoint:
                raise RuntimeError(f"TUI command returned at N{actual}, expected N{endpoint}")
            after = readback(s)
            if after["film_parameters"]["timestep-max"] != 1e-6:
                raise RuntimeError("Film timestep changed")
            if not all(math.isfinite(v[0]) for v in after["fields"].values()):
                raise RuntimeError("Nonfinite endpoint report")
            pair = prior.save_pair(s, work / f"block-N{endpoint}.cas.h5", endpoint)
            prior.dump(out / f"endpoint-N{endpoint}.json", {"pair": pair, "readback": after})
            histories = {k: prior.file_history(p) for k, p in paths.items()}
            expected = list(range(17586, endpoint + 1))
            if any(h["iterations"] != expected for h in histories.values()):
                raise RuntimeError("Native report coordinates are incomplete")
            prior.dump(out / "report-histories.json", histories)
            manifest.setdefault("completed_arms", []).append({"label": label,
                "steps": steps, "native_end": endpoint, "pair": pair})
            manifest.update(native_end=endpoint, actual_local_updates=endpoint - 17586,
                            total_restart_updates=endpoint - 13586, latest_pair=pair)
            if endpoint == 23586:
                comparison = {k: {"local": v[0], "server1_reference": remote_reference[k][0],
                                   "difference": v[0] - remote_reference[k][0]}
                              for k, v in after["fields"].items() if k in remote_reference}
                prior.dump(out / "local-replay-vs-server1.json", comparison)
                manifest["lineage_limit"] = "Local 4-rank replay, not the inaccessible Server 1 18-rank N23586 field file"
            prior.dump(out / "run-manifest.json", manifest)
            print("LOCAL_ENDPOINT_SAVED", endpoint, pair["data_sha256"], flush=True)
        manifest.update(status="SOLVE_COMPLETE_ENDPOINT_SAVED", native_end=33586,
                        actual_local_updates=16000, total_restart_updates=20000,
                        final_pair=manifest["latest_pair"],
                        completed_utc=datetime.now(timezone.utc).isoformat(),
                        solver_left_open=True, final_reopen="PENDING_FINAL_CHECK")
        prior.dump(out / "run-manifest.json", manifest)
        print("LOCAL_FILM_20000_COMPLETE_SAVED", flush=True)
    except Exception:
        manifest.update(status="CONTROLLER_ERROR", error=traceback.format_exc(),
                        error_utc=datetime.now(timezone.utc).isoformat())
        prior.dump(out / "run-manifest.json", manifest)
        try:
            native = prior.native_iteration(s)
            manifest["failure_pair"] = prior.save_pair(s, work / f"failure-N{native}.cas.h5", native)
            prior.dump(out / "run-manifest.json", manifest)
        except Exception:
            prior.dump(out / "failure-preservation-error.json", {"error": traceback.format_exc()})
        raise
