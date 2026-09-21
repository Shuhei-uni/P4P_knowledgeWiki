"""Prove corrected Phase 7b expression sources in a bounded diagnostic child.

Fresh clean N0 parent; no patched pool or C. This is not the five-case screen:
mask-boundary instrumentation must be completed before a screen is counted.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import math
import signal
import sys
import traceback

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "src"))
from dotenv import load_dotenv
load_dotenv(BASE / ".env")
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.remote_text import read_text

ROOT = "C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal"
ZONE = "simple-spiral-separator--brine-outlet-"
TOPS = {20: -1.1836669883728028, 40: -.8827502412796020,
        60: -.5818334941864014, 80: -.2809167470932006, 100: .020}
COUNTS = {20: 21516, 40: 41258, 60: 59465, 80: 78608, 100: 98519}
VOLUMES = {20: .5612436425388415, 40: 1.4681621275, 60: 2.4628949897,
           80: 3.3772762231, 100: 4.4017292439}
HOOKS = {"phase-2": {"mass": "P7bSink"}, "mixture": {
    "x-momentum": "P7bSinkX", "y-momentum": "P7bSinkY", "z-momentum": "P7bSinkZ",
    "k": "P7bSinkK", "epsilon": "P7bSinkEpsilon"}}


def definitions(percent):
    loc = f'["{ZONE}"]'
    predicate = f"AND(y >= -1.4845837354660034[m], y <= {TOPS[percent]:.17g}[m])"
    d = {"P7bAlpha": 'Volumefraction(phase="phase-2")',
         "P7bMask": f"IF({predicate},1.0,0.0)",
         "P7bK": 'TurbulentKineticEnergyk',
         "P7bEpsilon": 'TurbulenceDissipationRate',
         "P7bSink": "-P7bMask*881.77[kg/m^3]*min(1.0,max(0.0,P7bAlpha))/0.0024095893[s]"}
    for axis in "xyz":
        d["P7bLiquid"+axis.upper()] = f'Velocity.{axis}(phase="phase-2")'
        d["P7bSink"+axis.upper()] = "P7bSink*P7bLiquid"+axis.upper()
    d.update({"P7bSinkK": "P7bSink*P7bK", "P7bSinkEpsilon": "P7bSink*P7bEpsilon",
              "P7bCount": f"CountIf({predicate},{loc})",
              "P7bGeometryVolume": f"VolumeInt(P7bMask,{loc})",
              "P7bWaterVolume": f"VolumeInt(P7bAlpha,{loc})",
              "P7bWaterMass": "881.77[kg/m^3]*P7bWaterVolume",
              "P7bCollectorVolume": f"VolumeInt(P7bMask*P7bAlpha,{loc})",
              "P7bCollectorMass": "881.77[kg/m^3]*P7bCollectorVolume",
              "P7bAboveVolume": "P7bWaterVolume-P7bCollectorVolume",
              "P7bRemoval": f"-VolumeInt(P7bSink,{loc})"})
    for phase,short in [("phase-2","Liquid"),("phase-1","Vapor"),("mixture","Mixture")]:
        for face,shortface in [("liquid-inlet","LiquidInlet"),("steam-inlet","SteamInlet"),("steam-outlet","Outlet"),("brine-outlet","BrineWall")]:
            d[f"P7b{short}{shortface}"] = f'MassFlow(["{face}"],phase="{phase}")'
        d[f"P7b{short}Boundary"] = "+".join(f"P7b{short}{x}" for x in ["LiquidInlet","SteamInlet","Outlet","BrineWall"])
        d[f"P7b{short}Closure"] = f"P7b{short}Boundary" + ("-P7bRemoval" if phase != "phase-1" else "")
    for face,short in [("liquid-inlet","Liquid"),("steam-inlet","Steam"),("steam-outlet","Outlet")]:
        d[f"P7bPressure{short}"] = f'AreaAve(StaticPressure,["{face}"])'
    d["P7bDropLiquid"] = "P7bPressureLiquid-P7bPressureOutlet"
    d["P7bDropSteam"] = "P7bPressureSteam-P7bPressureOutlet"
    return d


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent", type=int, choices=list(TOPS), default=20)
    parser.add_argument("--iterations", type=int, choices=[0, 50], default=0)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = f"p7b-source-proof-s{args.percent}-{stamp}"
    out = BASE / "output/phase07b_preparation" / run
    out.mkdir()
    r = {"run_id": run, "scientific_screen": False, "percent": args.percent,
         "requested_diagnostic_iterations": args.iterations,
         "parent_case": ROOT+"/case-data/p7b-clean-initial-20260912T080713Z.cas.h5",
         "prepared_case": f"{ROOT}/case-data/{run}-prepared.cas.h5",
         "final_case": f"{ROOT}/case-data/{run}-final.cas.h5",
         "report": f"{ROOT}/reports/{run}.out", "steps": [], "definitions": definitions(args.percent)}
    def persist():
        (out/"result.json").write_text(json.dumps(r,indent=2,default=str)+"\n")
    def timeout(*_): raise TimeoutError("Source proof deadline")
    signal.signal(signal.SIGALRM,timeout)
    def stage(name,fn,seconds=60):
        e={"name":name,"state":"STARTED"};r['steps'].append(e);persist();print(name,flush=True)
        signal.alarm(seconds)
        try:
            value=fn();e.update(state="PASS",value=value);return value
        except Exception as exc:
            e.update(state="FAILED",error=str(exc));raise
        finally:
            signal.alarm(0);persist()
    def flags():
        return {p:s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[p].sources.enable()
                for p in ["mixture","phase-1","phase-2"]}
    def source_state():
        return {p:s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[p].sources.get_state()
                for p in ["mixture","phase-1","phase-2"]}
    def named(name,definition):
        group=s.settings.setup.named_expressions
        if name not in group.get_object_names():group.create(name=name)
        group=s.settings.setup.named_expressions;group[name].definition=definition
        assert group[name].definition()==definition
    s=None
    try:
        signal.alarm(30);s=connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5);signal.alarm(0)
        s.transcript.start(file_name=str(out/'setup.trn'),write_to_stdout=False)
        assert remote_file_exists(s,r['parent_case'])
        stage('load_clean_initial_pair',lambda:s.settings.file.read_case_data(file_name=r['parent_case']),120)
        assert not any(flags().values())
        assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==0
        assert s.settings.setup.general.solver.time()=='steady'
        stage('profile_update',lambda:s.settings.solution.run_calculation.profile_update_interval.set_state(1))
        for name,definition in r['definitions'].items():
            stage('define_'+name,lambda n=name,d=definition:named(n,d))
        count=stage('collector_cell_count',lambda:s.settings.setup.named_expressions['P7bCount'].get_value())
        volume=stage('collector_geometric_volume',lambda:s.settings.setup.named_expressions['P7bGeometryVolume'].get_value())
        assert count==COUNTS[args.percent] and math.isclose(volume,VOLUMES[args.percent],rel_tol=1e-9)
        for ph,terms in HOOKS.items():
            src=s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources
            src.enable=True
            for eq,expression in terms.items():
                src=s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources
                src.terms[eq].resize(size=1)
                src.terms[eq][0].set_state({'option':'value','value':expression})
                assert src.terms[eq][0].value()==expression
        r['source_slots']=stage('source_readback',source_state)
        r['explicit_jacobian']='No derivative slot exposed/assigned in these native expression source entries; no user-defined Jacobian claimed.'
        scalar_names=[n for n in r['definitions'] if n not in {
            'P7bAlpha','P7bMask','P7bK','P7bEpsilon','P7bSink','P7bLiquidX','P7bLiquidY','P7bLiquidZ',
            'P7bSinkX','P7bSinkY','P7bSinkZ','P7bSinkK','P7bSinkEpsilon','P7bCount','P7bGeometryVolume'}]
        report_names=[]
        for name in scalar_names:
            rn='proof-'+name.lower();reports=s.settings.solution.report_definitions.single_valued_expression
            reports.create(name=rn);reports=s.settings.solution.report_definitions.single_valued_expression
            reports[rn].definition=name;assert reports[rn].definition()==name;report_names.append(rn)
        native=s.settings.solution.report_definitions.volume
        rn='proof-native-water';native.create(name=rn);native[rn].set_state({'report_type':'volume-integral','field':'phase-2-vof','cell_zones':[ZONE]});report_names.append(rn)
        rf=s.settings.solution.monitor.report_files;rf.create(name='p7b-source-proof-history')
        rf['p7b-source-proof-history'].set_state({'file_name':r['report'],'report_defs':report_names,'frequency':1,'active':True})
        # Disable the inherited history so this child cannot append to the preserved parent's report.
        rf['p7b-clean-water-history'].active=False
        r['reports']=stage('reports_readback',lambda:s.settings.solution.report_definitions.get_state())
        r['initial_metrics']=stage('compute_initial_reports',lambda:s.settings.solution.report_definitions.compute(report_defs=report_names))
        stage('save_prepared_pair',lambda:s.settings.file.write_case_data(file_name=r['prepared_case']),120)
        assert all(remote_file_exists(s,r['prepared_case'].replace('.cas.h5',suffix)) for suffix in ['.cas.h5','.dat.h5'])
        stage('reopen_prepared_pair',lambda:s.settings.file.read_case_data(file_name=r['prepared_case']),120)
        assert source_state()==r['source_slots']
        for name,definition in r['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==definition
        assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==0
        s.transcript.stop()
        if 'SEGMENTATION VIOLATION' in (out/'setup.trn').read_text():raise RuntimeError('Cortex fault during source setup')
        r['status']='SOURCE_CONFIGURATION_PERSISTENCE_PASS';persist()
        if args.iterations:
            s.transcript.start(file_name=str(out/'solve.trn'),write_to_stdout=False)
            stage('run_diagnostic',lambda:s.settings.solution.run_calculation.iterate(iter_count=args.iterations),1800)
            r['final_iteration']=stage('final_iteration',lambda:s.settings.setup.named_expressions['P7bGlobalIteration'].get_value())
            assert r['final_iteration']==args.iterations, f"Solve did not reach horizon: {r['final_iteration']} != {args.iterations}; inspect solve.trn"
            r['final_metrics']=stage('compute_final_reports',lambda:s.settings.solution.report_definitions.compute(report_defs=report_names))
            stage('save_final_pair',lambda:s.settings.file.write_case_data(file_name=r['final_case']),120)
            assert all(remote_file_exists(s,r['final_case'].replace('.cas.h5',suffix)) for suffix in ['.cas.h5','.dat.h5'])
            (out/'history.out').write_text(stage('retrieve_history',lambda:read_text(s,r['report'])))
            s.transcript.stop()
            assert r['final_iteration']==args.iterations
            assert 'SEGMENTATION VIOLATION' not in (out/'solve.trn').read_text()
            r['status']='DIAGNOSTIC_HORIZON_COMPLETED';persist()
    except Exception as exc:
        signal.alarm(0);r.update(status='FAILED',error=str(exc));(out/'error.txt').write_text(traceback.format_exc());raise
    finally:
        if s is not None:
            try:s.transcript.stop()
            except Exception:pass
        persist();print('EVIDENCE',out,flush=True)


if __name__=='__main__':main()
