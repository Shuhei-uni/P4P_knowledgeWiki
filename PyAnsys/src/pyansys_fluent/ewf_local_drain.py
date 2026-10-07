"""Local EWF liquid removal independent of the bulk solver and inlet command."""
from __future__ import annotations

import math

WALL='wall:004'
PREFIX='P72d'


def definitions(density, tau_s=.0015, refresh_span_s=15e-6, max_fraction=.01):
    if any(not math.isfinite(v) or v<=0 for v in [density,tau_s,refresh_span_s]):
        raise ValueError('Positive density, capture time and source-refresh span required')
    if not 0<max_fraction<1:
        raise ValueError('Source depletion fraction must lie between zero and one')
    return {
        'P72dDensity':f'{density:.17g}[kg/m^3]',
        'P72dTau':f'{tau_s:.17g}[s]',
        'P72dRefreshSpan':f'{refresh_span_s:.17g}[s]',
        'P72dMaxFraction':f'{max_fraction:.17g}',
        'P72dEnabled':'0',
        'P72dRate':'min(1/P72dTau,P72dMaxFraction/P72dRefreshSpan)',
        'P72dHeight':'max(FilmThickness,0[m])',
        'P72dSink':'-P72dEnabled*P72dRate*P72dDensity*P72dHeight',
        **{f'P72dSink{axis.upper()}':f'P72dSink*FilmVelocity.{axis}' for axis in 'xyz'},
        'P72dRemoval':f'-AreaInt(P72dSink,["{WALL}"])',
        'P72dInventory':f'AreaInt(P72dDensity*P72dHeight,["{WALL}"])',
    }


def configure(solver,*,tau_s=.0015,refresh_span_s=15e-6,max_fraction=.01,enabled=False):
    p=dict(solver.rp_vars('wall-film/model-parameters'))
    if p['ewf-adaptive?'] or p['timestep-max']>refresh_span_s:
        raise RuntimeError('Drain source-refresh bound requires a verified fixed film step')
    material=p['film-material'].strip('"')
    density=solver.settings.setup.materials.fluid[material].density.get_state()
    if density['option']!='value':
        raise RuntimeError('This drain requires the verified constant liquid density')
    d=definitions(float(density['value']),tau_s,refresh_span_s,max_fraction)
    expressions=solver.settings.setup.named_expressions
    for name,value in d.items():
        if name not in expressions.get_object_names():expressions.create(name=name)
        expressions[name].definition=value
        if expressions[name].definition()!=value:raise RuntimeError('Expression readback differs: '+name)
    wall=solver.settings.setup.boundary_conditions.wall[WALL].phase['mixture'].wall_film
    if not wall.eulerian_film_wall() or wall.film_condition_type()!='film-wall-initial':
        raise RuntimeError('The lower film wall must be allocated with Initial Condition')
    wall.enable_flow_momentum_coupling=False
    wall.enable_film_source_terms=True
    wall.film_mass_source.set_state({'option':'value','value':'P72dSink'})
    wall.momentum_source.set_state([{'option':'value','value':'P72dSink'+axis} for axis in 'XYZ'])
    # Both arms use the same native source hooks. The dimensionless switch
    # makes the reported source zero in OFF, rather than reporting a potential
    # sink that is not actually applied by the solver.
    set_enabled(solver,enabled)
    solver.settings.solution.run_calculation.profile_update_interval=1
    return {'definitions':d,'density':density,'tau_s':tau_s,'refresh_span_s':refresh_span_s,
            'maximum_fraction_per_declared_refresh':max_fraction,'wall':wall.get_state()}


def set_enabled(solver,enabled):
    solver.settings.setup.named_expressions['P72dEnabled'].definition='1' if enabled else '0'


def audit(solver,enabled):
    wall=solver.settings.setup.boundary_conditions.wall[WALL].phase['mixture'].wall_film.get_state()
    if not wall['enable_film_source_terms'] or wall['enable_flow_momentum_coupling']:
        raise RuntimeError('Drain activation or wall momentum-feedback state differs')
    assert wall['film_mass_source']['value']=='P72dSink'
    assert [v['value'] for v in wall['momentum_source']]==['P72dSink'+axis for axis in 'XYZ']
    assert float(solver.settings.setup.named_expressions['P72dEnabled'].get_value())==int(enabled)
    p=dict(solver.rp_vars('wall-film/model-parameters'))
    span=float(solver.settings.setup.named_expressions['P72dRefreshSpan'].get_value())
    rate=float(solver.settings.setup.named_expressions['P72dRate'].get_value())
    if p['ewf-adaptive?'] or p['timestep-max']>span or solver.settings.solution.run_calculation.profile_update_interval()!=1:
        raise RuntimeError('Live stepping or profile cadence invalidates the drain bound')
    assert rate*span<=.01*(1+1e-10)
    return {'wall':wall,'rate_s_inverse':rate,'refresh_span_s':span,'source_only_fraction_bound':rate*span}
