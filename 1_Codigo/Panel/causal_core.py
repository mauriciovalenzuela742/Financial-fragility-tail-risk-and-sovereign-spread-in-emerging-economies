"""Núcleo de identificación causal — funciones probadas, reutilizadas por los notebooks.
Métodos: (A) wild cluster bootstrap, (B) proyecciones locales estado-dependientes,
(C) triple interacción con instituciones, (D) IV shift-share con FE dobles."""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')

CTRL_CAND = ['debt_gdp','fisc_bal','res_gdp','ca_gdp','infl_yoy','reer']

def load(infile):
    P = pd.read_csv(infile); P['country'] = P['country'].str.lower()
    P['pi'] = pd.PeriodIndex(P['quarter'], freq='Q')
    P['t']  = P['pi'].dt.to_timestamp(); P['year'] = P['pi'].dt.year
    P = P.sort_values(['country','pi']).reset_index(drop=True)
    P['GaR_pp'] = P['GaR']*100
    if 'ES' in P: P['ES_pp'] = P['ES']*100
    for v in ['JLoss','GaR_pp'] + (['ES_pp'] if 'ES_pp' in P else []):
        P[v+'_c'] = P[v] - P[v].mean()
    P['JxG_c'] = P['JLoss_c']*P['GaR_pp_c']
    if 'ES_pp_c' in P: P['JxES_c'] = P['JLoss_c']*P['ES_pp_c']
    P['dJLoss'] = P.groupby('country')['JLoss'].diff()
    P['EMBI_lag'] = P.groupby('country')['EMBI_bps'].shift(1)
    return P

def ctrls_in(P): return [c for c in CTRL_CAND if c in P.columns and P[c].notna().sum()>0]

# ---------- utilería: demean two-way (within país + tiempo), robusto a desbalance ----------
def demean2(d, cols, ent='country', tim='quarter', iters=30):
    X = d[cols].astype(float).copy()
    for _ in range(iters):
        X = X - X.groupby(d[ent].values).transform('mean')
        X = X - X.groupby(d[tim].values).transform('mean')
    return X

def cluster_se(Xd, e, clusters, XtX_inv):
    # SE cluster-robusto (por país) para OLS sobre datos ya demean-eados
    k = Xd.shape[1]; meat = np.zeros((k,k))
    for g in np.unique(clusters):
        m = clusters==g; Xg = Xd[m]; eg = e[m]
        s = Xg.T @ eg; meat += np.outer(s,s)
    G = len(np.unique(clusters)); n,k2 = Xd.shape
    adj = (G/(G-1))*((n-1)/(n-k2))
    V = XtX_inv @ meat @ XtX_inv * adj
    return V

# ---------- (A) WILD CLUSTER BOOTSTRAP (restringido, Rademacher) ----------
def wild_cluster_boot(P, key='JxG_c', regs=('JLoss_c','GaR_pp_c','JxG_c'), ctrls=None, B=999, seed=7):
    ctrls = ctrls or []
    cols = list(regs) + ctrls
    d = P.dropna(subset=['EMBI_bps']+cols).copy()
    clusters = d['country'].values
    yv = demean2(d, ['EMBI_bps'], iters=40)['EMBI_bps'].values
    Xd = demean2(d, cols, iters=40).values
    ki = cols.index(key)
    XtX_inv = np.linalg.inv(Xd.T@Xd)
    beta = XtX_inv @ (Xd.T@yv); e = yv - Xd@beta
    V = cluster_se(Xd, e, clusters, XtX_inv); se = np.sqrt(V[ki,ki]); t_obs = beta[ki]/se
    # modelo restringido (key=0): quitar columna key
    keep = [i for i in range(len(cols)) if i!=ki]; Xr = Xd[:,keep]
    br = np.linalg.lstsq(Xr, yv, rcond=None)[0]; fit_r = Xr@br; res_r = yv - fit_r
    rng = np.random.default_rng(seed); uniq = np.unique(clusters)
    tb = np.empty(B)
    for b in range(B):
        w = rng.choice([-1.0,1.0], size=len(uniq)); wmap = dict(zip(uniq,w))
        wv = np.array([wmap[c] for c in clusters])
        ystar = fit_r + wv*res_r
        bstar = XtX_inv @ (Xd.T@ystar); estar = ystar - Xd@bstar
        Vs = cluster_se(Xd, estar, clusters, XtX_inv)
        tb[b] = bstar[ki]/np.sqrt(Vs[ki,ki])   # H0: key=0
    p = np.mean(np.abs(tb) >= abs(t_obs))
    return dict(theta=beta[ki], se_cluster=se, t=t_obs, p_wildboot=p, B=B, G=len(uniq), n=len(yv))

# ---------- (B) PROYECCIONES LOCALES ESTADO-DEPENDIENTES ----------
def local_projections(P, H=8, sev_pct=0.30, ctrls=None):
    ctrls = ctrls or []
    thr = P['GaR_pp'].quantile(sev_pct)
    P = P.copy(); P['Rsev'] = (P['GaR_pp'] <= thr).astype(float)
    P['dJ_S'] = P['dJLoss']*P['Rsev']; P['dJ_B'] = P['dJLoss']*(1-P['Rsev'])
    base_cols = ['dJ_S','dJ_B','GaR_pp_c','EMBI_lag'] + ctrls
    out = []
    for h in range(H+1):
        d = P.copy()
        d['y'] = d.groupby('country')['EMBI_bps'].shift(-h)
        cols = ['y'] + base_cols
        d = d.dropna(subset=cols)
        if d['country'].nunique() < 2 or len(d) < len(base_cols)+5:
            out.append((h, np.nan,np.nan,np.nan,np.nan)); continue
        yv = demean2(d, ['y'])['y'].values
        Xd = demean2(d, base_cols).values
        XtX_inv = np.linalg.inv(Xd.T@Xd); beta = XtX_inv@(Xd.T@yv); e = yv-Xd@beta
        V = cluster_se(Xd, e, d['country'].values, XtX_inv)
        iS, iB = base_cols.index('dJ_S'), base_cols.index('dJ_B')
        out.append((h, beta[iS], np.sqrt(V[iS,iS]), beta[iB], np.sqrt(V[iB,iB])))
    return pd.DataFrame(out, columns=['h','beta_sev','se_sev','beta_ben','se_ben']), thr

# ---------- (C) TRIPLE INTERACCIÓN CON INSTITUCIONES ----------
def triple_institucional(P, inst_file='instituciones.csv', var='rule_of_law', ctrls=None):
    ctrls = ctrls or []
    I = pd.read_csv(inst_file); I['country'] = I['country'].str.lower()
    d = P.merge(I[['country',var]], on='country', how='left').dropna(subset=[var]).copy()
    d[var+'_z'] = (d[var]-d[var].mean())/d[var].std()
    d['J_I']   = d['JLoss_c']*d[var+'_z']
    d['G_I']   = d['GaR_pp_c']*d[var+'_z']
    d['JxG_I'] = d['JxG_c']*d[var+'_z']          # <- triple: cómo cambia la amplificación con instituciones
    regs = ['JLoss_c','GaR_pp_c','JxG_c','J_I','G_I','JxG_I'] + ctrls
    d = d.dropna(subset=['EMBI_bps']+regs)
    yv = demean2(d, ['EMBI_bps'])['EMBI_bps'].values
    Xd = demean2(d, regs).values
    XtX_inv = np.linalg.inv(Xd.T@Xd); beta = XtX_inv@(Xd.T@yv); e = yv-Xd@beta
    V = cluster_se(Xd, e, d['country'].values, XtX_inv)
    res = {}
    for name in ['JxG_c','JxG_I','J_I']:
        i = regs.index(name); res[name] = (beta[i], np.sqrt(V[i,i]), beta[i]/np.sqrt(V[i,i]))
    res['_meta'] = dict(var=var, n=len(yv), paises=d['country'].nunique())
    return res

# ---------- (D) IV SHIFT-SHARE con FE dobles ----------
def _first_stage_F(P, global_var, ctrls, pre_year=2016):
    d = P.dropna(subset=['EMBI_bps','JLoss_c','GaR_pp_c', global_var]).copy()
    phi = {}
    for c, gg in d[d.year < pre_year].groupby('country'):
        phi[c] = np.polyfit(gg[global_var], gg['JLoss'], 1)[0] if (len(gg)>5 and gg[global_var].std()>0) else np.nan
    gm = np.nanmean(list(phi.values()))
    d['phi'] = d['country'].map(lambda c: phi.get(c, gm)); d['phi']=d['phi'].fillna(gm)
    d['Z'] = d['phi']*d[global_var]
    exog = ['GaR_pp_c']+ctrls
    dd = d.dropna(subset=['EMBI_bps','JLoss_c']+exog+['Z'])
    dm = demean2(dd, ['JLoss_c']+exog+['Z'])
    Xf = dm[exog+['Z']].values; jf = dm['JLoss_c'].values     # primera etapa del NIVEL (un instrumento)
    bf = np.linalg.lstsq(Xf, jf, rcond=None)[0]; sf=(jf-Xf@bf)@(jf-Xf@bf)
    Xr = dm[exog].values; br=np.linalg.lstsq(Xr, jf, rcond=None)[0]; sr=(jf-Xr@br)@(jf-Xr@br)
    return ((sr-sf)/1)/(sf/(len(jf)-Xf.shape[1]))

def iv_shiftshare(P, global_var='auto', ctrls=None, pre_year=2016,
                  candidatos=('UST10Y_log','VIX','VIX_cboe','OnOffRun_spread_log','X_global_idx',
                              'USD_NEER_log')):
    from linearmodels.iv import IV2SLS
    ctrls = ctrls or []
    if global_var == 'auto':   # elige el shock global con primera etapa más fuerte
        cand = [g for g in candidatos if g in P.columns and P[g].notna().sum()>0]
        Fs = {g: _first_stage_F(P, g, ctrls, pre_year) for g in cand}
        global_var = max(Fs, key=Fs.get)
    d = P.dropna(subset=['EMBI_bps','JLoss_c','GaR_pp_c', global_var]).copy()
    g = d.groupby('country')
    # exposición φ_i: sensibilidad de JLoss al shock global en pre-periodo
    phi = {}
    for c, gg in d[d.year < pre_year].groupby('country'):
        if len(gg) > 5 and gg[global_var].std()>0:
            phi[c] = np.polyfit(gg[global_var], gg['JLoss'], 1)[0]
        else: phi[c] = np.nan
    gm = np.nanmean(list(phi.values()))
    d['phi'] = d['country'].map(lambda c: phi.get(c, gm)); d['phi']=d['phi'].fillna(gm)
    d['Z']  = d['phi']*d[global_var]                 # instrumento shift-share
    d['ZxG']= d['Z']*d['GaR_pp_c']                   # instrumento para la interacción
    exog = ['GaR_pp_c'] + ctrls
    dd = d.dropna(subset=['EMBI_bps','JLoss_c','JxG_c','Z','ZxG']+exog).copy()
    dm = demean2(dd, ['EMBI_bps','JLoss_c','JxG_c','Z','ZxG']+exog); dm['country']=dd['country'].values
    from numpy.linalg import lstsq
    # primera etapa (F) para JLoss_c usando Z
    Xf = dm[exog+['Z']].values; jf = dm['JLoss_c'].values
    bf = lstsq(Xf, jf, rcond=None)[0]; sf=(jf-Xf@bf)@(jf-Xf@bf)
    Xr = dm[exog].values; br=lstsq(Xr, jf, rcond=None)[0]; sr=(jf-Xr@br)@(jf-Xr@br)
    Fstat = ((sr-sf)/1)/(sf/(len(jf)-Xf.shape[1]))
    out = dict(shock_global=global_var, F_primera=Fstat, n=len(dm), paises=dd['country'].nunique())
    # (D1) IV de NIVEL: un solo endógeno (JLoss_c), instrumento Z  -> objeto causal creíble
    try:
        m1 = IV2SLS(dm['EMBI_bps'], dm[exog], dm[['JLoss_c']], dm[['Z']]).fit(cov_type='clustered', clusters=dm['country'])
        out.update(beta_JLoss_IV=m1.params['JLoss_c'], se_JLoss=m1.std_errors['JLoss_c'], p_JLoss=m1.pvalues['JLoss_c'])
    except Exception as ex:
        out['error_nivel'] = str(ex)[:60]
    # (D2) IV con interacción (dos endógenos): reportado con cautela (segundo instrumento débil)
    try:
        m2 = IV2SLS(dm['EMBI_bps'], dm[exog], dm[['JLoss_c','JxG_c']], dm[['Z','ZxG']]).fit(cov_type='clustered', clusters=dm['country'])
        out.update(theta_IV=m2.params['JxG_c'], se_theta_IV=m2.std_errors['JxG_c'])
    except Exception as ex:
        out['theta_IV']=float('nan')
    return out

def _shift_share_Z(P, global_var, pre_year):
    """phi_c (exposicion pre-periodo) * global_var_t -> instrumento shift-share."""
    d = P.copy()
    phi = {}
    for c, gg in d[d.year < pre_year].groupby('country'):
        if len(gg) > 5 and gg[global_var].std() > 0:
            phi[c] = np.polyfit(gg[global_var], gg['JLoss'], 1)[0]
        else:
            phi[c] = np.nan
    gm = np.nanmean(list(phi.values()))
    d['phi'] = d['country'].map(lambda c: phi.get(c, gm)); d['phi'] = d['phi'].fillna(gm)
    return d['phi'] * d[global_var]

def iv_shiftshare_overid(P, global_vars, ctrls=None, pre_year=2012):
    """IV shift-share SOBRE-IDENTIFICADO: un instrumento Z_g = phi_c(g) * g_t por cada
    shock global en `global_vars` (>=2), un solo endogeno (JLoss_c a nivel). Reporta
    el F de la 1a etapa de cada instrumento por separado, el F conjunto, el efecto de
    nivel 2SLS y el test de Sargan de sobre-identificacion (nulo: instrumentos validos)."""
    from linearmodels.iv import IV2SLS
    ctrls = ctrls or []
    d = P.dropna(subset=['EMBI_bps','JLoss_c','GaR_pp_c']+list(global_vars)).copy()
    zcols = []
    for g in global_vars:
        zc = f'Z_{g}'
        d[zc] = _shift_share_Z(d, g, pre_year)
        zcols.append(zc)
    exog = ['GaR_pp_c'] + ctrls
    dd = d.dropna(subset=['EMBI_bps','JLoss_c']+exog+zcols).copy()
    dm = demean2(dd, ['EMBI_bps','JLoss_c']+exog+zcols); dm['country'] = dd['country'].values

    # F individual de cada instrumento (controlando por los demas exog, sin los otros Z)
    Fs = {}
    for zc in zcols:
        Xf = dm[exog+[zc]].values; jf = dm['JLoss_c'].values
        bf = np.linalg.lstsq(Xf, jf, rcond=None)[0]; sf=(jf-Xf@bf)@(jf-Xf@bf)
        Xr = dm[exog].values; br=np.linalg.lstsq(Xr, jf, rcond=None)[0]; sr=(jf-Xr@br)@(jf-Xr@br)
        Fs[zc] = ((sr-sf)/1)/(sf/(len(jf)-Xf.shape[1]))
    # F conjunto (todos los Z a la vez)
    Xf = dm[exog+zcols].values; jf = dm['JLoss_c'].values
    bf = np.linalg.lstsq(Xf, jf, rcond=None)[0]; sf=(jf-Xf@bf)@(jf-Xf@bf)
    Xr = dm[exog].values; br=np.linalg.lstsq(Xr, jf, rcond=None)[0]; sr=(jf-Xr@br)@(jf-Xr@br)
    F_joint = ((sr-sf)/len(zcols))/(sf/(len(jf)-Xf.shape[1]))

    out = dict(instrumentos=list(global_vars), F_individual=Fs, F_conjunto=F_joint,
              n=len(dm), paises=dd['country'].nunique(), pre_year=pre_year)
    m2 = IV2SLS(dm['EMBI_bps'], dm[exog], dm[['JLoss_c']], dm[zcols]).fit(
        cov_type='clustered', clusters=dm['country'])
    out.update(beta_JLoss_IV=m2.params['JLoss_c'], se_JLoss=m2.std_errors['JLoss_c'],
              p_JLoss=m2.pvalues['JLoss_c'])
    try:
        out.update(sargan_stat=m2.sargan.stat, sargan_p=m2.sargan.pval)
    except Exception as ex:
        out['sargan_error'] = str(ex)[:80]
    return out

if __name__ == '__main__':
    import sys
    f = sys.argv[1] if len(sys.argv)>1 else 'Panel_final_all17.csv'
    P = load(f); ctr = ctrls_in(P)
    print(f'=== {f} | países={P.country.nunique()} | controles={len(ctr)} ===')
    print('[A] wild cluster bootstrap (B=199):')
    print('   ', wild_cluster_boot(P, ctrls=ctr, B=199))
    print('[B] local projections (h=0..6):')
    lp,thr = local_projections(P, H=6, ctrls=ctr); print(lp.round(2).to_string(index=False)); print('    umbral severo GaR_pp<=%.2f'%thr)
    print('[C] triple institucional (rule_of_law):')
    print('   ', triple_institucional(P, ctrls=ctr))
    print('[D] IV shift-share (X_global_idx):')
    print('   ', iv_shiftshare(P, ctrls=ctr))
