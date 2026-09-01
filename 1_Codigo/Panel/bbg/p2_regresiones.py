# -*- coding: utf-8 -*-
"""
p2_regresiones.py -- mecanismo JLoss x GaR sobre el CDS soberano, UN SOLO panel Bloomberg.

Insumo: bbg/Panel_bloomberg.csv  (todas las economias; la muestra efectiva son las filas
con CDS + JLoss + GaR simultaneamente).

Metodologia (identica a NUMEROS_CANONICOS): linearmodels.PanelOLS, efectos fijos pais+tiempo,
errores Driscoll-Kraay (kernel bartlett). JLoss y GaR (pp) centradas.

Salidas -> bbg/:
  tabla_theta_bbg.csv       M1 / M2 (referencia, +controles) / M3 (+globales) / cluster
  robustez_bbg.csv          pre-2020, ES, sin-COVID, sin-deuda, leave-one-out
  umbral_bbg.csv            modelo de umbral de Hansen
  efecto_marginal_bbg.csv   dEMBI/dJLoss por percentil de GaR
  diagnosticos_bbg.csv      Pesaran CD, AR(1), R2
"""
import os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL_CSV = os.path.join(HERE, "Panel_bloomberg.csv")
CTRLS = ["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]
GLOB = ["VIX", "UST10Y_log", "US_HY_spread_log"]


# Variable dependiente PRINCIPAL: spread EMBI Global (Chari et al. 2024).
# CDS_bps queda para la robustez (spec "CDS" en la tabla de robustez).
DV = "EMBI_bps"


def prep(dv=DV):
    d = pd.read_csv(PANEL_CSV)
    d["GaR_pp"] = d["GaR"] * 100.0
    if "ES" in d:
        d["ES_pp"] = d["ES"] * 100.0
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    d["year"] = pd.PeriodIndex(d["quarter"], freq="Q").year
    # muestra efectiva del mecanismo
    d = d.dropna(subset=[dv, "JLoss", "GaR_pp"]).copy()
    d["_DV"] = d[dv]
    return d


def fit(d, extra_rhs, cov, tail="GaR_pp", time_fe=True, dv="_DV"):
    dd = d.dropna(subset=[dv, "JLoss", tail] + extra_rhs).copy()
    if dd["country"].nunique() < 3 or len(dd) < 30:
        return None, None
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["tail_c"] = dd[tail] - dd[tail].mean()
    dd["JxT"] = dd["JLoss_c"] * dd["tail_c"]
    rhs = ["JLoss_c", "tail_c", "JxT"] + extra_rhs
    eff = "EntityEffects + TimeEffects" if time_fe else "EntityEffects"
    f = f"{dv} ~ {' + '.join(rhs)} + {eff}"
    md = dd.set_index(["country", "t"])
    kw = (dict(cov_type="kernel", kernel="bartlett") if cov == "dk" else
          dict(cov_type="clustered", cluster_entity=True) if cov == "pais" else
          dict(cov_type="clustered", cluster_time=True))
    m = PanelOLS.from_formula(f, md).fit(**kw)
    return m, dd


def row(m, label):
    return dict(spec=label, theta=m.params["JxT"], se=m.std_errors["JxT"],
               t=m.tstats["JxT"], p=m.pvalues["JxT"], N=int(m.nobs),
               paises=int(m.entity_info.total), b1=m.params["JLoss_c"],
               b2=m.params["tail_c"], R2w=m.rsquared_within)


def wild_boot(d, extra_rhs, B=999, seed=7):
    """wild cluster bootstrap (Rademacher, restringido) del p-valor de theta."""
    dd = d.dropna(subset=["_DV", "JLoss", "GaR_pp"] + extra_rhs).copy()
    for v in ("JLoss", "GaR_pp"):
        dd[v + "_c"] = dd[v] - dd[v].mean()
    dd["JxT"] = dd["JLoss_c"] * dd["GaR_pp_c"]
    cols = ["JLoss_c", "GaR_pp_c", "JxT"] + extra_rhs

    def dm(x):
        for _ in range(40):
            x = x - x.groupby(dd["country"].values).transform("mean")
            x = x - x.groupby(dd["quarter"].values).transform("mean")
        return x
    y = dm(dd[["_DV"]]).values.ravel()
    X = dm(dd[cols]).values
    cl = dd["country"].values
    ki = cols.index("JxT")
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ (X.T @ y); e = y - X @ beta

    def cse(resid):
        meat = np.zeros((X.shape[1],) * 2)
        for g in np.unique(cl):
            s = X[cl == g].T @ resid[cl == g]
            meat += np.outer(s, s)
        G = len(np.unique(cl))
        V = XtXi @ meat @ XtXi * (G / (G - 1)) * ((len(y) - 1) / (len(y) - X.shape[1]))
        return np.sqrt(V[ki, ki])
    t_obs = beta[ki] / cse(e)
    keep = [i for i in range(len(cols)) if i != ki]
    br = np.linalg.lstsq(X[:, keep], y, rcond=None)[0]
    fit_r = X[:, keep] @ br; res_r = y - fit_r
    rng = np.random.default_rng(seed); uniq = np.unique(cl)
    tb = []
    for _ in range(B):
        w = dict(zip(uniq, rng.choice([-1.0, 1.0], len(uniq))))
        ys = fit_r + np.array([w[c] for c in cl]) * res_r
        bs = XtXi @ (X.T @ ys); es = ys - X @ bs
        tb.append(bs[ki] / cse(es))
    return float(np.mean(np.abs(tb) >= abs(t_obs)))


def umbral_hansen(d, extra_rhs, n_grid=120):
    dd = d.dropna(subset=["_DV", "JLoss", "GaR_pp"] + extra_rhs).copy()
    def within(x):
        x = x.astype(float)
        for _ in range(30):
            x = x - x.groupby(dd["country"].values).transform("mean")
            x = x - x.groupby(dd["quarter"].values).transform("mean")
        return x
    y = within(dd[["_DV"]]).values.ravel()
    q = dd["GaR_pp"].values
    ex = within(dd[extra_rhs]).values if extra_rhs else np.empty((len(y), 0))

    def sse(gam):
        lo = (q <= gam).astype(float)
        Z = np.column_stack([within(pd.DataFrame({"a": dd["JLoss"].values * lo})).values.ravel(),
                             within(pd.DataFrame({"a": dd["JLoss"].values * (1 - lo)})).values.ravel()])
        X = np.column_stack([Z, ex])
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        return (y - X @ b) @ (y - X @ b), b
    grid = np.quantile(q, np.linspace(.10, .90, n_grid))
    best = min(((g, *sse(g)) for g in grid), key=lambda z: z[1])
    Xl = np.column_stack([within(pd.DataFrame({"a": dd["JLoss"].values})).values.reshape(-1, 1), ex])
    b0 = np.linalg.lstsq(Xl, y, rcond=None)[0]
    sse0 = (y - Xl @ b0) @ (y - Xl @ b0)
    LR = (sse0 - best[1]) / (best[1] / len(y))
    return dict(gamma=best[0], efecto_severo=best[2][0], efecto_benigno=best[2][1],
                LR=LR, N=len(y))


def main():
    d = prep()
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    print(f"Panel: {len(d)} obs, {d['country'].nunique()} paises con datos, "
          f"{d['quarter'].min()}..{d['quarter'].max()}")

    # ---------- Cuadro unico ----------
    trows = []
    for lbl, ex, cov, tfe in [("M1 (FE pais+tiempo)", [], "dk", True),
                              ("M2 (+controles domesticos)", ctr, "dk", True),
                              ("M3 (FE pais + factores globales)", ctr + GLOB, "dk", False),
                              ("M2 cluster pais", ctr, "pais", True),
                              ("M2 cluster tiempo", ctr, "tiempo", True)]:
        m, _ = fit(d, ex, cov, time_fe=tfe)
        if m is None:
            print(f"  {lbl}: no estimable"); continue
        r = row(m, lbl)
        if lbl.startswith("M1") or lbl.startswith("M2 (") or lbl.startswith("M3"):
            r["p_wildboot"] = wild_boot(d, ex, B=999)
        trows.append(r)
        wb = f", wildboot p={r.get('p_wildboot'):.3f}" if r.get("p_wildboot") is not None else ""
        print(f"  {lbl:28s} theta={r['theta']:+.4f} (t={r['t']:+.2f}, p={r['p']:.3f}, "
              f"N={r['N']}, paises={r['paises']}, R2w={r['R2w']:+.2f}{wb})")
    pd.DataFrame(trows).to_csv(os.path.join(HERE, "tabla_theta_bbg.csv"), index=False)

    # ---------- Robustez ----------
    rrows = []
    # pre-2020 (hallazgo prominente)
    m, _ = fit(d[d.year < 2020], ctr, "dk")
    if m: rrows.append(row(m, "pre-2020 (< 2020Q1)"))
    m, _ = fit(d[d.year >= 2020], ctr, "dk")
    if m: rrows.append(row(m, "solo 2020-2026"))
    # sin COVID
    m, _ = fit(d[(d.year < 2020) | (d.year > 2021)], ctr, "dk")
    if m: rrows.append(row(m, "sin 2020-2021"))
    # ES
    m, _ = fit(d, ctr, "dk", tail="ES_pp")
    if m: rrows.append(row(m, "cola = Expected Shortfall"))
    # sin deuda/PIB
    m, _ = fit(d, [c for c in ctr if c != "debt_gdp"], "dk")
    if m: rrows.append(row(m, "sin deuda/PIB"))
    # variable dependiente = CDS 5Y (robustez; Chari et al. usan CDS como alternativa)
    dcds = prep(dv="CDS_bps")
    ctr_cds = [c for c in CTRLS if c in dcds.columns and dcds[c].notna().sum() > 50]
    m, _ = fit(dcds, ctr_cds, "dk")
    if m: rrows.append(row(m, "DV = CDS 5Y (robustez)"))
    m, _ = fit(dcds, [], "dk")
    if m: rrows.append(row(m, "DV = CDS 5Y, M1 sin controles"))
    # M1 sin controles ya esta arriba; aqui M2 sin globales explicitos = M2 base (referencia)
    # leave-one-country-out sobre M2
    for c in sorted(d["country"].unique()):
        m, _ = fit(d[d.country != c], ctr, "dk")
        if m: rrows.append(row(m, f"sin {c}"))
    pd.DataFrame(rrows).to_csv(os.path.join(HERE, "robustez_bbg.csv"), index=False)
    for r in rrows:
        print(f"  {r['spec']:26s} theta={r['theta']:+.4f} (t={r['t']:+.2f}, N={r['N']})")

    # ---------- Umbral ----------
    u = umbral_hansen(d, ctr)
    pd.DataFrame([u]).to_csv(os.path.join(HERE, "umbral_bbg.csv"), index=False)
    print(f"  umbral Hansen: GaR_pp={u['gamma']:+.2f}  severo={u['efecto_severo']:+.2f}  "
          f"benigno={u['efecto_benigno']:+.2f}  LR={u['LR']:.1f}")

    # ---------- Efecto marginal ----------
    m, dd = fit(d, ctr, "dk")
    b1, th, V = m.params["JLoss_c"], m.params["JxT"], m.cov
    gbar = dd["GaR_pp"].mean()
    emr = []
    for pc in (.1, .25, .5, .75, .9):
        v = dd["GaR_pp"].quantile(pc); gc = v - gbar
        se = np.sqrt(V.loc["JLoss_c", "JLoss_c"] + gc**2 * V.loc["JxT", "JxT"]
                     + 2 * gc * V.loc["JLoss_c", "JxT"])
        emr.append(dict(pct=int(pc * 100), GaR_pp=v, dEMBI_dJLoss=b1 + th * gc, se=se))
    pd.DataFrame(emr).to_csv(os.path.join(HERE, "efecto_marginal_bbg.csv"), index=False)
    for r in emr:
        print(f"  p{r['pct']:<2d} GaR={r['GaR_pp']:+.2f} -> dEMBI/dJLoss={r['dEMBI_dJLoss']:+.2f} (se {r['se']:.2f})")

    # ---------- Diagnosticos ----------
    e = m.resids
    df = dd.assign(e=e.values)
    piv = df.pivot_table(index="quarter", columns="country", values="e")
    cs = piv.columns; rs, npair = [], 0
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            idx = piv[cs[i]].dropna().index.intersection(piv[cs[j]].dropna().index)
            if len(idx) > 10:
                rs.append(np.corrcoef(piv[cs[i]][idx], piv[cs[j]][idx])[0, 1] * np.sqrt(len(idx)))
                npair += 1
    CD = np.sqrt(2 / (npair * (npair - 1) + 1e-9)) * np.nansum(rs) if npair else np.nan
    df["e_lag"] = df.groupby("country")["e"].shift(1)
    ww = df.dropna(subset=["e", "e_lag"])
    diag = dict(pesaran_CD=CD, pesaran_p=2 * (1 - stats.norm.cdf(abs(CD))),
                AR1_resid=np.corrcoef(ww["e"], ww["e_lag"])[0, 1],
                N=int(m.nobs), R2_within=m.rsquared_within, R2_overall=m.rsquared_overall)
    pd.DataFrame([diag]).to_csv(os.path.join(HERE, "diagnosticos_bbg.csv"), index=False)
    print(f"  Pesaran CD={CD:.2f} (p={diag['pesaran_p']:.3f})  AR(1)={diag['AR1_resid']:+.2f}  "
          f"R2w={diag['R2_within']:+.2f}")
    print("\nGuardado: tabla_theta_bbg.csv, robustez_bbg.csv, umbral_bbg.csv, "
          "efecto_marginal_bbg.csv, diagnosticos_bbg.csv")


if __name__ == "__main__":
    main()
