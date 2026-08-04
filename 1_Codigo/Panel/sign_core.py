"""Robustez del SIGNO de theta (interacción JLoss × cola).
Objetivo: defender que theta<0 es una regularidad empírica estable, sin afirmar causalidad.
Métodos: (1) menú de especificaciones/submuestras/medidas-de-cola, (2) probabilidad de
signo por bootstrap de bloques (países), (3) test de permutación del signo, (4) placebos."""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
import causal_core as cc   # reutiliza load(), demean2(), cluster_se(), ctrls_in()

def _demean(d, cols, fe, iters=40):
    if fe == 'pooled':
        X = d[cols].astype(float)
        return (X - X.mean()).values
    if fe == 'ent':
        X = d[cols].astype(float)
        return (X - X.groupby(d['country'].values).transform('mean')).values
    if fe == 'time':
        X = d[cols].astype(float)
        return (X - X.groupby(d['quarter'].values).transform('mean')).values
    return cc.demean2(d, cols, iters=iters).values   # 2way

def theta_hat(P, tail='GaR_pp', ctrls=None, fe='2way', dep='EMBI_bps', extra=None,
              flip=False, sample_mask=None, fd=False, winsor=None, iters=40):
    ctrls = ctrls or []; extra = extra or []
    d = P.copy()
    if sample_mask is not None: d = d[sample_mask].copy()
    if tail == 'GaR_st' and 'GaR_st' in d:   # llevar a pp, comparable con GaR
        d = d.assign(GaR_st=d['GaR_st']*100)
    d['tail_c'] = d[tail] - d[tail].mean()
    d['J_c']    = d['JLoss'] - d['JLoss'].mean()
    d['Jx']     = d['J_c'] * d['tail_c']
    cols = [dep, 'J_c', 'tail_c', 'Jx'] + ctrls + extra
    d = d.dropna(subset=cols)
    if winsor:
        lo, hi = d[dep].quantile(winsor), d[dep].quantile(1-winsor)
        d[dep] = d[dep].clip(lo, hi)
    if fd:  # primeras diferencias por país, luego pooled
        d = d.sort_values(['country','pi'])
        for c in [dep,'J_c','tail_c','Jx']+ctrls+extra:
            d[c] = d.groupby('country')[c].diff()
        d = d.dropna(subset=cols); fe='pooled'
    if d['country'].nunique() < 2 or len(d) < len(cols)+3: return np.nan
    y = _demean(d, [dep], fe, iters)[:,0]
    X = _demean(d, ['J_c','tail_c','Jx']+ctrls+extra, fe, iters)
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    th = beta[2]
    return -th if flip else th

# ---------- (1) MENÚ DE ESPECIFICACIONES ----------
def theta_menu(P, ctrls=None):
    ctrls = ctrls or []; rows = []
    yr = P['year']
    add = lambda name, val: rows.append({'especificación':name, 'θ':val, 'signo':'—' if pd.isna(val) else ('neg' if val<0 else 'POS')})
    add('Pooled (sin FE)',              theta_hat(P, fe='pooled'))
    add('FE país',                      theta_hat(P, fe='ent'))
    add('FE tiempo',                    theta_hat(P, fe='time'))
    add('FE país+tiempo (M2)',          theta_hat(P, fe='2way'))
    if ctrls: add('FE2 + controles (M3)', theta_hat(P, fe='2way', ctrls=ctrls))
    add('FE2 + VIX' if 'VIX' in P else 'FE2 + VIX_cboe',
        theta_hat(P, fe='2way', extra=[c for c in ['VIX','VIX_cboe'] if c in P][:1]))
    if 'X_global_idx' in P: add('FE2 + X_global_idx', theta_hat(P, fe='2way', extra=['X_global_idx']))
    if 'X_dom_idx' in P:    add('FE2 + X_dom_idx',    theta_hat(P, fe='2way', extra=['X_dom_idx']))
    add('Primeras diferencias',         theta_hat(P, fd=True, ctrls=ctrls))
    add('EMBI winsorizado 1%',          theta_hat(P, fe='2way', ctrls=ctrls, winsor=0.01))
    add('Sin COVID (≤2019)',            theta_hat(P, fe='2way', ctrls=ctrls, sample_mask=(yr<2020)))
    add('Sin 2020–21 (crisis)',         theta_hat(P, fe='2way', ctrls=ctrls, sample_mask=~yr.isin([2020,2021])))
    # medidas alternativas de cola (misma orientación: menor = peor)
    if 'ES' in P:      add('Cola = ES (FE2)',      theta_hat(P, tail='ES_pp' if 'ES_pp' in P else 'ES', fe='2way', ctrls=ctrls))
    if 'GaR_st' in P:  add('Cola = GaR skew-t',    theta_hat(P, tail='GaR_st', fe='2way', ctrls=ctrls))
    return pd.DataFrame(rows)

def theta_menu_placebos(P, ctrls=None):
    """Falsación: interacción de JLoss con la métrica de cola INVERTIDA (prob_neg, mayor=peor)
    debe dar signo OPUESTO (positivo); interacciones con variables NO-cola no deben ser
    sistemáticamente negativas."""
    ctrls = ctrls or []; rows=[]
    if 'prob_neg' in P:
        rows.append({'placebo':'prob_neg (cola invertida) → se espera POS',
                     'θ_interac': theta_hat(P, tail='prob_neg', fe='2way', ctrls=ctrls)})
    for v in ['VIX','VIX_cboe','reer','infl_yoy','g_GDP']:
        if v in P and P[v].notna().sum()>0:
            rows.append({'placebo':f'JLoss × {v} (no-cola)',
                         'θ_interac': theta_hat(P, tail=v, fe='2way', ctrls=ctrls)})
    return pd.DataFrame(rows)

# ---------- ruta rápida en numpy (bincount) para remuestreo ----------
def _blocks(P, ctrls):
    qmap = {q:i for i,q in enumerate(sorted(P['quarter'].unique()))}
    B = []
    for c, g in P.groupby('country'):
        g = g.dropna(subset=['EMBI_bps','JLoss','GaR']+ctrls)
        if len(g) < 3: continue
        arr = np.column_stack([g['EMBI_bps'].values, g['JLoss'].values, g['GaR'].values]
                              + [g[k].values for k in ctrls])
        tc = np.array([qmap[q] for q in g['quarter'].values])
        B.append((arr, tc))
    return B, len(qmap)

def _fast_demean2(A, ent, tim, ne, nt, iters=15):
    A = A.copy(); ce = np.maximum(np.bincount(ent, minlength=ne),1); ct = np.maximum(np.bincount(tim, minlength=nt),1)
    for _ in range(iters):
        for codes, cnt, ng in ((ent,ce,ne),(tim,ct,nt)):
            m = np.empty((ng, A.shape[1]))
            for j in range(A.shape[1]): m[:,j] = np.bincount(codes, weights=A[:,j], minlength=ng)/cnt
            A -= m[codes]
    return A

def _theta_blocks(blocks, nt, nctrl, permute=False, rng=None, iters=15):
    mats, ent, tim = [], [], []
    for e,(arr,tc) in enumerate(blocks):
        mats.append(arr); ent.append(np.full(len(arr), e)); tim.append(tc)
    M = np.vstack(mats); ent = np.concatenate(ent); tim = np.concatenate(tim)
    y = M[:,0]; J = M[:,1]; G = M[:,2]*100; C = M[:,3:3+nctrl]
    if permute: G = rng.permutation(G)
    Jc = J-J.mean(); Gc = G-G.mean(); Jx = Jc*Gc
    D = np.column_stack([Jc, Gc, Jx, C]) if nctrl else np.column_stack([Jc, Gc, Jx])
    A = _fast_demean2(np.column_stack([y, D]), ent, tim, len(blocks), nt, iters)
    beta = np.linalg.lstsq(A[:,1:], A[:,0], rcond=None)[0]
    return beta[2]

# ---------- (2) PROBABILIDAD DE SIGNO POR BOOTSTRAP DE BLOQUES (países) ----------
def sign_probability(P, ctrls=None, B=2000, seed=11):
    ctrls = ctrls or []; blocks, nt = _blocks(P, ctrls); nc = len(ctrls)
    th_obs = _theta_blocks(blocks, nt, nc)
    rng = np.random.default_rng(seed); ne = len(blocks); draws = np.empty(B)
    for b in range(B):
        pick = rng.integers(0, ne, size=ne)
        draws[b] = _theta_blocks([blocks[i] for i in pick], nt, nc)
    return dict(theta=th_obs, p_neg=float(np.mean(draws<0)),
                ci_lo=float(np.percentile(draws,2.5)), ci_hi=float(np.percentile(draws,97.5)),
                mediana=float(np.median(draws)), B=B, draws=draws)

# ---------- (3) TEST DE PERMUTACIÓN DEL SIGNO ----------
def permutation_sign(P, ctrls=None, B=2000, seed=3):
    ctrls = ctrls or []; blocks, nt = _blocks(P, ctrls); nc = len(ctrls)
    th_obs = _theta_blocks(blocks, nt, nc)
    rng = np.random.default_rng(seed); null = np.empty(B)
    for b in range(B): null[b] = _theta_blocks(blocks, nt, nc, permute=True, rng=rng)
    return dict(theta=th_obs, p_perm_1cola=float(np.mean(null<=th_obs)),
                null_media=float(null.mean()), null_sd=float(null.std()), B=B, null=null)

if __name__ == '__main__':
    import sys
    f = sys.argv[1] if len(sys.argv)>1 else 'Panel_final_all17.csv'
    P = cc.load(f); ctr = cc.ctrls_in(P)
    print(f'=== {f} ({P.country.nunique()} países) ===')
    m = theta_menu(P, ctr); print(m.to_string(index=False))
    neg = (m['θ']<0).sum(); tot = m['θ'].notna().sum()
    print(f'\nθ<0 en {neg}/{tot} especificaciones alineadas')
    print('\nPlacebos:'); print(theta_menu_placebos(P, ctr).to_string(index=False))
    print('\nProbabilidad de signo (bootstrap bloques, B=500):', sign_probability(P, ctr, B=500))
    print('Permutación (B=500):', permutation_sign(P, ctr, B=500))
