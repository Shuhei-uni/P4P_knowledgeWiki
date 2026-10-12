"""Put the final quality table and plot beside the delivered meshes."""
import base64,csv,hashlib,io
from publish_single_family import *

def write_local_csv():
    rows=[dict(r,volume_difference_percent=100*r['volume_delta'],
               inlet_area_difference_percent=100*r['area_deltas']['inlet'],
               outlet_area_difference_percent=100*r['area_deltas']['steamoutlet']) for r in collect()]
    stream=io.StringIO()
    fields=['file','cells','effective_h_m','cell_ratio_to_previous','min_oq',
            'max_skewness','mean_oq','max_aspect_ratio','max_size_change',
            'cells_below_oq03','cells_size_change_ge300','min_cell_volume_m3',
            'volume_m3','volume_difference_percent','inlet_area_difference_percent',
            'outlet_area_difference_percent','free_faces','multi_faces']
    writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore')
    writer.writeheader();writer.writerows(rows)
    (OUT/'mesh-quality-summary.csv').write_text(stream.getvalue())
    return OUT/'mesh-quality-summary.csv'

def main():
    delivery=json.loads((OUT/'delivery.json').read_text())
    if delivery['status']!='COMPLETE':raise RuntimeError('Mesh delivery is incomplete')
    write_local_csv()
    assets=[OUT/'mesh-quality-summary.csv',OUT/'family-quality.png']
    s=connect();s.events.stop();records=[]
    for asset in assets:
        data=asset.read_bytes();sha=hashlib.sha256(data).hexdigest().upper()
        payload=base64.b64encode(data).decode('ascii')
        encoded=WORK+'/'+asset.name+'.b64'
        if remote_file_exists(s,encoded):
            if read_text(s,encoded)!=payload:raise RuntimeError('Existing different encoded asset')
        else:write_ascii_text_new(s,encoded,payload)
        dest=SHARE+'/'+asset.name
        verified=WORK+'/'+asset.name+'-verified-'+uuid.uuid4().hex+'.json'
        code="\n".join(["$ErrorActionPreference='Stop'",
            '$dst='+psquote(dest),'$sha='+psquote(sha),
            'if(!(Test-Path -LiteralPath $dst)){[IO.File]::WriteAllBytes($dst,[Convert]::FromBase64String([IO.File]::ReadAllText('+psquote(encoded)+')))}',
            'if((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash -ne $sha){throw "Report asset hash mismatch"}',
            '[pscustomobject]@{file=$dst;sha256=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash;bytes=(Get-Item -LiteralPath $dst).Length} | ConvertTo-Json | Set-Content -LiteralPath '+psquote(verified)+' -Encoding Ascii'])
        remote_ps_file(s,code)
        record=json.loads(read_text(s,verified))
        if record!={'file':dest,'sha256':sha,'bytes':len(data)}:
            raise RuntimeError('Report asset readback differs')
        records.append(record)
    save_json(OUT/'quality-assets-manifest.json',records)
    print(json.dumps(records,indent=2),flush=True)

if __name__=='__main__':main()
