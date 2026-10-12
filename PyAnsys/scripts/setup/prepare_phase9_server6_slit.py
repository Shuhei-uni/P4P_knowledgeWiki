"""Preserve Server 6, load hash-verified N5080; inspect before configuration."""
import argparse,json,time
from phase9_server6_slit_common import attach,run,OUT,ROOT
from pyansys_fluent.stage4_native import exclusive_writer_lock

def main():
    with exclusive_writer_lock(OUT/'controller.lock'):
        if (OUT/'parent-loaded.json').exists():raise RuntimeError('Reconcile existing parent load receipt')
        s=attach();run.require_idle(s)
        if s.settings.solution.run_calculation.iterating():raise RuntimeError('Server 6 is solving')
        tag=str(time.time_ns());folder=run.WORK/'slit154k'
        run.ensure_remote_directory(s,str(folder/'scratch'))
        preserved=run.save(s,folder,'preserved-before-slit-'+tag)
        run.dump(OUT/'preserved-before-load.json',preserved)
        source=run.SHARED/'P4P-Fluent-Artifacts/Phase72A/Stage3/slit154k-20261005/final-N5080'
        known=json.loads((ROOT/'output/phase72a-stage3-slit154k-server3/20261005/run-manifest.json').read_text())['final_pair']
        pair={'native_iteration':5080}
        for kind,ext in [('case','cas'),('data','dat')]:
            src=source/('final-N5080.'+ext+'.h5');target=folder/('source-N5080-'+tag+'.'+ext+'.h5')
            if not run.remote_file_exists(s,str(src)):raise FileNotFoundError(str(src))
            code="$ErrorActionPreference='Stop'; Copy-Item -LiteralPath '"+str(src)+"' -Destination '"+str(target)+"'"
            if run.base.powershell(s,code) not in (0,None):raise RuntimeError('Parent copy failed')
            digest=run.remote_file_sha256(s,str(target),str(folder/'scratch'/('parent-'+kind+'-'+tag+'.sha256.txt')))
            if digest!=known[kind+'_sha256']:raise RuntimeError('Parent hash differs')
            pair[kind]=str(target);pair[kind+'_sha256']=digest
        archive=run.SHARED/'P4P-Fluent-Artifacts/Phase72A/ContactAbsorber/local20000/20261004T081120Z/contact-libraries.zip'
        digest=run.remote_file_sha256(s,str(archive),str(folder/'scratch'/('udf-'+tag+'.sha256.txt')))
        if digest!=run.base.HASHES['contact-libraries.zip']:raise RuntimeError('UDF hash differs')
        if run.base.powershell(s,"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath '"+str(archive)+"' -DestinationPath '"+str(run.WORK)+"' -Force") not in (0,None):raise RuntimeError('UDF extraction failed')
        run.load(s,pair)
        state=run.base.state(s)
        walls=s.settings.setup.boundary_conditions.wall.get_object_names()
        receipt={'parent':pair,'preserved':preserved,'state':state,'film':run.film(s),'bulk_audit':run.bulk_audit(s),'walls':walls,
                 'equations':s.settings.solution.controls.equations.get_state(),
                 'wall_states':{n:s.settings.setup.boundary_conditions.wall[n].get_state() for n in walls},
                 'review':'Idle owned Server 6; preserve loaded endpoint; verified local copies; hash-verified UDF; explicit load and native readback. No initialization or solve.'}
        run.dump(OUT/'parent-loaded.json',receipt)
        print(json.dumps({'status':'PARENT_LOADED_FOR_AUDIT','iteration':run.native_iteration(s),'film':receipt['film'],'walls':walls,'bulk_audit':receipt['bulk_audit']}),flush=True)
if __name__=='__main__':main()
