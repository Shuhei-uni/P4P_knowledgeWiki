"""Copy the verified mesh family to a new folder beside the user sources."""
import uuid
from build_single_inlet_family import *
from summarise_single_family import collect,IDS

SHARE=('C:/Users/syok443/OneDrive - The University of Auckland/2026 Sem 1/700/'
       'P4PCFD/CAD PurnantoV2/single-inlet-refinement-20261008')

def psquote(value):return "'"+value.replace("'","''")+"'"

def remote_ps_file(s,code):
    """Run a verified script with a short Windows command line."""
    script=WORK+'/delivery-'+uuid.uuid4().hex+'.ps1'
    write_ascii_text_new(s,script,code)
    command='powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+script+'"'
    return s.scheme.eval('(system "'+quote_scheme_string(command)+'")')

def main():
    rows=collect()
    if len(rows)!=7:raise RuntimeError('The family is incomplete')
    if min(r['min_oq'] for r in rows)<.2:raise RuntimeError('A level needs quality recovery')
    s=connect();s.events.stop()
    native_controls=[]
    for row in rows:
        wf=row['remote_mesh'].removesuffix('.msh.h5')+'.wft'
        native=json.loads(read_text(s,wf))
        tasks={t['_name_']:t.get('Arguments',{}) for k,t in native['workflow']['ROOT'].items()
               if k.startswith('TaskObject:')}
        controls=tasks['Generate the Surface Mesh']['CFDSurfaceMeshControls']
        expected=json.loads((OUT/(row['id']+'-recipe.json')).read_text())
        target={t['_name_']:t.get('Arguments',{}) for k,t in expected['workflow']['ROOT'].items()
                if k.startswith('TaskObject:')}
        for key in ['MinSize','MaxSize','CurvatureNormalAngle']:
            if abs(float(controls[key])-float(target['Generate the Surface Mesh']['CFDSurfaceMeshControls'][key]))>1e-12:
                raise RuntimeError('Saved surface control differs '+row['id']+' '+key)
        actual=tasks['Improve Volume Mesh']
        if float(actual['CellQualityLimit'])!=.3 or actual['VMImprovePreferences']['VIgnoreFeature']!='no':
            raise RuntimeError('Saved quality control differs '+row['id'])
        if int(actual['VMImprovePreferences']['VIQualityIterations'])!=row['quality_iteration_limit']:
            raise RuntimeError('Saved iteration limit differs '+row['id'])
        native_controls.append({'id':row['id'],'workflow':wf,'surface':controls,
                                'volume':tasks['Generate the Volume Mesh'],
                                'quality':actual})
    save_json(OUT/'saved-workflow-control-readback.json',native_controls)
    # Copy only final, save/reopen-verified products. Existing identical files
    # may be verified again; an existing different file is never overwritten.
    pairs=[(r['remote_mesh'],SHARE+'/'+r['file']) for r in rows]
    pairs.append((CAD,SHARE+'/separator-purnanto(single-homo).agdb'))
    code=["$ErrorActionPreference='Stop'",'New-Item -ItemType Directory -Path '+psquote(SHARE)+' -Force | Out-Null','$records=@()']
    for src,dst in pairs:
        code += ['$src='+psquote(src),'$dst='+psquote(dst),
          '$sha=(Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash',
          'if(Test-Path -LiteralPath $dst){if((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash -ne $sha){throw "Different destination already exists"}}else{Copy-Item -LiteralPath $src -Destination $dst}',
          'if((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash -ne $sha){throw "Copy hash mismatch"}',
          '$records += [pscustomobject]@{source=$src;shared=$dst;bytes=(Get-Item -LiteralPath $dst).Length;sha256=$sha}']
    receipt=WORK+'/final-copy-manifest-'+uuid.uuid4().hex+'.json'
    code+=['$records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath '+psquote(receipt)+' -Encoding Ascii']
    remote_ps_file(s,'\n'.join(code))
    manifest=json.loads(read_text(s,receipt));save_json(OUT/'final-copy-manifest.json',manifest)
    if len(manifest)!=8:raise RuntimeError('Incomplete copy receipt')
    expected_pairs=set(pairs)
    if {(r['source'],r['shared']) for r in manifest}!=expected_pairs:
        raise RuntimeError('Copy receipt paths do not match selected products')
    cad_record=next(r for r in manifest if r['source']==CAD)
    cad_sha='24777C3009AEA1784C629989A79E722DA17A24FC4BA30058AD73EAC59FE2F5D7'
    if cad_record['sha256'].upper()!=cad_sha:raise RuntimeError('Source CAD hash differs')
    # Portable recipe file beside each mesh. These are the source task controls
    # used in generation, rebased only to the copied CAD file.
    for row in rows:
        w=json.loads((OUT/(row['id']+'-recipe.json')).read_text())
        w['workflow']['ROOT']['TaskObject:TaskObject1']['Arguments']['FileName']=SHARE+'/separator-purnanto(single-homo).agdb'
        wf=SHARE+'/'+row['file'].removesuffix('.msh.h5')+'.wft'
        payload=json.dumps(w,indent=2)
        if remote_file_exists(s,wf):
            if read_text(s,wf)!=payload:raise RuntimeError('Existing different workflow '+wf)
        else:write_ascii_text_new(s,wf,payload)
    # Leave the anchor in the GUI for the user's inspection.
    anchor=next(r for r in rows if r['id']=='curvature-anchor')
    s.meshing.File.ReadMesh(FileName=anchor['remote_mesh'])
    final=audit(s);save_json(OUT/'final-loaded-anchor.json',final)
    if final['cell_count']!=anchor['cells']:raise RuntimeError('Final GUI restore mismatch')
    rows=collect()
    result={'status':'COMPLETE','folder':SHARE,'files':manifest,'levels':rows,
            'parent':'Separator-purnanto-single-733k.msh.h5','source_cad_sha256':cad_sha,
            'loaded_mesh':anchor['file']}
    payload=json.dumps(result,indent=2)
    summary_path=SHARE+'/mesh-family-summary.json'
    if remote_file_exists(s,summary_path):
        if read_text(s,summary_path)!=payload:raise RuntimeError('Existing different shared summary')
    else:write_ascii_text_new(s,summary_path,payload)
    save_json(OUT/'delivery.json',result)
    print(json.dumps({'status':'COMPLETE','shared_folder':SHARE,'loaded':anchor['file']}),flush=True)

if __name__=='__main__':main()
