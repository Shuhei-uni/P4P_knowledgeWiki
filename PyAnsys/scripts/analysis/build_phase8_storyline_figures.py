"""Reconstruct matched Phase 8 plots and a hash-verified spatial export catalog.

Uses saved reports only; does not run Fluent or change source artifacts.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from compare_phase8_coupled_f1_f2 import chain, read_history, series

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "PyAnsys/output/phase8-storyline-20260930"
PHASE = ROOT / "Project/experiments/phase-08-storyline-reconstruction"
DIRS = {"F1":"f1-one-inlet", "F2":"f2-split-inlet", "F3":"f3-coupled-dpm", "F4":"f4-coupled-dpm-ewf"}
SPEEDS = [20.11,23.46,26.81,29.48,32.14]
COLORS = ["#31688e","#35b779","#d99b24","#9253a1","#c54843"]

def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def digest(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def save(fig, folder, name):
    folder.mkdir(parents=True,exist_ok=True)
    fig.tight_layout()
    p=folder/name
    fig.savefig(p,dpi=200,bbox_inches="tight")
    plt.close(fig)
    return str(p.relative_to(ROOT)).replace("\\","/")

def style(axes):
    for ax in np.array(axes).flat:
        ax.grid(alpha=.2)

def fate(receipt):
    track=receipt.get("particle_tracks",{})
    flows={item["name"]:float(item["state"]["initial_values"]["mass_flow_rate"]["total_flow_rate"])
           for item in track.get("injections",[])}
    sizes={item["name"]:float(item["diameter_um"]) for item in track.get("injections",[])}
    rows=[]
    for r in track.get("results",[]):
        if r.get("status")!="ok": raise RuntimeError(f"Invalid track report: {r['name']}")
        c=r["counts"]; n=int(c["tracked"])
        if n<=0 or sum(int(c[k]) for k in ["escaped","trapped","incomplete"])!=n:
            raise RuntimeError(f"Unaccounted trajectories: {r['name']}")
        rows.append({"name":r["name"],"diameter_um":sizes[r["name"]],"weight":flows[r["name"]],
                     **{k:int(c[k])/n for k in ["escaped","trapped","incomplete"]}})
    rows.sort(key=lambda x:x["diameter_um"])
    total=sum(r["weight"] for r in rows)
    return {"bins":rows,"weighted":{k:sum(r["weight"]*r[k] for r in rows)/total for k in ["escaped","trapped","incomplete"]}} if total else None

def load_run(p):
    d=read(p)
    reports={k:read_history(v) for k,v in d["report_paths"].items()}
    common=sorted(set.intersection(*(set(reports[k]) for k in ["p8-mass-phase2-total","p8-flux-phase2-steamoutlet","p8-flux-mixture-steamoutlet"])))
    x=np.array(common)
    val=lambda k:np.array([reports[k][int(i)] for i in x])
    liquid=val("p8-flux-phase2-liquidinlet")+val("p8-flux-phase2-steaminlet")
    eulerian=val("p8-flux-mixture-liquidinlet")+val("p8-flux-mixture-steaminlet")
    total_liquid=liquid/(1-float(d.get("fraction",0)))
    from assess_phase8_carrier_window import RESIDUAL
    import re
    residuals={int(i):float(v) for i,v in RESIDUAL.findall(Path(d["paths"]["transcript"]).read_text())}
    return {"manifest":d,"reports":reports,"x":x,"out":-val("p8-flux-phase2-steamoutlet")/total_liquid,
            "inventory":val("p8-mass-phase2-total"),"gap":(eulerian+val("p8-flux-mixture-steamoutlet"))/eulerian,
            "pressure":(val("p8-pressure-steaminlet")-val("p8-pressure-steamoutlet"))/1000,
            "residual_x":np.array(sorted(residuals)),"residual":np.array([residuals[i] for i in sorted(residuals)]),
            "fate":fate(d)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    catalog=[]; stats={"families":{},"plots":{},"solve_issued":False}
    manifest_paths=list((ROOT/"PyAnsys/output/phase8-carrier").glob("*/manifest.json"))+list((ROOT/"PyAnsys/output/phase8-ewf").glob("*/manifest.json"))+list((ROOT/"PyAnsys/output/phase8-single-face").glob("*/manifest.json"))
    runs={p:read(p) for p in manifest_paths}
    def add(p,id,label,family,role,tracks=False):
        d=read(p); pair=d.get("child_pair") or d["checkpoints"][-1]
        for kind in ["case","data"]:
            if digest(pair[kind])!=pair[kind+"_sha256"]: raise RuntimeError(f"Hash mismatch: {pair[kind]}")
        end=pair.get("native_iteration",pair.get("active_iteration",d.get("achieved_active_iterations")))
        entry={"id":id,"label":label,"family":family,"role":role,"source_manifest":str(p.relative_to(ROOT)).replace("\\","/"),
               "pair":pair,"iteration":end,"speed":float(d.get("speed_m_s",26.81)),"fraction":d.get("fraction",0),
               "figure_dir":str((PHASE/DIRS[family]/"figures").relative_to(ROOT)).replace("\\","/"),"tracks":tracks}
        catalog.append(entry); return entry
    selected={}
    for family in ["F1","F2"]:
        family_runs={}; summaries=[]
        for speed in SPEEDS:
            matches=[p for p,d in runs.items() if d.get("family")==family and d.get("status")=="COMPLETE" and d.get("speed_m_s")==speed and d.get("achieved_active_iterations")==10000 and "coupled-gts" in str(p)]
            if len(matches)!=1: raise RuntimeError(f"Ambiguous {family}/{speed}: {matches}")
            p=matches[0]; d=runs[p]
            parents=[p]
            while "source_manifest" in d:
                q=Path(d["source_manifest"])
                if not q.is_absolute(): q=ROOT/q
                d=read(q); parents.insert(0,q)
            c=chain(parents); x=np.arange(10,10001,10); s=series(c,x)
            family_runs[speed]=(c,s,x)
            add(p,f"{family}-{speed:g}-n10000",f"{family} {speed:g} m/s N10000",family,"speed-sweep")
            idx=x>=9500
            summaries.append({"speed":speed,"out_pct":float(np.mean(s["liquid_out_fraction"][idx])*100),"inventory":float(s["inventory_kg"][-1]),"pressure_kpa":float(np.mean(s["pressure_drop_pa"][idx])/1000),"gap_pct":float(np.mean(np.abs(s["boundary_gap_fraction"][idx]))*100)})
        stats["families"][family]=summaries
        selected[family]=family_runs
        folder=PHASE/DIRS[family]/"figures"
        fig,axs=plt.subplots(1,3,figsize=(13,4))
        for ax,key,label in zip(axs,["out_pct","inventory","pressure_kpa"],["Steam-outlet liquid / liquid feed (%)","Final liquid inventory (kg)","Steam-face to outlet pressure difference (kPa)"]):
            ax.plot(SPEEDS,[s[key] for s in summaries],"o-",color=COLORS[0 if family=="F1" else 1]);ax.set(xlabel="Nominal inlet speed (m/s)",ylabel=label)
        fig.suptitle(f"{family}: five-speed Coupled series, N10000 (routing/pressure: last 500 iterations)")
        style(axs); save(fig,folder,"speed-response.png")
        fig,axs=plt.subplots(1,2,figsize=(12,4))
        for color,(speed,(_,s,x)) in zip(COLORS,family_runs.items()):
            axs[0].plot(x,s["liquid_out_fraction"]*100,label=f"{speed:g} m/s",color=color)
            axs[1].plot(x,s["inventory_kg"],color=color)
        axs[0].legend();axs[0].set_ylabel("Steam-outlet liquid / feed (%)");axs[1].set_ylabel("Domain liquid inventory (kg)")
        for ax in axs:ax.set_xlabel("Native steady iteration")
        style(axs);save(fig,folder,"routing-inventory-history.png")
        fig,axs=plt.subplots(1,2,figsize=(12,4))
        for color,(speed,(_,s,x)) in zip(COLORS,family_runs.items()):
            axs[0].plot(x,s["boundary_gap_fraction"]*100,label=f"{speed:g} m/s",color=color)
            axs[1].semilogy(x,s["continuity"],color=color)
        axs[0].legend();axs[0].set_ylabel("Signed mixture boundary gap / feed (%)");axs[1].set_ylabel("Continuity residual")
        for ax in axs:ax.set_xlabel("Native steady iteration")
        style(axs);save(fig,folder,"numerical-context.png")
        fates=[]
        for speed in SPEEDS:
            tag=str(speed).replace(".","p")
            receipt=next((ROOT/"PyAnsys/output/phase8-analysis"/f"{tag}-{family.lower()}-diagnostic-dpm").glob("summary.json"))
            fates.append(read(receipt))
        fig,axs=plt.subplots(1,2,figsize=(12,4))
        for key,color in zip(["escaped","trapped","incomplete"],["#31688e","#35b779","#d99b24"]):
            axs[0].plot(SPEEDS,[r["weighted_fate_fraction"][key]*100 for r in fates],"o-",label=key,color=color)
        axs[0].legend();axs[0].set(xlabel="Nominal inlet speed (m/s)",ylabel="Diagnostic weight fraction (%)")
        matrix=np.array([[b["incomplete_fraction"]*100 for b in r["bins"]] for r in fates])
        im=axs[1].imshow(matrix,aspect="auto",vmin=0,vmax=100,cmap="cividis");axs[1].set_xticks(range(7),[f"{b['diameter_um']:.0f}" for b in fates[0]["bins"]]);axs[1].set_yticks(range(5),[f"{s:g}" for s in SPEEDS]);axs[1].set(xlabel="Droplet diameter (µm)",ylabel="Inlet speed (m/s)");fig.colorbar(im,ax=axs[1],label="Incomplete tracks (%)")
        style([axs[0]]);save(fig,folder,"droplet-speed-response.png")
        fig,axs=plt.subplots(2,3,figsize=(14,8),sharey=True)
        for ax,speed,r in zip(axs.flat,SPEEDS,fates):
            bottom=np.zeros(7)
            for key,color in zip(['escaped','trapped','incomplete'],['#31688e','#35b779','#d99b24']):
                a=np.array([b[key+'_fraction']*100 for b in r['bins']]);ax.bar(range(7),a,bottom=bottom,label=key,color=color);bottom+=a
            ax.set_xticks(range(7),[f"{b['diameter_um']:.0f}" for b in r['bins']]);ax.set_title(f'{speed:g} m/s');ax.set_xlabel('Diameter (µm)')
        axs[0,0].set_ylabel('Tracked trajectories (%)');axs[1,0].set_ylabel('Tracked trajectories (%)');axs[0,0].legend(fontsize=8);axs[1,2].axis('off');save(fig,folder,'droplet-bin-fates.png')
        stats["families"][family+"_fates"]=[{"speed":s,"weighted":r["weighted_fate_fraction"]} for s,r in zip(SPEEDS,fates)]
        ref=read(ROOT/f"PyAnsys/output/phase8-analysis/26p81-{family.lower()}-diagnostic-dpm/summary.json")
        add(ROOT/Path(ref["build_receipt"]),f"{family}-26.81-diagnostic",f"{family} reference one-way DPM",family,"particle-views",True)
    # Pilot comparisons deliberately keep the original held-source package and horizon.
    pilots=[]
    for speed in [20.11,23.46,26.81,32.14]:
        p=next(p for p,d in runs.items() if d.get("family")=="F3" and d.get("status")=="COMPLETE" and d.get("speed_m_s")==speed and d.get("fraction")==.025 and d.get("requested_additional_iterations")==1000 and "extension" not in str(p))
        pilots.append(load_run(p));add(p,f"F3-{speed:g}-2p5-n11000",f"F3 {speed:g} m/s 2.5% N11000","F3","speed-pilot",speed==26.81)
    p5=next(p for p,d in runs.items() if d.get("family")=="F3" and d.get("status")=="COMPLETE" and d.get("fraction")==.05 and "upd100" in str(p) and "extension" not in str(p))
    pilot5=load_run(p5);add(p5,"F3-26.81-5-n11000","F3 26.81 m/s 5% N11000","F3","loading-pilot",True)
    def histories(group,labels,folder,name,title):
        fig,axs=plt.subplots(2,2,figsize=(12,7))
        for run,label,color in zip(group,labels,COLORS):
            for ax,key in zip(axs.flat,["out","inventory","gap","pressure"]):
                ax.plot(run["x"],run[key]*(100 if key in ["out","gap"] else 1),label=label,color=color)
        for ax,y in zip(axs.flat,["Eulerian outlet liquid / total liquid feed (%)","Domain Eulerian liquid mass (kg)","Signed Eulerian boundary gap / Eulerian feed (%)","Steam-face to outlet pressure difference (kPa)"]):ax.set(xlabel="Native steady iteration",ylabel=y)
        axs[0,0].legend(fontsize=8);style(axs);fig.suptitle(title);save(fig,folder,name)
    folder=PHASE/DIRS["F3"]/"figures"
    histories(pilots,[f"{r['manifest']['speed_m_s']:g} m/s" for r in pilots],folder,"pilot-speed-response.png","F3: matched 2.5% held-source pilots, N10000–11000")
    histories([pilots[2],pilot5],["2.5%","5%"],folder,"pilot-loading-response.png","F3: loading contrast at 26.81 m/s, held sources, N10000–11000")
    fig,axs=plt.subplots(2,3,figsize=(14,8),sharey=True)
    for ax,r in zip(axs.flat,pilots+[pilot5]):
        rows=r["fate"]["bins"]; bottom=np.zeros(7)
        for key,color in zip(["escaped","trapped","incomplete"],["#31688e","#35b779","#d99b24"]):
            a=np.array([b[key] for b in rows])*100;ax.bar(range(7),a,bottom=bottom,label=key,color=color);bottom+=a
        ax.set_xticks(range(7),[f"{b['diameter_um']:.0f}" for b in rows]);ax.set_title(f"{r['manifest']['speed_m_s']:g} m/s, {r['manifest']['fraction']*100:g}%");ax.set_xlabel("Diameter (µm)")
    axs[0,0].set_ylabel("Tracked trajectories (%)");axs[1,0].set_ylabel("Tracked trajectories (%)");axs[0,0].legend(fontsize=8);axs[1,2].axis("off");save(fig,folder,"pilot-droplet-fates.png")
    continuations=[]
    for tag in ["26p81", "32p14"]:
        p=next(p for p,d in runs.items() if d.get("status")=="COMPLETE" and f"F3-{tag}-2p5pct" in str(p) and "averaged-sources" in str(p) and ("to25000" in str(p) if tag=="26p81" else "to15000" in str(p)))
        continuations.append(load_run(p));add(p,f"F3-{tag}-averaged",f"F3 {runs[p]['speed_m_s']:g} m/s 2.5% averaged N{runs[p]['checkpoints'][-1]['native_iteration']}","F3","numerical-adaptation")
    low_path=next(p for p,d in runs.items() if d.get("status")=="COMPLETE" and "F3-20p11-2p5pct" in str(p) and "averaged-sources-extension-to20000" in str(p))
    low=load_run(low_path)
    add(low_path,"F3-20p11-averaged","F3 20.11 m/s 2.5% averaged N20000","F3","numerical-adaptation")
    deep5_path=next(p for p,d in runs.items() if d.get("status")=="COMPLETE" and "F3-26p81-5pct" in str(p) and "upd100-extension-to20000" in str(p))
    deep5=load_run(deep5_path)
    add(deep5_path,"F3-26p81-5pct-n20000","F3 26.81 m/s 5% held sources N20000","F3","numerical-adaptation")
    histories([pilots[0],low,pilot5,deep5],["20.11 2.5% pilot","20.11 2.5% averaged N20000","26.81 5% pilot","26.81 5% held N20000"],folder,"additional-continuation-context.png","F3: low-speed and 5% continuations at their actual native coordinates")
    # Compare raw late histories with their true coordinates, not a manufactured common timeline.
    histories([pilots[2],continuations[0],pilots[3],continuations[1]],["26.81 pilot","26.81 averaged continuation","32.14 pilot","32.14 averaged continuation"],folder,"source-averaging-context.png","F3: numerical adaptations at unequal native horizons")
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    for ax,tag in zip(axs,["26p81","32p14"]):
        probe=read(ROOT/f"PyAnsys/output/phase8-analysis/{tag}-f3-2p5pct-dpm-200k-step-sensitivity/summary.json")
        bottom=np.zeros(2)
        for key,color in zip(["escaped","trapped","incomplete"],["#31688e","#35b779","#d99b24"]):
            a=np.array([probe["represented_fate_fraction"][k][key]*100 for k in ["baseline","probe"]]);ax.bar([0,1],a,bottom=bottom,label=key,color=color);bottom+=a
        ax.set_xticks([0,1],["50,000 steps","200,000 steps"]);ax.set_ylabel("Represented DPM feed (%)");ax.set_title(f"{tag.replace('p','.')} m/s, 2.5%, same carrier per panel")
    axs[0].legend(fontsize=8);save(fig,folder,"tracking-cap-sensitivity.png")
    stats["families"]["F3"]=[{"speed":r["manifest"]["speed_m_s"],"fraction":r["manifest"]["fraction"],"out_pct":float(r["out"][-1]*100),"inventory":float(r["inventory"][-1]),"fates":r["fate"]["weighted"]} for r in pilots+[pilot5]]
    p4=next(p for p,d in runs.items() if d.get("family")=="F4" and d.get("status")=="COMPLETE")
    r4=load_run(p4);add(p4,"F4-26.81-5-n11000","F4 26.81 m/s 5% provisional EWF N11000","F4","film-pilot")
    for fam,group,labels in [("F3",pilots+[pilot5],[f"{r['manifest']['speed_m_s']:g} m/s, {r['manifest']['fraction']*100:g}%" for r in pilots+[pilot5]]),("F4",[pilot5,r4],["F3: no film","F4: provisional EWF"])]:
        fig,axs=plt.subplots(1,2,figsize=(12,4))
        for run,label,color in zip(group,labels,COLORS):
            axs[0].plot(run['x'],run['gap']*100,label=label,color=color)
            axs[1].semilogy(run['residual_x'],run['residual'],color=color)
        axs[0].legend(fontsize=8);axs[0].set_ylabel('Signed Eulerian boundary gap / Eulerian feed (%)');axs[1].set_ylabel('Continuity residual')
        for ax in axs:ax.set_xlabel('Native steady iteration')
        style(axs);save(fig,PHASE/DIRS[fam]/'figures','numerical-context.png')
    folder=PHASE/DIRS["F4"]/"figures"
    histories([pilot5,r4],["F3: no film","F4: provisional EWF"],folder,"f3-f4-mechanism-response.png","Film addition: 26.81 m/s, 5% DPM, N10000–11000")
    fig,axs=plt.subplots(2,2,figsize=(12,7))
    for ax,field,label,factor in zip(axs.flat,["p8-ewf-film-mass-total","p8-ewf-thickness-max","p8-ewf-stripped-mass-total","p8-ewf-outflow-mass-total"],["Film mass (kg)","Maximum film thickness (mm)","Cumulative stripped mass (kg)","Cumulative film outflow mass (kg)"],[1,1000,1,1]):
        h=r4["reports"][field];x=sorted(h);ax.plot(x,[h[i]*factor for i in x],color=COLORS[1]);ax.set(xlabel="Native steady iteration",ylabel=label)
    style(axs);save(fig,folder,"film-response.png")
    stats["families"]["F4"]={"out_pct":float(r4["out"][-1]*100),"inventory":float(r4["inventory"][-1]),"film_mass":r4["reports"]["p8-ewf-film-mass-total"][int(r4["x"][-1])]}
    stage_paths=[ROOT/e["source_manifest"] for e in catalog if e["id"] in ["F1-26.81-n10000","F2-26.81-n10000"]]+[p5,p4]
    stage_runs=[load_run(p) for p in stage_paths]
    fig,axs=plt.subplots(1,3,figsize=(13,4.5))
    stage_stats=[]
    for r in stage_runs:
        late=r["x"]>=r["x"][-1]-500
        stage_stats.append({"family":r["manifest"]["family"],"end":int(r["x"][-1]),"out_pct":float(np.mean(r["out"][late])*100),"inventory":float(r["inventory"][-1]),"pressure_kpa":float(np.mean(r["pressure"][late]))})
    labels=[f"{r['family']}\nN{r['end']}" for r in stage_stats]
    for ax,key,label in zip(axs,["out_pct","inventory","pressure_kpa"],["Eulerian outlet liquid / total liquid feed (%)","Final Eulerian liquid inventory (kg)","Steam-face to outlet pressure difference (kPa)"]):
        ax.bar(labels,[r[key] for r in stage_stats],color=COLORS[:4]);ax.set_ylabel(label)
    style(axs);fig.suptitle("26.81 m/s storyline stages: F1/F2 full Eulerian feed; F3/F4 5% allocated DPM")
    save(fig,PHASE/"figures","reference-storyline-response.png")
    stats["reference_stages"]=stage_stats
    for p,d in runs.items():
        if d.get("status")=="COMPLETE" and d.get("family") in ["F1","F2"] and d.get("achieved_active_iterations")==2000 and "coupled" not in str(p):
            add(p,f"{d['family']}-simple-{'single' if 'single-face' in str(p) else 'mixed'}",f"{d['family']} SIMPLE {'single face' if 'single-face' in str(p) else 'original faces'} N2000",d["family"],"historical-numerics")
        elif d.get("status")=="COMPLETE" and d.get("family")=="F1-single-face":
            add(p,"F1-simple-single","F1 SIMPLE merged single inlet N2000","F1","historical-numerics")
    simple_reference=[]
    for speed in SPEEDS:
        matches=[(p,d) for p,d in runs.items() if d.get("family")=="F1" and d.get("status")=="COMPLETE"
                 and d.get("speed_m_s")==speed and d.get("achieved_active_iterations")==10000
                 and d.get("source_case","").endswith("F1-purnanto-parity-26p81.cas.h5")]
        if len(matches)!=1:raise RuntimeError(f"Expected one F1 SIMPLE N10000 pair at {speed:g} m/s, found {len(matches)}")
        p,d=matches[0]
        simple_reference.append(p)
        add(p,f"F1-{speed:g}-simple-n10000",f"F1 {speed:g} m/s SIMPLE original two faces N10000","F1","numerical-package-comparison")
    # Phase-level paired speed response.
    fig,axs=plt.subplots(1,3,figsize=(13,4))
    for family,color in zip(["F1","F2"],COLORS):
        rows=stats["families"][family]
        for ax,key in zip(axs,["out_pct","inventory","pressure_kpa"]):ax.plot(SPEEDS,[r[key] for r in rows],"o-",label=family,color=color)
    for ax,label in zip(axs,["Steam-outlet liquid / feed (%)","Final liquid inventory (kg)","Pressure difference (kPa)"]):ax.set(xlabel="Nominal inlet speed (m/s)",ylabel=label)
    axs[0].legend();style(axs);save(fig,PHASE/"figures","f1-f2-speed-comparison.png")
    (OUT/"catalog.json").write_text(json.dumps(catalog,indent=2)+"\n")
    (OUT/"summary.json").write_text(json.dumps(stats,indent=2)+"\n")
    print(json.dumps({"cases":len(catalog),"catalog":str(OUT/"catalog.json"),"summary":str(OUT/"summary.json")},indent=2))

if __name__=="__main__":main()
