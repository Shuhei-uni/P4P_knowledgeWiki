---
schema_version: 2
plan_id: 09c-two-way-dpm-interaction
parent_case_path: 'C:\Users\syok443\P4P simulation\TwoPhaseInletV2(Purnanto).cas.h5'
parent_case_sha256: '0000000000000000000000000000000000000000000000000000000000000000'
output_case_path: 'C:\Users\syok443\P4P simulation\scratch\TwoPhaseInletV2(Purnanto)-09c-two-way-dpm.cas.h5'
build_script_path: scripts/setup/setup09c_two_way_dpm_coupling_case.py
build_script_sha256: '2acac34e7726a834dcdc4db71e930587f70fd77b4bc64aed3c3907064075cea0'
---

# 09c — two-way DPM interaction build request

The agent must author and commit the referenced Python build script before this
plan can execute. The script is the executable case definition: it contains
the ordered Fluent TUI/PyFluent calls, live readbacks, and failure checks for
this one build. Markdown records intent and provenance only; it is never a
Fluent command language.

For this controlled 09c derivative, the script must make only these changes:

1. Enable global **DPM Interaction with Continuous Phase**.
2. Enable **Update DPM Sources Every Flow Iteration**.
3. Set the source update interval to `1`.

It must then read those values back, preserve the inherited injection
inventory, and write the new case to the declared scratch path. No
initialisation, iteration, data write, EWF change, boundary change, or other
model mutation is authorised.
