from pathlib import Path
import json,hashlib,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'PyAnsys/output/phase8-storyline-20260930'
PHASE=ROOT/'Project/experiments/phase-08-storyline-reconstruction'
def main():
    catalog=json.loads((OUT/'catalog.json').read_text())
    exports=json.loads((OUT/'export-receipt.json').read_text())
    tracks=json.loads((OUT/'track-export-receipt.json').read_text())
    ranges=json.loads((OUT/'range-receipt.json').read_text())['display_ranges']
    entries={e['id']:e for e in catalog}
    expected={e['id'] for e in catalog if e['role']!='particle-views'}
    assert expected==set(exports['cases'])
    images=[]
    cameras={}
    for id,r in exports['cases'].items():
        assert r['status']=='EXPORTED',id
        assert {'liquid','inlet-liquid','vertical-vectors','inlet-vectors'}<=r['images'].keys()
        for kind,im in r['images'].items():
            if kind not in ['film-thickness','film-vectors']:
                if kind in cameras:assert cameras[kind]==im['camera'],(id,kind,'camera mismatch')
                else:cameras[kind]=im['camera']
            state=im['graphics_state']
            field=state['field']
            if field in ranges:
                actual=state['range_options']
                assert [actual['minimum'],actual['maximum']]==ranges[field],(id,kind)
            if 'vectors' in kind:
                assert state['options']['skip']==0 and state['options']['scale']==.1
            images.append(im)
    assert {e['id'] for e in catalog if e['tracks']}==set(tracks['cases'])
    for r in tracks['cases'].values():
        assert r['dpm_settings_unchanged']
        images.extend(r['images'].values())
    for im in images:
        p=ROOT/im['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==im['sha256']
        with Image.open(p) as image:
            assert image.size in [(1800,2400),(2400,1800)]
            image.verify()
    for entry in catalog:
        for kind in ['case','data']:
            with Path(entry['pair'][kind]).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['pair'][kind+'_sha256'],entry['id']
    missing=[];linked=0
    for p in [PHASE/'results.md']+list(PHASE.glob('*/results.md')):
        for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            linked+=1
            if not (p.parent/target.strip('<>')).exists():missing.append([str(p),target])
    assert not missing,missing
    plots=list(PHASE.glob('**/figures/*.png'))
    for p in plots:
        with Image.open(p) as im:im.verify()
    result={'status':'VERIFIED','selected_pairs':len(catalog),'spatial_snapshots':len(expected),'native_images':len(images),'all_figure_files':len(plots),'markdown_image_links':linked,'source_hashes_unchanged':True,'shared_ranges_cameras_and_vector_policy_verified':True,'solve_issued':False,'visual_qa':'Direct representative image inspection across all families and rendering types; all files checked for integrity and all native exports checked against recorded field/range/camera policy.'}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
