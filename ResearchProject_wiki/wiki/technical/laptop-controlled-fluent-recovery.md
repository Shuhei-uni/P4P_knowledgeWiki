# Laptop-Controlled Fluent Recovery Architecture

## Project Decision

**Status:** `Accepted architecture — pending live Windows verification`

The laptop agent remains the scientific controller. It researches Fluent paths,
builds and verifies setups through direct PyFluent/TUI calls, selects valid
checkpoints, interprets results, and decides the next action.

The licensed Fluent computer supplies only:

- a watchdog that keeps Fluent available and publishes replacement connection
  credentials after a genuine process or gRPC failure; and
- a deterministic worker for explicitly requested load/run/checkpoint/save
  workloads.

The Fluent computer does not compile setups, choose recovery state, retry an
interrupted scientific step, or interpret CFD evidence.

## Evidence and Operating Contract

The executable design, credential handling, request schema, and forced-crash
acceptance workflow are maintained in
`../../../PyAnsys/docs/LAPTOP_CONTROLLED_FLUENT.md`.

The implemented setup-plan-to-results operating sequence, including the
laptop-owned ledger, explicit checkpoint verification, resumable analysis
manifest, and hashed result manifest, is maintained in
`../../../PyAnsys/docs/SETUP_TO_RESULTS_WORKFLOW.md`.

## Project Impact

- Fatal Fluent failures should no longer require physical return to the
  university computer.
- Case identity and checkpoint selection remain part of the laptop-side
  evidence trail.
- A resumed case/data field must not be hybrid-initialized again.
- Recovery automation does not increase the scientific authority of an
  incomplete or non-converged result.

## Remaining Verification

- Confirm the private shared directory synchronizes atomic replacements.
- Confirm the advertised host and restarted gRPC port are reachable through the
  university network/VPN.
- Complete the controlled forced-crash and explicit-resume acceptance test on
  the licensed Fluent computer.
