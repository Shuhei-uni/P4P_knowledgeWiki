"""Run the read-only pipe comparison on the Fluent PC and fetch small evidence."""
from build_single_inlet_family import *
from summarise_single_family import collect
parser=argparse.ArgumentParser()
parser.add_argument('--selected',action='store_true')
args=parser.parse_args()
s=connect();s.events.stop()
script=REMOTE+'/check_central_pipe_h5.py'
payload=Path(__file__).with_name('check_central_pipe_h5.py').read_text()
if not remote_file_exists(s,script):write_ascii_text_new(s,script,payload)
name='selected-central-pipe-check.json' if args.selected else 'central-pipe-check.json'
output=REMOTE+'/'+name
exe='C:/Program Files/ANSYS Inc/v252/commonfiles/CPython/3_10/winx64/Release/python/python.exe'
sources=[REMOTE+'/single-parent/Separator-purnanto-single-733k.msh.h5',
    WORK+'/Separator-purnanto-single-381k.msh.h5',WORK+'/Separator-purnanto-single-357k.msh.h5']
if args.selected:
    rows=collect()
    if len(rows)!=7:raise RuntimeError('Seven verified levels required')
    sources=[sources[0]]+[r['remote_mesh'] for r in rows]
def q(x):return "'"+x.replace("'","''")+"'"
remote_ps(s,'& '+q(exe)+' '+q(script)+' '+q(output)+' '+' '.join(q(p) for p in sources))
data=json.loads(read_text(s,output));save_json(OUT/name,data)
if len(data)!=len(sources):raise RuntimeError('Incomplete central-pipe audit')
for row in data:
    if row['deep_pipe_core_cells'] or any(b['core_r_lt025_cells'] for b in row['bands'] if b['y_range_m'][1]<=6.261):
        raise RuntimeError('Cells detected inside the central pipe core '+row['file'])
print(json.dumps([{k:v for k,v in row.items() if k!='slice_cell_centers_xy_m'} for row in data],indent=2),flush=True)
