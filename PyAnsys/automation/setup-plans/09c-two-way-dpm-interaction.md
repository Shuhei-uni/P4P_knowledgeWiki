---
schema_version: 1
plan_id: 09c-two-way-dpm-interaction
recipe_id: dpm_two_way_interaction
parent_case_path: 'C:\Users\syok443\P4P simulation\TwoPhaseInletV2(Purnanto).cas.h5'
parent_case_sha256: '0000000000000000000000000000000000000000000000000000000000000000'
output_case_path: 'C:\Users\syok443\P4P simulation\scratch\TwoPhaseInletV2(Purnanto)-09c-two-way-dpm.cas.h5'
expected_parent_interaction:
  enabled: false
  update_sources_every_iteration: false
  iteration_interval: 1
update_sources_every_iteration: true
iteration_interval: 1
---

# 09c — two-way DPM interaction

Build a case-only `09c` derivative from the pinned `08b` parent. The only
permitted mutation is the named DPM continuous-phase interaction recipe. The
runner must prove the parent identity, interaction preconditions, unchanged
injection inventory, Fluent write visibility, and unchanged parent hash.
