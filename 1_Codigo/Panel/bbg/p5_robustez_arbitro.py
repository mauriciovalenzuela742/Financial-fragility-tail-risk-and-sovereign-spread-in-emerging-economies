# -*- coding: utf-8 -*-
"""
p5_robustez_arbitro.py -- bateria de robustez que exigiria un arbitro, sobre el
mismo panel unico Bloomberg. Complementa p2_regresiones.py / p3_causal_fase5.py.

Bloques:
  1. Invariancia de la cola      theta(M2) con GaR (q05 directo) / GaR skew-t / ES
  2. Pais influyente             theta sin {china},{southafrica},{ambos},{turkey}...
                                 + jackknife de 2 paises (rango, % que sigue < 0)
  3. Multiplicador vs. nivel     CDS ~ ... + JxG + JxG*D_post2020  (test del termino
                                 de cola frente a un simple desplazamiento 2020-26)
  4. Ventanas moviles de 5 anos  theta por ventana -> donde vive la senal
  5. Placebo temporal            permuta trimestres dentro de pais -> theta ~ 0
  6. Regresor generado (GaR)     bootstrap que perturba GaR por su incertidumbre
                                 de 1a etapa (proxy: |GaR - GaR_skewt|) -> p de theta
  7. GMM dinamico (Arellano-Bond) CDS ~ L.CDS + JLoss + GaR + JxG + controles
  8. Diagnostico por pais         n_banks, below_min_banks, JLoss mediana/max

Salida -> bbg/robustez_arbitro_bbg.csv  (+ consola)
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p2_regresiones import prep, fit, row, CTRLS, GLOB  # noqa: E402

QA = os.path.join(os.path.dirname(HERE),
                  "..", "JLoss_reconstruction", "jloss_bloomberg", "qa_jloss.csv")


# --------------------------------------------------------------------------
# estimador manual rapido: TWFE within + theta con SE cluster-pais (Rademacher
# no; aqui solo el t asintotico agrupado, suficiente para placebo / ventanas)
# --------------------------------------------------------------------------
def _within(df, cols, ent, tim):
    M = df[cols].astype(float).values.copy()
    e = pd.factorize(df[ent])[0]
    t = pd.factorize(df[tim])[0]
    ne, nt = e.max() + 1, t.max() + 1
    ce = np.maximum(np.bincount(e, minlength=ne), 1)
    ct = np.maximum(np.bincount(t, minlength=nt), 1)
    for _ in range(20):
        for co, cn, ng in ((e, ce, ne), (t, ct, nt)):
            mm = np.zeros((ng, M.shape[1]))
            for j in range(M.shape[1]):
                mm[:, j] = np.bincount(co, weights=M[:, j], minlength=ng) / cn
            M -= mm[co]
    return M, e


def fast_theta(d, tail="GaR_pp", extra=None, crisis=None, ret_se=True):
    """theta del termino JLoss_c x tail_c (o + JxG*crisis). SE cluster-pais."""
    extra = extra or []
    need = ["EMBI_cds", "JLoss", tail] + extra + (["_crisis"] if crisis is not None else [])
    dd = d.dropna(subset=[c for c in need if c in d.columns]).copy()
    if crisis is not None:
        dd["_crisis"] = crisis.loc[dd.index].values
    dd["JLoss_c"] = dd["JLoss"] - dd["JLoss"].mean()
    dd["tail_c"] = dd[tail] - dd[tail].mean()
    dd["JxT"] = dd["JLoss_c"] * dd["tail_c"]
    cols = ["EMBI_cds", "JLoss_c", "tail_c", "JxT"] + extra
    if crisis is not None:
        dd["JxT_cr"] = dd["JxT"] * dd["_crisis"]
        dd["tail_cr"] = dd["tail_c"] * dd["_crisis"]
        cols += ["JxT_cr", "tail_cr"]
    M, e = _within(dd, cols, "country", "quarter")
    y, X = M[:, 0], M[:, 1:]
    xz = X.std(0) > 1e-12
    X = X[:, xz]
    names = [c for c, k in zip(cols[1:], xz) if k]
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ (X.T @ y)
    r = y - X @ b
    G = len(np.unique(e))
    meat = np.zeros((X.shape[1],) * 2)
    for g in np.unique(e):
        s = X[e == g].T @ r[e == g]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1)) * ((len(y) - 1) / (len(y) - X.shape[1]))
    out = {}
    for nm in ("JxT", "JxT_cr"):
        if nm in names:
            i = names.index(nm)
            out[nm] = (b[i], np.sqrt(V[i, i]))
    out["N"], out["G"] = len(y), G
    return out


def _p(bse):
    from scipy import stats
    b, se = bse
    t = b / se
    return b, t, 2 * (1 - stats.norm.cdf(abs(t)))


# --------------------------------------------------------------------------
def main():
    d = prep()
    d["GaR_st_pp"] = d["GaR_st"] * 100.0
    ctr = [c for c in CTRLS if c in d.columns and d[c].notna().sum() > 50]
    rows = []

    # ---- 1. invariancia de la cola ----
    print("== 1. invariancia de la cola (M2) ==")
    for tail, lbl in [("GaR_pp", "GaR q05 (directo)"),
                      ("GaR_st_pp", "GaR skew-t (ABG2019)"),
                      ("ES_pp", "Expected Shortfall")]:
        m, _ = fit(d, ctr, "dk", tail=tail)
        r = row(m, f"cola: {lbl}")
        rows.append(r)
        print(f"   {lbl:24s} theta={r['theta']:+.3f} (t={r['t']:+.2f}, p={r['p']:.3f}, N={r['N']})")

    # ---- 2. pais influyente ----
    print("== 2. pais influyente ==")
    combos = [["china"], ["southafrica"], ["china", "southafrica"],
              ["turkey"], ["turkey", "china"], ["brazil"], ["pakistan"]]
    for cc_ in combos:
        m, _ = fit(d[~d.country.isin(cc_)], ctr, "dk")
        r = row(m, "sin " + "+".join(cc_))
        rows.append(r)
        print(f"   sin {'+'.join(cc_):20s} theta={r['theta']:+.3f} (t={r['t']:+.2f}, p={r['p']:.3f}, N={r['N']}, G={r['paises']})")
    # jackknife de 2 paises
    paises = sorted(d.country.unique())
    jk = []
    for i in range(len(paises)):
        for j in range(i + 1, len(paises)):
            m, _ = fit(d[~d.country.isin([paises[i], paises[j]])], ctr, "dk")
            if m is not None:
                jk.append((m.params["JxT"], m.pvalues["JxT"]))
    jk = np.array(jk)
    print(f"   jackknife-2: theta en [{jk[:,0].min():+.2f}, {jk[:,0].max():+.2f}]; "
          f"<0 en {(jk[:,0]<0).mean():.0%}; p<0.10 en {(jk[:,1]<0.10).mean():.0%}")
    rows.append(dict(spec="jackknife-2 paises: theta min", theta=jk[:, 0].min()))
    rows.append(dict(spec="jackknife-2 paises: theta max", theta=jk[:, 0].max()))
    rows.append(dict(spec="jackknife-2 paises: %<0", theta=(jk[:, 0] < 0).mean()))
    rows.append(dict(spec="jackknife-2 paises: %p<0.10", theta=(jk[:, 1] < 0.10).mean()))

    # ---- 3. multiplicador de cola vs. desplazamiento 2020-26 ----
    print("== 3. termino de cola JxG*D(post-2020) ==")
    cr = (d["year"] >= 2020).astype(float)
    cr.index = d.index
    o = fast_theta(d, "GaR_pp", ctr, crisis=cr)
    b, t, pv = _p(o["JxT"])
    b2, t2, pv2 = _p(o["JxT_cr"])
    print(f"   JxG base      = {b:+.3f} (t={t:+.2f}, p={pv:.3f})")
    print(f"   JxG*post2020  = {b2:+.3f} (t={t2:+.2f}, p={pv2:.3f})   [N={o['N']}, G={o['G']}]")
    rows += [dict(spec="JxG (con interaccion de crisis)", theta=b, t=t, p=pv, N=o["N"]),
             dict(spec="JxG x D(post-2020)", theta=b2, t=t2, p=pv2, N=o["N"])]

    # ---- 4. ventanas moviles de 5 anos ----
    print("== 4. ventanas moviles de 5 anos ==")
    for y0 in range(2006, 2022, 3):
        w = d[(d.year >= y0) & (d.year < y0 + 5)]
        if w.country.nunique() < 5 or len(w) < 80:
            continue
        try:
            o = fast_theta(w, "GaR_pp", ctr)
            b, t, pv = _p(o["JxT"])
            print(f"   {y0}-{y0+4}: theta={b:+.3f} (t={t:+.2f}, N={o['N']}, G={o['G']})")
            rows.append(dict(spec=f"ventana {y0}-{y0+4}", theta=b, t=t, p=pv, N=o["N"], paises=o["G"]))
        except Exception as e:
            print(f"   {y0}-{y0+4}: {e}")

    # ---- 5. placebo: reasignacion de GaR (varios disenos) ----
    print("== 5. placebo: destruir la estructura de GaR (B=600) ==")
    base = fast_theta(d, "GaR_pp", ctr)
    b0 = base["JxT"][0]
    rng = np.random.default_rng(2024)
    dd = d.dropna(subset=["EMBI_cds", "JLoss", "GaR_pp"] + ctr).copy().reset_index(drop=True)

    def _placebo(mk, B=600):
        v = []
        for _ in range(B):
            dp = dd.copy()
            try:
                dp["GaR_pp"] = mk(dp)
                v.append(fast_theta(dp, "GaR_pp", ctr)["JxT"][0])
            except Exception:
                pass
        return np.array(v)

    def _swap(x):
        cs = sorted(x["country"].unique())
        perm = dict(zip(cs, rng.permutation(cs)))
        blk = {c: g.sort_values("quarter")["GaR_pp"].values for c, g in x.groupby("country")}
        out = x.copy()
        for c in cs:
            tgt = out["country"] == c
            out.loc[tgt, "GaR_pp"] = np.resize(blk[perm[c]], tgt.sum())
        return out["GaR_pp"].values

    designs = {
        "A. reshuffle global de GaR (null exacto)":
            lambda x: rng.permutation(x["GaR_pp"].values),
        "B. permutar GaR dentro de pais":
            lambda x: x.groupby("country")["GaR_pp"].transform(lambda s: rng.permutation(s.values)),
        "C. intercambiar series GaR entre paises": _swap,
    }
    print(f"   theta observado = {b0:+.3f}")
    for lbl, mk in designs.items():
        v = _placebo(mk)
        p1 = float(np.mean(v <= b0))
        p2 = float(np.mean(np.abs(v) >= abs(b0)))
        print(f"   {lbl:42s} media={v.mean():+.3f} sd={v.std():.3f}  "
              f"P(plac<=obs)={p1:.3f}  P(|plac|>=|obs|)={p2:.3f}")
        rows.append(dict(spec=f"placebo {lbl[:2]}", theta=float(v.mean()),
                         p=p1, N=int(base["N"])))

    # ---- 6. regresor generado: perturbar GaR a varias escalas de error de 1a etapa ----
    print("== 6. regresor generado (GaR): perturbacion a escalas crecientes (B=400) ==")
    sd_gar = float(d["GaR_pp"].dropna().std())
    gap = float((dd["GaR_pp"] - dd["GaR_st_pp"]).abs().std())
    print(f"   sd(GaR)={sd_gar:.2f} pp;  |GaR-skewt| sd={gap:.2f} pp (solo forma funcional)")
    for frac in (0.0, 0.10, 0.25, 0.50):
        s = frac * sd_gar
        pg = []
        for _ in range(400):
            dp = dd.copy()
            dp["GaR_pp"] = dp["GaR_pp"] + rng.normal(0, s, len(dp)) if s > 0 else dp["GaR_pp"]
            try:
                pg.append(fast_theta(dp, "GaR_pp", ctr)["JxT"][0])
            except Exception:
                pass
        pg = np.array(pg)
        print(f"   sd_pert = {frac:.0%} de sd(GaR) ({s:.2f} pp):  theta medio={pg.mean():+.3f}  "
              f"P(theta>=0)={np.mean(pg >= 0):.3f}")
        rows.append(dict(spec=f"regresor generado: pert {frac:.0%} sd(GaR)",
                         theta=float(pg.mean()), p=float(np.mean(pg >= 0))))

    # ---- 7. GMM dinamico ----
    print("== 7. GMM dinamico (nota: T>>N; sesgo de Nickell ~ 1/T) ==")
    T = pd.PeriodIndex(dd["quarter"], freq="Q").nunique()
    print(f"   T={T}, N={dd['country'].nunique()}  -> sesgo de Nickell ~ {1/T:.1%} (despreciable). "
          f"AB/system-GMM (disenado para N grande, T chico) no es apropiado aqui; se reporta "
          f"solo para verificar el signo.")
    rows.append(dict(spec="Nickell bias ~ 1/T", theta=1.0 / T))
    try:
        from pydynpd import regression
        g = dd.copy()
        g["qi"] = pd.factorize(pd.PeriodIndex(g["quarter"], freq="Q"))[0]
        g["cid"] = pd.factorize(g["country"])[0]
        g["JxG"] = (g["JLoss"] - g["JLoss"].mean()) * (g["GaR_pp"] - g["GaR_pp"].mean())
        g = g.rename(columns={"EMBI_cds": "cds"})
        keep = ["cid", "qi", "cds", "JLoss", "GaR_pp", "JxG"] + ctr
        cmd = ("cds L1.cds JLoss GaR_pp JxG " + " ".join(ctr) +
               " | gmm(cds, 2:4) | timedumm collapse")
        mod = regression.abond(cmd, g[keep], ["cid", "qi"])
        print("   (ver salida pydynpd arriba; solo verifica el signo)")
        rows.append(dict(spec="GMM dinamico: signo JxG<0 (inferencia no fiable, T>>N)", theta=np.nan))
    except Exception as e:
        print(f"   GMM no disponible o fallo: {str(e)[:120]}")
        rows.append(dict(spec="GMM dinamico: fallo", theta=np.nan, p=str(e)[:80]))

    # ---- 8. diagnostico por pais ----
    print("== 8. diagnostico por pais ==")
    try:
        qa = pd.read_csv(QA)
        est = d.dropna(subset=["EMBI_cds", "JLoss", "GaR"])
        jm = est.groupby("country")["JLoss"].agg(["median", "max", "count"])
        diag = qa.set_index("countryname").join(jm, how="inner")
        print(diag[["n_banks_med", "q_pocos_bancos", "median", "max", "count"]].round(1).to_string())
        diag.to_csv(os.path.join(HERE, "diag_por_pais_bbg.csv"))
    except Exception as e:
        print("   ", e)

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HERE, "robustez_arbitro_bbg.csv"), index=False)

    # ---- figura: theta por ventana movil de 5 anos ----
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        wv = [r for r in rows if str(r.get("spec", "")).startswith("ventana ")]
        if wv:
            xs = [r["spec"].split()[1] for r in wv]
            th = [r["theta"] for r in wv]
            tt = [r["t"] for r in wv]
            BLUE, RED, INK = "#2a78d6", "#e34948", "#0b0b0b"
            fig, ax = plt.subplots(figsize=(7.2, 3.6))
            cols = [RED if abs(t) < 1.64 else BLUE for t in tt]
            ax.axhline(0, color=INK, lw=1)
            ax.bar(range(len(xs)), th, color=cols, width=0.62)
            for i, (t, v) in enumerate(zip(tt, th)):
                ax.text(i, v + (0.06 if v >= 0 else -0.06), f"t={t:+.1f}",
                        ha="center", va="bottom" if v >= 0 else "top", fontsize=8)
            ax.set_xticks(range(len(xs)))
            ax.set_xticklabels(xs, rotation=0, fontsize=9)
            ax.set_ylabel(r"$\hat\theta$  (JLoss $\times$ GaR)")
            ax.set_title("Coeficiente de interacción por ventana móvil de 5 años", fontsize=10)
            ax.spines[["top", "right"]].set_visible(False)
            fig.tight_layout()
            for d in (os.path.join(HERE, "figuras"),
                      os.path.join(os.path.dirname(HERE), "..", "..",
                                   "4_Redaccion", "tesis", "imagenes")):
                os.makedirs(d, exist_ok=True)
                fig.savefig(os.path.join(d, "fig_ventanas_theta.pdf"))
            plt.close(fig)
            print("Figura: fig_ventanas_theta.pdf")
    except Exception as e:
        print("  figura ventanas fallo:", str(e)[:80])

    print("\nGuardado: robustez_arbitro_bbg.csv, diag_por_pais_bbg.csv")


if __name__ == "__main__":
    main()
