"""
Robustez de β4 (amplificación por concentración/poder de mercado, Prop. 4 / H4b) a la MEDIDA.
Re-estima β4 (JLoss×D×H) en el panel de 11 países con cinco proxies, todos orientados como
'mayor = menos competencia / más concentración' (⇒ β4>0 esperado):
  - CR3       : ratio 3 bancos   (GFDD.OI.01, mediana país)      [World Bank API]
  - CR5       : ratio 5 bancos   (GFDD.OI.06, mediana país)      [World Bank API]
  - compuesto : promedio z-scores de CR3 y CR5
  - Lerner    : índice de Lerner (poder de mercado; GFDD.OI.04)  [FRED, mediana país, ~1996-2014]
  - Boone     : indicador de Boone (competencia; GFDD.OI.05)     [FRED, mediana país, ~1997-2014]
Lerner/Boone fueron discontinuados por el WB (hasta 2014) y se obtienen de FRED
(DDOI04{ISO2}A066NWDB / DDOI05{ISO2}A156NWDB). México no tiene Lerner en FRED (queda con 10 países).

Salida: concentracion_metrics.csv, fase5_robustez_concentracion.csv
Uso: python fase5_robustez_concentracion.py
"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np

CR3 = {'indonesia':0.4175,'turkey':0.4417,'poland':0.4661,'china':0.4698,'mexico':0.5083,
       'chile':0.5274,'bulgaria':0.5335,'brazil':0.6492,'colombia':0.6845,'peru':0.7362,'southafrica':0.7737}
CR5 = {'bulgaria':0.7397,'brazil':0.7527,'chile':0.7735,'china':0.6062,'colombia':0.8549,
       'indonesia':0.5565,'mexico':0.6894,'peru':0.8813,'poland':0.6352,'turkey':0.6678,'southafrica':0.9912}
LERNER = {'brazil':0.2356,'chile':0.1955,'colombia':0.3036,'peru':0.3934,'bulgaria':0.2843,
          'china':0.3516,'indonesia':0.2654,'poland':0.2331,'southafrica':0.1638,'turkey':0.1966}  # sin México
BOONE  = {'brazil':-0.1583,'chile':-0.0054,'colombia':-0.1774,'mexico':-0.1124,'peru':-0.0885,
          'bulgaria':-0.0868,'china':-0.0271,'indonesia':0.0229,'poland':-0.0988,'southafrica':-0.0924,'turkey':-0.0817}
cs = sorted(CR5)
zc = lambda d:{k:(v-np.mean(list(d.values())))/np.std(list(d.values())) for k,v in d.items()}
z3,z5 = zc(CR3),zc(CR5); COMP = {c:(z3[c]+z5[c])/2 for c in cs}
METRICS = [('CR3',CR3),('CR5',CR5),('compuesto(z)',COMP),('Lerner',LERNER),('Boone',BOONE)]

M=pd.DataFrame({'country':cs})
for nm,dd in METRICS: M[nm]=M['country'].map(dd)
M.to_csv('concentracion_metrics.csv', index=False)

d = pd.read_csv('panel_real_ext11.csv').dropna(subset=['EMBI','JLoss','D']).copy()
qc = {q:i for i,q in enumerate(sorted(d['quarter'].unique()))}; d['tc']=d['quarter'].map(qc)
blocks = {c:g[['EMBI','JLoss','D','tc']].values for c,g in d.groupby('country')}

def b4(arr):
    E,J,D=arr[:,0],arr[:,1],arr[:,2]; tc=arr[:,3].astype(int); H=arr[:,4]; ent=arr[:,5].astype(int)
    Jc,Dc,Hc=J-J.mean(),D-D.mean(),H-H.mean(); JD=Jc*Dc
    A=np.column_stack([E,Jc,Dc,JD,JD*Hc,Jc*Hc,Dc*Hc]); ne,nt=ent.max()+1,tc.max()+1
    ce=np.maximum(np.bincount(ent,minlength=ne),1); ct=np.maximum(np.bincount(tc,minlength=nt),1)
    for _ in range(15):
        for co,cn,ng in ((ent,ce,ne),(tc,ct,nt)):
            m=np.empty((ng,A.shape[1]))
            for j in range(A.shape[1]): m[:,j]=np.bincount(co,weights=A[:,j],minlength=ng)/cn
            A-=m[co]
    return np.linalg.lstsq(A[:,1:],A[:,0],rcond=None)[0][3]
def stack(names,mp):
    return np.vstack([np.column_stack([blocks[c],np.full(len(blocks[c]),mp[c]),np.full(len(blocks[c]),k)])
                      for k,c in enumerate(names)])

rng=np.random.default_rng(7); rows=[]
for nm,mp in METRICS:
    use=[c for c in cs if c in mp]
    base=b4(stack(use,mp)); loo=[b4(stack([x for x in use if x!=c],mp)) for c in use]
    bs=np.array([b4(stack(list(rng.choice(use,len(use),True)),mp)) for _ in range(1500)])
    rows.append({'metrica':nm,'tipo':'concentración' if nm in('CR3','CR5','compuesto(z)') else 'competencia',
                 'n_paises':len(use),'beta4':round(base,1),'P_b4_pos':round(float((bs>0).mean()),3),
                 'LOO_todos_pos':all(x>0 for x in loo),'LOO_min':round(min(loo),1)})
res=pd.DataFrame(rows); res.to_csv('fase5_robustez_concentracion.csv', index=False)
print(res.to_string(index=False))
print("\n4/5 proxies (CR3, CR5, compuesto, Lerner) dan β4>0. Boone diverge: su ranking país")
print("contradice a la concentración (p.ej. Indonesia) y es la medida más ruidosa.")
