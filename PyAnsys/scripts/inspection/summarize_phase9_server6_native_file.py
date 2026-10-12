"""Stream a Server6 transcript and hash its pair on the host; no Fluent commands."""
import argparse,hashlib,json,math,re,shutil
from pathlib import Path
FILM=re.compile(r'Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)')
INNER=re.compile(r'sub-iteration:\s*(\d+) residual - h:\s*([^;]+); u:\s*([^;]+); v:\s*(\S+)')
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 m=json.loads(Path(a.manifest).read_text());path=Path(m['active_transcript']);n=0;peak=0.;first=last=None;inner=None;observed=passed=0;bad=[];finite=clocks=True;fatal=[];clock=m['accepted_film_s'];dt=m['active_step_s']
 with path.open(errors='replace') as f:
  for line in f:
   if re.search(r'floating point exception|fatal error|received signal|Divergence detected',line,re.I):fatal.append(line.strip()[:300])
   r=INNER.search(line)
   if r:inner=[float(r[k].strip()) for k in [2,3,4]]
   r=FILM.search(line)
   if r:
    row=[float(v) for v in r.groups()];n+=1;first=first or row;last=row;peak=max(peak,row[2]);finite&=all(math.isfinite(v) for v in row);clocks&=math.isclose(row[0],clock+n*dt,abs_tol=1e-10,rel_tol=1e-6) and math.isclose(row[1],dt,rel_tol=1e-7)
    if inner is not None:observed+=1;passed+=int(all(math.isfinite(v) and 0<=v<=1e-5 for v in inner))
    inner=None
 pair={'native_iteration':m['active_target']};files={}
 for key,suffix in [('case','cas.h5'),('data','dat.h5')]:
  f=Path(str(path)[:-3]+suffix);files[key]={'path':str(f),'exists':f.exists(),'size_bytes':f.stat().st_size if f.exists() else None};pair[key]=str(f)
  if f.exists():
   h=hashlib.sha256()
   with f.open('rb') as stream:
    for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
   pair[key+'_sha256']=h.hexdigest()
 x={'status':'HOST_NATIVE_TRANSCRIPT_AND_PAIR_SUMMARY','stage':m['active_stage'],'film_rows':n,'first_film_row':first,'last_film_row':last,'peak_courant':peak,'finite_film_rows':finite,'clocks_match':clocks,'fatal_lines':fatal,'inner_steps_observed':observed,'inner_steps_passed':passed,'pair':pair,'files':files,'transcript_size_bytes':path.stat().st_size,'disk_free_bytes':shutil.disk_usage(path.parent).free,'solver_mutations':0}
 Path(a.output).write_text(json.dumps(x,indent=2)+'\n')
if __name__=='__main__':main()
