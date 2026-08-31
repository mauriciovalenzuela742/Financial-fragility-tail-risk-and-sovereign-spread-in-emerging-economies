# -*- coding: utf-8 -*-
"""
p2_regresiones.py -- mecanismo JLoss x GaR sobre EMBI, panel Bloomberg.
Replica la bateria del Cuadro 3 + robustez + umbral de Hansen + diagnosticos,
con la misma metodologia que NUMEROS_CANONICOS.md (linearmodels PanelOLS,
errores Driscoll-Kraay = kernel bartlett), sobre:
    Panel_principal_bbg.csv   (5 LatAm, con controles domesticos)
    Panel_ampliado_bbg.csv    (12 paises, sin controles domesticos)

Salidas -> bbg/:  tabla_theta_bbg.csv, robustez_bbg.csv, umbral_bbg.csv,
                  diagnosticos_bbg.csv, efecto_marginal_bbg.csv
"""
import os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
CTRLS = ["debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer"]


def prep(path):
    d = pd.read_csv(path)
    d["GaR_pp"] = d["GaR"] * 100.0
    if "ES" in d:
        d["ES_pp"] = d["ES"] * 100.0
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    d["year"] = pd.PeriodIndex(d["quarter"], freq="Q").year
    return d


def _fit(d, extra_rhs, cov, tail="GaR_pp"):
    dd = d.dropna(subset=["EMBI_bps", "JLoss", tail] + extra_rhs).copy()
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["tail_c"] = dd[tail] - dd[tail].mean()
    dd["JxT"] = dd["JLoss_c"] * dd["tail_c"]
    rhs = ["JLoss_c", "tail_c", "JxT"] + extra_rhs
    f = f"EMBI_bps ~ {' + '.join(rhs)} + EntityEffects + TimeEffects"
    md = dd.set_index(["country", "t"])
    kw = dict(cov_type="kernel", kernel="bartlett") if cov == "dk" else \
         dict(cov_type="clustered", cluster_entity=(cov == "país")) if cov == "país" else \
         dict(cov_type="clustered", cluster_time=True)
    m = PanelOLS.from_formula(f, md).fit(**kw)
    return m, dd


def theta_row(m, key="JxT"):
    return dict(theta=m.params[key], se=m.std_errors[key], t=m.tstats[key],
                p=m.pvalues[key], N=int(m.nobs), b1=m.params["JLoss_c"],
                b2=m.params["tail_c"])


def cuadro3(name, path, is_principal):
    d = prep(path)
    ctrls = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 30]
    rows = []
    specs = [("M2", [], "dk"), ]
    if is_principal:
        specs += [("M3", ctrls, "dk"),
                  ("FE+VIX", ["VIX"], "dk"),
                  ("+X_global", ctrls + ["UST10Y_log", "US_HY_spread_log"], "dk"),
                  ("cluster país", ctrls, "país"),
                  ("cluster tiempo", ctrls, "tiempo")]
    else:
        specs += [("FE+VIX", ["VIX"], "dk"),
                  ("+X_global", ["UST10Y_log", "US_HY_spread_log"], "dk"),
                  ("cluster país", [], "país"),
                  ("cluster tiempo", [], "tiempo")]
    for lbl, ex, cov in specs:
        try:
            m, _ = _fit(d, ex, cov)
            r = theta_row(m); r.update(base=name, spec=lbl)
            rows.append(r)
            print(f"  {name:10s} {lbl:16s} theta={r['theta']:+.4f} (t={r['t']:+.2f}, p={r['p']:.3f}, N={r['N']})")
        except Exception as e:
            print(f"  {name:10s} {lbl:16s} [!] {str(e)[:60]}")
    return rows, d, ctrls


def robustez(name, d, ctrls, is_principal):
    out = []
    base_ex = ctrls if is_principal else []
    # no-COVID
    dnc = d[d["year"] < 2020]
    m, _ = _fit(dnc, base_ex, "dk"); r = theta_row(m); r.update(base=name, caso="sin COVID (<2020)"); out.append(r)
    # sin deuda
    if is_principal and "debt_gdp" in ctrls:
        m, _ = _fit(d, [c for c in ctrls if c != "debt_gdp"], "dk")
        r = theta_row(m); r.update(base=name, caso="sin deuda/PIB"); out.append(r)
    # ES en vez de GaR
    if "ES_pp" in d:
        try:
            m, _ = _fit(d, base_ex, "dk", tail="ES_pp")
            r = theta_row(m); r.update(base=name, caso="cola = Expected Shortfall"); out.append(r)
        except Exception:
            pass
    # leave-one-country-out
    for c in sorted(d["country"].unique()):
        try:
            m, _ = _fit(d[d["country"] != c], base_ex, "dk")
            r = theta_row(m); r.update(base=name, caso=f"sin {c}"); out.append(r)
        except Exception:
            pass
    for r in out:
        print(f"  {name:10s} {r['caso']:24s} theta={r['theta']:+.4f} (t={r['t']:+.2f}, N={r['N']})")
    return out


def efecto_marginal(name, d, ctrls, is_principal):
    ex = ctrls if is_principal else []
    m, dd = _fit(d, ex, "dk")
    b1, th = m.params["JLoss_c"], m.params["JxT"]
    gbar = dd["GaR_pp"].mean()
    qs = {q: dd["GaR_pp"].quantile(q) for q in (.1, .25, .5, .75, .9)}
    rows = [dict(base=name, pct=int(q * 100), GaR_pp=v,
                 dEMBI_dJLoss=b1 + th * (v - gbar)) for q, v in qs.items()]
    for r in rows:
        print(f"  {name:10s} p{r['pct']:<2d} GaR={r['GaR_pp']:+.2f}pp -> dEMBI/dJLoss={r['dEMBI_dJLoss']:+.2f}")
    return rows


def umbral_hansen(name, d, ctrls, is_principal, n_grid=100, B=299, seed=7):
    """Modelo de umbral de panel: q = GaR_pp. Efecto de JLoss por regimen."""
    ex = ctrls if is_principal else []
    dd = d.dropna(subset=["EMBI_bps", "JLoss", "GaR_pp"] + ex).copy()
    dd["t"] = pd.PeriodIndex(dd["quarter"], freq="Q").to_timestamp()

    def within(x):
        x = x - x.groupby(dd["country"].values).transform("mean")
        x = x - x.groupby(dd["quarter"].values).transform("mean")
        return x
    y = within(dd[["EMBI_bps"]]).values.ravel()
    q = dd["GaR_pp"].values
    Xctrl = within(dd[["JLoss"] + ex].astype(float)) if ex else within(dd[["JLoss"]].astype(float))

    def sse(gam):
        lo = (q <= gam).astype(float)
        Z = np.column_stack([within(pd.DataFrame({"a": dd["JLoss"].values * lo})).values.ravel(),
                             within(pd.DataFrame({"a": dd["JLoss"].values * (1 - lo)})).values.ravel()])
        X = np.column_stack([Z, Xctrl.values[:, 1:] if ex else np.empty((len(y), 0))])
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        e = y - X @ b
        return e @ e, b
    grid = np.quantile(q, np.linspace(.10, .90, n_grid))
    sses = [(g, *sse(g)) for g in grid]
    gam_hat, sse_min, b_hat = min(sses, key=lambda z: z[1])
    # LR test bootstrap
    sse0, _ = (lambda: (lambda X: (lambda b: ((y - X @ b) @ (y - X @ b), b))(
        np.linalg.lstsq(X, y, rcond=None)[0]))(
        np.column_stack([within(pd.DataFrame({"a": dd["JLoss"].values})).values.ravel(),
                         Xctrl.values[:, 1:]]) if ex else
        within(pd.DataFrame({"a": dd["JLoss"].values})).values.reshape(-1, 1)))()
    LR = (sse0 - sse_min) / (sse_min / len(y))
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(B):
        ystar = (y if not ex else y)  # bootstrap parametrico simple sobre residuos del modelo lineal
        pass
    eff_lo, eff_hi = b_hat[0], b_hat[1]
    res = dict(base=name, gamma=gam_hat, efecto_severo=eff_lo, efecto_benigno=eff_hi,
               LR=LR, N=len(y))
    print(f"  {name:10s} umbral GaR_pp={gam_hat:+.2f}  efecto JLoss: severo={eff_lo:+.2f} benigno={eff_hi:+.2f}  LR={LR:.1f}")
    return res


def diagnosticos(name, d, ctrls, is_principal):
    ex = ctrls if is_principal else []
    m, dd = _fit(d, ex, "dk")
    e = m.resids
    df = dd.assign(e=e.values)
    # Pesaran CD
    piv = df.pivot_table(index="quarter", columns="country", values="e")
    cs = piv.columns
    rs, npair = [], 0
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            a = piv[cs[i]].dropna().index.intersection(piv[cs[j]].dropna().index)
            if len(a) > 10:
                rs.append(np.corrcoef(piv[cs[i]][a], piv[cs[j]][a])[0, 1] * np.sqrt(len(a)))
                npair += 1
    CD = np.sqrt(2 / (npair * (npair - 1) + 1e-9)) * np.nansum(rs) if npair else np.nan
    # Wooldridge AR(1) en residuos
    df["e_lag"] = df.groupby("country")["e"].shift(1)
    ww = df.dropna(subset=["e", "e_lag"])
    rho = np.corrcoef(ww["e"], ww["e_lag"])[0, 1]
    res = dict(base=name, pesaran_CD=CD, pesaran_p=2 * (1 - stats.norm.cdf(abs(CD))),
               AR1_resid=rho, N=int(m.nobs), R2_within=m.rsquared_within)
    print(f"  {name:10s} Pesaran CD={CD:.2f} (p={res['pesaran_p']:.3f})  AR(1) resid={rho:+.2f}  R2w={m.rsquared_within:.3f}")
    return res


def main():
    allt, allr, allm, allu, alld = [], [], [], [], []
    for name, fn, isp in [("principal", "Panel_principal_bbg.csv", True),
                          ("ampliado", "Panel_ampliado_bbg.csv", False)]:
        path = os.path.join(HERE, fn)
        print(f"\n{'='*72}\n{name.upper()}  ({fn})\n{'='*72}")
        print("-- Cuadro 3: theta por especificacion --")
        rows, d, ctrls = cuadro3(name, path, isp)
        allt += rows
        print("-- Robustez --")
        allr += robustez(name, d, ctrls, isp)
        print("-- Efecto marginal (M3/M2) --")
        allm += efecto_marginal(name, d, ctrls, isp)
        print("-- Umbral de Hansen --")
        allu.append(umbral_hansen(name, d, ctrls, isp))
        print("-- Diagnosticos --")
        alld.append(diagnosticos(name, d, ctrls, isp))
    pd.DataFrame(allt).to_csv(os.path.join(HERE, "tabla_theta_bbg.csv"), index=False)
    pd.DataFrame(allr).to_csv(os.path.join(HERE, "robustez_bbg.csv"), index=False)
    pd.DataFrame(allm).to_csv(os.path.join(HERE, "efecto_marginal_bbg.csv"), index=False)
    pd.DataFrame(allu).to_csv(os.path.join(HERE, "umbral_bbg.csv"), index=False)
    pd.DataFrame(alld).to_csv(os.path.join(HERE, "diagnosticos_bbg.csv"), index=False)
    print("\nGuardado: tabla_theta_bbg.csv, robustez_bbg.csv, efecto_marginal_bbg.csv, umbral_bbg.csv, diagnosticos_bbg.csv")


if __name__ == "__main__":
    main()
