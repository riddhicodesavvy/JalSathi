"""Create data-derived SVG EDA plots; reads but never modifies source CSV."""
from pathlib import Path
from html import escape
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'reports'/'eda'; OUT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(ROOT/'water_potability.csv'); features=[c for c in df if c!='Potability']
W,H=1100,680; BLUE='#2563eb'; GREEN='#059669'; INK='#18212f'
def start(title,sub=''):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="white"/>',f'<text x="50" y="42" font-family="Arial" font-size="24" font-weight="bold" fill="{INK}">{escape(title)}</text>',f'<text x="50" y="68" font-family="Arial" font-size="14" fill="#536170">{escape(sub)}</text>']
def tx(x,y,s,size=12,anchor='middle',color=INK,rot=None):
 t=f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
 return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="Arial" font-size="{size}" fill="{color}"{t}>{escape(str(s))}</text>'
def save(name,p):
 p.append('</svg>'); (OUT/name).write_text('\n'.join(p),encoding='utf8')
def panels(title,subtitle,filename,kind):
 p=start(title,subtitle); cw,ch=330,165; x0,y0=75,108
 for idx,c in enumerate(features):
  row,col=divmod(idx,3); x=x0+col*350; y=y0+row*185; vals=df[c].dropna(); lo=float(vals.min()); hi=float(vals.max()); span=hi-lo or 1
  px=x+20; py=y+30; pw=285; ph=110
  p.append(tx(x+cw/2,y+17,c,14))
  p.append(f'<line x1="{px}" y1="{py+ph}" x2="{px+pw}" y2="{py+ph}" stroke="#334155"/>')
  if kind in ('hist','byclass'):
   bins=20; classes=[None] if kind=='hist' else [0,1]; groups=[]
   for k in classes:
    v=vals if k is None else df.loc[df.Potability==k,c].dropna(); cnt=[0]*bins
    for z in v: cnt[min(bins-1,int((z-lo)/span*bins))]+=1
    groups.append((k,cnt))
   m=max(max(a) for _,a in groups) or 1
   for k,cnt in groups:
    color='#94a3b8' if k is None else (BLUE if k==0 else GREEN)
    for b,n in enumerate(cnt):
     bh=n/m*ph; p.append(f'<rect x="{px+b*pw/bins:.1f}" y="{py+ph-bh:.1f}" width="{pw/bins-1:.1f}" height="{bh:.1f}" fill="{color}" fill-opacity=".65"/>')
  elif kind in ('box','target'):
   groups=[(None,vals)] if kind=='box' else [(k,df.loc[df.Potability==k,c].dropna()) for k in (0,1)]
   for gi,(k,v) in enumerate(groups):
    q1,q2,q3=v.quantile([.25,.5,.75]); xx=px+pw*(.5 if k is None else (.28+.44*gi)); color=BLUE if k in (None,0) else GREEN
    yy=lambda z: py+ph-(z-lo)/span*ph
    p += [f'<line x1="{xx}" y1="{yy(v.min()):.1f}" x2="{xx}" y2="{yy(v.max()):.1f}" stroke="{color}"/>',f'<rect x="{xx-28}" y="{yy(q3):.1f}" width="56" height="{yy(q1)-yy(q3):.1f}" fill="{color}" fill-opacity=".25" stroke="{color}"/>',f'<line x1="{xx-28}" y1="{yy(q2):.1f}" x2="{xx+28}" y2="{yy(q2):.1f}" stroke="{color}" stroke-width="3"/>']
    if k is not None:p.append(tx(xx,py+ph+14,k,10))
  elif kind=='points':
   for k,color in [(0,BLUE),(1,GREEN)]:
    v=df.loc[df.Potability==k,c].dropna()
    for i,z in enumerate(v):
     xx=px+(i/max(1,len(v)-1))*pw; yy=py+ph-(z-lo)/span*ph
     p.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="1.4" fill="{color}" fill-opacity=".35"/>')
  p += [tx(px,py+ph+15,f'{lo:.3g}',9,'start','#64748b'),tx(px+pw,py+ph+15,f'{hi:.3g}',9,'end','#64748b')]
 save(filename,p)

# class distribution
p=start('Potability class distribution','Observed dataset target counts (0 = non-potable; 1 = potable)'); counts=df.Potability.value_counts().sort_index(); base=560; scale=400/counts.max()
for i,(k,n) in enumerate(counts.items()):
 x=300+i*300; bh=n*scale; color=BLUE if k==0 else GREEN
 p += [f'<rect x="{x}" y="{base-bh:.1f}" width="150" height="{bh:.1f}" fill="{color}"/>',tx(x+75,base-bh-12,f'{n:,} ({n/len(df):.1%})',16),tx(x+75,base+25,['Non-potable (0)','Potable (1)'][k],14)]
save('01_class_distribution.svg',p)

# missingness heatmap
p=start('Missing-value heatmap','Blue = observed; pink = missing. Horizontal position represents sample order.'); x0,y0,w,rh=175,115,860,36
for j,c in enumerate(df):
 p.append(tx(160,y0+j*rh+22,c,13,'end')); p.append(f'<rect x="{x0}" y="{y0+j*rh}" width="{w}" height="25" fill="{BLUE}"/>')
 for i in range(len(df)):
  if pd.isna(df.iloc[i,j]): p.append(f'<rect x="{x0+i*w/len(df):.2f}" y="{y0+j*rh}" width="{w/len(df)+.15:.2f}" height="25" fill="#fecaca"/>')
save('02_missingness_heatmap.svg',p)

# correlation heatmap
corr=df.corr(numeric_only=True); p=start('Pearson correlation heatmap','Descriptive linear association only; correlation does not establish causation.'); left,top,cell=265,130,55
for i,r in enumerate(corr.index):
 p.append(tx(left-8,top+i*cell+34,r,11,'end')); p.append(tx(left+i*cell+cell/2,top-8,r,10,rot=-50))
 for j,c in enumerate(corr.columns):
  v=corr.loc[r,c]; red=int(255*(1-max(v,0))); blue=int(255*(1+min(v,0))); green=int(255*(1-abs(v))); fill=f'#{red:02x}{green:02x}{blue:02x}'; xx=left+j*cell; yy=top+i*cell
  p += [f'<rect x="{xx}" y="{yy}" width="{cell}" height="{cell}" fill="{fill}" stroke="white"/>',tx(xx+cell/2,yy+33,f'{v:.2f}',11)]
save('03_correlation_heatmap.svg',p)
panels('Feature distributions','Observed values; histograms exclude missing observations.','04_feature_distributions.svg','hist')
panels('Feature boxplots','1.5 x IQR flags are screening hints, not proof that a measurement is invalid.','05_feature_boxplots.svg','box')
panels('Feature distributions by potability','Overlaid histograms: blue = label 0; green = label 1.','06_distributions_by_potability.svg','byclass')
panels('Feature versus target: class boxplots','Blue = label 0; green = label 1; descriptive, not causal.','07_feature_target_boxplots.svg','target')
panels('Feature versus target: sample points','Each dot is one observed row; color marks target class.','08_feature_target_points.svg','points')

# numeric diagnostic table
rows=[]
for c in features:
 s=df[c]; v=s.dropna(); q1,q3=v.quantile([.25,.75]); lo=q1-1.5*(q3-q1); hi=q3+1.5*(q3-q1)
 rows.append({'feature':c,'count':s.count(),'missing':s.isna().sum(),'missing_pct':100*s.isna().mean(),'min':s.min(),'max':s.max(),'mean':s.mean(),'median':s.median(),'std_sample':s.std(),'zeros':(s==0).sum(),'negative':(s<0).sum(),'iqr_flag_count':((s<lo)|(s>hi)).sum(),'iqr_lower':lo,'iqr_upper':hi})
pd.DataFrame(rows).to_csv(OUT/'feature_diagnostics.csv',index=False)
print(f'Generated 8 SVG figures and feature_diagnostics.csv in {OUT}')
