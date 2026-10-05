"""Build the separate authorized hydraulic benchmark after preserving the separator."""
from pathlib import Path
import sys,json,fcntl,signal
sys.path.insert(0,str(Path.cwd()/'PyAnsys/scripts/setup'))
from build_phase09_pool import *
from pyansys_fluent.remote_text import write_ascii_text_new
s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
f=open('PyAnsys/output/phase09-preflight/server1.lock','a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
r=json.loads(Path('PyAnsys/output/drainage-benchmark/restore-parent.json').read_text());assert remote_file_exists(s,r['case'])
path='C:/Users/qtra338/P4P/experiments/phase-09-steady-vof-pool/case-data/diagnostic-duct-20260930.msh'
write_ascii_text_new(s,path,Path('PyAnsys/output/drainage-benchmark/duct.msh').read_text());s.settings.file.read_mesh(file_name=path)
a=s.settings.setup
a.models.multiphase.model='none';a.models.viscous.model='laminar';a.models.energy.enabled=False;a.general.operating_conditions.gravity.enable=False;a.general.operating_conditions.operating_pressure=1120000
b=s.settings.solution
m=a.materials.fluid;m.create(name='benchmark-liquid');m['benchmark-liquid'].density.value=881.77;m['benchmark-liquid'].viscosity.value=145.96e-6;a.cell_zone_conditions.fluid['fluid'].general.material='benchmark-liquid'
a.boundary_conditions.set_zone_type(zone_list=['outlet'],new_type='outlet-vent');v=a.boundary_conditions.outlet_vent['outlet'].momentum;v.loss_coefficient.option='constant';v.loss_coefficient.value=0;v.gauge_pressure.value=0;v.backflow_pressure_spec='Static Pressure'
b.methods.p_v_coupling.flow_scheme='SIMPLE'
