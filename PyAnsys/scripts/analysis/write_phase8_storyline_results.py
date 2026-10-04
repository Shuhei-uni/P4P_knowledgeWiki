"""Write requested Phase 8 results from computed summaries and native export receipts."""
from pathlib import Path
import json
import os
import re

ROOT=Path(__file__).resolve().parents[3]
PHASE=ROOT/"Project/experiments/phase-08-storyline-reconstruction"
OUT=ROOT/"PyAnsys/output/phase8-storyline-20260930"
DIRS={"F1":"f1-one-inlet","F2":"f2-split-inlet","F3":"f3-coupled-dpm","F4":"f4-coupled-dpm-ewf"}

def relative(path,base):return os.path.relpath(path,base).replace("\\","/")

def embedded_images(text,base):
    def replace(match):
        target=match.group(2).strip('<>')
        if target.startswith(('https://','http://','data:')):return match.group(0)
        path=(base/target).resolve()
        if not path.is_file():raise RuntimeError(f"Missing embedded figure: {path}")
        return f"![{match.group(1)}]({relative(path,base)})"
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',replace,text)

def main():
    summary=json.loads((OUT/"summary.json").read_text())
    exports=json.loads((OUT/"export-receipt.json").read_text())
    tracks=json.loads((OUT/"track-export-receipt.json").read_text()) if (OUT/"track-export-receipt.json").exists() else {"cases":{}}
    catalog=json.loads((OUT/"catalog.json").read_text())
    ranges=json.loads((OUT/"range-receipt.json").read_text())["display_ranges"]
    families=summary["families"]
    def img(path,base,alt):
        p=ROOT/path if isinstance(path,str) else path
        if not p.exists():raise RuntimeError(f"Missing result figure: {p}")
        return f"![{alt}]({relative(p.resolve(),base)})"
    def native(id,kind,base):return img(exports["cases"][id]["images"][kind]["path"],base,id+" "+kind)
    def simple_dpm_section(base):
        path=ROOT/"PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/f1-simple-diagnostic-dpm-fates.json"
        if not path.exists():return ""
        dpm=json.loads(path.read_text(encoding="utf-8"))
        table="| Speed (m/s) | Escaped represented weight (%) | Trapped represented weight (%) | Incomplete represented weight (%) |\n| ---: | ---: | ---: | ---: |\n"
        for row in dpm["runs"]:
            f=row["weighted_fate_fraction"]
            table+=f"| {row['speed_m_s']:.2f} | {100*f['escaped']:.2f} | {100*f['trapped']:.2f} | {100*f['incomplete']:.2f} |\n"
        return "### One-way DPM diagnostics on the SIMPLE carriers\n\n"+img(ROOT/"PyAnsys"/dpm["figure"],base,"F1 SIMPLE carrier one-way DPM diagnostic fates")+"\n\n"+table+"\nThese seven-bin cases use 5% inert, one-way DPM weight, a 50,000-step tracking cap, and the same full-feed Eulerian SIMPLE carriers. The large incomplete share is unresolved trajectory weight. The fates are diagnostic outcomes on numerically poor carriers, not separator efficiency or validated separation.\n\n"
    def ref(base):
        return f"[hash-verified case catalog]({relative(OUT/'catalog.json',base)}), [native export receipt]({relative(OUT/'export-receipt.json',base)}), [surface/range receipt]({relative(OUT/'range-receipt.json',base)}) and [plot summary]({relative(OUT/'summary.json',base)})."
    def gallery(family,base):
        entries=[e for e in catalog if e["family"]==family and e["role"]!="particle-views"]
        text="| Saved snapshot | Liquid, vertical cut | Liquid, inlet slice | Vertical vectors | Inlet vectors |\n| --- | --- | --- | --- | --- |\n"
        for e in entries:
            if e["id"] not in exports["cases"] or exports["cases"][e["id"]].get("status")!="EXPORTED":raise RuntimeError("Incomplete export "+e["id"])
            text+="| "+e["label"]+" | "+" | ".join(native(e["id"],k,base) for k in ["liquid","inlet-liquid","vertical-vectors","inlet-vectors"])+" |\n"
        return text
    def trajectory(family,base):
        text=""
        for id,r in tracks["cases"].items():
            if r["source"]["family"]!=family:continue
            text+=f"**{r['source']['label']} — inlet stream 0:**\n\n"
            text+="| 7.07 µm | 34.64 µm | 89.44 µm |\n| --- | --- | --- |\n| "+" | ".join(img(r["images"][k]["path"],base,id+" stream 0 "+k) for k in ["07","35","89"])+" |\n\n"
        return text+"Each row shows three deterministic illustrative paths, not a statistical sample. Native zone outlines provide vessel/inlet/outlet context; path colour represents diameter on the shared 5–100 µm range. The line endpoint alone is not a fate classification. The saved tracking controls were retained; no carrier iterations or source-case saves were issued. Diameter-resolved fate plots, rather than these selected paths, describe the full tracked ensemble.\n" if text else "No native trajectory export is available; the saved ensemble fate reports remain the particle evidence.\n"
    common=(f"Spatial images are native Fluent 2025 R2 exports from verified case/data pairs. The vertical cut is `z = 0`; the horizontal cut is `y = 2.065999985 m`, the midpoint of the measured steam-inlet elevation bounds. Vertical axis is `y`. Liquid volume fraction uses `0–1`; mixture velocity colours use `{ranges['velocity-magnitude'][0]:g}–{ranges['velocity-magnitude'][1]:g} m/s`. Bulk slice vectors are in-plane, fixed-length, use shared scale `0.1`, and show every available vector (`skip = 0`). They show projected direction; colour represents full mixture speed. Pressure contours use a shared gauge-pressure range `{ranges['pressure'][0]/1000:g}–{ranges['pressure'][1]/1000:g} kPa`.\n\n")
    def write_family(family,text):
        text=reportize_family(family,text)
        p=PHASE/DIRS[family]/"results.md"
        old=p.read_text(encoding='utf-8')
        marker="## Retained detailed execution evidence"
        if marker in old:
            old=old.split(marker,1)[1].split("<summary>Earlier receipts, numerical assessments and setup detail</summary>\n\n",1)[1].rsplit("\n</details>",1)[0]
            if old.startswith('Earlier pass/fail terminology below'):old=old.split('\n\n',1)[1]
        text+="\n## Figure provenance and claim limits\n\n"+common+"Evidence: "+ref(p.parent)+"\n\nPhase 8 reconstructs the simulation storyline. Numerical shortcomings are observations and interpretation limits, not progression gates. Steady native iterations are not physical time; inventory slopes must not be called physical storage rates. No new flow solves were performed for these results.\n\n"
        text+="## Retained detailed execution evidence\n\n<details>\n<summary>Earlier receipts, numerical assessments and setup detail</summary>\n\nEarlier pass/fail terminology below records the previous numerical screening rule. It is superseded as a Phase 8 progression/completion requirement by the [2026-09-30 clarification](../CONTEXT.md).\n\n"+old+"\n</details>\n"
        p.write_text(embedded_images(text,p.parent),encoding="utf-8")
    def reportize_family(family,text):
        """Keep the main argument readable while retaining the complete native atlas."""
        # The atlas remains available without interrupting the finding-led report.
        atlas=re.search(r'\| Saved snapshot \|.*?(?=\n\n)',text,re.S)
        appendix=""
        if atlas:
            appendix="\n## Supporting spatial atlas\n\n<details>\n<summary>All saved case contours and vectors</summary>\n\n"+atlas.group()+"\n\nColumns show separate native liquid contours and mixture-vector views. Shared planes, scales and source identities are specified below. SIMPLE and continuation snapshots have their own horizons and are not substitutes for matched pilot controls.\n\n</details>\n"
            reference={"F1":"F1-26.81-n10000","F2":"F2-26.81-n10000","F3":"F3-26.81-2p5-n11000","F4":"F4-26.81-5-n11000"}[family]
            base=PHASE/DIRS[family]
            selected="| Reference snapshot | Vertical liquid distribution | Inlet-plane circulation |\n| --- | --- | --- |\n| "+reference+" | "+native(reference,"liquid",base)+" | "+native(reference,"inlet-vectors",base)+" |"
            text=text[:atlas.start()]+selected+text[atlas.end():]
        if family in ["F1","F2"]:
            mixed=family=="F1"
            text=text.replace("## Speed response","## Higher speed changes inventory and pressure, with little change in outlet routing")
            before=("Across 20.11–32.14 m/s, F1's outlet fraction stays within 99.65–99.73%, but its final liquid inventory rises from 1,021.5 to 1,629.6 kg, an increase of about 60%. The inlet-to-outlet pressure difference rises from 43.29 to 100.88 kPa. Thus, the speed sweep changes the internal state and pressure requirement much more than the fraction of liquid reaching the steam outlet.\n\n" if mixed else "Across 20.11–32.14 m/s, F2's outlet fraction stays within 99.38–99.43%. Its inventory first decreases slightly and then rises to 1,911.1 kg; the pressure difference increases from 45.67 to 102.26 kPa. The inventory response is therefore not monotonic across the whole sweep, although pressure rises at every speed. Compared with F1, the split inlet retains more liquid at all five matched endpoints.\n\n")
            text=text.replace(f"![{family} speed response]",before+f"![{family} speed response]",1)
            text=text.replace("(figures/speed-response.png)",f"(figures/speed-response.png)\n\n*Figure {family}.1. Five independent {family} Coupled carriers at N10,000. Outlet routing and pressure use each final-500 window; inventory is the saved endpoint. Increasing speed raises pressure, while outlet routing remains above 99%.*",1)
            text=text.replace("(figures/routing-inventory-history.png)",f"(figures/routing-inventory-history.png)\n\n*Figure {family}.2. Routing and inventory histories of the same five carriers. The histories locate each endpoint within its numerical development; the horizontal axis is steady iteration, not physical time.*",1)
            text=text.replace("## Liquid distribution and flow structure","## Retained liquid occupies the lower region and outer wall")
            text=text.replace("## Spatial observations\n\n",f"*Figure {family}.3. Reference-speed {family} carrier at N10,000, with a separate gauge-pressure view above. The centre cut identifies lower-region and wall enrichment; inlet-plane vectors show circumferential circulation. These local views support the inventory interpretation without measuring removal.*\n\n")
            text=text.replace("## One-way droplet response","## Diagnostic droplets reveal unresolved transport rather than a complete separation result")
            observation=("F1's unresolved injection-weighted fraction rises from 59.93% at 20.11 m/s to 82.75% at 32.14 m/s. The apparent decline in completed fates with speed must therefore be read alongside a growing unresolved category.\n\n" if mixed else "F2 retains 74.30–80.76% unresolved injection weight, without a monotonic trend across the speeds. At 26.81 m/s, 80.76% is unresolved, compared with 77.30% in F1. This small cross-family difference does not establish a droplet-separation ranking.\n\n")
            text=text.replace(f"![{family} seven-bin fates",observation+f"![{family} seven-bin fates",1)
            text=text.replace("(figures/droplet-bin-fates.png)",f"(figures/droplet-bin-fates.png)\n\n*Figure {family}.4. Saved one-way diagnostic tracking on the five N10,000 carriers, using the common seven-bin injection distribution. The orange category retains incomplete trajectories in each bin; it is not assigned to capture or escape.*",1)
            text=text.replace("(figures/droplet-speed-response.png)",f"(figures/droplet-speed-response.png)\n\n*Figure {family}.5. Injection-weighted aggregate fates and per-bin incomplete fractions from the same diagnostic records. Aggregate weights and trajectory counts answer different questions.*",1)
            conclusion=("F1 supplies the mixed-feed reference: more speed produces more retained liquid and a larger pressure difference, without resolving the high steam-outlet liquid routing. This motivates comparing the inlet representation in F2 and following droplets separately in F3." if mixed else "F2 supplies the split-inlet stage: the internal liquid state differs from F1, but almost all Eulerian liquid still reaches the steam outlet. Separating the inlet phases alone does not establish a satisfactory removal path in the closed-bottom model; F3 adds explicit droplet transport and feedback to investigate another part of that history.")
            closing=(" The five-speed SIMPLE reconstruction is reported separately from the selected Coupled adaptation: it exposes large mixture-boundary gaps and inventory drift, so its outlet ratios and diagnostic DPM fates cannot be read as separation performance. Its connection to historical 08b is numerical-method lineage, not exact topology or mesh parity." if mixed else " The five-speed SIMPLE snapshots preserve an earlier method branch; the quantitative F2 sweep remains the declared Coupled adaptation.")
            text+="\n## What this stage establishes\n\n"+conclusion+closing+"\n"
        elif family=="F3":
            text=text.replace("## Matched pilot comparisons","## Allocating more liquid to DPM changes the bulk response")
            text=text.replace("(figures/pilot-speed-response.png)","(figures/pilot-speed-response.png)\n\n*Figure F3.1. Four same-protocol 2.5% pilots, each continued from its own same-speed F2 N10,000 carrier to N11,000. The responses contain overshoot and continued evolution; endpoints are bounded pilot observations.*",1)
            text=text.replace("![F3 matched loading pilots]","At 26.81 m/s, the 5% pilot loses more Eulerian inventory over the same 1,000 iterations than the 2.5% pilot and ends with a lower Eulerian outlet fraction. Figure F3.2 shows that this difference develops through an oscillatory adjustment after allocation/coupling begins.\n\n![F3 matched loading pilots]",1)
            text=text.replace("(figures/pilot-loading-response.png)","(figures/pilot-loading-response.png)\n\n*Figure F3.2. Matched 26.81 m/s, 2.5% and 5% pilots, N10,000–11,000. Outlet percentages use unchanged total liquid feed, whereas the numerator and inventory represent Eulerian liquid only. The comparison combines allocation and feedback.*",1)
            text=text.replace("## Spatial response","## The broad liquid structure persists through the pilot change")
            text=text.replace("## Diameter-resolved particle response","## Intermediate droplets dominate the unresolved tracking problem")
            text=text.replace("![F3 pilot droplet fates]","The 14, 24 and 35 µm bins remain almost entirely incomplete in the pilot fate plots. At the reference 2.5% point, the 89 µm trajectories are trapped while the smallest bin has both escaped and trapped trajectories. The response therefore depends strongly on diameter, and the completed smallest/largest bins cannot represent the unresolved middle of the distribution.\n\n![F3 pilot droplet fates]",1)
            text=text.replace("(figures/pilot-droplet-fates.png)","(figures/pilot-droplet-fates.png)\n\n*Figure F3.3. Seven-bin trajectory-count fates from the five N11,000 pilot tracking records. These per-bin percentages differ from the mass-weighted allocated-feed percentages in the table. Large unresolved middle bins prevent a complete carryover conclusion.*",1)
            text=text.replace("(figures/tracking-cap-sensitivity.png)","(figures/tracking-cap-sensitivity.png)\n\n*Figure F3.4. Fixed-carrier tracking probes at 26.81 m/s N25,000 and 32.14 m/s N15,000. The cap changes within each panel; carrier horizon differs across panels. More tracking resolves some trajectories but leaves most represented feed incomplete.*",1)
            text+="\n## What this stage establishes\n\nF3 recreates the transition from diagnostic paths to mass-carrying coupled droplets. Both liquid allocation and feedback affect the carrier, while unresolved intermediate-size trajectories remain the main particle-evidence limit. The next historical step, F4, adds a wall-film representation to examine attachment and wall transport; F3 does not establish the missing fates as captured liquid.\n"
        else:
            text=text.replace("## Matched mechanism comparison","## The film package produces a large bulk-routing change")
            text=text.replace("(figures/f3-f4-mechanism-response.png)","(figures/f3-f4-mechanism-response.png)\n\n*Figure F4.1. Matched 26.81 m/s, 5% F3/F4 pilots from N10,000 to N11,000. F4 adds the provisional wall-film package. Its lower Eulerian outlet flow accompanies a falling bulk inventory and a large open boundary gap.*",1)
            text=text.replace("## Film formation and transport","## Film forms locally, but drainage is not established")
            text=text.replace("(figures/film-response.png)","(figures/film-response.png)\n\n*Figure F4.2. Native film reports from the F4 pilot. Film mass continues to increase to 1.321 kg; stripped and film-outflow totals reach 0.1876 and 0.00546 kg. Film formation is measurable, but the endpoint is not a stationary film balance.*",1)
            text=text.replace("The wall-surface thickness view shows where the retained film is located; this is a 3D wall view, not a centre-plane bulk-liquid contour.","*Figure F4.3. F4 N11,000 wall-film thickness on the 3D wall, shared range 0–0.2 mm. Film concentrates near inlet height, rather than covering the wall uniformly.*")
            text=text.replace("Film arrows use a temporary Fluent vector", "*Figure F4.4. F4 N11,000 native film-velocity vectors on the 3D wall, speed range 0–87 m/s. Circumferential transport is visible; arrows alone do not establish downward liquid removal.*\n\nFilm arrows use a temporary Fluent vector",1)
            text=text.replace("## Spatial observations\n\n", "The bulk and wall views must be interpreted together. ")
            text+="\n## What this stage establishes\n\nF4 recreates a film-forming wall treatment and a strong change in the represented bulk liquid state. The film/outflow reports and incomplete transfer accounting do not establish where the missing bulk throughput went. This stage therefore explains why later liquid-removal architecture and wall-treatment investigations were necessary, without claiming that the provisional film package solves separation.\n"
        return text+appendix
    def phase_report():
        comparison_path=ROOT/"PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/summary.json"
        simple_section=""
        def plot(family,name,alt):
            base=PHASE if family is None else PHASE/DIRS[family]
            return img(base/"figures"/(name+".png"),PHASE,alt)
        def pair(left,right,kind):
            return "| "+left+" | "+right+" |\n| --- | --- |\n| "+native(left,kind,PHASE)+" | "+native(right,kind,PHASE)+" |"
        if comparison_path.exists():
            comp=json.loads(comparison_path.read_text(encoding="utf-8"))
            table="| Speed (m/s) | Steam-outlet liquid / feed, Coupled → SIMPLE (%) | Final liquid inventory, Coupled → SIMPLE (kg) | Pressure difference, Coupled → SIMPLE (kPa) |\n| ---: | ---: | ---: | ---: |\n"
            for row in comp["runs"]:
                c=row["coupled_match"];s=row["last_window_mean"]
                table+=f"| {row['speed_m_s']:.2f} | {c['steam_outlet_liquid_feed_percent']:.3f} → {s['steam_outlet_liquid_feed_percent']:.3f} | {c['liquid_inventory_kg']:.1f} → {s['liquid_inventory_kg']:.1f} | {c['steam_face_to_outlet_pressure_drop_kpa']:.2f} → {s['steam_face_to_outlet_pressure_drop_kpa']:.2f} |\n"
            diagnostics="| Speed (m/s) | SIMPLE mixture boundary gap (% feed) | SIMPLE inventory slope (kg/iteration) | SIMPLE max continuity residual | Reverse-flow messages | Viscosity-limit messages |\n| ---: | ---: | ---: | ---: | ---: | ---: |\n"
            for row in comp["runs"]:
                s=row["last_window_mean"];e=row["events"]
                diagnostics+=f"| {row['speed_m_s']:.2f} | {s['absolute_mixture_boundary_gap_feed_percent']:.2f} | {s['inventory_slope_kg_per_steady_iteration']:.3f} | {s['continuity_residual_min_mean_max'][2]:.3f} | {e['reverse_flow_messages']} | {e['viscosity_limit_messages']} |\n"
            section="## Finding 1a — the F1 numerical package changes the matched carrier response\n\n"+img(ROOT/"PyAnsys"/comp["figure"],PHASE,"F1 SIMPLE versus Coupled at matched speeds")+"\n\n"+table+"\nSIMPLE numerical diagnostics, measured over N9,500–10,000:\n\n"+diagnostics+"\nThe F1 two-face feed, mesh and bounded horizon are matched. SIMPLE uses segregated pseudo-time off and second-order k; the Coupled recovery package uses Global Time Step and first-order k. Changes therefore belong to a package comparison and cannot be attributed to the pressure-coupling algorithm alone. The diagnostic thresholds describe numerical limitations; they are not Phase 8 progression gates.\n\n"
            simple_id="F1-26.81-simple-n10000"
            if simple_id in exports["cases"] and exports["cases"][simple_id].get("status")=="EXPORTED":
                section+="Reference-speed native liquid contours and inlet vectors at matched N10,000 endpoints:\n\n| SIMPLE package | Coupled recovery package |\n| --- | --- |\n| "+native(simple_id,"liquid",PHASE)+" | "+native("F1-26.81-n10000","liquid",PHASE)+" |\n| "+native(simple_id,"inlet-vectors",PHASE)+" | "+native("F1-26.81-n10000","inlet-vectors",PHASE)+" |\n\n"
            section+="Historical [08b setup](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md) and [results](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/results.md) document split `liquidinlet`/`steaminlet` mass-flow boundaries on a 7,601,261-cell mesh and a 58.73% whole-mixture imbalance ratio at N5,000. F1 applies mixed feed to both inlet faces on the 60,964-cell Phase 8 mesh. Although F1 SIMPLE shares the audited 00a SIMPLE, second-order and QUICK method family, it is not a topology- or mesh-identical 08b recreation.\n\n"
            section+=simple_dpm_section(PHASE)
            simple_section=section
        return f"""# Phase 8 results — reconstructing the model-development storyline

Phase 8 reconstructs how successive modelling choices changed the simulated liquid behaviour on the common 60,964-cell simplified geometry. The runs reproduce three parts of that history: mixed versus split inlet feed, allocated coupled droplets, and a provisional wall-film treatment. **The purpose is to explain the simulation history leading to the current model. Closing mass imbalance and reducing continuity are supporting diagnostics, not Phase 8 completion objectives.**

The main finding is that each added representation changes what can be observed. Splitting the inlet changes retained liquid without materially resolving steam-outlet routing. Coupled DPM reveals diameter-dependent transport but leaves most represented droplet feed unresolved. EWF produces measurable film and a large bulk-response change, while its available accounting remains insufficient to explain that change as liquid removal. These findings provide the evidence behind the progression toward later liquid-removal and wall-treatment work.

## Scope and comparison basis

These are new-mesh reconstructions, rather than the original historical simulation files or a quantitative replay of a published separator. F1/F2 revisit [Phases 1–2 inlet development](../phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md); F3 revisits [Phase 3 droplet representation](../phase-03-dpm-carryover-and-coupling/interpretation.md); F4 revisits [Phase 4 film mechanisms](../phase-04-ewf-wall-film-mechanisms/interpretation.md). The five speed points are the Phase 8 design, with 26.81 m/s as the reference.

| Comparison | What changes | Saved evidence used here |
| --- | --- | --- |
| F1 → F2 | Mixed feed on both inlet faces → pure-phase split feed | Five matched speeds; Coupled carriers at N10,000 and F1 SIMPLE comparison |
| F2 → F3 | Full Eulerian feed → allocated liquid DPM with feedback | Four 2.5% speed pilots and one 5% reference pilot at N11,000 |
| F3 → F4 | Coupled DPM → provisional E2.7-based EWF package | Matched 26.81 m/s, 5% pilots at N11,000 |

All four families retain a closed bottom and have no absorber. F1 applies the same mixed-phase condition to both original inlet faces. Its two-face SIMPLE series and Coupled recovery series now have matched N10,000 endpoints and windows; a separate merged single-inlet SIMPLE pilot remains a different setup recreation. F3/F4 comparisons change liquid allocation as well as coupling or film treatment, so the stages cannot be ranked as isolated physical improvements.

## Finding 1 — the split inlet changes retention more than outlet routing

The split inlet was introduced to represent liquid and steam entering different parts of the opening. Figure 1 tests whether that representation changes the carrier response across the common speed sweep.

{plot(None,'f1-f2-speed-comparison','Figure 1: matched F1 F2 speed response')}

*Figure 1. F1 mixed-feed and F2 split-feed Coupled carriers at five nominal speeds, each independently initialized and run to N10,000. Routing and area-weighted steam-face-to-outlet pressure difference use the final-500 window; inventory is the final saved value. The narrow outlet-axis range highlights small differences: every point remains above 99%.*

F1's final inventory rises from 1,021.5 to 1,629.6 kg with speed, whereas F2 retains 1,719–1,911 kg and has a shallow minimum at 23.46 m/s. At 26.81 m/s, F2 retains 1,734.5 kg compared with F1's 1,262.6 kg: about 472 kg, or 37%, more. The pressure difference rises with speed in both families and is slightly higher in F2 at every point. Yet the outlet fractions remain 99.65–99.73% in F1 and 99.38–99.43% in F2. The clear representation effect is on the internal state; neither carrier supplies an effective liquid-removal path in this geometry.

{pair('F1-26.81-n10000','F2-26.81-n10000','liquid')}

*Figure 2. Reference-speed vertical liquid-volume-fraction contours, N10,000, `z = 0`, common range 0–1. F2 has a deeper liquid-enriched lower region; both retain outer-wall enrichment and comparatively low liquid volume fraction in much of the central bulk.*

The contour difference supports the inventory measurement but does not quantify it: a plane samples only part of the volume. The larger retained mass is established by the domain report, rather than inferred from coloured area. Retained liquid also differs from removed liquid; the closed lower boundary limits what this redistribution can mean for separator performance.

{pair('F1-26.81-n10000','F2-26.81-n10000','inlet-vectors')}

*Figure 3. Native mixture vectors through inlet height at the same two endpoints. In-plane arrows show circumferential circulation; colour is full mixture speed, shared range 0–100 m/s. Common fixed arrow length and scale permit a direction comparison.*

Both cases retain the same broad circulation direction. The inlet split therefore modifies liquid placement within a circulating carrier instead of introducing a visibly different overall flow topology. This establishes the carrier reference for the later droplet stage.

{simple_section}

## Finding 2 — allocated DPM changes the carrier, while most droplet feed remains unresolved

F3 moves 2.5% or 5% of the total liquid feed into the common seven-bin fine-mist DPM distribution and enables feedback to the carrier. Total water feed is unchanged. The reference loading comparison begins from the same-speed F2 N10,000 basis and records the next 1,000 iterations.

{plot('F3','pilot-loading-response','Figure 4: matched F3 loading histories')}

*Figure 4. Reference-speed 2.5% and 5% F3 pilots, N10,000–11,000, with 100-iteration retracking and held sources. The outlet numerator is Eulerian liquid only, divided by total liquid feed including allocated DPM. Inventory is also Eulerian liquid only; these are not total carryover percentages.*

The 5% pilot exhibits a larger decrease in Eulerian inventory and ends at 1,676.3 kg, compared with 1,715.8 kg at 2.5%. Terminal Eulerian outlet fractions are 94.04% and 96.97%, respectively. Their histories contain overshoot and continued adjustment, so these endpoints describe the bounded pilot response. A lower bulk outlet percentage partly reflects moving liquid out of the Eulerian representation and cannot by itself demonstrate better separation. The [F3 report](f3-coupled-dpm/results.md) also shows that the broad lower-liquid and outer-wall structure persists in the native pilot contours.

{plot('F3','pilot-droplet-fates','Figure 5: F3 diameter-resolved pilot fates')}

*Figure 5. Saved seven-bin trajectory-count fates for the four 2.5% speed pilots and the 5% reference pilot at N11,000. Green is trapped, blue escaped and orange incomplete. Per-bin trajectory fractions are distinct from the injection-weighted represented-feed fractions quoted below.*

The 14, 24 and 35 µm bins are almost entirely incomplete, while the smallest and largest bins have more completed fates. At the reference 2.5% pilot, the 89 µm trajectories are trapped, but the smallest bin includes escape as well as trapping. This is evidence of diameter-dependent transport, with a large missing middle of the distribution. The injection-weighted unresolved fractions are 79.31% at 2.5% and 78.98% at 5%; roughly 79% of represented DPM feed therefore remains unclassified at both reference pilots.

Across the four 2.5% speed pilots, unresolved represented feed increases from 67.32% at 20.11 m/s to 86.16% at 32.14 m/s, while the trapped fraction falls from 31.18% to 12.11%. That trend describes the recorded fate categories under the chosen controls. It does not establish that faster flow physically reduces capture, because unresolved mass dominates and may change the final allocation. Native trajectory examples in the family report illustrate circulation but do not substitute for these ensemble statistics.

The earlier continuation campaign also exposed a tracking-limit effect. On fixed averaged-source carriers, increasing the cap from 50,000 to 200,000 steps reduced unresolved feed from 82.01% to 73.55% at 26.81 m/s and from 83.40% to 78.27% at 32.14 m/s. Their horizons differ, so they are sensitivity probes rather than matched speed pilots. F3 consequently establishes explicit droplet transport and feedback in the storyline, with incomplete tracking retained as a finding rather than hidden inside an efficiency estimate.

## Finding 3 — EWF forms film and changes bulk routing, but does not explain liquid removal

F4 adds the provisional E2.7-based film package on `wall` to the 26.81 m/s, 5% coupled-droplet setup. The bottom remains excluded and the absorber remains off. Figure 6 compares the same N10,000–11,000 pilot interval with F3.

{plot('F4','f3-f4-mechanism-response','Figure 6: matched F3 F4 mechanism histories')}

*Figure 6. Reference-speed 5% F3 and provisional F4 pilot histories. F4 shows much lower Eulerian outlet flow and inventory, accompanied by a large open Eulerian boundary gap. This is a film-package response, with incomplete transfer accounting.*

F4 ends with 25.541 kg/s Eulerian liquid through the steam outlet, equivalent to 21.84% of total liquid feed, and 771.42 kg bulk inventory. The final-500 Eulerian boundary gap averages 80.761 kg/s. The magnitude of the outlet change is clear, but its interpretation depends on the destinations and transfers of the liquid. A low bulk outlet flux alone cannot establish capture or drainage.

{pair('F3-26.81-5-n11000','F4-26.81-5-n11000','liquid')}

*Figure 7. Matched 5% F3/F4 vertical bulk-liquid contours at N11,000, common range 0–1. F4 retains a liquid-enriched lower region but has a weaker wall-adjacent band above it. This spatial change agrees with the lower reported bulk inventory.*

{plot('F4','film-response','Figure 8: F4 film formation histories')}

*Figure 8. Native F4 film inventory, maximum thickness, cumulative stripped mass and cumulative film outflow over N10,000–11,000. Film inventory continues to rise to 1.321 kg; maximum thickness reaches approximately 0.165 mm. Cumulative quantities are masses, not rates.*

The film is measurable, but it has not reached a stationary inventory at the saved endpoint. Cumulative stripping is 0.1876 kg and film outflow is 0.00546 kg. Those inventories and accumulated masses cannot close a missing mass-flow ledger without compatible transfer-rate accounting. The native film DPM mass-source report was unavailable, and F4 lacks a directly comparable complete particle fate ledger.

| Wall-film thickness | Wall-film velocity |
| --- | --- |
| {native('F4-26.81-5-n11000','film-thickness',PHASE)} | {native('F4-26.81-5-n11000','film-vectors',PHASE)} |

*Figure 9. F4 N11,000 native 3D wall-film views. Thickness uses 0–0.2 mm; film-speed colour uses 0–87 m/s, with vectors assembled from all three recorded film-velocity components. Film concentrates near inlet height and substantial circumferential motion remains visible.*

These fields show film formation and wall transport, without establishing downward drainage. The supported result is that the provisional film treatment changes the represented liquid state strongly. Its accounting limits remain part of the reconstruction and prevent translating the bulk-outlet reduction into a separation-efficiency improvement.

## How these findings lead toward the current model

{plot(None,'reference-storyline-response','Figure 10: reference-speed stage comparison')}

*Figure 10. Reference-speed stage summary: full-Eulerian F1/F2 at N10,000 and 5%-allocated F3/F4 at N11,000. Outlet and pressure bars use the final-500 mean; inventories use the endpoint. In particular, the F4 mean outlet bar differs from its 21.84% terminal value. This is a modelling-stage comparison with changing representation and horizon.*

The reconstructed sequence makes the reasons for the model changes visible. Inlet representation changes liquid distribution and retention, yet leaves high bulk outlet routing. DPM adds a separate diameter-dependent transport question and carrier feedback, while exposing unresolved particle fates. EWF adds measurable wall film but raises an unresolved liquid-accounting question. None of these stages provides a demonstrated lower liquid-removal path in the common closed-bottom geometry.

The original [full-geometry brine-outlet investigation](../phase-05-full-geometry-v2/interpretation.md) and [pool-control work](../phase-06-full-geometry-with-brine-pool/interpretation.md) then supply historical context for the return to a simplified removal architecture; they cannot be recreated on this truncated geometry. The later [Phase 7.1A virtual outlet](../phase-07-1a-absorber-convergence/interpretation.md) and [Phase 7.2A wall-treatment investigation](../phase-07-2a-wall-liquid-routing/interpretation.md) own the evidence for those developments. Phase 8 explains this progression without claiming that an absorber-equipped comparison has already been run.

## Coverage and limits of the report

Saved evidence covers 16 of the intended 60 core points: five F1, five F2, five F3 and one provisional F4. Additional SIMPLE, numerical-continuation and tracking-probe snapshots preserve parts of the investigation without increasing core-matrix coverage. Most F3/F4 loading combinations remain absent. The report therefore supports the demonstrated stage contrasts, rather than a complete response surface or an optimum setup.

Steady native iterations do not define physical elapsed time; inventory slopes are not physical storage rates. The common closed-bottom geometry, assumed fine-mist distribution, incomplete DPM fates and provisional film basis bound the conclusions. Mass balance and continuity histories remain in the family reports to make those limits inspectable. They do not determine whether an unresolved stage belongs in the history.

## Supporting family reports and provenance

- [F1 mixed-feed results](f1-one-inlet/results.md): speed response, liquid distribution, diagnostic droplets and separate SIMPLE snapshots.
- [F2 split-feed results](f2-split-inlet/results.md): matched speed response, retention and diagnostic droplet evidence.
- [F3 coupled-droplet results](f3-coupled-dpm/results.md): speed/loading pilots, diameter-resolved fates and numerical/tracking sensitivity.
- [F4 wall-film results](f4-coupled-dpm-ewf/results.md): matched bulk response, film formation and open accounting.

{common}Machine evidence: {ref(PHASE)}

The family reports retain complete spatial atlases and earlier execution receipts in supporting sections. All figures derive from preserved saved evidence, with verified source hashes and no new carrier iterations or case/data overwrites. The experimental loop remains paused.
"""
    for family in ["F1","F2"]:
        base=PHASE/DIRS[family];rows=families[family];fates=families[family+"_fates"]
        mixed=family=="F1"
        answer=("The mixed-feed Coupled sweep has almost unchanged high liquid routing to the steam outlet across speed, while retained liquid mass and pressure difference increase. This supplies the mixed-inlet stage of the storyline, including its closed-bottom limitation." if mixed else "Splitting the inlet phases changes retained liquid mass and the inlet flow representation, but the Coupled sweep still routes almost all Eulerian liquid to the steam outlet. It supplies the next historical stage rather than demonstrating successful separation.")
        text=f"# Phase 8 {family} — {'mixed feed' if mixed else 'split feed'} results\n\n{answer}\n\n"
        text+="## Comparison basis\n\nFive nominal speeds on the same 60,964-cell partition, full Eulerian liquid feed, closed bottom, absorber/EWF off, and matched Coupled/Global Time Step/first-order-k numerics. Each speed starts with fresh Hybrid initialization and reaches N10,000. Routing and pressure summaries use N9,500–10,000; inventories are final snapshots. These Coupled cases are numerical adaptations of the SIMPLE recreation.\n\n"
        if mixed:text+="The main sweep assigns mixed-phase feed to both original inlet faces. The separately recreated merged single-inlet SIMPLE case is shown below and must not be conflated with this two-face sweep.\n\n"
        text+="## Speed response\n\n"+img(base/"figures/speed-response.png",base,family+" speed response")+"\n\n"
        text+="| Speed (m/s) | Outlet liquid / feed, last-500 mean (%) | Final liquid inventory (kg) | Steam-face–outlet pressure difference (kPa) | Unresolved diagnostic DPM weight (%) |\n| ---: | ---: | ---: | ---: | ---: |\n"
        for row,fr in zip(rows,fates):text+=f"| {row['speed']:.2f} | {row['out_pct']:.3f} | {row['inventory']:.1f} | {row['pressure_kpa']:.2f} | {100*fr['weighted']['incomplete']:.2f} |\n"
        text+="\n"+img(base/"figures/routing-inventory-history.png",base,family+" routing and inventory histories")+"\n\nThe raw histories distinguish the evolving carrier from its final checkpoint. Inventory is Eulerian liquid mass, not removed liquid. The pressure metric uses the recorded area-weighted `steaminlet` and `steamoutlet` reports; it is not a mass-weighted pressure loss.\n\n"
        text+="## Liquid distribution and flow structure\n\n"+gallery(family,base)+"\nThe centre cut and inlet slice answer different questions: the first shows vertical liquid distribution; the second retains the offset inlet and shows circumferential flow. Compare speed cases within the same numerical branch and horizon. The SIMPLE snapshots document an earlier stage and are not matched N10,000 speed controls.\n\n"
        reference=family+"-26.81-n10000"
        text+="Reference-speed gauge pressure:\n\n"+native(reference,"pressure",base)+"\n\n"
        text+="## One-way droplet response\n\n"+img(base/"figures/droplet-speed-response.png",base,family+" droplet speed response")+"\n\nThe left plot uses injection-weighted fate fractions; the right gives the incomplete trajectory fraction in each size bin. Both retain incomplete tracks. Diagnostic parcel weights do not add physical inlet mass to these full-Eulerian-feed carriers. High unresolved fractions prevent converting escaped weight into separator efficiency.\n\n"+trajectory(family,base)
        text+="\n## Numerical context\n\n"+img(base/"figures/numerical-context.png",base,family+" numerical context")+"\n\nThe reported boundary gap and continuity are supporting diagnostics. Reverse outlet flow and viscosity limiting were recorded in these runs; a low residual or bounded inventory does not validate the closed-bottom separator. See the [phase result](../results.md) for the matched F1/F2 comparison.\n"
        text=text.replace("## One-way droplet response", "## Spatial observations\n\n"+("The mixed-feed centre cuts retain liquid enrichment at the bottom and along the outer walls. The wall band becomes more pronounced at the higher speeds, consistent with the increasing domain inventory. Most of the central annular bulk remains at low liquid volume fraction on the shared 0–1 scale. The inlet-plane arrows turn around the central exclusion and show circulation rather than a direct inlet-to-outlet path. These are local field observations, not a liquid removal measurement.\n\n" if mixed else "The split-feed centre cut has a deeper liquid-enriched lower region than the mixed-feed reference at 26.81 m/s, consistent with its larger inventory. Both show an outer-wall liquid band and low-volume-fraction central bulk; the inlet slice shows enrichment around the outer circumference and a locally stronger band near the inlet junction. The inlet-plane vectors retain the same circulation direction. Use the inventory report to quantify the difference; a centre-plane colour footprint alone does not measure the 3D liquid mass.\n\n")+"## One-way droplet response")
        text=text.replace("## One-way droplet response\n\n", "## One-way droplet response\n\n"+img(base/"figures/droplet-bin-fates.png",base,family+" seven-bin fates at every speed")+"\n\n")
        if mixed:
            comparison_path=ROOT/"PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/summary.json"
            if comparison_path.exists():
                comp=json.loads(comparison_path.read_text(encoding="utf-8"))
                simple_figure=img(ROOT/"PyAnsys"/comp["figure"],base,"F1 SIMPLE versus Coupled carrier comparison")
                table="| Speed (m/s) | Steam-outlet liquid / feed, Coupled → SIMPLE (%) | Final liquid inventory, Coupled → SIMPLE (kg) | Pressure difference, Coupled → SIMPLE (kPa) |\n| ---: | ---: | ---: | ---: |\n"
                for row in comp["runs"]:
                    c=row["coupled_match"];s=row["last_window_mean"]
                    table+=f"| {row['speed_m_s']:.2f} | {c['steam_outlet_liquid_feed_percent']:.3f} → {s['steam_outlet_liquid_feed_percent']:.3f} | {c['liquid_inventory_kg']:.1f} → {s['liquid_inventory_kg']:.1f} | {c['steam_face_to_outlet_pressure_drop_kpa']:.2f} → {s['steam_face_to_outlet_pressure_drop_kpa']:.2f} |\n"
                diagnostics="| Speed (m/s) | SIMPLE mixture boundary gap (% feed) | SIMPLE inventory slope (kg/iteration) | SIMPLE max continuity residual | Reverse-flow messages | Viscosity-limit messages |\n| ---: | ---: | ---: | ---: | ---: | ---: |\n"
                for row in comp["runs"]:
                    s=row["last_window_mean"];e=row["events"]
                    diagnostics+=f"| {row['speed_m_s']:.2f} | {s['absolute_mixture_boundary_gap_feed_percent']:.2f} | {s['inventory_slope_kg_per_steady_iteration']:.3f} | {s['continuity_residual_min_mean_max'][2]:.3f} | {e['reverse_flow_messages']} | {e['viscosity_limit_messages']} |\n"
                text+="\n## SIMPLE versus Coupled: matched outcomes, different numerical packages\n\n"+simple_figure+"\n\n"+table+"\nSIMPLE numerical diagnostics over N9,500–10,000:\n\n"+diagnostics+"\nBoth series use the same two-face F1 topology, five total-feed targets, 60,964-cell mesh and fresh initialized parent, with N10,000 endpoints and N9,500–10,000 response windows. The SIMPLE branch uses segregated pseudo-time off and second-order `k`; the comparison branch uses Coupled/Global Time Step and first-order `k`. This is a numerical-package comparison. It does not isolate the pressure-coupling algorithm from the discretization and time-stepping changes. These diagnostics describe numerical limitations; they are not Phase 8 progression gates.\n\n"
                simple_id="F1-26.81-simple-n10000"
                if simple_id in exports["cases"] and exports["cases"][simple_id].get("status")=="EXPORTED":
                    text+="Reference-speed native liquid contours and inlet vectors at the same N10,000 horizon:\n\n| SIMPLE package | Coupled recovery package |\n| --- | --- |\n| "+native(simple_id,"liquid",base)+" | "+native("F1-26.81-n10000","liquid",base)+" |\n| "+native(simple_id,"inlet-vectors",base)+" | "+native("F1-26.81-n10000","inlet-vectors",base)+" |\n\n"
                text+="Historical [08b setup](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md) and [results](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/results.md) remain separate comparison anchors: the documented run used split `liquidinlet`/`steaminlet` mass-flow boundaries on 7,601,261 cells and its N5,000 carrier report showed a 58.73% mixture imbalance ratio. F1 SIMPLE shares the audited 00a SIMPLE/second-order/QUICK numerical-method family, but F1 applies mixed-phase feed to both inlet faces on 60,964 cells. SIMPLE alone therefore does not make this a topology-, mesh-, or result-identical 08b replication.\n"
                text+=simple_dpm_section(base)
        write_family(family,text)
    base=PHASE/DIRS["F3"]
    text="# Phase 8 F3 — allocated two-way droplets\n\nF3 changes both the liquid representation and carrier feedback: a stated part of the total liquid feed is moved from Eulerian liquid to coupled DPM. The matched pilots show transient routing changes and strongly size-dependent unresolved fates. They extend the storyline even when numerical diagnostics are poor.\n\n## Matched pilot comparisons\n\nThe speed comparison uses four 2.5% pilots, each from its independent same-speed F2 N10,000 parent, at N10,000–11,000 with 100-iteration retracking and held sources. The 26.81 m/s loading comparison uses the same 2.5% and 5% protocol. 29.48 m/s and the larger selected loading fractions have not been run in this series.\n\n"
    text+=img(base/"figures/pilot-speed-response.png",base,"F3 matched speed pilots")+"\n\n"+img(base/"figures/pilot-loading-response.png",base,"F3 matched loading pilots")+"\n\n"
    text+="| Speed (m/s) | Allocated DPM (%) | N11,000 Eulerian outlet liquid / total liquid feed (%) | Eulerian inventory (kg) | DPM escaped (% of allocated feed) | DPM trapped (%) | DPM unresolved (%) |\n| ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n"
    for r in families["F3"]:text+=f"| {r['speed']:.2f} | {r['fraction']*100:g} | {r['out_pct']:.3f} | {r['inventory']:.1f} | {r['fates']['escaped']*100:.2f} | {r['fates']['trapped']*100:.2f} | {r['fates']['incomplete']*100:.2f} |\n"
    text+="\nThe outlet numerator is Eulerian liquid only, while the denominator is the unchanged total liquid feed, including allocated DPM. A lower value than F2 therefore partly reflects the representation change; it is not the total liquid carryover. At 26.81 m/s the 2.5% and 5% pilots end at 96.97% and 94.04%, respectively, with 79.31% and 78.98% of DPM feed unresolved.\n\n## Spatial response\n\n"+gallery("F3",base)+"\nCompare the N11,000 pilots first. Averaged-source snapshots at N25,000 and N15,000 are distinct numerical adaptations at unequal development horizons.\n\n## Diameter-resolved particle response\n\n"+img(base/"figures/pilot-droplet-fates.png",base,"F3 pilot droplet fates")+"\n\n"+trajectory("F3",base)
    text+="\n## Numerical adaptation and tracking sensitivity\n\n"+img(base/"figures/source-averaging-context.png",base,"F3 source averaging at unequal horizons")+"\n\n"+img(base/"figures/additional-continuation-context.png",base,"F3 low-speed and 5% continuations")+"\n\nThe earlier continuation campaign investigated source cadence, relaxation, linearization and averaging. These results document that investigation; they do not redefine Phase 8 as a convergence campaign. The final original and averaged-source segments are shown at their actual coordinates, with intervening segments available in the retained receipts.\n\n"+img(base/"figures/tracking-cap-sensitivity.png",base,"F3 tracking cap sensitivity")+"\n\nIncreasing the tracking cap from 50,000 to 200,000 steps reduced unresolved represented DPM feed from 82.01% to 73.55% at 26.81 m/s and from 83.40% to 78.27% at 32.14 m/s. Each panel holds its carrier fixed; the two carriers have different horizons. The further 500,000-step 24/35 µm reference probe did not change their fate counts. These probes show sensitivity to termination limits, not completed droplet separation.\n"
    text=text.replace("Averaged-source snapshots at N25,000 and N15,000 are distinct numerical adaptations at unequal development horizons.","The 2.5% averaged-source snapshots at N20,000, N25,000 and N15,000, and the 5% held-source N20,000 snapshot, are separate numerical adaptations at unequal development horizons.")
    text+="\n## Numerical context\n\n"+img(base/"figures/numerical-context.png",base,"F3 pilot accounting and continuity context")+"\n\nThe continuity and boundary-gap histories give context for the pilot response; they do not decide whether this historical stage belongs in Phase 8.\n"
    text=text.replace("## Diameter-resolved particle response", "The reference 2.5% and 5% centre cuts retain the same broad lower-liquid and outer-wall pattern seen in F2; the loading change does not visibly replace that structure at this pilot horizon. The mixture inlet vectors still show circumferential circulation. Quantitative routing and inventory histories resolve differences that are subtle on the shared full-range contours.\n\n## Reference-speed pressure\n\n| 2.5% pilot | 5% pilot |\n| --- | --- |\n| "+native('F3-26.81-2p5-n11000','pressure',base)+" | "+native('F3-26.81-5-n11000','pressure',base)+" |\n\n## Diameter-resolved particle response")
    write_family("F3",text)
    base=PHASE/DIRS["F4"];id="F4-26.81-5-n11000"
    text="# Phase 8 F4 — provisional wall-film addition\n\nThe provisional EWF pilot introduced measurable wall film and a strong reduction in bulk Eulerian liquid reaching the steam outlet. Bulk liquid inventory also fell substantially and the Eulerian accounting remained open. The supported storyline observation is a change in liquid/film behaviour, not a measured separation-efficiency gain.\n\n## Matched mechanism comparison\n\nF3 and F4 use 26.81 m/s, 5% allocated DPM, the same F2 carrier basis, and N10,000–11,000 pilots. F4 adds the provisional E2.7-based film package on `wall` only; the bottom remains excluded and the absorber remains off. Its cap and film numerical controls are recorded adaptations, not finalized Phase 7.2A settings.\n\n"
    text+=img(base/"figures/f3-f4-mechanism-response.png",base,"F3 F4 mechanism response")+"\n\nF4 ends with 25.541 kg/s Eulerian liquid through the steam outlet (21.84% of total liquid feed) and 771.42 kg bulk liquid inventory. The final-500 Eulerian boundary gap averages 80.761 kg/s. Film inventory is only 1.321 kg, so it cannot by itself explain the bulk accounting difference.\n\n## Bulk liquid and flow views\n\n"+gallery("F4",base)+"\nReference-speed pressure:\n\n"+native(id,"pressure",base)+"\n\n## Film formation and transport\n\n"+img(base/"figures/film-response.png",base,"F4 film histories")+"\n\nMaximum thickness reaches about 0.165 mm, well below the 0.3 m exploratory cap. Cumulative stripped mass reaches 0.1876 kg and cumulative film outflow reaches 0.00546 kg. These are masses in kg, not rates inferred from carrier iteration.\n\n"+native(id,"film-thickness",base)+"\n\nThe wall-surface thickness view shows where the retained film is located; this is a 3D wall view, not a centre-plane bulk-liquid contour.\n\n"
    r=exports["cases"][id]
    if "film-vectors" in r["images"]:text+=native(id,"film-vectors",base)+"\n\nFilm arrows use a temporary Fluent vector assembled from the recorded film-x/y/z-velocity components and use the separate film-speed range recorded in the export receipt.\n"
    else:text+="**Film-vector evidence gap:** "+str(r.get("film_vectors_gap","unavailable"))+" No bulk-mixture vector field is substituted for film velocity.\n"
    text+="\n## Interpretation limits\n\nPhase accretion, DPM collection, wall/global splash and stripping were enabled; wall Flow Momentum Coupling and film surface tension were off. A stored surface-tension coefficient does not imply an active force. The native film DPM mass-source report was unavailable, and Fluent reused an existing inlet injection as the stripping template. F4 therefore has no directly comparable complete DPM fate ledger; it is excluded from the DPM fate-percentage comparison rather than assigned zero unresolved mass. Final F3/F4 performance comparison remains provisional pending the declared EWF basis.\n"
    text+="\n## Numerical context\n\n"+img(base/"figures/numerical-context.png",base,"F3 F4 accounting and continuity context")+"\n\nThe sharp bulk-routing change coincides with a large open Eulerian boundary gap. That limits physical claims while remaining part of the reconstructed history.\n"
    text=text.replace("## Interpretation limits", "## Spatial observations\n\nThe F4 bulk centre cut still has a liquid-enriched bottom region, but the wall-adjacent band above it is weaker than in the matched F3 pilot. The wall-film thickness is concentrated in a band around the inlet-height region rather than uniformly covering the vessel. The strongest film-speed colours occupy that band; the arrows show substantial circumferential motion, so film formation alone does not demonstrate downward drainage. Film vectors use all three recorded components on the 3D wall; the common in-plane policy below applies to the bulk slice vectors.\n\n## Interpretation limits")
    write_family("F4",text)
    (PHASE/"results.md").write_text(embedded_images(phase_report(),PHASE),encoding="utf-8")
    print("Wrote four family results and phase-level results")

if __name__=="__main__":main()
