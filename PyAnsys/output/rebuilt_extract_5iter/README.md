# Actual Fluent Setup Archive: rebuilt_extract_5iter

## Archive Metadata

- Exported at (UTC): `2026-06-11T09:57:50+00:00`
- Fluent version: `Ansys Fluent 2026 R1`
- Source case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\purnanto-extended-rebuilt.cas.h5`
- Source data: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\purnanto-extended-rebuilt.dat.h5`
- Related setup report: ``
- Notes label: ``

## Boundary Summary

- `pressure_outlet`: `steamoutlet`
- `velocity_inlet`: `liquidinlet, steaminlet`
- `wall`: `bottom, wall`
- `non_reflecting_bc`: `general_nrbc, turbo_specific_nrbc`
- `perforated_wall`: `model_setup, setup_method`
- `settings`: `advanced, mass_flow, pressure_outlet, target_mass_flow_rate_settings`

## Solver Snapshot

- Multiphase: `{'model': 'mixture', 'mixture_parameters': {'slip_velocity_on': True}, 'number_of_phases': {'number_of_eulerian_phases': 2}, 'vof_parameters': {'vof_formulation': 'implicit', 'interface_modeling_options': {'interface_type': 'dispersed'}}, 'advanced_formulation': {'implicit_body_force': False}, 'phases': {'phase-1': {'name': 'phase-1', 'material': 'water-vapor-at-psep'}, 'phase-2': {'name': 'phase-2', 'material': 'water-liquid-at-psep', 'diameter': 'constant', 'constant_dia': 1e-05, 'granular': False, 'iac': False}}, 'phase_interaction': {'forces': {'surface_tension_model': False, 'drag_mixture': [{'drag_method': 'schiller-naumann', 'drag_mod': 'none'}], 'slip_velocity': [{'ppt_methods': 'manninen-et-al'}], 'surface_tension': [{'ppt_methods': 'none'}]}, 'mass_transfer_list': [], 'intf_area': [{'ppt_methods': 'ia-symmetric'}]}}`
- Energy: `{'enabled': False}`
- Viscous: `{'model': 'k-epsilon', 'k_epsilon_model': 'rng', 'k_epsilon': {'differential_viscosity_model': True, 'swirl_dominated_flow': True, 'coefficients': {}}, 'near_wall_treatment': {'wall_treatment': 'standard-wall-fn'}, 'options': {'curvature_correction': {'enabled': False}, 'production_kato_launder_enabled': False, 'production_limiter': {'enabled': False}}, 'multiphase_turbulence': {'multiphase_options': {'dispersion_in_relative_velocity': False}}, 'turbulence_expert': {'turbulence_damping': {'enable_turb_damping': False}, 'turb_non_newtonian': False}, 'user_defined_functions': {'turb_visc': 'none'}}`
- Pressure-velocity coupling: `{'flow_scheme': 'SIMPLE', 'solve_n_phase': False}`
- Discretization: `{}`
- Iteration count: `5`
- Fluent cwd: `None`

## Files

- `metadata.json`
- `settings_snapshot.json`
- `scheme_snapshot.json`
- `notes.txt`

## Capture Notes

- setup.models.multiphase.model.child_names: unavailable ('model' object has no attribute 'child_names')
- setup.models.multiphase.mixture_parameters.slip_velocity_on.child_names: unavailable ('slip_velocity_on' object has no attribute 'child_names')
- setup.models.multiphase.vaporization_pressure: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/vaporization-pressure)
- setup.models.multiphase.vaporization_pressure.child_names: unavailable ('vaporization_pressure' object has no attribute 'child_names')
- setup.models.multiphase.non_condensable_gas: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/non-condensable-gas)
- setup.models.multiphase.non_condensable_gas.child_names: unavailable ('non_condensable_gas' object has no attribute 'child_names')
- setup.models.multiphase.liquid_surface_tension: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/liquid-surface-tension)
- setup.models.multiphase.liquid_surface_tension.child_names: unavailable ('liquid_surface_tension' object has no attribute 'child_names')
- setup.models.multiphase.bubble_number_density: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/bubble-number-density)
- setup.models.multiphase.bubble_number_density.child_names: unavailable ('bubble_number_density' object has no attribute 'child_names')
- setup.models.multiphase.hybrid_models: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/hybrid-models)
- setup.models.multiphase.hybrid_models.coupled_level_set: unavailable ('<session>.settings.setup.models.multiphase.hybrid_models' is currently inactive.)
- setup.models.multiphase.hybrid_models.multi_fluid_vof: unavailable ('<session>.settings.setup.models.multiphase.hybrid_models' is currently inactive.)
- setup.models.multiphase.number_of_phases.number_of_eulerian_phases.child_names: unavailable ('number_of_eulerian_phases' object has no attribute 'child_names')
- setup.models.multiphase.number_of_eulerian_discrete_phases: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/number-of-eulerian-discrete-phases)
- setup.models.multiphase.number_of_eulerian_discrete_phases.child_names: unavailable ('number_of_eulerian_discrete_phases' object has no attribute 'child_names')
- setup.models.multiphase.vof_sub_models: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/vof-sub-models)
- setup.models.multiphase.vof_sub_models.open_channel_flow: unavailable ('<session>.settings.setup.models.multiphase.vof_sub_models' is currently inactive.)
- setup.models.multiphase.vof_sub_models.open_channel_flow_wave_bc: unavailable ('<session>.settings.setup.models.multiphase.vof_sub_models' is currently inactive.)
- setup.models.multiphase.vof_parameters.vof_formulation.child_names: unavailable ('vof_formulation' object has no attribute 'child_names')
- setup.models.multiphase.vof_parameters.vof_cutoff: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/vof-parameters/vof-cutoff)
- setup.models.multiphase.vof_parameters.vof_cutoff.child_names: unavailable ('vof_cutoff' object has no attribute 'child_names')
- setup.models.multiphase.vof_parameters.vof_courant_number: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/vof-parameters/vof-courant-number)
- setup.models.multiphase.vof_parameters.vof_courant_number.child_names: unavailable ('vof_courant_number' object has no attribute 'child_names')
- setup.models.multiphase.advanced_formulation.implicit_body_force.child_names: unavailable ('implicit_body_force' object has no attribute 'child_names')
- setup.models.multiphase.advanced_formulation.explicit_expert_options: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/advanced-formulation/explicit-expert-options)
- setup.models.multiphase.phases.child_names: unavailable ('phases' has no attribute 'child_names')
- setup.models.multiphase.phase_interaction.mass_transfer_list.child_names: unavailable ('super' object has no attribute 'child_names')
- setup.models.multiphase.phase_interaction.intf_area.child_names: unavailable ('super' object has no attribute 'child_names')
- setup.models.multiphase.phase_interaction.interfacial_discretization: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/phase-interaction/interfacial-discretization)
- setup.models.multiphase.wet_steam_settings: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/wet-steam-settings)
- setup.models.multiphase.wet_steam_settings.max_liquid_mass_fraction: unavailable ('<session>.settings.setup.models.multiphase.wet_steam_settings' is currently inactive.)
- setup.models.multiphase.wet_steam_settings.virial_equation_of_state: unavailable ('<session>.settings.setup.models.multiphase.wet_steam_settings' is currently inactive.)
- setup.models.multiphase.wet_steam_settings.droplet_growth_rate: unavailable ('<session>.settings.setup.models.multiphase.wet_steam_settings' is currently inactive.)
- setup.models.multiphase.wet_steam_settings.stagnation_conditions: unavailable ('<session>.settings.setup.models.multiphase.wet_steam_settings' is currently inactive.)
- setup.models.multiphase.wet_steam_settings.enhanced_source_linearization: unavailable ('<session>.settings.setup.models.multiphase.wet_steam_settings' is currently inactive.)
- setup.models.multiphase.wet_steam_enabled: unavailable (api-get-var: the object is not active
Error Object: setup/models/multiphase/wet-steam-enabled)
- setup.models.multiphase.wet_steam_enabled.child_names: unavailable ('wet_steam_enabled' object has no attribute 'child_names')
- solution.initialization.initialization_type.child_names: unavailable ('initialization_type' object has no attribute 'child_names')
- solution.initialization.reference_frame.child_names: unavailable ('reference_frame_8' object has no attribute 'child_names')
- solution.initialization.defaults: unavailable (api-get-var: the object is not active
Error Object: solution/initialization/defaults)
- solution.initialization.defaults.child_names: unavailable ('defaults' has no attribute 'child_names')
- solution.initialization.localized_turb_init: unavailable (api-get-var: the object is not active
Error Object: solution/initialization/localized-turb-init)
- solution.initialization.localized_turb_init.enabled: unavailable ('<session>.settings.solution.initialization.localized_turb_init' is currently inactive.)
- solution.initialization.localized_turb_init.turbulent_intensity: unavailable ('<session>.settings.solution.initialization.localized_turb_init' is currently inactive.)
- solution.initialization.localized_turb_init.turbulent_viscosity_ratio: unavailable ('<session>.settings.solution.initialization.localized_turb_init' is currently inactive.)
- solution.initialization.hybrid_init_options.species_setting: unavailable (api-get-var: the object is not active
Error Object: solution/initialization/hybrid-init-options/species-setting)
- solution.initialization.open_channel_auto_init: unavailable (api-get-var: the object is not active
Error Object: solution/initialization/open-channel-auto-init)
- solution.initialization.open_channel_auto_init.boundary_zone: unavailable ('<session>.settings.solution.initialization.open_channel_auto_init' is currently inactive.)
- solution.initialization.open_channel_auto_init.open_channel_initialization_method: unavailable ('<session>.settings.solution.initialization.open_channel_auto_init' is currently inactive.)
- solution.initialization.open_channel_auto_init.flat_init: unavailable ('<session>.settings.solution.initialization.open_channel_auto_init' is currently inactive.)
- solution.initialization.open_channel_auto_init.wavy_surface_init: unavailable ('<session>.settings.solution.initialization.open_channel_auto_init' is currently inactive.)
- solution.initialization.fmg: unavailable (api-get-var: the object is not active
Error Object: solution/initialization/fmg)
- solution.initialization.fmg.fmg_courant_number: unavailable ('<session>.settings.solution.initialization.fmg' is currently inactive.)
- solution.initialization.fmg.enable_fmg_verbose: unavailable ('<session>.settings.solution.initialization.fmg' is currently inactive.)
- solution.initialization.fmg.viscous_terms: unavailable ('<session>.settings.solution.initialization.fmg' is currently inactive.)
- solution.initialization.fmg.species_reactions: unavailable ('<session>.settings.solution.initialization.fmg' is currently inactive.)
- solution.initialization.fmg.turbulent_viscosity_ratio: unavailable ('<session>.settings.solution.initialization.fmg' is currently inactive.)
- solution.initialization.enable_profile_memory_flushing.child_names: unavailable ('enable_profile_memory_flushing' object has no attribute 'child_names')
- solution.initialization.species_selection: unavailable (api-get-var: the object is not active
Error Object: solution/initialization/species-selection)
- solution.initialization.species_selection.selected_species: unavailable ('<session>.settings.solution.initialization.species_selection' is currently inactive.)
- scheme (cx-send '(getcwd)): unavailable (An error occurred in the server while evaluating the Scheme expression)
- scheme (cx-send '(getcwd)): unavailable (An error occurred in the server while evaluating the Scheme expression)
