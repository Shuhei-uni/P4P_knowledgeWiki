"""Build a minimal-text supervisor meeting PDF from verified Phase7b figures."""
from pathlib import Path
import json,hashlib
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
ROOT=Path(__file__).resolve().parents[3];E=ROOT/'PyAnsys/output/phase07b-meeting-20260922';F=E/'figures';G=ROOT/'PyAnsys/output/phase07b-g1'
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True);PDF=OUT/'phase-7b-supervisor-meeting-2026-09-22.pdf'
fonts=Path('/System/Library/Fonts/Supplemental')
for name,file in [('Arial','Arial.ttf'),('ArialBold','Arial Bold.ttf'),('ArialItalic','Arial Italic.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
W,H=landscape(A3);M=44;c=canvas.Canvas(str(PDF),pagesize=(W,H));c.setTitle('Phase 7b - Full-geometry liquid removal | Supervisor meeting');c.setAuthor('Andy | P4P');c.setSubject('G1 discovery screen: geometry, collector masks, liquid fractions, mass balance and residuals')
ink=HexColor('#182d3a');muted=HexColor('#586875');teal=HexColor('#087f86')
styles={name:ParagraphStyle(name,fontName='Arial',fontSize=size,leading=size*1.35,textColor=ink) for name,size in [('body',18),('caption',14),('small',11)]}
page=0;provenance=[]
def text(txt,x,y,width,style='body'):
 p=Paragraph(txt,styles[style]);w,h=p.wrap(width,1000);p.drawOn(c,x,y-h);return y-h

def begin(title,kicker='PHASE 7b / G1 DISCOVERY SCREEN'):
 global page
 page+=1;c.setFillColor(teal);c.setFont('ArialBold',11);c.drawString(M,H-31,kicker)
 c.setFillColor(ink);c.setFont('ArialBold',25);c.drawString(M,H-66,title)
 c.setStrokeColor(HexColor('#d7e0e4'));c.line(M,40,W-M,40);c.setFont('Arial',10);c.setFillColor(muted)
 c.drawString(M,23,'Andy | Supervisor meeting | 22 September 2026');c.drawRightString(W-M,23,str(page))
def end():c.showPage()
def figure_page(title,file,caption,source):
 begin(title);maxw=W-2*M;maxh=H-185
 with Image.open(file) as im:iw,ih=im.size
 scale=min(maxw/iw,maxh/ih);w,h=iw*scale,ih*scale
 c.drawImage(str(file),(W-w)/2,117+(maxh-h)/2,width=w,height=h,mask='auto')
 text(caption,M,100,W-2*M,'caption');text('Source: '+source,M,63,W-2*M,'small');end()
 provenance.append({'page':page,'title':title,'figure':str(file.relative_to(ROOT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'caption':caption,'source':source})

begin('Full-geometry liquid removal: what did the five cases show?','PHASE 7b / MEETING BRIEF')
y=text('<b>No tested thickness achieved an acceptable steady solution.</b>',M,H-110,W-2*M)
y=text('Four cases reached 5,000 iterations. S100 failed numerically at attempted N4183.',M,y-13,W-2*M)
y=text('Question: can a lower ideal collector remove liquid while preserving balanced, steady separator flow?',M,y-28,W-2*M)
y=text('Fixed: full geometry; steady Mixture / RNG; Energy off; split inlets; brine face closed; tau = 0.0024096 s.',M,y-11,W-2*M)
rows=[['Case','Completed iterations','Final water mass (kg)','Late liquid imbalance*','Outcome'],['S20','5,000','825.2','336.8%','Criteria failed'],['S40','5,000','707.3','252.6%','Criteria failed'],['S60','5,000','639.9','502.5%','Criteria failed'],['S80','5,000','613.3','343.6%','Criteria failed'],['S100','4,182','-','-','Diverged at attempted 4,183']]
t=Table(rows,colWidths=[90,180,210,200,W-2*M-680],rowHeights=[42]+[46]*5)
t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'ArialBold'),('FONTNAME',(0,1),(-1,-1),'Arial'),('FONTSIZE',(0,0),(-1,-1),16),('TEXTCOLOR',(0,0),(-1,-1),ink),('LINEBELOW',(0,0),(-1,0),1,teal),('LINEBELOW',(0,-1),(-1,-1),.6,HexColor('#c7d2d8')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8)]))
tw,th=t.wrap(W-2*M,H);t.drawOn(c,M,y-30-th);y=y-30-th-15
text('* Mean absolute source-inclusive liquid imbalance / feed, N4501-5000. Screening threshold: 1%.',M,y,W-2*M,'caption')
text('<b>Interpretation:</b> lower inventory alone does not establish steady collection. All completed cases also failed inventory and all-equation residual criteria.',M,y-41,W-2*M,'body')
text('<b>Next proposal:</b> hold S40 geometry fixed; test weaker removal (tau = 0.02 s, then 0.10 s). Proposed only; no new runs started.',M,y-105,W-2*M,'body');end()
figure_page('01 / Separator geometry',F/'geometry-overview.png','Native mesh surfaces and a central fluid section. The ideal collector retains the lower geometry; the physical brine-outlet face is a wall. No standing pool is required.','S100 preserved N4000 pair; native boundary and z=0 section geometry.')
figure_page('02 / What changes between the cases?',F/'collector-regions.png','Shading shows geometric removal extents, not liquid. Percentages refer to height, not volume; Fluent selects cells by centroid elevation. The dotted line is the historical cutoff at y=+0.020 m.','Verified geometry and S20-S100 elevation definitions; common lower datum y=-1.484584 m.')
figure_page('03 / All five cases: matched numerical history',G/'G1-common-history.png','Changing thickness changes inventory and removal. Larger removal is not evidence of successful collection when the source-inclusive mass balance remains open.','G1 native reports, N1-4000; all five runs. Later histories are shown separately.')
figure_page('04 / Completed cases: late inventory and mass balance',G/'G1-late-history.png','All four completed cases retain drift and strong imbalance. The source is counted once; steady-iteration inventory slopes are not physical storage rates.','S20/S40/S60/S80, N4001-5000; S100 has no complete prescribed late window.')
figure_page('05 / Full-height liquid fraction: first central plane',F/'liquid-fraction-z0-all-cases.png','Liquid fraction: 0 = no liquid; 1 = all liquid. Dashed lines locate the collectors. S100 is a recovery snapshot at N4000, not an equivalent N5000 endpoint.','Native phase-2 facet values at z=0; four final N5000 pairs and S100 recovery N4000.')
figure_page('06 / Full-height liquid fraction: orthogonal plane',F/'liquid-fraction-x0-all-cases.png','The second plane exposes azimuthal differences. These are unconverged field snapshots; use them to understand liquid distribution, not to claim validated separation efficiency.','Native phase-2 facet values at x=0; common 0-1 scale; S100 recovery N4000.')
figure_page('07 / Liquid fraction above the collector',G/'G1-spatial-phase-2-vof.png','Liquid-rich outer regions persist. Lower total inventory does not produce a uniform improvement at every height. All four planes lie above the maximum collector top.','Original G1 comparison; y=0.5, 1.5, 3 and 5 m; native facets; S100 N4000, others N5000.')
figure_page('08 / Mixture speed above the collector',G/'G1-spatial-velocity-magnitude.png','Common 0-80 m/s scale. These section snapshots do not show the full domain or the larger speed excursions recorded earlier in the runs.','Original G1 comparison; native mixture velocity magnitude; same four planes and snapshot indices.')
figure_page('09 / Liquid speed above the collector',G/'G1-spatial-phase-2-velocity-magnitude.png','Common 0-80 m/s scale. Zero liquid speed in nearly liquid-free regions is not evidence of a stagnant liquid pool.','Original G1 comparison; native phase-2 velocity magnitude; same four planes and snapshot indices.')
figure_page('10 / Residuals: every active equation',F/'residuals-completed-cases.png','All four completed cases fail the 10^-3 throughout-final-window requirement for continuity, k, epsilon and liquid fraction. The three momentum equations pass that late-window indicator.','Complete native residual histories N1-5000; seven equations; identical vertical limits across these four cases.')
figure_page('11 / S100: numerical failure',F/'residuals-S100-failure.png','S100 was already unconverged at N4000. Epsilon, pressure and velocity escalated before the floating-point exception at attempted N4183. The failure cause and repeatability are not isolated.','All seven native residuals; left N1-4100, right N4100-4182. Full N1-4182 records remain in the evidence bundle.')
# Traceability remains compact and out of the narrative.
begin('Evidence key and interpretation limits','PHASE 7b / SOURCE RECORDS')
text('All figures are derived from recorded Fluent data or verified mesh geometry. No new solve was performed for this report.',M,H-115,W-2*M)
comparison=json.loads((G/'comparison.json').read_text());y=H-175
for case,r in comparison['cases'].items():
 y=text(f'<b>{case}</b> &nbsp; {r["run"]}',M,y,W-2*M,'body')-14
text('Source of scientific interpretation: Project/experiments/phase-07b-full-geometry-liquid-removal/results.md',M,y-16,W-2*M,'caption')
text('Four N5000 endpoints; S100 recovery fields at N4000. S100 has no N5000 endpoint or complete late window. Every completed iteration is recorded; finite runaway values are not physical predictions.',M,y-70,W-2*M)
text('<b>Scope:</b> finite discovery screen, not physical validation. No case is promoted. Full reports, hashes and original figures remain linked in the project evidence.',M,y-148,W-2*M)
text('G1 graph set is retained in full. New geometry, axial liquid-fraction and residual comparisons accompany it. Separate per-case liquid-fraction images are included in the figure bundle.',M,y-228,W-2*M,'caption');end()
c.save()
receipt={'pdf':str(PDF.relative_to(ROOT)),'pages':page,'page_format':'A3 landscape for readable engineering figures','sources':provenance,'extraction':str((E/'extraction.json').relative_to(ROOT)),'g1_summary':'Project/experiments/phase-07b-full-geometry-liquid-removal/results.md','claim_limit':'Unconverged discovery; S100 fields at recovery N4000, other cases final N5000','iterations_issued_for_report':0}
(E/'report-provenance.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'pdf':str(PDF),'pages':page}))
