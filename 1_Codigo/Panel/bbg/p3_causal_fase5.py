# -*- coding: utf-8 -*-
"""
p3_causal_fase5.py -- identificacion causal (A-D) + puente OI/datos (H4a/H4b),
panel Bloomberg. Reutiliza causal_core.py del proyecto y la logica de
fase5_estimacion_real.py.

Entrada  : bbg/Panel_principal_bbg.csv, bbg/Panel_ampliado_bbg.csv,
           bbg/panel_real_principal_bbg.csv, bbg/panel_real_ampliado_bbg.csv
Salida   : bbg/causal_bbg.csv, bbg/fase5_bbg.csv
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.dirname(HERE)
sys.path.insert(0, PANEL)
from linearmodels.panel import PanelOLS
import causal_core as cc


# ---------------- causal battery ----------------
def causal_block(name, path):
    # causal_core espera EMBI_bps, GaR, JLoss, quarter, country + (opc) controles
    P = cc.load(path)
    ctr = cc.ctrls_in(P)
    rows = []
    a = cc.wild_cluster_boot(P, ctrls=ctr, B=999)
    rows.append(dict(base=name, metodo="wild cluster bootstrap", theta=a["theta"],
                     t=a["t"], p_normal=None, p_wildboot=a["p_wildboot"],
                     extra=f"G={a['G']} n={a['n']}"))
    try:
        lp, thr = cc.local_projections(P, H=8, ctrls=ctr)
        pk = lp.loc[lp["beta_sev"].abs().idxmax()]
        rows.append(dict(base=name, metodo="local projections (pico sev.)",
                         theta=pk["beta_sev"], t=pk["beta_sev"] / pk["se_sev"],
                         p_normal=None, p_wildboot=None,
                         extra=f"h={int(pk['h'])} se={pk['se_sev']:.2f} thr={thr:.2f}"))
    except Exception as e:
        rows.append(dict(base=name, metodo="local projections", extra=str(e)[:50]))
    try:
        iv = cc.iv_shiftshare(P, ctrls=ctr)
        rows.append(dict(base=name, metodo="IV shift-share (nivel)",
                         theta=iv.get("beta_JLoss_IV"), t=None, p_normal=iv.get("p_JLoss"),
                         p_wildboot=None,
                         extra=f"shock={iv.get('shock_global')} F1={iv.get('F_primera'):.1f} theta_IV={iv.get('theta_IV')}"))
    except Exception as e:
        rows.append(dict(base=name, metodo="IV shift-share", extra=str(e)[:50]))
    try:
        ti = cc.triple_institucional(P, ctrls=ctr)
        b, se, t = ti["JxG_I"]
        rows.append(dict(base=name, metodo="triple institucional (JxG x WGI)",
                         theta=b, t=t, extra=f"n={ti['_meta']['n']} paises={ti['_meta']['paises']}"))
    except Exception as e:
        rows.append(dict(base=name, metodo="triple institucional", extra=str(e)[:50]))
    for r in rows:
        print(f"  {name:10s} {r['metodo']:34s} theta={r.get('theta')!s:>10.10}  {r.get('extra','')}")
    return rows


# ---------------- fase5 H4a/H4b ----------------
XCOLS = ["JLoss_c", "D_c", "JL_D", "JL_D_H", "JL_H", "D_H"]


def prep_f5(df, hhicol):
    d = df.dropna(subset=["EMBI", "JLoss", "D", hhicol]).copy()
    for v in ["JLoss", "D"]:
        d[v + "_c"] = d[v] - d[v].mean()
    d["HHI_c"] = d[hhicol] - d[hhicol].mean()
    d["JL_D"] = d["JLoss_c"] * d["D_c"]
    d["JL_D_H"] = d["JL_D"] * d["HHI_c"]
    d["JL_H"] = d["JLoss_c"] * d["HHI_c"]
    d["D_H"] = d["D_c"] * d["HHI_c"]
    return d


def fit_f5(df, hhicol, use_debt):
    d = prep_f5(df, hhicol)
    ctrl = " + debt" if (use_debt and "debt" in d and d["debt"].notna().all()) else ""
    m = PanelOLS.from_formula(
        f"EMBI ~ {' + '.join(XCOLS)}{ctrl} + EntityEffects + TimeEffects",
        d.set_index(["country", "time"])).fit(cov_type="clustered", cluster_entity=True)
    return dict(N=int(m.nobs), paises=d["country"].nunique(),
                b3=m.params["JL_D"], t3=m.tstats["JL_D"],
                b4=m.params["JL_D_H"], t4=m.tstats["JL_D_H"])


def b4_bootstrap(df, hhicol, B=1000, seed=7):
    d = df.dropna(subset=["EMBI", "JLoss", "D", hhicol]).copy()
    qc = {q: i for i, q in enumerate(sorted(d["quarter"].unique()))}
    d["tc"] = d["quarter"].map(qc)
    blk = {c: g[["EMBI", "JLoss", "D", hhicol, "tc"]].values for c, g in d.groupby("country")}
    cs = list(blk)

    def _b4(names):
        parts = [np.column_stack([blk[c], np.full(len(blk[c]), k)]) for k, c in enumerate(names)]
        A = np.vstack(parts)
        E, J, D, H = A[:, 0], A[:, 1], A[:, 2], A[:, 3]
        tc = A[:, 4].astype(int); ent = A[:, 5].astype(int)
        Jc, Dc, Hc = J - J.mean(), D - D.mean(), H - H.mean()
        JD = Jc * Dc
        M = np.column_stack([E, Jc, Dc, JD, JD * Hc, Jc * Hc, Dc * Hc])
        ne, nt = ent.max() + 1, tc.max() + 1
        ce = np.maximum(np.bincount(ent, minlength=ne), 1)
        ct = np.maximum(np.bincount(tc, minlength=nt), 1)
        for _ in range(12):
            for co, cn, ng in ((ent, ce, ne), (tc, ct, nt)):
                mm = np.empty((ng, M.shape[1]))
                for jj in range(M.shape[1]):
                    mm[:, jj] = np.bincount(co, weights=M[:, jj], minlength=ng) / cn
                M -= mm[co]
        return np.linalg.lstsq(M[:, 1:], M[:, 0], rcond=None)[0][3]
    base = _b4(cs)
    loo = {c: _b4([x for x in cs if x != c]) for c in cs}
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        try:
            bs.append(_b4(list(rng.choice(cs, len(cs), True))))
        except Exception:
            pass
    bs = np.array(bs)
    return dict(b4=base, p_pos=float((bs > 0).mean()),
                ci=(float(np.percentile(bs, 5)), float(np.percentile(bs, 95))),
                loo_min=min(loo.values()), loo_max=max(loo.values()))


def fase5_block(name, path, use_debt):
    df = pd.read_csv(path)
    df["country"] = df["country"].str.lower()
    rows = []
    for hhicol, lbl in [("HHI", "estructural"), ("HHI_anual", "anual")]:
        if df[hhicol].notna().sum() < 30:
            continue
        r = fit_f5(df, hhicol, use_debt)
        rb = b4_bootstrap(df, hhicol)
        r.update(base=name, HHI=lbl, p_b4_pos=rb["p_pos"], ci90=rb["ci"],
                 loo=f"[{rb['loo_min']:+.0f},{rb['loo_max']:+.0f}]")
        rows.append(r)
        print(f"  {name:10s} HHI {lbl:11s} b3={r['b3']:+.2f}(t{r['t3']:+.2f})  "
              f"b4={r['b4']:+.0f}(t{r['t4']:+.2f})  P(b4>0)={rb['p_pos']:.0%}  LOO={r['loo']}")
    return rows


def main():
    print("=== IDENTIFICACION CAUSAL (Bloomberg) ===")
    crows = []
    crows += causal_block("principal", os.path.join(HERE, "Panel_principal_bbg.csv"))
    crows += causal_block("ampliado", os.path.join(HERE, "Panel_ampliado_bbg.csv"))
    pd.DataFrame(crows).to_csv(os.path.join(HERE, "causal_bbg.csv"), index=False)

    print("\n=== H4a / H4b  (JLoss x D x HHI, Bloomberg) ===")
    frows = []
    frows += fase5_block("principal", os.path.join(HERE, "panel_real_principal_bbg.csv"), True)
    frows += fase5_block("ampliado", os.path.join(HERE, "panel_real_ampliado_bbg.csv"), False)
    pd.DataFrame(frows).to_csv(os.path.join(HERE, "fase5_bbg.csv"), index=False)
    print("\nGuardado: causal_bbg.csv, fase5_bbg.csv")


if __name__ == "__main__":
    main()
