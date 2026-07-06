# Hybrid Fluent Extraction Bundle: purnanto-enthalpy1760-live-extract

## Metadata

- Exported at (UTC): `2026-06-11T05:40:47+00:00`
- Related setup report: ``
- Notes label: `Purnanto exact setup at 1760J`
- Remote case path: `C:\Users\syok443\Documents\Purnanto\enthalpy1760.cas`
- Remote data path: `C:\Users\syok443\Documents\Purnanto\enthalpy1760.dat`
- Offline case file: ``
- Offline data file: ``

## Coverage Summary

- Live PyFluent export: `captured`
- Offline case export: `skipped`
- Offline data export: `skipped`
- Notes recorded: `89`

## Bundle Layout

- `manifest.json`: top-level metadata and status
- `live/`: live PyFluent capture bundle if a session was available
- `offline_case/`: local case-file inventory if a local case file was supplied
- `offline_data/`: local data-file inventory if a local data file was supplied
- `notes.txt`: capture gaps and path failures

## Interpretation Rules

- Treat `live/targeted_branches.json` as the main settings-tree evidence.
- Treat offline candidate strings as supporting hints, not as proof of effective live Fluent state.
- Any branch missing from the live export should be treated as unresolved until checked on the Fluent machine.

## Notes

- Data filename does not match Fluent default pairing; loading case then explicit data.
- settings.file.auto_save.save_data_file_every.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: file/auto-save/save-data-file-every)
- settings.mesh.adapt.multi_layer_refinement.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: mesh/adapt/multi-layer-refinement)
- settings.mesh.anisotropic_adaption.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: mesh/anisotropic-adaption)
- settings.mesh.anisotropic_adaption.operations: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.mesh.anisotropic_adaption.iterations: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.mesh.anisotropic_adaption.fixed_zones: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.mesh.anisotropic_adaption.indicator: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.mesh.anisotropic_adaption.target: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.mesh.anisotropic_adaption.maximum_anisotropic_ratio: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.mesh.anisotropic_adaption.minimum_edge_length: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.mesh.anisotropic_adaption.minimum_cell_quality: unavailable (InactiveObjectError: '<session>.mesh.anisotropic_adaption' is currently inactive.)
- settings.setup.models.optics.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/optics)
- settings.setup.models.ablation.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/ablation)
- settings.setup.mesh_interfaces.mapped_interface_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/mesh-interfaces/mapped-interface-options)
- settings.setup.geometry.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/geometry)
- settings.setup.geometry.parts: unavailable (InactiveObjectError: '<session>.setup.geometry' is currently inactive.)
- settings.setup.physics.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/physics)
- settings.setup.physics.volumes: unavailable (InactiveObjectError: '<session>.setup.physics' is currently inactive.)
- settings.setup.physics.interfaces: unavailable (InactiveObjectError: '<session>.setup.physics' is currently inactive.)
- settings.setup.profiles.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/profiles)
- settings.solution.methods.axisymmetric.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/methods/axisymmetric)
- settings.solution.methods.flux_type.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/methods/flux-type)
- settings.solution.methods.convergence_acceleration_for_stretched_meshes.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/methods/convergence-acceleration-for-stretched-meshes)
- settings.solution.methods.nita_expert_controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/methods/nita-expert-controls)
- settings.solution.methods.overset.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/methods/overset)
- settings.solution.methods.reduced_rank_extrapolation_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/methods/reduced-rank-extrapolation-options)
- settings.solution.methods.residual_smoothing.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/methods/residual-smoothing)
- settings.solution.controls.p_v_controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/controls/p-v-controls)
- settings.solution.controls.pseudo_time_method_local_time_step.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/controls/pseudo-time-method-local-time-step)
- settings.solution.controls.pseudo_time_explicit_relaxation_factor.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/controls/pseudo-time-explicit-relaxation-factor)
- settings.solution.controls.acoustics_wave_eqn_controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/controls/acoustics-wave-eqn-controls)
- settings.solution.controls.contact_solution_controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/controls/contact-solution-controls)
- settings.solution.initialization.localized_turb_init.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/initialization/localized-turb-init)
- settings.solution.initialization.open_channel_auto_init.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/initialization/open-channel-auto-init)
- settings.solution.initialization.fmg.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/initialization/fmg)
- settings.solution.run_calculation.pseudo_time_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/run-calculation/pseudo-time-settings)
- settings.solution.run_calculation.adaptive_time_stepping.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/run-calculation/adaptive-time-stepping)
- settings.solution.run_calculation.cfl_based_adaptive_time_stepping.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/run-calculation/cfl-based-adaptive-time-stepping)
- settings.solution.run_calculation.transient_controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/run-calculation/transient-controls)
- settings.solution.run_calculation.data_sampling_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: solution/run-calculation/data-sampling-options)
- settings.results.plot.profile_data.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: results/plot/profile-data)
- settings.results.plot.interpolated_data.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: results/plot/interpolated-data)
- settings.results.report.flow.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: results/report/flow)
- settings.results.report.modified_setting_options.get_state: unavailable (RuntimeError: Stream removed (recvmsg:Operation timed out))
- settings.results.report.population_balance: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.results.report.heat_exchanger: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.results.report.system: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.results.report.surface_integrals: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.results.report.volume_integrals: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.results.report.phasic_integrals_enabled: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.design: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.parametric_studies: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.current_parametric_study: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.parameters: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.parallel: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.get_state: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.file: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.mesh: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.server: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.solution: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.results: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.design: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.parametric_studies: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.current_parametric_study: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.parameters: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.parallel: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- setup: unresolved candidate paths (settings.setup -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- setup_general: unresolved candidate paths (settings.setup.general -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- setup_models: unresolved candidate paths (settings.setup.models -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- multiphase_model: unresolved candidate paths (settings.setup.models.multiphase -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out; settings.setup.models.multiphase_model -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- viscous_model: unresolved candidate paths (settings.setup.models.viscous -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- discrete_phase_model: unresolved candidate paths (settings.setup.models.discrete_phase -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out; settings.setup.models.discrete_phase_model -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out; settings.setup.models.dpm -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- materials: unresolved candidate paths (settings.setup.materials -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- boundary_conditions: unresolved candidate paths (settings.setup.boundary_conditions -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- cell_zone_conditions: unresolved candidate paths (settings.setup.cell_zone_conditions -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- solution: unresolved candidate paths (settings.solution -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- solution_initialization: unresolved candidate paths (settings.solution.initialization -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- results: unresolved candidate paths (settings.results -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- file_api: unresolved candidate paths (settings.file -> RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- dir(solver.settings): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- scheme (rpgetvar 'flow-time): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- scheme (rpgetvar 'time-step): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- scheme (rpgetvar 'physical-time-step): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- scheme (rpgetvar 'number-of-iterations): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- scheme (cx-send '(getcwd)): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- scheme (rpgetvar 'operating-pressure): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- scheme (rpgetvar 'gravity): unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
