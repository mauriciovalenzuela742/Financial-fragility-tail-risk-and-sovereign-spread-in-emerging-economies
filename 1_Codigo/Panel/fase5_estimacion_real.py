"""
Fase V sobre DATOS REALES — estimación de la ecuación con triple interacción (OI × datos).
Une la arista de Organización Industrial con los paneles empíricos: prueba H4a (β3>0,
complementariedad JLoss×D) y H4b (β4>0, amplificación por concentración HHI).

Insumos (formato plantilla, generados desde Panel_final_all17 / Panel_extended_15paises):
  panel_real_final17.csv  (5 países LatAm)   — con controles domésticos (debt)
  panel_real_ext11.csv    (11 países)        — sin controles domésticos
Columnas: country,time,quarter,EMBI,JLoss,D(=-GaR),HHI(estructural),HHI_anual,debt,growth_q,gfac
HHI: concentración bancaria GFDD (ratio 3 bancos). 'HHI' = MEDIANA por país (nivel estructural,
robusto a los quiebres de fuente del GFDD); 'HHI_anual' = serie anual (robustez, con quiebres).

Uso: python fase5_estimacion_real.py
Requiere: pandas, numpy, linearmodels, matplotlib.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS

XCOLS = ['JLoss_c','D_c','JL_D','JL_D_H','JL_H','D_H']

def prep(df, hhicol):
    df = df.dropna(subset=['EMBI','JLoss','D',hhicol]).copy()
    for v in ['JLoss','D']: df[v+'_c'] = df[v]-df[v].mean()
    df['HHI_c'] = df[hhicol]-df[hhicol].mean()
    df['JL_D']  = df['JLoss_c']*df['D_c']
    df['JL_D_H']= df['JL_D']*df['HHI_c']
    df['JL_H']  = df['JLoss_c']*df['HHI_c']
    df['D_H']   = df['D_c']*df['HHI_c']
    return df

def fit_twfe(df, hhicol, use_debt):
    d = prep(df, hhicol)
    ctrl = ' + debt' if (use_debt and 'debt' in d and d['debt'].notna().all()) else ''
    m = PanelOLS.from_formula(
        f'EMBI ~ {" + ".join(XCOLS)}{ctrl} + EntityEffects + TimeEffects',
        d.set_index(['country','time'])).fit(cov_type='clustered', cluster_entity=True)
    mean_h = d[hhicol].mean()
    me = lambda h: m.params['JL_D'] + m.params['JL_D_H']*(h-mean_h)
    return d, m, me

# --- bootstrap de bloques (países) y leave-one-out en numpy rápido ---
def _b4_fast(arr):   # arr cols: EMBI,JLoss,D,HHI,tc,ent
    E,J,D,H = arr[:,0],arr[:,1],arr[:,2],arr[:,3]; tc=arr[:,4].astype(int); ent=arr[:,5].astype(int)
    Jc,Dc,Hc = J-J.mean(),D-D.mean(),H-H.mean(); JD=Jc*Dc
    A = np.column_stack([E,Jc,Dc,JD,JD*Hc,Jc*Hc,Dc*Hc])
    ne,nt = ent.max()+1,tc.max()+1
    ce=np.maximum(np.bincount(ent,minlength=ne),1); ct=np.maximum(np.bincount(tc,minlength=nt),1)
    for _ in range(12):
        for co,cn,ng in ((ent,ce,ne),(tc,ct,nt)):
            m=np.empty((ng,A.shape[1]))
            for j in range(A.shape[1]): m[:,j]=np.bincount(co,weights=A[:,j],minlength=ng)/cn
            A-=m[co]
    return np.linalg.lstsq(A[:,1:],A[:,0],rcond=None)[0][3]

def robustez_b4(df, hhicol, B=1000, seed=7):
    d = df.dropna(subset=['EMBI','JLoss','D',hhicol]).copy()
    qc={q:i for i,q in enumerate(sorted(d['quarter'].unique()))}; d['tc']=d['quarter'].map(qc)
    blocks={c:g[['EMBI','JLoss','D',hhicol,'tc']].values for c,g in d.groupby('country')}
    cs=list(blocks)
    def stack(names):
        parts=[np.column_stack([blocks[c], np.full(len(blocks[c]),k)]) for k,c in enumerate(names)]
        return np.vstack(parts)
    base=_b4_fast(stack(cs))
    loo={c:_b4_fast(stack([x for x in cs if x!=c])) for c in cs}
    rng=np.random.default_rng(seed); bs=[]
    for _ in range(B):
        try: bs.append(_b4_fast(stack(list(rng.choice(cs,len(cs),True)))))
        except Exception: pass
    bs=np.array(bs)
    return dict(b4=base, loo=loo, p_pos=float(np.mean(bs>0)),
                ci=(float(np.percentile(bs,5)),float(np.percentile(bs,95))), B=len(bs))

def run(path, tag, use_debt):
    df=pd.read_csv(path)
    print(f"\n{'='*70}\n{tag}  ({df.country.nunique()} países, n={len(df)})\n{'='*70}")
    rows=[]
    for hhicol,lbl in [('HHI','estructural (mediana, limpio)'),('HHI_anual','anual (con quiebres GFDD)')]:
        d,m,me=fit_twfe(df,hhicol,use_debt)
        lo,hi=d[hhicol].quantile(.1),d[hhicol].quantile(.9)
        print(f"\n-- HHI {lbl} --")
        print(f"  β3 (JLoss×D)      = {m.params['JL_D']:+.2f}  (t={m.tstats['JL_D']:+.2f})")
        print(f"  β4 (JLoss×D×HHI)  = {m.params['JL_D_H']:+.1f}  (t={m.tstats['JL_D_H']:+.2f})   <-- amplificación (H4b)")
        print(f"  ∂²EMBI/∂JLoss∂D:  baja conc={me(lo):+.2f}  |  alta conc={me(hi):+.2f}")
        rb=robustez_b4(df,hhicol,B=1000)
        print(f"  robustez β4: P(β4>0) boot={rb['p_pos']:.0%}  IC90=[{rb['ci'][0]:+.0f},{rb['ci'][1]:+.0f}]  "
              f"LOO rango=[{min(rb['loo'].values()):+.0f},{max(rb['loo'].values()):+.0f}]")
        rows.append(dict(base=tag,HHI=lbl,b3=m.params['JL_D'],t3=m.tstats['JL_D'],
                         b4=m.params['JL_D_H'],t4=m.tstats['JL_D_H'],
                         me_baja=me(lo),me_alta=me(hi),P_b4_pos=rb['p_pos']))
    return rows, (d,m)

if __name__=='__main__':
    all_rows=[]
    r1,_=run('panel_real_final17.csv','Panel final all17 (5 países)', use_debt=True); all_rows+=r1
    r2,(dext,mext)=run('panel_real_ext11.csv','Panel extendido (11 países)', use_debt=False); all_rows+=r2
    pd.DataFrame(all_rows).to_csv('fase5_real_resultados.csv', index=False)

    # figura: efecto marginal de la complementariedad vs concentración (panel extendido, HHI estructural)
    d,m,me=fit_twfe(pd.read_csv('panel_real_ext11.csv'),'HHI',False)
    hs=np.linspace(d['HHI'].quantile(.05),d['HHI'].quantile(.95),50)
    plt.figure(figsize=(8,5)); plt.axhline(0,color='grey',lw=.8)
    plt.plot(hs*100,[me(h) for h in hs],color='#1f3b73',lw=2.2)
    plt.xlabel('Concentración bancaria (ratio 3 bancos, %)')
    plt.ylabel(r'$\partial^2 EMBI/\partial JLoss\,\partial D$  (complementariedad)')
    plt.title('Prop. 4 / H4b — la complementariedad JLoss×riesgo-de-cola\ncrece con la concentración bancaria (panel 11 países)')
    plt.tight_layout(); plt.savefig('fase5_real_amplificacion.png',dpi=140,bbox_inches='tight')
    print('\nGuardado: fase5_real_resultados.csv y fase5_real_amplificacion.png')
