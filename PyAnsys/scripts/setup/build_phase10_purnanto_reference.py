"""Restore the recorded 00a carrier settings on the saved 08b case scaffold.

No solves. Original case and mesh files remain unchanged. Credentials are env-only.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/meshing'), str(ROOT / 'src')]
from publish_single_family import connect, remote_ps_file, psquote, read_text
from pyansys_fluent.common import remote_file_exists

OUT = ROOT / 'output/phase10-single-inlet-mesh-convergence'
WORK = 'C:/Users/syok443/Documents/FluentRuns/Phase10/20261008'
SOURCE = WORK + '/inputs/08b-reference.cas.h5'
COMMON = WORK + '/inputs/purnanto-00a-carrier-common.cas.h5'


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, default=str))


def snapshot(s):
    return {'setup': s.settings.setup.get_state(),
            'methods': s.settings.solution.methods.get_state(),
            'controls': s.settings.solution.controls.get_state(),
            'residual_equations': s.settings.solution.monitor.residual.equations.get_state()}


def main():
    s = connect(); s.events.stop()
    if remote_file_exists(s, COMMON):
        raise FileExistsError('Reconcile existing common reference before rebuilding')
    s.settings.file.read_case(file_name=SOURCE)
    before = snapshot(s)
    dump('reference-scaffold-before.json', before)
    inlet = s.settings.setup.boundary_conditions.mass_flow_inlet
    assert set(inlet.get_object_names()) == {'liquidinlet', 'steaminlet'}
    inlet['liquidinlet'].set_state(inlet['steaminlet'].get_state())
    s.settings.mesh.modify_zones.merge_zones(zone_names=['liquidinlet', 'steaminlet'])
    survivor = inlet.get_object_names()
    assert len(survivor) == 1
    s.settings.mesh.modify_zones.zone_name(zone_name=survivor[0], new_name='inlet')
    inlet = s.settings.setup.boundary_conditions.mass_flow_inlet['inlet']
    inlet.phase['phase-1'].momentum.mass_flow_rate.value = 80.69
    inlet.phase['phase-2'].momentum.mass_flow_rate.value = 116.92
    inlet.phase['mixture'].turbulence.turbulent_intensity = 0.0211
    inlet.phase['mixture'].turbulence.hydraulic_diameter = 0.724
    outlet = s.settings.setup.boundary_conditions.pressure_outlet['steamoutlet']
    outlet.phase['mixture'].turbulence.backflow_turbulent_intensity = 0.021525
    outlet.phase['mixture'].turbulence.backflow_hydraulic_diameter = 0.724
    s.settings.setup.general.operating_conditions.operating_density.method = 'mixture-averaged'
    s.settings.solution.methods.spatial_discretization.discretization_scheme['k'] = 'second-order-upwind'
    injections = s.settings.setup.models.discrete_phase.injections
    names = injections.get_object_names()
    if names:
        injections.delete(name_list=names)
    assert not injections.get_object_names()
    assert not s.settings.setup.models.discrete_phase.general_settings.interaction.enabled()
    after = snapshot(s)
    assert after['setup']['models']['multiphase']['model'] == 'mixture'
    assert after['setup']['models']['viscous']['k_epsilon_model'] == 'rng'
    assert after['setup']['general']['solver']['time'] == 'steady'
    dump('common-reference-before-save.json', after)
    for group, values in after['setup']['materials'].items():
        assert values == before['setup']['materials'][group], 'Material properties changed: ' + group
    removed_material_groups = set(before['setup']['materials']) - set(after['setup']['materials'])
    assert removed_material_groups <= {'inert_particle'}, removed_material_groups
    assert after['controls'] == before['controls']
    assert after['residual_equations'] == before['residual_equations']
    s.settings.file.write_case(file_name=COMMON)
    assert remote_file_exists(s, COMMON)
    s.settings.file.read_case(file_name=COMMON)
    reopened = snapshot(s)
    assert reopened == after, 'Common-case settings changed on reopen'
    receipt = WORK + '/common-reference-identity.json'
    remote_ps_file(s, '$ErrorActionPreference="Stop"\n'
                   '@{case=' + psquote(COMMON) + ';sha256=(Get-FileHash -LiteralPath '
                   + psquote(COMMON) + ' -Algorithm SHA256).Hash} | ConvertTo-Json | '
                   'Set-Content -LiteralPath ' + psquote(receipt) + ' -Encoding Ascii')
    identity = json.loads(read_text(s, receipt))
    dump('common-reference-setup.json', reopened)
    dump('common-reference-build.json', {'status': 'SAVED_REOPENED', 'identity': identity,
         'source_identity': json.loads((OUT / 'reference-identity.json').read_text()),
         'scientific_reference': 'Project/experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00a-live-setup-audit/setup.md',
         'changes_from_08b_scaffold': ['single mixed inlet, phase flows preserved',
             'inlet turbulence diameter 0.724 m', 'inlet intensity 2.11%',
             'outlet backflow intensity 2.1525%, diameter 0.724 m',
             'operating density mixture-averaged', 'second-order k',
             'no active DPM injections; no DPM carrier feedback'],
         'unrecorded_advanced_settings': 'Retained from 08b scaffold; not claimed as byte-identical original 00a settings',
         'new_solve_iterations': 0})
    print('COMMON_REFERENCE_SAVED_REOPENED', json.dumps(identity), flush=True)


if __name__ == '__main__':
    main()
