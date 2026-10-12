"""Show the original and rebuilt near-centre cell samples from the saved files."""
import argparse,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/p4p-mesh-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_single_inlet_family import OUT
parser=argparse.ArgumentParser()
parser.add_argument('--selected',action='store_true')
args=parser.parse_args()
name='selected-central-pipe-check.json' if args.selected else 'central-pipe-check.json'
rows=json.loads((OUT/name).read_text())
rebuilt=next(r for r in rows if r['cell_count']==681844) if args.selected else rows[1]
rebuilt_label=f"Rebuilt {round(rebuilt['cell_count']/1000)}k"
fig,axes=plt.subplots(1,2,figsize=(7.5,6),sharex=True,sharey=True,layout='constrained')
for ax,row,title in zip(axes,[rows[0],rebuilt],['Original 733k',rebuilt_label]):
    xy=np.asarray(row['slice_cell_centers_xy_m'])
    ax.scatter(xy[:,0],xy[:,1],s=3,color='#276b8f',alpha=.65,label='Nearby fluid cell centres')
    ax.fill_betweenx([0,6.261],-.25,.25,color='#ededed',label='Checked core: zero cells')
    radius=row['central_wall']['max_radius_m']
    ax.plot([-radius,-radius],[0,5.761],color='#555',lw=1)
    ax.plot([radius,radius],[0,5.761],color='#555',lw=1)
    ax.axhline(6.261,color='#b07c25',ls='--',lw=1,label='Outlet plane')
    ax.set(title=title,xlabel='x (m)',xlim=(-.65,.65),ylim=(0,7))
    ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('y (m)')
axes[1].legend(fontsize=8,loc='center',bbox_to_anchor=(.5,-.16))
fig.suptitle('Central pipe check from saved meshes\nCell centre samples near z = 0; both pipe cores are empty',fontsize=11)
fig.savefig(OUT/('selected-central-pipe-comparison.png' if args.selected else 'central-pipe-comparison.png'),dpi=180)
