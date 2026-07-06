# Hybrid Fluent Extraction Bundle: purnanto-enthalpy1520-live-extract

## Metadata

- Exported at (UTC): `2026-06-11T05:32:55+00:00`
- Related setup report: ``
- Notes label: `Purnanto exact setup at 1520J`
- Remote case path: `C:\Users\syok443\Documents\Purnanto\enthalpy1520.cas`
- Remote data path: `C:\Users\syok443\Documents\Purnanto\enthalpy1520.dat`
- Offline case file: ``
- Offline data file: ``

## Coverage Summary

- Live PyFluent export: `captured`
- Offline case export: `skipped`
- Offline data export: `skipped`
- Notes recorded: `675`

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
- settings.results.report.population_balance.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: results/report/population-balance)
- settings.results.report.heat_exchanger.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: results/report/heat-exchanger)
- settings.design.gradient_based.observables.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/observables)
- settings.design.gradient_based.controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/controls)
- settings.design.gradient_based.monitors.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/monitors)
- settings.design.gradient_based.calculation.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/calculation)
- settings.design.gradient_based.postprocess_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/postprocess-options)
- settings.design.gradient_based.reporting.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/reporting)
- settings.design.gradient_based.design_tool.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/design-tool)
- settings.design.gradient_based.optimizer.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/optimizer)
- settings.parallel.multidomain.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: parallel/multidomain)
- settings.parallel.multidomain.conjugate_heat_transfer: unavailable (InactiveObjectError: '<session>.parallel.multidomain' is currently inactive.)
- settings.parallel.multidomain.solve: unavailable (InactiveObjectError: '<session>.parallel.multidomain' is currently inactive.)
- settings.parallel.network.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: parallel/network)
- settings.parallel.network.shell_script_path: unavailable (InactiveObjectError: '<session>.parallel.network' is currently inactive.)
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
- settings.results.report.population_balance.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: results/report/population-balance)
- settings.results.report.heat_exchanger.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: results/report/heat-exchanger)
- settings.design.gradient_based.observables.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/observables)
- settings.design.gradient_based.controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/controls)
- settings.design.gradient_based.monitors.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/monitors)
- settings.design.gradient_based.calculation.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/calculation)
- settings.design.gradient_based.postprocess_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/postprocess-options)
- settings.design.gradient_based.reporting.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/reporting)
- settings.design.gradient_based.design_tool.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/design-tool)
- settings.design.gradient_based.optimizer.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: design/gradient-based/optimizer)
- settings.parallel.multidomain.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: parallel/multidomain)
- settings.parallel.multidomain.conjugate_heat_transfer: unavailable (InactiveObjectError: '<session>.parallel.multidomain' is currently inactive.)
- settings.parallel.multidomain.solve: unavailable (InactiveObjectError: '<session>.parallel.multidomain' is currently inactive.)
- settings.parallel.network.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: parallel/network)
- settings.parallel.network.shell_script_path: unavailable (InactiveObjectError: '<session>.parallel.network' is currently inactive.)
- settings.setup.general.operating_conditions.inlet_temperature_for_operating_density.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/general/operating-conditions/inlet-temperature-for-operating-density)
- settings.setup.general.operating_conditions.inlet_temperature_for_operating_density.enable: unavailable (InactiveObjectError: '<session>.setup.general.operating_conditions.inlet_temperature_for_operating_density' is currently inactive.)
- settings.setup.general.operating_conditions.inlet_temperature_for_operating_density.zone_name: unavailable (InactiveObjectError: '<session>.setup.general.operating_conditions.inlet_temperature_for_operating_density' is currently inactive.)
- settings.setup.models.energy.two_temperature.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/energy/two-temperature)
- settings.setup.models.energy.two_temperature.enable: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.robustness_enhancement: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.nasa9_enhancement: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.set_verbosity: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.translational_vibrational_energy_relaxation: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.viscous.k_omega_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/k-omega-options)
- settings.setup.models.viscous.k_omega_options.kw_low_re_correction: unavailable (InactiveObjectError: '<session>.setup.models.viscous.k_omega_options' is currently inactive.)
- settings.setup.models.viscous.k_omega_options.kw_shear_correction: unavailable (InactiveObjectError: '<session>.setup.models.viscous.k_omega_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/geko-options)
- settings.setup.models.viscous.geko_options.wall_distance_free: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.version: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.cjet: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.creal: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.cnw_sub: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.cjet_aux: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.cbf_lam: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.geko_options.cbf_tur: unavailable (InactiveObjectError: '<session>.setup.models.viscous.geko_options' is currently inactive.)
- settings.setup.models.viscous.near_wall_treatment.enhanced_wall_treatment_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/near-wall-treatment/enhanced-wall-treatment-options)
- settings.setup.models.viscous.les_model_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/les-model-options)
- settings.setup.models.viscous.les_model_options.dynamic_stress: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.dynamic_energy_flux: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.dynamic_scalar_flux: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.subgrid_dynamic_fvar: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.cvreman: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.csigma: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.near_wall_rans_layer: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.cw1: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.les_model_options.cw2: unavailable (InactiveObjectError: '<session>.setup.models.viscous.les_model_options' is currently inactive.)
- settings.setup.models.viscous.reynolds_stress_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/reynolds-stress-options)
- settings.setup.models.viscous.reynolds_stress_options.solve_tke: unavailable (InactiveObjectError: '<session>.setup.models.viscous.reynolds_stress_options' is currently inactive.)
- settings.setup.models.viscous.reynolds_stress_options.wall_echo: unavailable (InactiveObjectError: '<session>.setup.models.viscous.reynolds_stress_options' is currently inactive.)
- settings.setup.models.viscous.des_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/des-options)
- settings.setup.models.viscous.des_options.all_len_modified: unavailable (InactiveObjectError: '<session>.setup.models.viscous.des_options' is currently inactive.)
- settings.setup.models.viscous.des_options.des_limiter_option: unavailable (InactiveObjectError: '<session>.setup.models.viscous.des_options' is currently inactive.)
- settings.setup.models.viscous.sbes_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/sbes-options)
- settings.setup.models.viscous.sbes_options.hybrid_model: unavailable (InactiveObjectError: '<session>.setup.models.viscous.sbes_options' is currently inactive.)
- settings.setup.models.viscous.sbes_options.user_defined: unavailable (InactiveObjectError: '<session>.setup.models.viscous.sbes_options' is currently inactive.)
- settings.setup.models.viscous.sbes_options.update_interval_k_omega: unavailable (InactiveObjectError: '<session>.setup.models.viscous.sbes_options' is currently inactive.)
- settings.setup.models.viscous.sbes_options.les_subgrid_scale_model: unavailable (InactiveObjectError: '<session>.setup.models.viscous.sbes_options' is currently inactive.)
- settings.setup.models.viscous.sbes_options.les_subgrid_dynamic_fvar: unavailable (InactiveObjectError: '<session>.setup.models.viscous.sbes_options' is currently inactive.)
- settings.setup.models.viscous.user_defined_transition.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/user-defined-transition)
- settings.setup.models.viscous.user_defined_transition.f_length: unavailable (InactiveObjectError: '<session>.setup.models.viscous.user_defined_transition' is currently inactive.)
- settings.setup.models.viscous.user_defined_transition.re_theta_c: unavailable (InactiveObjectError: '<session>.setup.models.viscous.user_defined_transition' is currently inactive.)
- settings.setup.models.viscous.user_defined_transition.re_theta_t: unavailable (InactiveObjectError: '<session>.setup.models.viscous.user_defined_transition' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/transition-model-options)
- settings.setup.models.viscous.transition_model_options.crossflow_transition: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.critical_reynolds_number_correlation: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.clambda_scale: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.capg_hightu: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.cfpg_hightu: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.capg_lowtu: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.cfpg_lowtu: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.ctu_hightu: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.ctu_lowtu: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.rec_max: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.rec_c1: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.rec_c2: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.cbubble_c1: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.cbubble_c2: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_model_options.rv1_switch: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_model_options' is currently inactive.)
- settings.setup.models.viscous.transition_sst_option.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/viscous/transition-sst-option)
- settings.setup.models.viscous.transition_sst_option.enable_roughness_correlation: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_sst_option' is currently inactive.)
- settings.setup.models.viscous.transition_sst_option.roughness_correlation_fcn: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_sst_option' is currently inactive.)
- settings.setup.models.viscous.transition_sst_option.geometric_roughness_ht_val: unavailable (InactiveObjectError: '<session>.setup.models.viscous.transition_sst_option' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/discrete-ordinates)
- settings.setup.models.radiation.discrete_ordinates.n_theta_divisions: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.n_phi_divisions: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.n_theta_pixels: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.n_phi_pixels: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.do_acceleration: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.method_partially_specular_wall: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.fast_second_order_discrete_ordinate: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.blending_factor: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.discrete_ordinates.do_energy_coupling: unavailable (InactiveObjectError: '<session>.setup.models.radiation.discrete_ordinates' is currently inactive.)
- settings.setup.models.radiation.monte_carlo.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/monte-carlo)
- settings.setup.models.radiation.monte_carlo.number_of_histories: unavailable (InactiveObjectError: '<session>.setup.models.radiation.monte_carlo' is currently inactive.)
- settings.setup.models.radiation.monte_carlo.under_relaxation: unavailable (InactiveObjectError: '<session>.setup.models.radiation.monte_carlo' is currently inactive.)
- settings.setup.models.radiation.monte_carlo.target_cells_per_volume_cluster: unavailable (InactiveObjectError: '<session>.setup.models.radiation.monte_carlo' is currently inactive.)
- settings.setup.models.radiation.s2s.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/s2s)
- settings.setup.models.radiation.s2s.viewfactor_settings: unavailable (InactiveObjectError: '<session>.setup.models.radiation.s2s' is currently inactive.)
- settings.setup.models.radiation.s2s.clustering_settings: unavailable (InactiveObjectError: '<session>.setup.models.radiation.s2s' is currently inactive.)
- settings.setup.models.radiation.s2s.radiosity_solver_control: unavailable (InactiveObjectError: '<session>.setup.models.radiation.s2s' is currently inactive.)
- settings.setup.models.radiation.solve_frequency.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/solve-frequency)
- settings.setup.models.radiation.solve_frequency.method: unavailable (InactiveObjectError: '<session>.setup.models.radiation.solve_frequency' is currently inactive.)
- settings.setup.models.radiation.solve_frequency.time_step_interval: unavailable (InactiveObjectError: '<session>.setup.models.radiation.solve_frequency' is currently inactive.)
- settings.setup.models.radiation.solve_frequency.time_interval: unavailable (InactiveObjectError: '<session>.setup.models.radiation.solve_frequency' is currently inactive.)
- settings.setup.models.radiation.solve_frequency.iteration_interval: unavailable (InactiveObjectError: '<session>.setup.models.radiation.solve_frequency' is currently inactive.)
- settings.setup.models.radiation.solar_load.illumination_parameters.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/solar-load/illumination-parameters)
- settings.setup.models.radiation.solar_load.solar_calculator.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/solar-load/solar-calculator)
- settings.setup.models.radiation.solar_load.autoread_solar_data.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/solar-load/autoread-solar-data)
- settings.setup.models.radiation.solar_load.autosave_solar_data.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/radiation/solar-load/autosave-solar-data)
- settings.setup.models.species.options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/options)
- settings.setup.models.species.options.inlet_diffusion: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.thermal_diffusion: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.thickened_flame_model: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.diffusion_energy_source: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.multi_component_diffusion_mf: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.multi_component_diffusion: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.liquid_energy_diffusion: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.save_gradients: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.species_migration: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.options.species_transport_expert: unavailable (InactiveObjectError: '<session>.setup.models.species.options' is currently inactive.)
- settings.setup.models.species.reactions.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/reactions)
- settings.setup.models.species.reactions.enable_volumetric_reactions: unavailable (InactiveObjectError: '<session>.setup.models.species.reactions' is currently inactive.)
- settings.setup.models.species.reactions.enable_wall_surface: unavailable (InactiveObjectError: '<session>.setup.models.species.reactions' is currently inactive.)
- settings.setup.models.species.reactions.enable_particle_reactions: unavailable (InactiveObjectError: '<session>.setup.models.species.reactions' is currently inactive.)
- settings.setup.models.species.reactions.enable_electrochemical_surface: unavailable (InactiveObjectError: '<session>.setup.models.species.reactions' is currently inactive.)
- settings.setup.models.species.wall_surface_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/wall-surface-options)
- settings.setup.models.species.wall_surface_options.heat_of_surface_reactions: unavailable (InactiveObjectError: '<session>.setup.models.species.wall_surface_options' is currently inactive.)
- settings.setup.models.species.wall_surface_options.mass_deposition_source: unavailable (InactiveObjectError: '<session>.setup.models.species.wall_surface_options' is currently inactive.)
- settings.setup.models.species.wall_surface_options.reaction_diffusion_balance: unavailable (InactiveObjectError: '<session>.setup.models.species.wall_surface_options' is currently inactive.)
- settings.setup.models.species.wall_surface_options.surface_reaction_aggresiveness_factor: unavailable (InactiveObjectError: '<session>.setup.models.species.wall_surface_options' is currently inactive.)
- settings.setup.models.species.wall_surface_options.surface_reaction_rate_temperature_factor: unavailable (InactiveObjectError: '<session>.setup.models.species.wall_surface_options' is currently inactive.)
- settings.setup.models.species.wall_surface_options.surface_reaction_solid_fraction: unavailable (InactiveObjectError: '<session>.setup.models.species.wall_surface_options' is currently inactive.)
- settings.setup.models.species.turb_chem_interaction_model_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/turb-chem-interaction-model-options)
- settings.setup.models.species.turb_chem_interaction_model_options.chemistry_iterations: unavailable (InactiveObjectError: '<session>.setup.models.species.turb_chem_interaction_model_options' is currently inactive.)
- settings.setup.models.species.turb_chem_interaction_model_options.aggresiveness_factor: unavailable (InactiveObjectError: '<session>.setup.models.species.turb_chem_interaction_model_options' is currently inactive.)
- settings.setup.models.species.turb_chem_interaction_model_options.transport_time_scale_factor: unavailable (InactiveObjectError: '<session>.setup.models.species.turb_chem_interaction_model_options' is currently inactive.)
- settings.setup.models.species.turb_chem_interaction_model_options.min_temperature: unavailable (InactiveObjectError: '<session>.setup.models.species.turb_chem_interaction_model_options' is currently inactive.)
- settings.setup.models.species.species_transport_expert_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/species-transport-expert-options)
- settings.setup.models.species.species_transport_expert_options.linearize_convection_source: unavailable (InactiveObjectError: '<session>.setup.models.species.species_transport_expert_options' is currently inactive.)
- settings.setup.models.species.species_transport_expert_options.linearize_diffusion_source: unavailable (InactiveObjectError: '<session>.setup.models.species.species_transport_expert_options' is currently inactive.)
- settings.setup.models.species.species_transport_expert_options.blending: unavailable (InactiveObjectError: '<session>.setup.models.species.species_transport_expert_options' is currently inactive.)
- settings.setup.models.species.species_transport_expert_options.minimum_cell_quality_threshold: unavailable (InactiveObjectError: '<session>.setup.models.species.species_transport_expert_options' is currently inactive.)
- settings.setup.models.species.edc_model_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/edc-model-options)
- settings.setup.models.species.edc_model_options.edc_choice: unavailable (InactiveObjectError: '<session>.setup.models.species.edc_model_options' is currently inactive.)
- settings.setup.models.species.edc_model_options.edc_constant_coefficient_options: unavailable (InactiveObjectError: '<session>.setup.models.species.edc_model_options' is currently inactive.)
- settings.setup.models.species.edc_model_options.edc_pasr_model_options: unavailable (InactiveObjectError: '<session>.setup.models.species.edc_model_options' is currently inactive.)
- settings.setup.models.species.edc_model_options.user_defined_edc_scales: unavailable (InactiveObjectError: '<session>.setup.models.species.edc_model_options' is currently inactive.)
- settings.setup.models.species.tfm_model_options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/tfm-model-options)
- settings.setup.models.species.tfm_model_options.efficiency_function: unavailable (InactiveObjectError: '<session>.setup.models.species.tfm_model_options' is currently inactive.)
- settings.setup.models.species.tfm_model_options.number_of_points_in_flame: unavailable (InactiveObjectError: '<session>.setup.models.species.tfm_model_options' is currently inactive.)
- settings.setup.models.species.tfm_model_options.integral_length_scale: unavailable (InactiveObjectError: '<session>.setup.models.species.tfm_model_options' is currently inactive.)
- settings.setup.models.species.tfm_model_options.sensor_method: unavailable (InactiveObjectError: '<session>.setup.models.species.tfm_model_options' is currently inactive.)
- settings.setup.models.species.tfm_model_options.sensor_reaction_index: unavailable (InactiveObjectError: '<session>.setup.models.species.tfm_model_options' is currently inactive.)
- settings.setup.models.species.tfm_model_options.beta_factor_omega_equation: unavailable (InactiveObjectError: '<session>.setup.models.species.tfm_model_options' is currently inactive.)
- settings.setup.models.species.tfm_model_options.sensor_num_smooths: unavailable (InactiveObjectError: '<session>.setup.models.species.tfm_model_options' is currently inactive.)
- settings.setup.models.species.integration_parameters.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/species/integration-parameters)
- settings.setup.models.species.integration_parameters.integration_method: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.integration_options: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.isat_options: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.chemistry_agglomeration: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.chemistry_agglomeration_options: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.relax_to_equilibrium_options: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.dynamic_mechanism_reduction: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.dynamic_mechanism_reduction_options: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.dimension_reduction: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.species.integration_parameters.dimension_reduction_mixture_options: unavailable (InactiveObjectError: '<session>.setup.models.species.integration_parameters' is currently inactive.)
- settings.setup.models.discrete_phase.general_settings.unsteady_tracking.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/discrete-phase/general-settings/unsteady-tracking)
- settings.setup.models.discrete_phase.physical_models.volume_displacement.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/discrete-phase/physical-models/volume-displacement)
- settings.setup.models.discrete_phase.physical_models.wall_film.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/discrete-phase/physical-models/wall-film)
- settings.setup.models.discrete_phase.numerics.source_term_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/discrete-phase/numerics/source-term-settings)
- settings.setup.models.discrete_phase.numerics.parcel_count_control.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/discrete-phase/numerics/parcel-count-control)
- settings.setup.models.optics.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/optics)
- settings.setup.models.optics.enable: unavailable (InactiveObjectError: '<session>.setup.models.optics' is currently inactive.)
- settings.setup.models.optics.beams: unavailable (InactiveObjectError: '<session>.setup.models.optics' is currently inactive.)
- settings.setup.models.optics.statistics: unavailable (InactiveObjectError: '<session>.setup.models.optics' is currently inactive.)
- settings.setup.models.optics.sampling_iterations: unavailable (InactiveObjectError: '<session>.setup.models.optics' is currently inactive.)
- settings.setup.models.optics.index_of_refraction: unavailable (InactiveObjectError: '<session>.setup.models.optics' is currently inactive.)
- settings.setup.models.optics.report: unavailable (InactiveObjectError: '<session>.setup.models.optics' is currently inactive.)
- settings.setup.models.optics.verbosity: unavailable (InactiveObjectError: '<session>.setup.models.optics' is currently inactive.)
- settings.setup.models.structure.options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/structure/options)
- settings.setup.models.structure.options.thermal_effects: unavailable (InactiveObjectError: '<session>.setup.models.structure.options' is currently inactive.)
- settings.setup.models.structure.controls.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/structure/controls)
- settings.setup.models.structure.controls.numerical_damping_factor: unavailable (InactiveObjectError: '<session>.setup.models.structure.controls' is currently inactive.)
- settings.setup.models.structure.controls.enhanced_strain: unavailable (InactiveObjectError: '<session>.setup.models.structure.controls' is currently inactive.)
- settings.setup.models.structure.controls.unsteady_damping_rayleigh: unavailable (InactiveObjectError: '<session>.setup.models.structure.controls' is currently inactive.)
- settings.setup.models.structure.controls.amg_stabilization: unavailable (InactiveObjectError: '<session>.setup.models.structure.controls' is currently inactive.)
- settings.setup.models.structure.controls.max_iter: unavailable (InactiveObjectError: '<session>.setup.models.structure.controls' is currently inactive.)
- settings.setup.models.structure.expert.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/structure/expert)
- settings.setup.models.structure.expert.include_pop_in_fsi_force: unavailable (InactiveObjectError: '<session>.setup.models.structure.expert' is currently inactive.)
- settings.setup.models.structure.expert.steady_2way_fsi: unavailable (InactiveObjectError: '<session>.setup.models.structure.expert' is currently inactive.)
- settings.setup.models.structure.expert.include_viscous_fsi_force: unavailable (InactiveObjectError: '<session>.setup.models.structure.expert' is currently inactive.)
- settings.setup.models.structure.expert.explicit_fsi_force: unavailable (InactiveObjectError: '<session>.setup.models.structure.expert' is currently inactive.)
- settings.setup.models.structure.expert.starting_t_re_initialization: unavailable (InactiveObjectError: '<session>.setup.models.structure.expert' is currently inactive.)
- settings.setup.models.ablation.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/ablation)
- settings.setup.models.ablation.enabled: unavailable (InactiveObjectError: '<session>.setup.models.ablation' is currently inactive.)
- settings.setup.models.echemistry.lithium_battery.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/echemistry/lithium-battery)
- settings.setup.models.echemistry.lithium_battery.echem_heating_enabled: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.lithium_battery' is currently inactive.)
- settings.setup.models.echemistry.lithium_battery.zone_assignment: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.lithium_battery' is currently inactive.)
- settings.setup.models.echemistry.lithium_battery.butler_volmer_rate: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.lithium_battery' is currently inactive.)
- settings.setup.models.echemistry.lithium_battery.material_property: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.lithium_battery' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/echemistry/electrolysis)
- settings.setup.models.echemistry.electrolysis.options: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.parameters: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.anode: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.electrolyte: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.cathode: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.electrical_tab: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.customization: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.echemistry.electrolysis.advanced: unavailable (InactiveObjectError: '<session>.setup.models.echemistry.electrolysis' is currently inactive.)
- settings.setup.models.battery.zone_assignment.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/zone-assignment)
- settings.setup.models.battery.zone_assignment.active_zone: unavailable (InactiveObjectError: '<session>.setup.models.battery.zone_assignment' is currently inactive.)
- settings.setup.models.battery.zone_assignment.passive_zone: unavailable (InactiveObjectError: '<session>.setup.models.battery.zone_assignment' is currently inactive.)
- settings.setup.models.battery.zone_assignment.passive_zone_tab: unavailable (InactiveObjectError: '<session>.setup.models.battery.zone_assignment' is currently inactive.)
- settings.setup.models.battery.zone_assignment.virtual_connection: unavailable (InactiveObjectError: '<session>.setup.models.battery.zone_assignment' is currently inactive.)
- settings.setup.models.battery.zone_assignment.virtual_connection_file: unavailable (InactiveObjectError: '<session>.setup.models.battery.zone_assignment' is currently inactive.)
- settings.setup.models.battery.zone_assignment.positive_tab: unavailable (InactiveObjectError: '<session>.setup.models.battery.zone_assignment' is currently inactive.)
- settings.setup.models.battery.zone_assignment.negative_tab: unavailable (InactiveObjectError: '<session>.setup.models.battery.zone_assignment' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/ntgk-model-settings)
- settings.setup.models.battery.ntgk_model_settings.initial_dod: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.ref_capacity: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.data_type: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.poly_u_function: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.poly_y_function: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.poly_t_dependence: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.u_table: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.y_table: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.internal_resistance_table: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.limit_current_enabled: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.provide_utable_enabled: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.limit_current_table: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ntgk_model_settings.monitor_names: unavailable (InactiveObjectError: '<session>.setup.models.battery.ntgk_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/ecm-model-settings)
- settings.setup.models.battery.ecm_model_settings.initial_soc: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.ref_capacity: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.two_set_data: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.data_type: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_rs: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_r1: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_c1: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_r2: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_c2: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_voc: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_rs_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_r1_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_c1_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_r2_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_c2_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.chen_voc_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_rs: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_r1: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_c1: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_r2: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_c2: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_voc: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_rs_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_r1_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_c1_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_r2_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_c2_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.poly_voc_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_rs: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_r1: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_c1: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_r2: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_c2: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_r3: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_c3: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_voc: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_rs_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_r1_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_c1_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_r2_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_c2_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_r3_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_c3_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.ecm_model_settings.table_voc_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.ecm_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/p2d-model-settings)
- settings.setup.models.battery.p2d_model_settings.initial_soc: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.ref_capacity: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_thickness: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_n_grid: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_size_ratio: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_p_diameter: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_n_sphere: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_size_ratio_r: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_cs_max: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_stio_0: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_stio_100: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_ce_0: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_vof: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_filler_f: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_ds: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_ed: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_brugg: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_sigma: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_i0: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_er: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_alpha_a: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_alpha_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.anode_ocv: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_thickness: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_n_grid: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_size_ratio: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_p_diameter: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_n_sphere: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_size_ratio_r: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_cs_max: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_stio_0: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_stio_100: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_ce_0: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_vof: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_filler_f: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_ds: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_ed: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_brugg: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_sigma: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_i0: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_er: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_alpha_a: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_alpha_c: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.cathode_ocv: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_thickness: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_n_grid: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_ce_0: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_vof: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_brugg: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_de: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_t_plus: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_sigma: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.electrolyte_activity: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.analytical_cs: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.analytical_cs_order: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.aging_model_enabled: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.aging_file: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.p2d_model_settings.aging_profile: unavailable (InactiveObjectError: '<session>.setup.models.battery.p2d_model_settings' is currently inactive.)
- settings.setup.models.battery.customized_echem_model_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/customized-echem-model-settings)
- settings.setup.models.battery.customized_echem_model_settings.memory_num_per_cell: unavailable (InactiveObjectError: '<session>.setup.models.battery.customized_echem_model_settings' is currently inactive.)
- settings.setup.models.battery.customized_echem_model_settings.initial_soc: unavailable (InactiveObjectError: '<session>.setup.models.battery.customized_echem_model_settings' is currently inactive.)
- settings.setup.models.battery.customized_echem_model_settings.reference_capacity: unavailable (InactiveObjectError: '<session>.setup.models.battery.customized_echem_model_settings' is currently inactive.)
- settings.setup.models.battery.cht_model_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/cht-model-settings)
- settings.setup.models.battery.cht_model_settings.same_for_active_enabled: unavailable (InactiveObjectError: '<session>.setup.models.battery.cht_model_settings' is currently inactive.)
- settings.setup.models.battery.cht_model_settings.energy_source_same_active: unavailable (InactiveObjectError: '<session>.setup.models.battery.cht_model_settings' is currently inactive.)
- settings.setup.models.battery.cht_model_settings.energy_source_active: unavailable (InactiveObjectError: '<session>.setup.models.battery.cht_model_settings' is currently inactive.)
- settings.setup.models.battery.cht_model_settings.tab_elec_current: unavailable (InactiveObjectError: '<session>.setup.models.battery.cht_model_settings' is currently inactive.)
- settings.setup.models.battery.fmu_model_settings.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/fmu-model-settings)
- settings.setup.models.battery.fmu_model_settings.energy_source_active: unavailable (InactiveObjectError: '<session>.setup.models.battery.fmu_model_settings' is currently inactive.)
- settings.setup.models.battery.fmu_model_settings.tab_elec_current: unavailable (InactiveObjectError: '<session>.setup.models.battery.fmu_model_settings' is currently inactive.)
- settings.setup.models.battery.eload_condition.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/eload-condition)
- settings.setup.models.battery.eload_condition.eload_settings: unavailable (InactiveObjectError: '<session>.setup.models.battery.eload_condition' is currently inactive.)
- settings.setup.models.battery.eload_condition.echem_stop_criterion: unavailable (InactiveObjectError: '<session>.setup.models.battery.eload_condition' is currently inactive.)
- settings.setup.models.battery.solution_option.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/solution-option)
- settings.setup.models.battery.solution_option.option_settings: unavailable (InactiveObjectError: '<session>.setup.models.battery.solution_option' is currently inactive.)
- settings.setup.models.battery.solution_option.cell_clustering: unavailable (InactiveObjectError: '<session>.setup.models.battery.solution_option' is currently inactive.)
- settings.setup.models.battery.advanced_models.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/advanced-models)
- settings.setup.models.battery.advanced_models.contact_resistance: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.advanced_models.orthotropic_k: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.advanced_models.thermal_abuse_model: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.advanced_models.capacity_fade_model: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.advanced_models.life_model: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.advanced_models.swelling_model: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.advanced_models.venting_model: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.advanced_models.udf_hooks: unavailable (InactiveObjectError: '<session>.setup.models.battery.advanced_models' is currently inactive.)
- settings.setup.models.battery.tool_kits.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/battery/tool-kits)
- settings.setup.models.battery.tool_kits.standalone_echem_model: unavailable (InactiveObjectError: '<session>.setup.models.battery.tool_kits' is currently inactive.)
- settings.setup.models.battery.tool_kits.parameter_estimation_tool: unavailable (InactiveObjectError: '<session>.setup.models.battery.tool_kits' is currently inactive.)
- settings.setup.models.battery.tool_kits.rom_tool_kit: unavailable (InactiveObjectError: '<session>.setup.models.battery.tool_kits' is currently inactive.)
- settings.setup.models.battery.tool_kits.pack_builder: unavailable (InactiveObjectError: '<session>.setup.models.battery.tool_kits' is currently inactive.)
- settings.setup.models.system_coupling.htc.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/system-coupling/htc)
- settings.setup.models.system_coupling.htc.calculation_method: unavailable (InactiveObjectError: '<session>.setup.models.system_coupling.htc' is currently inactive.)
- settings.setup.models.system_coupling.unsteady_statistics.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/system-coupling/unsteady-statistics)
- settings.setup.models.sofc.model_parameters.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/sofc/model-parameters)
- settings.setup.models.sofc.model_parameters.options: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.individual_bc_enabled: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.converg_voltage_enabled: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.system_voltage: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.system_current: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.leakage_current_density: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.electrolyte_thickness: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.electrolyte_resistivity: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.current_urf: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.model_parameters.fcycle_amg_enabled: unavailable (InactiveObjectError: '<session>.setup.models.sofc.model_parameters' is currently inactive.)
- settings.setup.models.sofc.electrochemistry.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/sofc/electrochemistry)
- settings.setup.models.sofc.electrochemistry.exchange_current: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrochemistry' is currently inactive.)
- settings.setup.models.sofc.electrochemistry.mole_fraction_ref: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrochemistry' is currently inactive.)
- settings.setup.models.sofc.electrochemistry.concentration_exp: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrochemistry' is currently inactive.)
- settings.setup.models.sofc.electrochemistry.bv_symmetry_factor: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrochemistry' is currently inactive.)
- settings.setup.models.sofc.electrolyte_porous.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/sofc/electrolyte-porous)
- settings.setup.models.sofc.electrolyte_porous.anode_interface: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrolyte_porous' is currently inactive.)
- settings.setup.models.sofc.electrolyte_porous.cathode_interface: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrolyte_porous' is currently inactive.)
- settings.setup.models.sofc.electrolyte_porous.tortuosity_interface: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrolyte_porous' is currently inactive.)
- settings.setup.models.sofc.electrolyte_porous.pore_size_interface: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electrolyte_porous' is currently inactive.)
- settings.setup.models.sofc.electric_field.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/sofc/electric-field)
- settings.setup.models.sofc.electric_field.voltage_tap: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electric_field' is currently inactive.)
- settings.setup.models.sofc.electric_field.current_tap: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electric_field' is currently inactive.)
- settings.setup.models.sofc.electric_field.conductive_regions: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electric_field' is currently inactive.)
- settings.setup.models.sofc.electric_field.contact_resistance_regions: unavailable (InactiveObjectError: '<session>.setup.models.sofc.electric_field' is currently inactive.)
- settings.setup.models.sofc.customized_udf.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/sofc/customized-udf)
- settings.setup.models.sofc.customized_udf.enabled: unavailable (InactiveObjectError: '<session>.setup.models.sofc.customized_udf' is currently inactive.)
- settings.setup.models.sofc.customized_udf.source_file: unavailable (InactiveObjectError: '<session>.setup.models.sofc.customized_udf' is currently inactive.)
- settings.setup.models.pemfc.options.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/options)
- settings.setup.models.pemfc.options.joule_heat: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.reaction_heat: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.electrochemistry: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.butlervolmer: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.multidiff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.anisotropic: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.pconductivity: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.halfcell: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.particlemodel: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.liquid_phase: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.liquid_pressure: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.liquid_in_channel: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.dynamic_head: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.knudsen_diffusion: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.temp_jref: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.n2_crossover: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.ice_phase: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.dissovled_urf: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.osmotic_urf: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.phasechange_urf: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.liquidremoval_urf: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.auto_amg: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.wdiff_model: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.bc_type: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.tot_voltage: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.options.tot_current: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.options' is currently inactive.)
- settings.setup.models.pemfc.parameters.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/parameters)
- settings.setup.models.pemfc.parameters.anode_jref: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.anode_cref: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.anode_exp: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.anode_ex_a: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.anode_ex_c: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.cathode_jref: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.cathode_cref: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.cathode_exp: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.cathode_ex_a: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.cathode_ex_c: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.leak_current: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.anode_stde: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.cathode_stde: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.std_temp: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.std_pre: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.open_voltage: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.anode_entro: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.cathode_entro: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.h2_diff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.o2_diff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.h2o_diff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.other_diff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.gas_diff_exp: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.transfer_currrent_exp: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.rk_exp: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.liquid_cov_exp: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.liquid_diss_const: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.liquid_rho: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.liquid_k: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.upper_liq_pre: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.lower_liq_pre: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.liq_diff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.velocity_ratio: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.gas_diss_const: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.osmotic_coeff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.lam_a1: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.lam_s1: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.n2_cross_coeff: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.desublimation_rate: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.parameters.sublimation_rate: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.parameters' is currently inactive.)
- settings.setup.models.pemfc.anode.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/anode)
- settings.setup.models.pemfc.anode.anode_cc_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.anode' is currently inactive.)
- settings.setup.models.pemfc.anode.anode_fc_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.anode' is currently inactive.)
- settings.setup.models.pemfc.anode.anode_gdl_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.anode' is currently inactive.)
- settings.setup.models.pemfc.anode.anode_mpl_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.anode' is currently inactive.)
- settings.setup.models.pemfc.anode.anode_ca_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.anode' is currently inactive.)
- settings.setup.models.pemfc.membrane.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/membrane)
- settings.setup.models.pemfc.membrane.mem_zone_list: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_update: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_material: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_eqv_weight: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_alpha: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_beta: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_diff_corr: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_permeability: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.membrane.mem_act: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.membrane' is currently inactive.)
- settings.setup.models.pemfc.cathode.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/cathode)
- settings.setup.models.pemfc.cathode.cathode_cc_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.cathode' is currently inactive.)
- settings.setup.models.pemfc.cathode.cathode_fc_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.cathode' is currently inactive.)
- settings.setup.models.pemfc.cathode.cathode_gdl_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.cathode' is currently inactive.)
- settings.setup.models.pemfc.cathode.cathode_mpl_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.cathode' is currently inactive.)
- settings.setup.models.pemfc.cathode.cathode_ca_zone: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.cathode' is currently inactive.)
- settings.setup.models.pemfc.electrical_tab.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/electrical-tab)
- settings.setup.models.pemfc.electrical_tab.anode_tab: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.electrical_tab' is currently inactive.)
- settings.setup.models.pemfc.electrical_tab.cathode_tab: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.electrical_tab' is currently inactive.)
- settings.setup.models.pemfc.advanced.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/advanced)
- settings.setup.models.pemfc.advanced.contact_resis: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.advanced' is currently inactive.)
- settings.setup.models.pemfc.advanced.coolant_channel: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.advanced' is currently inactive.)
- settings.setup.models.pemfc.advanced.stack_management: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.advanced' is currently inactive.)
- settings.setup.models.pemfc.report.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/pemfc/report)
- settings.setup.models.pemfc.report.electrolyte_area: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.report' is currently inactive.)
- settings.setup.models.pemfc.report.monitor_enable: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.report' is currently inactive.)
- settings.setup.models.pemfc.report.monitor_frequency: unavailable (InactiveObjectError: '<session>.setup.models.pemfc.report' is currently inactive.)
- settings.setup.boundary_conditions.settings.pressure_far_field.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/boundary-conditions/settings/pressure-far-field)
- settings.setup.boundary_conditions.settings.pressure_far_field.riemann_invariants_tangency_correction: unavailable (InactiveObjectError: '<session>.setup.boundary_conditions.settings.pressure_far_field' is currently inactive.)
- settings.setup.boundary_conditions.settings.pressure_far_field.type: unavailable (InactiveObjectError: '<session>.setup.boundary_conditions.settings.pressure_far_field' is currently inactive.)
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
- settings.setup.general.operating_conditions.inlet_temperature_for_operating_density.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/general/operating-conditions/inlet-temperature-for-operating-density)
- settings.setup.general.operating_conditions.inlet_temperature_for_operating_density.enable: unavailable (InactiveObjectError: '<session>.setup.general.operating_conditions.inlet_temperature_for_operating_density' is currently inactive.)
- settings.setup.general.operating_conditions.inlet_temperature_for_operating_density.zone_name: unavailable (InactiveObjectError: '<session>.setup.general.operating_conditions.inlet_temperature_for_operating_density' is currently inactive.)
- settings.setup.models.energy.two_temperature.get_state: unavailable (RuntimeError: api-get-var: the object is not active
Error Object: setup/models/energy/two-temperature)
- settings.setup.models.energy.two_temperature.enable: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.robustness_enhancement: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.nasa9_enhancement: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.set_verbosity: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.energy.two_temperature.translational_vibrational_energy_relaxation: unavailable (InactiveObjectError: '<session>.setup.models.energy.two_temperature' is currently inactive.)
- settings.setup.models.viscous.k_omega_model: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.k_omega_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.geko_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.rng_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.near_wall_treatment: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.reynolds_stress_model: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.subgrid_scale_model: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.les_model_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.reynolds_stress_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.rans_model: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.des_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.transition_module: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.hybrid_rans_les: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.sbes_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.user_defined_transition: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.multiphase_turbulence: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.turbulence_expert: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.transition_model_options: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.transition_sst_option: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.user_defined: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.sa_enhanced_wall_treatment: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.viscous.sa_damping: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.radiation: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.species: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.discrete_phase: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.virtual_blade_model: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.optics: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.structure: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.ablation: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.echemistry: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.battery: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.system_coupling: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.sofc: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
- settings.setup.models.pemfc: unavailable (RuntimeError: failed to connect to all addresses; last error: UNKNOWN: ipv4:10.104.144.221:57580: Failed to connect to remote host: connect() timed out)
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
