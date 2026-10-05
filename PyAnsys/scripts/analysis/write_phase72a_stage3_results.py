"""Write the Stage 3 evidence-led results report from audited reductions."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/phase72a-stage3-server3/20261005'
P = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction'


def main():
    s = json.loads((OUT / 'analysis-summary.json').read_text())
    a = s['arms']; ref = s['reference']; text = []
    def lines(*rows): text.extend(rows)
    def table(headers, rows):
        lines('| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |')
        for row in rows: lines('| ' + ' | '.join(str(x) for x in row) + ' |')
        lines('')
    def figure(filename, alt, caption):
        lines(f'![{alt}](figures/{filename})', '', caption, '')
    lines('# Stage 3 — Shortened reconstruction: results report', '')
    table(['Question / decision', 'Result'], [
        ['Did the prescribed run finish?', 'Yes: bulk N0–N3000; fixed and adaptive film N3000–N6000; both final paired endpoints reopened'],
        ['Did the carrier scalars reproduce the reference?', 'Final-500 pressure, vapor outlet, liquid carryover and bulk inventory meet declared snapshot tolerances'],
        ['Did the developed film reproduce?', 'No: only 3 ms elapsed; inventory is 4.18% of the developed reference'],
        ['Did adaptive stepping accelerate film time?', 'No observed acceleration: printed steps remain 1 µs; both arms reach 3 ms'],
        ['Is the separator steady or fully balanced?', 'Not qualified: film fills, bulk inventory still falls, source fluctuates and whole-separator accounting remains open'],
        ['Can this recipe be used for mesh convergence now?', 'No; retain it as a tested carrier-startup candidate, not a qualified reconstruction'],
        ['Next compute decision', 'Analyse these completed screens first; no further solve or mesh case submitted'],
        ['Run contract', '[Setup and predeclared tolerances](setup.md)'],
        ['Machine evidence', '[Audited summary](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/analysis-summary.json)'],
        ['Reference', 'Corrected R3/contact N33586, independent four-rank replay; developed but not stationary'],
        ['Current endpoint', 'Server 3 adaptive N6000, 18 compute ranks; saved locally; verified idle before postprocessing'],
    ])
    lines('## Carrier reconstruction', '')
    table(['Metric', 'Reference snapshot', 'Fixed final-500 mean', 'Adaptive final-500 mean', 'Fixed / adaptive difference', 'Declared screen'], [
        [label, f"{ref[key] * factor:.4f}", f"{a['fixed']['comparisons'][key]['final_500_mean'] * factor:.4f}",
         f"{a['adaptive']['comparisons'][key]['final_500_mean'] * factor:.4f}",
         f"{a['fixed']['comparisons'][key]['difference_percent']:+.3f}% / {a['adaptive']['comparisons'][key]['difference_percent']:+.3f}%", f'±{tol}%: both pass']
        for key, label, factor, tol in [('pressure_drop_Pa', 'Pressure drop (kPa)', .001, 5),
                                      ('vapor_outlet_kg_s', 'Vapor outlet (kg/s)', 1, 5),
                                      ('liquid_carryover_kg_s', 'Liquid carryover (kg/s)', 1, 10),
                                      ('bulk_inventory_kg', 'Bulk liquid inventory (kg)', 1, 10)]])
    figure('carrier-final-window.png', 'Carrier response during the last 1000 updates',
           'Native report histories, N5000–N6000. Thin traces are raw values; solid trends are trailing 100-update means. Dashed black lines are the preserved N33586 snapshot, not a stationary reference window. Similar means support a carrier snapshot screen; continuing inventory decline limits the claim.')
    table(['Inventory / window sensitivity', 'Fixed', 'Adaptive', 'Meaning'], [
        ['Bulk inventory change, last 500 updates (kg)', f"{a['fixed']['comparisons']['bulk_inventory_kg']['windows']['500']['change_first_to_last']:.4f}", f"{a['adaptive']['comparisons']['bulk_inventory_kg']['windows']['500']['change_first_to_last']:.4f}", 'Continued decline; not a stationary inventory'],
        ['Bulk mean, last 250 / 500 / 1000 updates (kg)', ' / '.join(f"{a['fixed']['comparisons']['bulk_inventory_kg']['windows'][str(w)]['mean']:.3f}" for w in [250,500,1000]), ' / '.join(f"{a['adaptive']['comparisons']['bulk_inventory_kg']['windows'][str(w)]['mean']:.3f}" for w in [250,500,1000]), 'Screen depends on the stated finite window'],
        ['Liquid carryover mean, last 250 / 500 / 1000 (kg/s)', ' / '.join(f"{a['fixed']['comparisons']['liquid_carryover_kg_s']['windows'][str(w)]['mean']:.4f}" for w in [250,500,1000]), ' / '.join(f"{a['adaptive']['comparisons']['liquid_carryover_kg_s']['windows'][str(w)]['mean']:.4f}" for w in [250,500,1000]), 'Outlet response is close across finite windows'],
    ])
    figure('bulk-startup.png', 'Low feed, ramp and target hold before EWF is enabled',
           'Native N1–N3000 histories with EWF equations off. The source is the independently verified contact sink; flux histories are boundary-only. The dry-film N3000 state still has 123.15 kg of bulk liquid. The closer carrier response develops after EWF is enabled, so the 3000-update bulk hold alone is not a reproduced endpoint.')
    lines('## Film development and matched-time comparison', '')
    table(['Film quantity', 'Reference N33586', 'Fixed N6000', 'Adaptive N6000', 'Judgement'], [
        ['Elapsed time from common dry-film parent (ms)', 'Different developed lineage', '3.000', '3.000', 'Matched native elapsed time'],
        ['Film inventory (kg)', f"{ref['film_mass_kg']:.6f}", f"{a['fixed']['film_mass_end_kg']:.6f}", f"{a['adaptive']['film_mass_end_kg']:.6f}", 'About 95.82% below reference; fails ±10% screen'],
        ['Maximum thickness (mm)', f"{ref['film_max_m']*1000:.6f}", f"{a['fixed']['comparisons']['film_max_m']['endpoint']*1000:.6f}", f"{a['adaptive']['comparisons']['film_max_m']['endpoint']*1000:.6f}", 'About 71.21% below reference; fails screen'],
        ['Area-mean thickness (mm)', f"{ref['film_mean_m']*1000:.6f}", f"{a['fixed']['comparisons']['film_mean_m']['endpoint']*1000:.6f}", f"{a['adaptive']['comparisons']['film_mean_m']['endpoint']*1000:.6f}", 'About 95.82% below reference; fails screen'],
        ['Cumulative drainage since dry start (kg)', 'Different time origin', f"{a['fixed']['drained_mass_kg']:.8g}", f"{a['adaptive']['drained_mass_kg']:.8g}", 'Nearly all accretion remains stored'],
        ['Fixed/adaptive inventory difference', '—', 'Matched-time endpoint', f"{s['film_endpoint_fixed_adaptive_difference_percent']:+.6f}%", 'Agreement does not establish developed-film reproduction'],
        ['Peak thickness before final endpoint (mm)', 'Different developed lineage', f"{a['fixed']['peak_thickness_m']*1000:.6f} at N{a['fixed']['peak_thickness_native_iteration']}", f"{a['adaptive']['peak_thickness_m']*1000:.6f} at N{a['adaptive']['peak_thickness_native_iteration']}", 'Peak later falls while inventory grows; peak thickness alone cannot establish stationarity'],
    ])
    figure('film-reproduction.png', 'Film thickness development and percentage of reference',
           'Native film-wall reports on the only active EWF wall, `wall`. The green comparison band is the declared ±10% snapshot tolerance. Both endpoint values and final-500 means fail the inventory and thickness screens. Film thickness is a distribution diagnostic, not a stationarity test.')
    figure('film-matched-time.png', 'Film inventory, accretion, drainage and ledger on native time',
           'Film ledger: ΔM + ΔD − ∫A dt. A is native film-phase accretion (kg/s); D is cumulative edge outflow (kg). Fixed integration uses every accepted native clock. The adaptive shaded band bounds the 13 missing step clocks without assigning invented times to those updates.')
    table(['Film window', 'Fixed inventory growth (kg/s)', 'Adaptive inventory growth (kg/s)', 'Fixed drainage (kg/s)', 'Interpretation'], [
        [f"{i}–{i+1} ms", f"{a['fixed']['windows'][i]['inventory_growth_kg_s']:.3f}", f"{a['adaptive']['windows'][i]['inventory_growth_kg_s']:.3f}", f"{a['fixed']['windows'][i]['drainage_kg_s']:.8f}", 'Accretion fills the wall film'] for i in range(3)])
    table(['Ledger / timestep evidence', 'Fixed', 'Adaptive', 'Claim limit'], [
        ['Worst absolute film ledger error (% of integrated accretion)', f"{a['fixed']['film_ledger_worst_bound_percent']:.8f}%", f"≤{a['adaptive']['film_ledger_worst_bound_percent']:.8f}%", 'Both below the 1% screen; adaptive value is a conservative bound'],
        ['Printed accepted film step (µs)', '1.000', '1.000', 'No native step increase observed'],
        ['Observed peak film Courant number', f"{a['fixed']['observed_peak_film_cfl']:.6f}", f"{a['adaptive']['observed_peak_film_cfl']:.6f}", 'Adaptive peak covers observed records only'],
        ['Adaptive controls', 'Fixed mode', 'Initial 1 µs; target 0.1; increase 1.2; decrease 2.0', 'Readback confirms candidate settings; mechanism behind unchanged steps remains unverified'],
        ['Effective timestep contrast', 'Observed 1 µs steps', 'Observed 1 µs steps', 'Supports short-run repeatability at this step; does not test larger adaptive steps'],
        ['Missing per-update clocks', '0 after terminal reconciliation', 'N4392–N4404 (13 updates)', 'Full mass/source histories exist; individual accepted steps in this interval remain unknown'],
        ['Terminal clock', '3.000 ms', '3.000 ms', 'Printed final film line reconciled to paired/reopened N6000; terminal residual row absent'],
    ])
    figure('accepted-film-steps.png', 'Accepted film steps and Courant histories',
           'Native printed step and Courant evidence. Missing adaptive clock rows remain gaps. Low Courant number and a true adaptive flag do not prove that Fluent increased its timestep. This test does not establish an adaptive efficiency gain or an effective native maximum-step bound.')
    lines('## Source accounting and numerical limits', '')
    table(['Definition / observation', 'Evidence', 'Meaning'], [
        ['Native report-file liquid flux', 'Endpoint histories equal the computed `without-sources` values', 'Use boundary flow directly; do not subtract the UDF source again'],
        ['Instantaneous computed phase-2 flux', 'Contains boundary flow plus User Mass Source in each report', 'For a computed snapshot, remove the source once per boundary report before summing boundaries'],
        ['Independent source check', 'Contact expression equals −applied UDF source at every saved history row', 'Source implementation and reported contact removal agree'],
        ['Bulk boundary + contact residual', 'R = liquid feed − carrier liquid outlet − contact removal', 'Excludes EWF transfers; report separately from the film ledger'],
        ['R, final-500 mean (kg/s)', f"Fixed {a['fixed']['bulk_accounting']['boundary_plus_contact_final_500_kg_s']['mean']:.3f}; adaptive {a['adaptive']['bulk_accounting']['boundary_plus_contact_final_500_kg_s']['mean']:.3f}", 'Large residual; not a closed whole-separator account'],
        ['Conditional R − film accretion (kg/s)', f"Fixed {a['fixed']['bulk_accounting']['conditional_minus_film_accretion_final_500_kg_s']['mean']:.3f}; adaptive {a['adaptive']['bulk_accounting']['conditional_minus_film_accretion_final_500_kg_s']['mean']:.3f}", 'Still large; native bulk/film source scope must be audited before calling this a full balance'],
        ['Contact removal, final-500 mean ± standard deviation (kg/s)', f"Fixed {a['fixed']['comparisons']['contact_removal_kg_s']['windows']['500']['mean']:.2f} ± {a['fixed']['comparisons']['contact_removal_kg_s']['windows']['500']['std']:.2f}; adaptive {a['adaptive']['comparisons']['contact_removal_kg_s']['windows']['500']['mean']:.2f} ± {a['adaptive']['comparisons']['contact_removal_kg_s']['windows']['500']['std']:.2f}", 'Persistent source oscillation despite similar carrier means'],
        ['Scaled continuity, late mean', f"Fixed {a['fixed']['residual_last_500']['continuity']['mean']:.4f}; adaptive {a['adaptive']['residual_last_500']['continuity']['mean']:.4f}", 'High residual plateau; no numerical-convergence claim'],
        ['Warning events', 'Reverse-flow and turbulent-viscosity limiting recur; no detected fatal run events', 'Warnings help locate numerical limits; counts are transcript messages, not unique events'],
        ['Carrier time', 'Steady Coupled pseudo-time updates with EWF time advancement', 'Do not convert bulk kg/update inventory slope to a physical kg/s storage term'],
        ['DPM', 'Six inherited one-way diagnostic injections, each 1e-20 kg/s; no two-way carrier source', 'Definitions preserved; fresh complete particle-fate comparison is missing'],
        ['Film scope', '`wall` active; inner separator and lower wall patches are not film walls; Flow Momentum Coupling off', 'Film closure applies to the verified wall/report scope'],
    ])
    figure('numerical-accounting.png', 'Late source fluctuations, source residual and native residuals',
           'Raw N5000–N6000 histories. The boundary/contact residual and film accretion are separate rate diagnostics; this plot does not assert a verified interphase balance. Carrier inventory decline, source oscillation and continuity plateau prevent a steady whole-model claim.')
    lines('## Spatial comparison from native Fluent graphics', '')
    table(['Comparison policy', 'Value'], [
        ['Source identity', 'Preserved reference N33586, dry N3000 and fixed/adaptive N6000 paired checkpoints; remote hashes checked before loading'],
        ['Carrier plane', 'XY at Z = 0 m; orthographic view along +Z'],
        ['Shared field ranges', 'Liquid fraction 0–1; velocity 0–85 m/s; film thickness 0–0.35 mm'],
        ['Film surface', 'Only confirmed active EWF wall `wall`; projection is a front view of the three-dimensional wall'],
        ['Pixel source', 'Native Fluent picture exports; transferred without image reconstruction or compositing'],
        ['Provenance and visual QA', '[Native figure manifest](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/native-figure-manifest.json)'],
    ])
    table(['Developed reference N33586', 'Adaptive startup N6000, 3 ms'], [
        ['![Reference liquid fraction](figures/native-reference-N33586-phase-2-vof.png)', '![Adaptive liquid fraction](figures/native-adaptive-N6000-phase-2-vof.png)'],
        ['![Reference velocity](figures/native-reference-N33586-velocity-magnitude.png)', '![Adaptive velocity](figures/native-adaptive-N6000-velocity-magnitude.png)'],
        ['![Reference film thickness](figures/native-reference-N33586-film-thickness.png)', '![Adaptive film thickness](figures/native-adaptive-N6000-film-thickness.png)'],
    ])
    lines('Carrier contours support the close scalar screen, while the wall-film comparison shows the much smaller developed inventory. A centre-plane comparison does not prove agreement throughout the full three-dimensional volume.', '')
    table(['Same-plane native facet diagnostic', 'Dry N3000 vs reference', 'Fixed N6000 vs reference', 'Adaptive N6000 vs reference'], [
        ['Liquid fraction RMS absolute difference', *[f"{s['spatial_diagnostics'][case]['phase-2-vof']['unweighted_facet_rms_difference']:.6g}" for case in ['bulk','fixed','adaptive']]],
        ['Velocity RMS difference (m/s)', *[f"{s['spatial_diagnostics'][case]['velocity-magnitude']['unweighted_facet_rms_difference']:.6g}" for case in ['bulk','fixed','adaptive']]],
    ])
    lines('These are unweighted differences at the same native facet coordinates. They are supporting diagnostics; no mesh weighting or predeclared spatial tolerance is implied.', '')
    table(['Supporting native exports', 'Link'], [
        ['Fixed N6000', '[Liquid fraction](figures/native-fixed-N6000-phase-2-vof.png), [velocity](figures/native-fixed-N6000-velocity-magnitude.png), [film thickness](figures/native-fixed-N6000-film-thickness.png)'],
        ['Common dry-film N3000', '[Liquid fraction](figures/native-bulk-dry-N3000-phase-2-vof.png), [velocity](figures/native-bulk-dry-N3000-velocity-magnitude.png)'],
    ])
    lines('## Tested recipe, measured cost and next use', '')
    table(['Recipe step / cost', 'Measured result / status'], [
        ['0–1500', '25% target liquid/vapor mass flows; Coupled and R3 from start; EWF equations off'],
        ['1500–2500', 'Ten 100-update steps to target 116.92 / 80.69 kg/s'],
        ['2500–3000', 'Target-feed hold with EWF off; preserve common dry-film parent'],
        ['3000–6000', 'Initialize dry EWF; 3000 updates at 1 µs, or this tested adaptive candidate'],
        ['Bulk cost', f"{s['bulk_wall_seconds_including_smoke']/60:.2f} min, including smoke/evidence timing; excludes interruption waiting"],
        ['Fixed film cost', f"{a['fixed']['documented_block_wall_seconds']/60:.2f} min for 3000 updates and block endpoint saves"],
        ['One fixed reconstruction candidate', f"{s['fixed_recipe_measured_wall_seconds']/60:.2f} min documented startup + fixed-film blocks; preparation and fault/human waiting excluded"],
        ['Adaptive documented subtotal', f"{a['adaptive']['documented_block_wall_seconds']/60:.2f} min; pre-stop N4000–N4404 timing not captured; not a complete cost or speedup claim"],
        ['Historical cost comparison', 'Different hardware/rank history and no matching measured baseline; no demonstrated cost-reduction percentage'],
        ['Reusable now', 'Executable carrier startup and finite 3 ms film screen, with paired endpoints and evidence'],
        ['Before developed-film reconstruction', 'Investigate native adaptive control effectiveness; select a bounded physical-film-time continuation; compare against an explicitly chosen developed state'],
        ['Before a steady/full-separator claim', 'Sustained inventory/transfer balance; verified EWF mass-source scope; lower source oscillation; residual and full spatial evidence'],
        ['Before mesh convergence', 'Reconstruction qualification plus physical collector extent and wall/film-treatment preservation across meshes'],
        ['Current continuation decision', 'No further solve launched; existing evidence is sufficient to report this finite startup screen'],
    ])
    table(['Required evidence still missing', 'Effect on claims'], [
        ['Stationary developed-reference window', 'Snapshot agreement cannot certify a steady reference or reconstructed steady state'],
        ['Developed drainage and film distribution', 'Short startup is not a complete replacement for model-development history'],
        ['Verified whole-separator mass ledger including EWF source scope', 'Good film-only closure cannot establish bulk-plus-film conservation'],
        ['Fresh complete DPM fate comparison', 'No particle-routing reproduction claim'],
        ['13 adaptive step clocks and full adaptive solve timing', 'Bound film accounting; retain gaps; no full adaptive efficiency comparison'],
        ['Matched historical reconstruction cost', 'No quantified speed improvement over the old procedure'],
    ])
    table(['Machine artifact', 'Link'], [
        ['Execution and local checkpoint hashes', '[Run manifest](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/run-manifest.json)'],
        ['Completed resumed job', '[Job manifest](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/user-resume-job-manifest.json)'],
        ['Live N6000 idle / saved-field verification', '[Readback receipt](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/analysis-live-N6000.json)'],
        ['Exact native report scope', '[Report definitions](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/analysis-report-definitions.json)'],
        ['Analysis implementation', '[History reduction](../../../../PyAnsys/scripts/analysis/analyze_phase72a_stage3.py)'],
        ['Native spatial export implementation', '[Fluent graphics export](../../../../PyAnsys/scripts/inspection/export_phase72a_stage3_native.py)'],
    ])
    (P / 'results.md').write_text('\n'.join(text).rstrip() + '\n')
    state_path = P.parent / 'phase-state.yaml'; state_text = state_path.read_text()
    match = re.search(r'(?ms)^stage3_reconstruction:\n.*?(?=^[^\s#]|\Z)', state_text)
    if not match: raise RuntimeError('Stage 3 node missing')
    block = match.group(0)
    for key, value in {'status': 'SCREEN_ANALYSED_CARRIER_CLOSE_FILM_REPRODUCTION_FAILED', 'last_verified_native_iteration': '6000', 'run_submitted': 'false', 'completion_handoff': 'CLI_RETURN_FAILED_DESKTOP_CHAT_ACTIVE_WRITER'}.items():
        block = re.sub(rf'(?m)^  {key}:.*$', f'  {key}: {value}', block)
    updates = {'analysis_summary': 'PyAnsys/output/phase72a-stage3-server3/20261005/analysis-summary.json',
               'native_figure_manifest': 'PyAnsys/output/phase72a-stage3-server3/20261005/native-figure-manifest.json',
               'fixed_and_adaptive_final_reopen': 'PASS', 'added_film_time_each_arm_s': '0.003',
               'adaptive_clock_gap_range': '[4392, 4404]', 'adaptive_speedup': 'NOT_OBSERVED',
               'film_reproduction': 'FAILED_PREDECLARED_SCREEN', 'carrier_snapshot_screen': 'PASS_FINAL_500',
               'whole_separator_accounting': 'NOT_QUALIFIED', 'next_solve_selected': 'false'}
    for key, value in updates.items():
        if re.search(rf'(?m)^  {key}:', block): block = re.sub(rf'(?m)^  {key}:.*$', f'  {key}: {value}', block)
        else: block += f'  {key}: {value}\n'
    state_path.write_text(state_text[:match.start()] + block + state_text[match.end():])
    print('STAGE3_RESULTS_REPORT_WRITTEN')


if __name__ == '__main__':
    main()
