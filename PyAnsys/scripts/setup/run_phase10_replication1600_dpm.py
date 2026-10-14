"""Native one-way Case 4 DPM update on the verified M04 N1500 field.

One required fresh update, aggregate and nine per-injection reports, and paired
post-tracking checkpoints. No initialization or carrier iterations.
"""
import functools
import copy
import json
import os
from pathlib import Path
import queue
import sys
import threading
import time

import phase10_core as core
import ansys.fluent.core._grpc_services as low
import ansys.fluent.core.services as high
from ansys.fluent.core.utils.fluent_version import FluentVersion


def main():
    cfg=json.loads(Path(sys.argv[sys.argv.index('--config')+1]).read_text())
    root=Path(cfg['work']);manifest=root/'manifest.json';assert not manifest.exists(),'Reconcile existing update before replay'
    receipt={'experiment':cfg.get('experiment','R1600_DPM'),'status':'CONNECTING','controller_pid':os.getpid(),
             'parent':cfg['parent'],'carrier_iteration':1500,'solved_updates':0,'DPM_update_dispatches':0,
             'DPM_completed_updates':0,'tracking_issued':False,'report_files':{},'source_limits':cfg['source_limits']}
    def persist():core.dump(manifest,receipt)
    persist()
    for kind in ['case','data']:assert core.sha(cfg['parent'][kind])==cfg['parent'][kind+'_sha256']
    low._server_supports_v1=lambda channel:False
    high.create_service_factory=functools.partial(high.create_service_factory,product_version=FluentVersion.v252)
    core.pf.config.check_health=False
    attached=queue.Queue()
    def connect():
        try:attached.put(core.pf.connect_to_fluent(ip=cfg['ip'],port=cfg['port'],password=os.environ['PHASE10_API_PASSWORD'],
                        allow_remote_host=True,insecure_mode=True,cleanup_on_exit=False,start_watchdog=False,start_transcript=False))
        except BaseException as error:attached.put(error)
    threading.Thread(target=connect,daemon=True).start()
    try:s=attached.get(timeout=60)
    except queue.Empty:
        receipt['status']='CONNECTION_TIMEOUT_BEFORE_MUTATION';persist();os._exit(2)
    if isinstance(s,BaseException):receipt.update(status='CONNECTION_ERROR_BEFORE_MUTATION',error=str(s));persist();raise s
    s.events.stop();transcript=root/'DPM-tracking.trn'
    try:
        assert not s.settings.solution.run_calculation.iterating() and core.iteration(s)==1500
        before=cfg.get('settings_before',cfg['settings'])
        core.require_state_same(core.state(s),before)
        assert s.fields.solution_variable_info.get_zones_info()['fluid'].count==946967
        names=s.settings.setup.models.discrete_phase.injections.get_object_names()
        assert set(names)==set(cfg['injection_names']) and len(names)==9
        assert not s.settings.setup.models.discrete_phase.general_settings.interaction.enabled()
        reports_before=core.compute(s,cfg['carrier_reports']);receipt['carrier_reports_before']=reports_before
        with core.native_transcript(s.settings.file,transcript):
            if 'tracking_max_num_steps' in cfg:
                # Start the sensitivity from the preserved pre-tracking pair,
                # avoiding any inherited particle positions or report statistics.
                core.reopen(s,cfg['fresh_DPM_parent'])
                assert core.iteration(s)==1500
                core.require_state_same(core.state(s),before)
                core.require_state_same(core.compute(s,cfg['carrier_reports']),reports_before)
                expected=copy.deepcopy(before)
                expected['models']['discrete_phase']['tracking']['max_num_steps']=cfg['tracking_max_num_steps']
                core.require_state_same(expected,cfg['settings'])
                s.settings.setup.models.discrete_phase.tracking.max_num_steps=cfg['tracking_max_num_steps']
                core.require_state_same(core.state(s),expected)
                prepared=core.save_pair(s,root/'prepared-limit-M04-N1500')
                core.reopen(s,prepared)
                assert core.iteration(s)==1500
                core.require_state_same(core.state(s),expected)
                core.require_state_same(core.compute(s,cfg['carrier_reports']),reports_before)
                receipt.update(prepared_pair=prepared,controlled_delta={'max_num_steps':{
                    'before':before['models']['discrete_phase']['tracking']['max_num_steps'],
                    'after':cfg['tracking_max_num_steps']}},fresh_DPM_parent=cfg['fresh_DPM_parent'])
                persist()
            report=s.settings.results.report.discrete_phase
            report.set_per_injection_zone_summaries(enable=True,reset_dpm_summaries=False)
            core.require_state_same(core.state(s),cfg['settings'])
            # Persist dispatch before the blocking update. A reconnect cannot
            # assume this command failed or replay it from a timeout alone.
            receipt.update(status='TRACKING',tracking_issued=True,DPM_update_dispatches=1,transcript=str(transcript));persist()
            begin=time.perf_counter();s.tui.solve.dpm_update()
            receipt.update(status='TRACKED_REPORTS_PENDING',DPM_completed_updates=1,tracking_seconds=time.perf_counter()-begin);persist()
            assert core.iteration(s)==1500
            core.require_state_same(core.state(s),cfg['settings'])
            reports_after=core.compute(s,cfg['carrier_reports'])
            core.require_state_same(reports_after,reports_before)
            receipt.update(carrier_reports_after=reports_after,carrier_reports_unchanged=True)
            # Preserve a tracked endpoint before report/export operations.
            pair=core.save_pair(s,root/'tracked-M04-N1500');receipt['tracked_pair']=pair;persist()
            report.summary()
            aggregate=root/'DPM-aggregate.txt'
            report.extended_summary(write_to_file=True,file_name=str(aggregate),include_in_domain_particles=False,pick_injection=False)
            receipt['report_files']['aggregate']=str(aggregate);persist()
            for name in cfg['injection_names']:
                path=root/(name+'-DPM.txt')
                report.extended_summary(write_to_file=True,file_name=str(path),include_in_domain_particles=False,pick_injection=True,injection=name)
                assert path.is_file() and path.stat().st_size>0
                receipt['report_files'][name]=str(path);persist()
            assert aggregate.is_file() and aggregate.stat().st_size>0 and len(receipt['report_files'])==10
            receipt['report_sha256']={name:core.sha(path) for name,path in receipt['report_files'].items()}
            core.require_state_same(core.state(s),cfg['settings'])
            core.reopen(s,pair)
            assert core.iteration(s)==1500 and not s.settings.solution.run_calculation.iterating()
            core.require_state_same(core.state(s),cfg['settings'])
            core.require_state_same(core.compute(s,cfg['carrier_reports']),reports_before)
            receipt.update(final_pair=pair,strict_reopen_verified=True,settings_readback=core.state(s),
                           status='DPM_TRACKING_COMPLETE_EVIDENCE_PENDING',injection_names=cfg['injection_names'])
            persist()
        receipt['transcript_sha256']=core.sha(transcript);receipt['transcript_closed']=True;persist()
    except BaseException as error:
        receipt.update(status='DPM_ERROR_PRESERVE_ENDPOINT',error=type(error).__name__+': '+str(error));persist()
        # Do not restore/retrack automatically: a dispatched update may have
        # completed and its statistics are useful even if export failed.
        if receipt['DPM_completed_updates'] and 'tracked_pair' not in receipt:
            try:receipt['error_pair']=core.save_pair(s,root/'error-M04-N1500');persist()
            except BaseException as save_error:receipt['save_error']=str(save_error);persist()
        raise
    finally:s._fluent_connection._channel.close()
    print(json.dumps({k:receipt[k] for k in ['status','controller_pid','DPM_completed_updates','solved_updates','tracking_seconds']}),flush=True)


if __name__=='__main__':main()
