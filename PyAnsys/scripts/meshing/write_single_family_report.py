"""Write the project result from verified machine receipts only."""
import argparse,json
from build_single_inlet_family import ROOT,OUT
from summarise_single_family import collect

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--working-only',action='store_true',help='Report verified working files without claiming shared delivery')
    args=parser.parse_args()
    rows=collect()
    if len(rows)!=7:raise RuntimeError('Seven verified levels required')
    delivered=False
    if not args.working_only:
        delivery=json.loads((OUT/'delivery.json').read_text())
        if delivery['status']!='COMPLETE':raise RuntimeError('Delivery has not completed')
        delivered=True
    qmin=min(r['min_oq'] for r in rows);qmax=max(r['min_oq'] for r in rows)
    volmax=max(abs(r['volume_delta']) for r in rows)*100
    outletmax=max(abs(r['area_deltas']['steamoutlet']) for r in rows)*100
    inletmax=max(abs(r['area_deltas']['inlet']) for r in rows)*100
    head='''# Single-inlet mesh family — 8 October 2026

Seven meshes were rebuilt from the preserved `Separator-purnanto-single-733k.msh.h5` workflow and its supplied single-inlet CAD. The CAD file is unchanged. Every mesh has one `inlet`, the same boundary names/types, positive cell volumes, and zero free or multiply connected boundary faces after save/reopen. No CFD solve was run.

| Delivery | Location |
| --- | --- |
| Final meshes, recipes and CAD | `CAD PurnantoV2\\single-inlet-refinement-20261008` beside the user's source files on the Fluent PC/OneDrive |
| Local working meshes | `C:\\Users\\syok443\\P4P-mesh-audit-20261008\\single-family` |
| Evidence | [Family summary](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json), [copy hashes](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/final-copy-manifest.json), [delivery receipt](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/delivery.json) |

## Selected family

Counts were allowed to change. Fixed curvature capture imposes a coarse surface-mesh floor. The selected levels use actual counts to avoid nearly duplicate meshes. Each name uses the rounded count and the original single-inlet naming convention.

| Level | Mesh | Cells | Min OQ before improvement | Min OQ saved | Max skewness saved | Mean OQ saved |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
'''
    lines=[head]
    if not delivered:
        lines[0]=lines[0].replace('| Final meshes, recipes and CAD |','| Intended final folder; copy not verified |')
        lines[0]=lines[0].replace(', [copy hashes](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/final-copy-manifest.json), [delivery receipt](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/delivery.json)','')
        lines[0]=lines[0].replace('## Selected family','All seven working meshes are saved and verified. Fluent Meshing closed during the final copy. Shared-copy completion and restoration of the 682k anchor in the GUI are pending a new API connection.\n\n## Selected family')
    for i,r in enumerate(rows,1):
        lines.append(f"| {i} | `{r['file']}` | {r['cells']:,} | {r['before_min_oq']:.4f} | {r['min_oq']:.4f} | {r['max_skewness']:.4f} | {r['mean_oq']:.4f} |\n")
    lines.append('\n![Achieved refinement and quality](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-quality.png)\n\n')
    ratios=[r['cell_ratio_to_previous'] for r in rows[1:]]
    lines.append(f"Actual adjacent cell-count ratios range from {min(ratios):.3f} to {max(ratios):.3f}. The final level has a larger step ({rows[-1]['cell_ratio_to_previous']:.3f} in count; {rows[-1]['h_ratio_from_previous']:.3f} in effective h). Poly-hexcore uses discrete octree refinement levels, so counts need not vary smoothly with the size setting. [Ansys 2025 R2 volume-meshing guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/tgd_user_workflow_guided_tasks_vol_mesh_gen.html).\n\n")
    improved=sum(r['min_oq']>r['before_min_oq']+1e-12 for r in rows)
    lines.append(f'Minimum orthogonal quality improved in {improved} of {len(rows)} recorded before/after comparisons. Achieved minima range from **{qmin:.3f} to {qmax:.3f}**. The improvement target was 0.3; a target setting is not an achieved-quality claim.\n\n')
    recovered=[r for r in rows if r.get('recovery')]
    for r in recovered:
        lines.append(f"The {r['cells']:,}-cell level was recovered after a user-requested pause. The matching live volume was preserved, full quality arguments were restored and read back, and the native quality command was invoked with iteration limit {r['quality_iteration_limit']}. The recorded recovery comparison is {r['before_min_oq']:.4f} before versus {r['min_oq']:.4f} saved. The original pre-improvement value during volume generation was not captured for this level.\n\n")
    lines.append('| Level | Effective h = (V/N)^(1/3), m | Cell ratio to previous | Max Fluent aspect ratio | Max size change | Cells with size change >= 300 | Cells with OQ below 0.3 |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n')
    for i,r in enumerate(rows,1):
        ratio=f"{r['cell_ratio_to_previous']:.3f}" if i>1 else '—'
        tail=r['cells_size_change_ge300']
        tail_text=f"{tail:,}" if tail is not None else 'Not measured'
        lines.append(f"| {i} | {r['effective_h_m']:.5f} | {ratio} | {r['max_aspect_ratio']:.2f} | {r['max_size_change']:.2f} | {tail_text} | {r['cells_below_oq03']:,} ({r['cells_below_oq03']/r['cells']*100:.3f}%) |\n")
    lines.append('''
Aspect ratio and size change do not improve uniformly. The mesh retains thin wall-layer cells. The 682k anchor has two cells with size change at least 300, including a maximum of 881.63; additional diagnostic improvement did not reduce this maximum. The table reports those tradeoffs; improved minimum OQ and skewness do not mean every quality metric is better than every old mesh.

## Geometry and central pipe

All levels use the same preserved CAD, SHA256 `24777C3009AEA1784C629989A79E722DA17A24FC4BA30058AD73EAC59FE2F5D7`. Surface discretisation changes the polygonal area and volume slightly. Initial unrestricted coarse trials changed outlet area by 2.3%; those trials are excluded. The selected recipe holds curvature capture at 6 degrees.

| Level | Volume, m3 | Volume difference from original 733k | Inlet area difference | Outlet area difference | Maximum wall-area difference |
| --- | ---: | ---: | ---: | ---: | ---: |
''')
    for i,r in enumerate(rows,1):
        wall=max(abs(v) for k,v in r['area_deltas'].items() if k not in ['inlet','steamoutlet'])
        lines.append(f"| {i} | {r['volume_m3']:.6f} | {100*r['volume_delta']:+.4f}% | {100*r['area_deltas']['inlet']:+.5f}% | {100*r['area_deltas']['steamoutlet']:+.4f}% | {100*wall:.4f}% |\n")
    lines.append(f'\nMaximum absolute differences from the parent are {volmax:.4f}% for volume, {outletmax:.4f}% for outlet area, and {inletmax:.5f}% for inlet area. These measurements establish the recorded geometry representation; they do not prove exact parity with the original paper CAD.\n\n')
    lines.append('''The central-pipe check compared the original 733k mesh with the saved 357k and 381k builds. Each has zero cell centres in the pipe core (`r < 0.25 m`, below the outlet plane `y = 6.261 m`). All lower-band cell centres lie outside the central wall. Fluid cells above the outlet plane were already present in the original. No downstream pipe-fluid region was added. [Read-only cell comparison](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/central-pipe-check.json).

![Central-pipe comparison](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/central-pipe-comparison.png)

This preserves the supplied simplified 733k domain. It does not establish full physical-geometry parity with Purnanto 2013, including the lower brine outlet and exact scroll/head profiles. The supplied CAD is the parent for this mesh-convergence family.

## Fixed controls and checks

| Item | Control/evidence |
| --- | --- |
| CAD | Same preserved single-inlet AGDB on every level; no CAD edits |
| Surface controls | Curvature and Proximity; curvature normal angle 6 degrees; minimum/maximum lengths scaled from 0.01/0.05 m |
| Local outlet sizing | Scaled from 0.05 m |
| Volume mesh | Poly-hexcore; maximum cell length scaled from 0.08 m |
| Wall layers | 12 requested layers; growth 1.15; same wall scopes; smooth transition |
| Surface improvement | Source 733k task retained; no defeaturing/step removal |
| Volume improvement | Orthogonal quality target 0.3; iteration limit 25, except recovered level 26; geometric-feature ignoring disabled |
| Saved-mesh checks | Positive volume in every cell; zero free/multi boundary faces; same names/types; native mesh check; saved/reopened counts match |
| File delivery | New destination files; SHA256 equality between local working and shared copies; original source meshes preserved |

Fluent reported local stair-stepping of all requested wall layers at one location during the selected volume builds. Thus, 12 requested layers does not mean 12 layers everywhere. No solved wall y-plus is available. These files are mesh-preparation products; mesh independence and solver convergence still require the planned CFD study.

| Boundary | Type |
| --- | --- |
| `inlet` | velocity-inlet |
| `steamoutlet` | pressure-outlet |
| `bottom` | wall |
| `inlet-wall-1-wall-separator-purnanto` | wall |
| `inlet-wall-2-wall-separator-purnanto` | wall |
| `vessel-wall-wall-separator-purnanto` | wall |
| `wall` | wall |
| `separator-purnanto:1` | wall |

Implementation: [builder](../../PyAnsys/scripts/meshing/build_single_inlet_family.py), [selection](../../PyAnsys/scripts/meshing/build_remaining_single_levels.py), [summary checks](../../PyAnsys/scripts/meshing/summarise_single_family.py). Fluent version: 2025 R2 / 25.2. Curvature-control meaning: [Ansys 2025 R2 surface meshing guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/tgd_user_workflow_guided_surface_mesh_gen.html).
''')
    selected_pipe=OUT/'selected-central-pipe-check.json'
    if selected_pipe.exists():
        pipe_rows=json.loads(selected_pipe.read_text())
        if len(pipe_rows)!=8:raise RuntimeError('Incomplete selected-family pipe audit')
        if any(r['deep_pipe_core_cells'] or any(b['core_r_lt025_cells'] for b in r['bands'] if b['y_range_m'][1]<=6.261) for r in pipe_rows):
            raise RuntimeError('Central-pipe core cell audit failed')
        lines.append('\nThe final read-only HDF5 check covers the original mesh and all seven selected meshes. All eight have zero cell centres inside the checked pipe core below the outlet plane. [Final pipe audit](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/selected-central-pipe-check.json).\n\n![Original and selected anchor](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/selected-central-pipe-comparison.png)\n')
    path=ROOT.parent/'Project/technical/single-inlet-mesh-family-20261008.md'
    text=''.join(lines)
    if not delivered:
        text=text.replace('| File delivery | New destination files; SHA256 equality between local working and shared copies; original source meshes preserved |','| File delivery | Working files saved; original source meshes preserved; shared-copy hashes not yet verified |')
    path.write_text(text);print(path)

if __name__=='__main__':main()
