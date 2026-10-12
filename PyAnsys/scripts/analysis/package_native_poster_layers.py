"""Recover PNG alpha from paired native Fluent white/black hardcopies.

Fluent renders every mesh, film surface and pathline. This script performs only
background separation and packaging; it creates no geometry or CFD field.
The original native PNGs and their remote-file SHA-256 checks remain unchanged.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'PyAnsys/output/poster-N45606-native/20261010'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alpha_pair(white_path,black_path,target):
    with Image.open(white_path) as image:
        white=np.asarray(image.convert('RGB'))
    with Image.open(black_path) as image:
        black=np.asarray(image.convert('RGB'))
    assert white.shape==black.shape
    assert np.all(white[0]==255) and np.all(black[0]==0)
    output=np.zeros((*white.shape[:2],4),dtype=np.uint8)
    residual=0.0
    channel_spread=0.0
    for first in range(0,len(white),256):
        last=min(first+256,len(white))
        w=white[first:last].astype(np.float32)
        b=black[first:last].astype(np.float32)
        diff=w-b
        channel_spread=max(channel_spread,float(np.ptp(diff,axis=2).max()))
        alpha=np.clip(1-diff.mean(2)/255,0,1)
        color=np.divide(b,alpha[:,:,None],out=np.zeros_like(b),where=alpha[:,:,None]>1e-6)
        color=np.clip(color,0,255)
        output[first:last,:,:3]=np.rint(color).astype(np.uint8)
        output[first:last,:,3]=np.rint(alpha*255).astype(np.uint8)
        a=output[first:last,:,3].astype(np.float32)/255
        rgb=output[first:last,:,:3].astype(np.float32)
        residual=max(residual,float(np.abs(rgb*a[:,:,None]+255*(1-a[:,:,None])-w).max()),
                     float(np.abs(rgb*a[:,:,None]-b).max()))
    # White/black backgrounds must affect only compositing. Fail rather than
    # hide a changed palette, camera, lighting or native scene behind an alpha.
    assert residual<=4.0,(white_path.name,residual,channel_spread)
    assert output[:,:,3].max()>0 and output[:,:,3].min()==0
    assert not np.any(output[0,:,3]) and not np.any(output[-1,:,3])
    assert not np.any(output[:,0,3]) and not np.any(output[:,-1,3])
    Image.fromarray(output).save(target,dpi=(300,300))
    return {'white_source_sha256':sha(white_path),'black_source_sha256':sha(black_path),
            'output_sha256':sha(target),'resolution_px':[white.shape[1],white.shape[0]],
            'max_recomposition_error_8bit':residual,'max_background_difference_channel_spread_8bit':channel_spread}


def main():
    receipt=json.loads((OUT/'latest-export.json').read_text())
    assert receipt['status']=='EXPORTED' and receipt['scientific_state_unchanged']
    source=Path(receipt['figures'][0]['local']).parent
    selected=OUT/'selected'
    selected.mkdir(exist_ok=True)
    for artifact in receipt['figures']:
        assert sha(Path(artifact['local']))==artifact['sha256']
    for name in ['composite','quantitative-composite','film-thickness','absorber-full','inlet-detail']:
        shutil.copyfile(source/f'native-{name}.png',selected/f'native-{name}.png')
    checks={}
    for name in ['geometry','film','flow','absorber','inlets','composite']:
        filename='native-composite-transparent.png' if name=='composite' else f'layer-{name}.png'
        checks[name]=alpha_pair(source/f'native-{name}.png',source/f'native-{name}-black.png',selected/filename)
        print('NATIVE_ALPHA_LAYER',name,checks[name]['max_recomposition_error_8bit'],flush=True)
    manifest={'renderer':'Fluent 2025 R2 native scenes on Server 6',
              'native_export_receipt':str(source/'export-receipt.json'),
              'source_pair':receipt['source_pair'],'camera':receipt['camera'],
              'resolution_px':receipt['resolution'],'alpha_checks':checks,
              'alpha_method':'A=1-mean(W-B)/255; RGB=B/A. Matched native white and black hardcopies; no offline geometry, field interpolation, pathline integration or field rendering.',
              'caveat':'Separate layers have no mutual depth occlusion. Native composite preserves the scene depth.',
              'layer_order':['geometry','film','absorber','inlets','flow'],
              'script_sha256':sha(Path(__file__))}
    (selected/'layer-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
    shutil.copyfile(OUT/'configured.json',selected/'native-graphics-settings.json')
    if (OUT/'saved-graphics.json').exists():shutil.copyfile(OUT/'saved-graphics.json',selected/'saved-graphics.json')
    readme='''N45606 native Fluent poster figures\n\nAll CFD geometry, surfaces, contours and pathlines were rendered by Fluent\n2025 R2 on Server 6, from the hash-verified N45606 case/data pair.\n\nUse native-composite.png for the native combined view with a white background.\nUse native-composite-transparent.png on another poster background.\n\nFive PNG layers share a 2400 x 4000 canvas and camera: geometry, film, absorber,\ninlets and flow. Insert all at the same position and size. Opacity can be\nreduced further. The combined native scene handles mutual depth correctly.\n\nThe film layer is the native wet-wall surface at saved film thickness >10 nm,\ncoloured uniformly for the illustration. native-film-thickness.png and\nnative-quantitative-composite.png retain the native thickness colour field.\nThe amber base is the native bottom-boundary footprint of the absorber.\nnative-absorber-full.png shows its full native exterior, including the cell\nzone interface. The numerical absorber is not a resolved physical drain.\n\nNative pathlines track steam phase-1 and are coloured by its velocity magnitude.\nNo labels, legends, axes, floor grid, reflection or shadow are included.\nNo solver iterations, initialization or physical model changes were issued.\nN45606 still had film storage; these figures do not establish a steady film.\n\nTransparent layers are background-separated from two native hardcopies, one\non white and one on black. Recomposition checks are in layer-provenance.json.\nThe original PNGs were transferred with remote/local SHA-256 agreement.\n'''
    readme+='\nThe native inlet close-up shows the two boundary faces normal to their plane.\nThe liquid strip is 6.75 mm wide and is difficult to see in the whole vessel.\n'
    (selected/'README.txt').write_text(readme)
    with zipfile.ZipFile(OUT/'N45606-native-poster-figure-pack.zip','w',zipfile.ZIP_DEFLATED) as pack:
        for path in selected.iterdir():
            if path.is_file():pack.write(path,path.name)
    print('PACKAGED',OUT/'N45606-native-poster-figure-pack.zip',flush=True)


if __name__=='__main__':main()
