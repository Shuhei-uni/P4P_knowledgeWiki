# Workflow efficiency update

Status: **staged, not deployed**. This update leaves the active Phase 9 runners,
watchers, their dependencies, and machine records unchanged. Check the manifest
against current source before using it; another chat can change those files.

| Change | Implementation | Activation |
| --- | --- | --- |
| Film drainage before long film-only work | Build workflow plus `verify_drain_probe` | New/changed drainage setups; reuse matching verified evidence |
| Rounding and path comparison | `execution_contract.compare_state` | New runners; Phase 9 integration is staged |
| Transcript lifecycle | Shared `native_transcript` | Phase 9 integration is staged; preserves original errors |
| Runtime/object preflight | Explicit interpreter probe and object inventory check | New builds; run the probe on the execution host |
| Fixed native runs and retrieval | Run-control workflow | New detached launches; verify both execution and retrieval |
| Compact status and fewer RPCs | File-backed status tool; staged watcher health timing | Status tool is usable now; watcher edits wait for idle |
| Narrow file reads and report structure | Root instructions, evidence tool, writing skills | Future lookup and drafting |

The patch replaces duplicated comparison/transcript functions in both Phase 9
runners with the shared tested helpers. It also changes both watchers to perform
health checks on a timer or a new event, rather than on every poll of a persistent
failure. It preserves server assignments, scientific settings, solve horizons,
ramp spacing, checkpoint spacing, output paths, and wake-up authority.

## Offline checks

From the repository root:

```sh
python3 PyAnsys/workflow_updates/20261008/check_update.py
PYTHONPATH=PyAnsys/src python3 -m unittest discover -s PyAnsys/tests -p 'test_execution_efficiency.py' -v
```

The checker only parses source, compares hashes, checks patch applicability, and
reads local process identities. It never connects to Fluent or installs the patch.

## Use the evidence tool

```sh
python3 PyAnsys/tools/workflow_evidence.py status PyAnsys/output/phase9-mesh-convergence/20261007 --controller-name run_phase9_mesh_startup.py
python3 PyAnsys/tools/workflow_evidence.py json path/to/receipt.json --pointer /status --pointer /verified_native_end
python3 PyAnsys/tools/workflow_evidence.py section path/to/setup.md --heading 'Run schedule'
python3 PyAnsys/tools/workflow_evidence.py runtime --python PyAnsys/.venv/bin/python --module numpy --module h5py
python3 PyAnsys/tools/workflow_evidence.py drain-proof path/to/probe.json --setup-identity VERIFIED_SETUP_ID --frozen-bulk
```

`runtime` checks the computer where it executes. A Mac receipt does not qualify
a Windows interpreter. Use the same probe on the execution host, record any
extra dependency paths, and reuse the selected interpreter. It installs nothing.
The drain receipt must come from accepted native probe evidence; it contains
`setup_identity`, `direct_film_drain`, `native_evidence_verified`, `evidence_paths`,
`film_start_s`, `film_end_s`, `drained_mass_kg`, `ledger_error_percent`,
`ledger_limit_percent`, `bulk_equations`, and `bulk_fields_unchanged`. The default
frozen-bulk check requires `drift`, `flow`, `ke`, and `mp` all false. The helper
validates the receipt; it does not manufacture or independently certify evidence.
Outputs have an explicit size limit and fail with `OUTPUT_LIMIT` instead of
returning partial JSON. Narrow the selection when that happens.

## Deploy after the active processes are idle

1. Reconcile both owned servers, controllers, watchers and their latest preserved
   endpoints under the recorded authority. A stopped laptop process alone does
   not establish that Fluent is idle. Preserve server-local execution copies.
2. Run `check_update.py`. If any base hash changed, regenerate and review the
   patch rather than forcing it over concurrent edits. Also stop using any
   inactive watcher launch mechanism that would reload code during installation.
3. Once all affected processes are idle and reconciled, apply `changes.patch`
   with `git apply`. The new shared module must accompany the scripts if they
   are deployed to another computer.
4. Run the offline tests and the existing Phase 9 call-order tests. Resume from
   the verified endpoint without repeating accepted solve work.

No installation or live validation was performed as part of this maintenance.
The existing watchers already own supervision; the status tool does not launch
a second watcher. Independent server-file retrieval remains host-specific: test
the available route before a new detached launch and state its limits if absent.
