"""Verify Phase 9 preparation receipts and server-local final pairs."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'output/phase9-mesh-convergence/20261007'
LABELS = ['60k','342k','680k','997k','2_6M']


def main():
    campaign=json.loads((OUT/'campaign-manifest.json').read_text())
    assert campaign['status']=='COMPLETE_PREPARATION_ONLY'
    assert campaign['completed']==LABELS
    proof=[]
    for label in LABELS:
        m=json.loads((OUT/(label+'-run.json')).read_text())
        prepared=json.loads((OUT/(label+'-prepared-audited.json')).read_text())
        assert m['status'].startswith('FULL_FEED_PREPARED')
        assert m['final_equations']=={'drift':True,'flow':True,'ke':True,'mp':True}
        assert m['bulk_freeze'] is False and m['ewf_settings_final'] is False
        assert m['final_report_coverage']=='PASS'
        assert m['final_feed']=={'multiplier':1.0,'liquid_kg_s':116.92,'vapor_kg_s':80.69}
        assert prepared['settings_audit']=='08b-approved'
        assert prepared['bulk_audit']==json.loads((OUT/'08b-approved-bulk-contract.json').read_text())
        assert m['verified_native_end']-m['full_hold_start']>=m['minimum_full_hold']
        pair=m['final_pair']
        assert pair['native_iteration']==m['verified_native_end']
        for kind in ['case','data']:
            file=Path(pair[kind]);assert file.is_file() and file.stat().st_size>0
            digest=hashlib.sha256()
            with file.open('rb') as stream:
                for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
            assert digest.hexdigest()==pair[kind+'_sha256']
        histories=json.loads((OUT/(label+'-histories.json')).read_text())
        ids={str(n) for n in range(1581,m['verified_native_end']+1)}
        assert histories and all(ids.issubset(history) for history in histories.values())
        assert prepared['native_mesh']['cells']==m['cells']
        proof.append({'mesh':label,'cells':m['cells'],'status':m['status'],
                      'iteration':m['verified_native_end'],'pair_hashes':'PASS','report_coverage':'PASS'})
    (OUT/'completion-verification.json').write_text(json.dumps({'status':'VERIFIED_PREPARATION_ONLY','meshes':proof},indent=2)+'\n')
    print('VERIFIED_PREPARATION_ONLY: five full-feed pairs; all bulk equations active')


if __name__=='__main__':main()
