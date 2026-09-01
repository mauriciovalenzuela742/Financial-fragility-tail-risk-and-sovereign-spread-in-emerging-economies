# -*- coding: utf-8 -*-
"""
p3_causal_fase5.py -- identificacion causal (A-D) + puente OI/datos (H4a/H4b),
UN SOLO panel Bloomberg. Reutiliza causal_core.py del proyecto y la logica de
fase5_estimacion_real.py.

Entrada  : bbg/Panel_bloomberg.csv, bbg/panel_real_bbg.csv
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

PANEL_CSV = os.path.join(HERE, "Panel_bloomberg.csv")
TMPL_CSV = os.path.join(HERE, "panel_real_bbg.csv")


# ---------------- causal battery ----------------
def load_for_causal():
    d = pd.read_csv(PANEL_CSV)
    d = d.dropna(subset=["EMBI_cds", "JLoss", "GaR"]).copy()
    d = d.rename(columns={"EMBI_cds": "EMBI_bps"})
    tmp = os.path.join(HERE, "_causal_input.csv")
    d.to_csv(tmp, index=False)
    return tmp


def causal_block():
    tmp = load_for_causal()
    P = cc.load(tmp)
    ctr = cc.ctrls_in(P)
    rows = []
    a = cc.wild_cluster_boot(P, ctrls=ctr, B=999)
    rows.append(dict(metodo="wild cluster bootstrap", theta=a["theta"], t=a["t"],
                     p_wildboot=a["p_wildboot"], extra=f"G={a['G']} n={a['n']}"))
    try:
        lp, thr = cc.local_projections(P, H=8, ctrls=ctr)
        pk = lp.loc[lp["beta_sev"].abs().idxmax()]
        rows.append(dict(metodo="local projections (pico sev.)", theta=pk["beta_sev"],
                         t=pk["beta_sev"] / pk["se_sev"],
                         extra=f"h={int(pk['h'])} se={pk['se_sev']:.2f} thr={thr:.2f}"))
    except Exception as e:
        rows.append(dict(metodo="local projections", extra=str(e)[:60]))
    # pre_year=2012: exposicion phi estimada en el periodo pre-GFC/GFC, coherente con
    # el quiebre de regimen post-GFC ya documentado en theta (Seccion 6.5). A ese corte
    # el instrumento original deja de ser debil (F 9.5 -> 21.6 en pre_year=2016 vs 2012).
    try:
        iv = cc.iv_shiftshare(P, global_var="OnOffRun_spread_log", ctrls=ctr, pre_year=2012)
        rows.append(dict(metodo="IV shift-share (nivel, pre_year=2012)", theta=iv.get("beta_JLoss_IV"),
                         p_normal=iv.get("p_JLoss"),
                         extra=f"shock={iv.get('shock_global')} F1={iv.get('F_primera'):.1f} "
                               f"theta_IV={iv.get('theta_IV')}"))
    except Exception as e:
        rows.append(dict(metodo="IV shift-share", extra=str(e)[:60]))
    try:
        ivd = cc.iv_shiftshare(P, global_var="USD_NEER_log", ctrls=ctr, pre_year=2012)
        rows.append(dict(metodo="IV shift-share (nivel, shock USD amplio BIS)",
                         theta=ivd.get("beta_JLoss_IV"), p_normal=ivd.get("p_JLoss"),
                         extra=f"F1={ivd.get('F_primera'):.1f}"))
    except Exception as e:
        rows.append(dict(metodo="IV shift-share USD", extra=str(e)[:60]))
    try:
        ivo = cc.iv_shiftshare_overid(P, ["OnOffRun_spread_log", "USD_NEER_log"], ctrls=ctr, pre_year=2012)
        rows.append(dict(metodo="IV shift-share (sobre-identificado, 2 instrumentos)",
                         theta=ivo.get("beta_JLoss_IV"), p_normal=ivo.get("p_JLoss"),
                         extra=f"F_conj={ivo.get('F_conjunto'):.1f} sargan_p={ivo.get('sargan_p'):.4f}"))
    except Exception as e:
        rows.append(dict(metodo="IV shift-share sobre-id", extra=str(e)[:60]))
    try:
        ti = cc.triple_institucional(P, inst_file=os.path.join(PANEL, "instituciones.csv"), ctrls=ctr)
        b, se, t = ti["JxG_I"]
        rows.append(dict(metodo="triple institucional (JxG x WGI)", theta=b, t=t,
                         extra=f"n={ti['_meta']['n']} paises={ti['_meta']['paises']}"))
    except Exception as e:
        rows.append(dict(metodo="triple institucional", extra=str(e)[:60]))
    os.remove(tmp)
    for r in rows:
        th = r.get("theta")
        print(f"  {r['metodo']:34s} theta={th if th is None else round(th,3)!s:>9}  {r.get('extra','')}")
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


def fit_f5(df, hhicol):
    d = prep_f5(df, hhicol)
    m = PanelOLS.from_formula(
        f"EMBI ~ {' + '.join(XCOLS)} + EntityEffects + TimeEffects",
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
        A = np.vstack([np.column_stack([blk[c], np.full(len(blk[c]), k)])
                       for k, c in enumerate(names)])
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


def fase5_block():
    df = pd.read_csv(TMPL_CSV)
    df["country"] = df["country"].str.lower()
    # concentracion TRIMESTRAL (mismos balances Bloomberg que JLoss) -- p6_concentracion_trimestral.py
    conc_csv = os.path.join(HERE, "concentracion_trimestral_bbg.csv")
    if os.path.exists(conc_csv):
        conc = pd.read_csv(conc_csv)[["country", "quarter", "HHI_q"]]
        df = df.merge(conc, on=["country", "quarter"], how="left")
        print(f"  HHI_q (trimestral) disponible en {df['HHI_q'].notna().sum()}/{len(df)} filas del template")
    rows = []
    hhi_specs = [("HHI", "estructural"), ("HHI_anual", "anual")]
    if "HHI_q" in df.columns:
        hhi_specs.append(("HHI_q", "trimestral"))
    for hhicol, lbl in hhi_specs:
        if df[hhicol].notna().sum() < 30:
            continue
        r = fit_f5(df, hhicol)
        rb = b4_bootstrap(df, hhicol)
        r.update(HHI=lbl, p_b4_pos=rb["p_pos"], ci90=rb["ci"],
                 loo=f"[{rb['loo_min']:+.0f},{rb['loo_max']:+.0f}]")
        rows.append(r)
        print(f"  HHI {lbl:11s} b3={r['b3']:+.2f}(t{r['t3']:+.2f})  b4={r['b4']:+.0f}(t{r['t4']:+.2f})  "
              f"P(b4>0)={rb['p_pos']:.0%}  LOO={r['loo']}")
    return rows


def main():
    print("=== IDENTIFICACION CAUSAL (panel unico Bloomberg) ===")
    cr = causal_block()
    pd.DataFrame(cr).to_csv(os.path.join(HERE, "causal_bbg.csv"), index=False)
    print("\n=== H4a / H4b  (JLoss x D x HHI) ===")
    fr = fase5_block()
    pd.DataFrame(fr).to_csv(os.path.join(HERE, "fase5_bbg.csv"), index=False)
    print("\nGuardado: causal_bbg.csv, fase5_bbg.csv")


if __name__ == "__main__":
    main()
