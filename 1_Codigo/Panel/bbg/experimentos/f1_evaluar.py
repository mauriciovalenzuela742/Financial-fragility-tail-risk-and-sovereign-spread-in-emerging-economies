# -*- coding: utf-8 -*-
"""
f1_evaluar.py -- EXPERIMENTO de ingeniería de variables: evalúa todas las familias con un mismo protocolo.

=========================== PROTOCOLO, DECLARADO ANTES DE ESTIMAR (2026-10-13) ===========================
Regresión: ln EMBI(t) con efectos fijos de país y de tiempo; todas las variables nuevas entran rezagadas
un trimestre, como en la principal. Cada especificación declara su coeficiente de interés ("clave") y
una especificación base estimada sobre la MISMA muestra. Por cada una se reporta:
  (a) coeficiente, t agrupado por país y p del wild cluster bootstrap (Webb, B = 999);
  (b) ganancia de R2 dentro del país sobre la base;
  (c) estabilidad al excluir un país: signo, cuántas exclusiones con |t| > 2,18, valor sin Turquía y
      sin Polonia;
  (d) fuera de muestra: raíz del error cuadrático medio relativa a la base, por bloques de tiempo y
      dejando un país fuera; y sobre la muestra de reserva (2023Q3 en adelante, coeficientes estimados
      solo con datos hasta 2023Q2);
  (e) p corregido por todo lo probado: máximo |t| entre especificaciones bajo permutación (desplazamiento
      circular de la variable clave dentro de cada país, R = 199), y Holm dentro de cada familia.
Variable primaria de cada familia e hipótesis (signo esperado):
  F1 ln_costo_pib (+)    F2 lnJ_ancha (+)        F3 frac_estres (+)      F4 ln_banca_vol_esp (+)
  F5 D_baja (+), con D_alza como placebo (0)     F6 D_ins_sintasa (+, similar a D_ins)
  F7 D_mm4 (+)           F8 min_z (0: sin amplificación)                  F10 J_max4 (+)
  F9 (variable dependiente): spread propio del país; se espera que beta2 deje de depender de Polonia.
Placebos: tipo de cambio real transformado igual que la fragilidad; deben salir nulos.
Simplificación declarada: en (d) los efectos fijos se descuentan sobre la muestra completa.
===========================================================================================================
Salidas: experimentos/f1_resultados.csv y f1_seleccion.csv. No se integra a ningún documento.
"""
import os

import numpy as np
import pandas as pd

import x0_comun as x0

B = int(os.environ.get("JLOSS_B", 999))
R_PERM = int(os.environ.get("JLOSS_PERM", 199))
RESERVA = "2023Q3"
FILAS = []


def sig_q(q):
    return (pd.PeriodIndex(q, freq="Q") + 1).astype(str)


def cargar():
    d = x0.datos()
    F = pd.read_csv(os.path.join(x0.HERE, "features_panel.csv"))
    num = [c for c in F.columns if c not in ("country", "quarter", "embi_source") and F[c].dtype != object]
    L1 = F[["country", "quarter"] + num].copy(); L1["quarter"] = sig_q(L1["quarter"])
    d = d.merge(L1, on=["country", "quarter"], how="left", suffixes=("", "_f"))
    L2 = F[["country", "quarter", "lnJ", "D"]].copy(); L2["quarter"] = sig_q(sig_q(L2["quarter"]))
    d = d.merge(L2.rename(columns={"lnJ": "lnJ_l2", "D": "D_l2"}), on=["country", "quarter"], how="left")
    alt = pd.read_csv(os.path.join(x0.BBG, "embi_trimestral_alternativo.csv"))[["country", "quarter", "EMBI_eop5"]]
    d = d.merge(alt, on=["country", "quarter"], how="left")
    assert np.allclose(d["lnJ"], np.log(d["JLoss_l1"]), equal_nan=True) and np.allclose(d["D"], d["D_l1"], equal_nan=True)
    # variables dependientes alternativas (F9)
    e = d["EMBI_bps"]
    d["y_asinh"] = np.arcsinh(e); d["y_bc"] = (e ** 0.44 - 1) / 0.44; d["y_ln50"] = np.log(e + 50.0)
    lo, hi = d["ln_EMBI"].quantile([0.01, 0.99]); d["y_win"] = d["ln_EMBI"].clip(lo, hi)
    d["y_cierre"] = np.log(d["EMBI_eop5"].where(d["EMBI_eop5"] > 0))
    d["y_base"] = np.log(d["CDS_bps"].where(d["CDS_bps"] > 0)) - d["ln_EMBI"]
    d["y_pb"] = e
    # F8: simultaneidad (sobre las variables ya rezagadas)
    for v, n_ in (("J_c", "zJ"), ("T_c", "zD"), ("reer_ln", "zR")):
        g = d.groupby("country")[v]
        d[n_] = (d[v] - g.transform("mean")) / g.transform("std")
    d["min_z"] = np.minimum(d["zJ"], d["zD"]); d["min_z_placebo"] = np.minimum(d["zR"], d["zD"])
    d["pc_comun"] = (d["zJ"] + d["zD"]) / np.sqrt(2); d["pc_diverg"] = (d["zJ"] - d["zD"]) / np.sqrt(2)
    d["uv"] = d.groupby("country")["J_c"].rank(pct=True) * d.groupby("country")["T_c"].rank(pct=True)
    d["Jl2xD"] = (d["lnJ_l2"] - d["lnJ_l2"].mean()) * d["T_c"]
    s = d.dropna(subset=["D_l1", "lnJ_l2", "D_l2"])                       # mediación: D predicho por la fragilidad pasada
    A, _ = x0.within(s, ["D_l1", "lnJ_l2", "D_l2"])
    b, u = x0.ols(A[:, 0], A[:, 1:])
    d.loc[s.index, "D_predicho_J"] = b[0] * (s["lnJ_l2"] - s["lnJ_l2"].mean())
    d["D_resto"] = d["T_c"] - d["D_predicho_J"]
    d["costo_c"] = d["ln_costo_pib"] - d["ln_costo_pib"].mean(); d["costoxD"] = d["costo_c"] * d["T_c"]
    d["JxD"] = d["JxT"]
    return d


def glob_extra(s):
    """cargas por país de los factores globales (spread propio del país)."""
    P = pd.get_dummies(s["country"], drop_first=True).to_numpy(float)
    return np.hstack([P * np.log(s["VIX"].to_numpy())[:, None], P * np.log(s["US_HY_spread"].to_numpy())[:, None]])


def preparar(s, y, regs, extra=False):
    cols = np.column_stack([s[y].to_numpy(float)] + [s[r].to_numpy(float) for r in regs])
    A, _ = x0.within(s, cols, extra=glob_extra(s) if extra else None)
    return A[:, 0], A[:, 1:], pd.factorize(s["country"])[0]


def recm_cv(y, X, folds):
    err = np.zeros(len(y))
    for te in folds:
        b = np.linalg.lstsq(X[~te], y[~te], rcond=None)[0]
        err[te] = y[te] - X[te] @ b
    return np.sqrt((err ** 2).mean())


def evaluar(d, nombre, fam, regs, clave, base, y="ln_EMBI", prim=False, extra=False, nota="", pesada=True):
    s = d.dropna(subset=[y] + list(dict.fromkeys(regs + base))).copy()
    if len(s) < 200 or s["country"].nunique() < 8:
        print(f"   {nombre}: muestra insuficiente ({len(s)})"); return
    k = regs.index(clave)
    yw, Xw, g = preparar(s, y, regs, extra)
    b, se = x0.t_cluster(yw, Xw, k, g)
    _, ub = x0.ols(yw, Xw); r2 = 1 - (ub ** 2).sum() / (yw ** 2).sum()
    yb, Xb, _ = preparar(s, y, base, extra)
    _, u0 = x0.ols(yb, Xb); r2b = 1 - (u0 ** 2).sum() / (yb ** 2).sum()
    fila = dict(spec=nombre, familia=fam, primaria=int(prim), y=y, clave=clave, regs=" + ".join(regs), N=len(s),
                paises=s["country"].nunique(), b=b, t=b / se, r2=r2, r2_base=r2b, r2_gan=r2 - r2b, nota=nota)
    if pesada:
        fila["p_wild"] = x0.wild_wald(yw, Xw, [k], g, B=B, seed=7)[1]
        # (c) excluir un país
        bs, ts = {}, {}
        for c in sorted(s["country"].unique()):
            m = (s["country"] != c).to_numpy()
            yy, XX, gg = preparar(s[m], y, regs, extra)
            bb, ss = x0.t_cluster(yy, XX, k, gg); bs[c] = bb; ts[c] = bb / ss
        fila.update(loo_mismo_signo=sum(np.sign(v) == np.sign(b) for v in bs.values()), loo_n=len(bs),
                    loo_sig=sum(abs(v) > 2.179 for v in ts.values()), loo_min=min(bs.values()), loo_max=max(bs.values()),
                    b_sin_turquia=bs.get("turkey", np.nan), t_sin_turquia=ts.get("turkey", np.nan),
                    b_sin_polonia=bs.get("poland", np.nan), t_sin_polonia=ts.get("poland", np.nan))
        # (d) fuera de muestra
        tc = pd.factorize(s["quarter"], sort=True)[0]
        ft = [np.isin(tc, bl) for bl in np.array_split(np.unique(tc), 5)]
        fp = [g == c for c in np.unique(g)]
        fila["oos_tiempo"] = recm_cv(yw, Xw, ft) / recm_cv(yb, Xb, ft)
        fila["oos_pais"] = recm_cv(yw, Xw, fp) / recm_cv(yb, Xb, fp)
        te = (s["quarter"] >= RESERVA).to_numpy()
        if te.sum() >= 30:
            fila["reserva"] = recm_cv(yw, Xw, [te]) / recm_cv(yb, Xb, [te])
        # (e) permutación: mismo desplazamiento relativo por país en todas las especificaciones
        rng = np.random.default_rng(101)
        xk = s[clave].to_numpy(float); pos = [np.where(g == c)[0] for c in np.unique(g)]
        tp = np.empty(R_PERM)
        for r in range(R_PERM):
            xs = xk.copy()
            for ix in pos:
                xs[ix] = np.roll(xk[ix], int(rng.uniform(0.1, 0.9) * len(ix)))
            s2 = s.copy(); s2[clave] = xs
            yy, XX, gg = preparar(s2, y, regs, extra)
            bb, ss = x0.t_cluster(yy, XX, k, gg); tp[r] = bb / ss
        fila["_tperm"] = tp
    FILAS.append(fila)
    print(f"   {fam:8s} {nombre:28s} N={len(s):3d} b={b:+.4f} t={b / se:+.2f}"
          + (f" wild={fila['p_wild']:.3f} dR2={r2 - r2b:+.4f} LOO sig {fila['loo_sig']}/{fila['loo_n']}" if pesada else ""), flush=True)


def especificaciones(d):
    J, D = "J_c", "T_c"
    e = lambda *a, **k: evaluar(d, *a, **k)
    # ---- referencia
    e("base_J", "base", [J, D], J, [D], prim=True); e("base_D", "base", [J, D], D, [J], prim=True)
    e("base_JxD", "base", [J, D, "JxD"], "JxD", [J, D])
    # ---- F1 tamaño
    e("costo_pib", "F1", ["ln_costo_pib", D], "ln_costo_pib", [J, D], prim=True)
    e("costo_pib+nbancos", "F1", ["ln_costo_pib", "ln_nbancos", D], "ln_costo_pib", [J, D])
    e("tamano_dado_J", "F1", [J, "ln_tamano", D], "ln_tamano", [J, D])
    e("costo_reservas", "F1", ["ln_costo_reservas", D], "ln_costo_reservas", [J, D])
    e("costo_deuda", "F1", ["ln_costo_deuda", D], "ln_costo_deuda", [J, D])
    # ---- F2 piso
    e("J_ancha", "F2", ["lnJ_ancha", D], "lnJ_ancha", [J, D], prim=True)
    e("J_exceso", "F2", ["J_exceso", "J_enpiso", D], "J_exceso", [J, D])
    e("J_z", "F2", ["J_z", D], "J_z", [J, D]); e("J_pct", "F2", ["J_pct", D], "J_pct", [J, D])
    e("J_racha_fuera", "F2", [J, "J_racha_fuera", D], "J_racha_fuera", [J, D])
    # ---- F3 ingredientes
    e("frac_estres", "F3", ["frac_estres", D], "frac_estres", [J, D], prim=True)
    e("frac_estres_dado_J", "F3", [J, "frac_estres", D], "frac_estres", [J, D])
    e("frac_estres_1", "F3", ["frac_estres_1", D], "frac_estres_1", [J, D]); e("frac_estres_2", "F3", ["frac_estres_2", D], "frac_estres_2", [J, D])
    e("apalancamiento", "F3", ["ln_apalanc", "ln_vol_banca", D], "ln_apalanc", [J, D])
    e("volatilidad_banca", "F3", ["ln_apalanc", "ln_vol_banca", D], "ln_vol_banca", [J, D])
    e("dd_medio", "F3", ["dd_medio", D], "dd_medio", [J, D]); e("dd_min", "F3", ["dd_medio", "dd_min", D], "dd_min", [J, D])
    e("dd_dispersion", "F3", ["dd_medio", "dd_disp", D], "dd_disp", [J, D]); e("pd_ingenua", "F3", ["pd_ing_pond", D], "pd_ing_pond", [J, D])
    # ---- F4 banca frente a bolsa
    e("banca_vol_especifica", "F4", ["ln_banca_vol_esp", "ln_bolsa_vol", D], "ln_banca_vol_esp", [J, D], prim=True)
    e("bolsa_vol", "F4", ["ln_banca_vol_esp", "ln_bolsa_vol", D], "ln_bolsa_vol", [J, D])
    e("J_dado_bolsa", "F4", [J, "ln_bolsa_vol", "bolsa_ret", D], J, ["ln_bolsa_vol", "bolsa_ret", D])
    e("banca_ret_especifico", "F4", ["banca_ret_esp", "bolsa_ret", D], "banca_ret_esp", [J, D])
    e("bolsa_ret", "F4", ["banca_ret_esp", "bolsa_ret", D], "bolsa_ret", [J, D])
    e("banca_vol_total", "F4", ["ln_banca_vol", D], "ln_banca_vol", [J, D])
    # ---- F5 cola abierta
    e("D_baja", "F5", [J, "D_media", "D_baja"], "D_baja", [J, D], prim=True)
    e("D_media", "F5", [J, "D_media", "D_baja"], "D_media", [J, D])
    e("D_alza_placebo", "F5", [J, "D_media", "D_baja", "D_alza"], "D_alza", [J, D], nota="placebo")
    e("D_dispersion", "F5", [J, "D_media", "D_disp"], "D_disp", [J, D]); e("D_asimetria", "F5", [J, "D_media", "D_asim"], "D_asim", [J, D])
    e("D_profundidad", "F5", [J, "D_media", "D_baja", "D_prof"], "D_prof", [J, D])
    e("solo_media", "F5", [J, "D_media"], "D_media", [J, D])
    # ---- F6 índice financiero
    e("D_en_muestra", "F6", [J, "D_ins"], "D_ins", [J]); e("D_sin_tasa", "F6", [J, "D_ins_sintasa"], "D_ins_sintasa", [J], prim=True)
    e("D_sin_bolsa", "F6", [J, "D_ins_sinbolsa"], "D_ins_sinbolsa", [J])
    e("fci", "F6", [J, "fci"], "fci", [J]); e("D_dado_fci", "F6", [J, D, "fci"], D, [J, "fci"]); e("fci_dado_D", "F6", [J, D, "fci"], "fci", [J, D])
    for bl in ("fci_bolsa", "fci_tasa", "fci_cambio"):
        e(bl, "F6", [J, "fci_bolsa", "fci_tasa", "fci_cambio"], bl, [J])
    # ---- F7 frecuencia y ruido
    e("D_mm4", "F7", [J, "D_mm4"], "D_mm4", [J, D], prim=True); e("D_mm4_dado_D", "F7", [J, D, "D_mm4"], "D_mm4", [J, D])
    e("D_pct", "F7", [J, "D_pct"], "D_pct", [J, D]); e("sorpresa_crec", "F7", [J, D, "sorpresa_crec"], "sorpresa_crec", [J, D])
    e("cola_materializada", "F7", [J, D, "cola_materializada"], "cola_materializada", [J, D])
    # ---- F8 simultaneidad
    e("min_z", "F8", [J, D, "min_z"], "min_z", [J, D], prim=True); e("pc_comun", "F8", ["pc_comun", "pc_diverg"], "pc_comun", [J, D])
    e("pc_divergencia", "F8", ["pc_comun", "pc_diverg"], "pc_diverg", [J, D]); e("producto_rangos", "F8", [J, D, "uv"], "uv", [J, D])
    e("secuenciada", "F8", [J, D, "Jl2xD"], "Jl2xD", [J, D])
    e("D_predicho_por_J", "F8", [J, "D_predicho_J", "D_resto"], "D_predicho_J", [J, D]); e("D_resto", "F8", [J, "D_predicho_J", "D_resto"], "D_resto", [J, D])
    e("costo_x_D", "F8", ["costo_c", D, "costoxD"], "costoxD", ["costo_c", D])
    # ---- F10 memoria
    e("J_max4", "F10", ["J_max4", D], "J_max4", [J, D], prim=True); e("J_max4_dado_J", "F10", [J, "J_max4", D], "J_max4", [J, D])
    for v in ("J_d4", "J_brecha8", "J_vol4", "D_d4", "D_brecha8", "D_max4", "D_vol4"):
        e(v, "F10", [J, D, v], v, [J, D])
    # ---- placebos
    e("reer_z", "placebo", ["reer_z", D], "reer_z", [D], nota="placebo"); e("reer_max4", "placebo", [J, "reer_max4", D], "reer_max4", [J, D], nota="placebo")
    e("min_z_placebo", "placebo", [J, D, "min_z_placebo"], "min_z_placebo", [J, D], nota="placebo")
    # ---- F9 variable dependiente (coeficientes de la principal con otra medida del spread)
    for yv, lab, ex in (("ln_EMBI", "propio_del_pais", True), ("y_asinh", "asinh", False), ("y_bc", "boxcox044", False),
                        ("y_ln50", "ln_mas_50", False), ("y_win", "recortado", False), ("y_cierre", "cierre", False),
                        ("y_base", "base_cds_embi", False), ("y_pb", "puntos_basicos", False)):
        for kreg, kl in ((J, "b1"), (D, "b2"), ("JxD", "b3")):
            e(f"{lab}_{kl}", "F9", [J, D, "JxD"], kreg, [J, D] if kreg == "JxD" else [x for x in (J, D) if x != kreg], y=yv,
              prim=(lab == "propio_del_pais" and kl == "b2"), extra=ex, pesada=(kl != "b3" or lab == "propio_del_pais"))


def cerrar():
    T = pd.DataFrame(FILAS)
    con = T[T["_tperm"].notna()] if "_tperm" in T else T.iloc[0:0]
    if len(con):
        M = np.abs(np.vstack(con["_tperm"].to_numpy()))            # especificaciones x R
        prueba = con[(con["familia"] != "placebo") & (con["familia"] != "base")].index
        mx = M[[list(con.index).index(i) for i in prueba]].max(axis=0)
        T["p_maxt"] = np.nan
        T.loc[con.index, "p_maxt"] = [(1 + (mx >= abs(t)).sum()) / (len(mx) + 1) for t in con["t"]]
        T["p_perm_propia"] = np.nan
        T.loc[con.index, "p_perm_propia"] = [(1 + (M[j] >= abs(t)).sum()) / (M.shape[1] + 1) for j, t in enumerate(con["t"])]
        T.attrs["maxt_q95"] = float(np.quantile(mx, 0.95)); T.attrs["n_pruebas"] = len(prueba)
    T["p_holm_familia"] = np.nan
    for fam, x in T[T["p_wild"].notna()].groupby("familia") if "p_wild" in T else []:
        o = x["p_wild"].sort_values(); m = len(o); prev = 0.0
        for i, (ix, p) in enumerate(o.items()):
            prev = max(prev, min(1.0, (m - i) * p)); T.loc[ix, "p_holm_familia"] = prev
    T.drop(columns=["_tperm"], errors="ignore").to_csv(os.path.join(x0.HERE, "f1_resultados.csv"), index=False)
    print(f"\n-> f1_resultados.csv ({len(T)} especificaciones). |t| crítico por máximo-t (95 %): "
          f"{T.attrs.get('maxt_q95', float('nan')):.2f} sobre {T.attrs.get('n_pruebas', 0)} pruebas")
    return T


# ---------------------------------------------------------------- selección estable (LASSO)
def lasso(X, y, lam, it=300):
    n, k = X.shape; b = np.zeros(k); r = y.copy(); c2 = (X ** 2).sum(0)
    for _ in range(it):
        bmax = 0.0
        for j in range(k):
            rho = X[:, j] @ r + c2[j] * b[j]
            nb = np.sign(rho) * max(abs(rho) - lam * n, 0.0) / c2[j]
            if nb != b[j]:
                r -= X[:, j] * (nb - b[j]); bmax = max(bmax, abs(nb - b[j])); b[j] = nb
        if bmax < 1e-7:
            break
    return b


def seleccion(d, R=200):
    cand = ["J_c", "T_c", "ln_costo_pib", "frac_estres", "ln_apalanc", "ln_vol_banca", "ln_banca_vol_esp", "ln_bolsa_vol",
            "bolsa_ret", "D_media", "D_baja", "D_alza", "fci", "D_mm4", "J_max4", "min_z", "reer_z"]
    s = d.dropna(subset=["ln_EMBI"] + cand).copy()
    A, _ = x0.within(s, np.column_stack([s["ln_EMBI"].to_numpy(float)] + [s[c].to_numpy(float) for c in cand]))
    y = A[:, 0] / A[:, 0].std(); X = A[:, 1:] / A[:, 1:].std(0)
    tc = pd.factorize(s["quarter"], sort=True)[0]; g = pd.factorize(s["country"])[0]
    ft = [np.isin(tc, bl) for bl in np.array_split(np.unique(tc), 5)]
    lams = np.geomspace(0.002, 0.3, 14)
    cv = [np.mean([((y[te] - X[te] @ lasso(X[~te], y[~te], lam)) ** 2).mean() for te in ft]) for lam in lams]
    lam = lams[int(np.argmin(cv))]
    b0 = lasso(X, y, lam)
    rng = np.random.default_rng(3); frec = np.zeros(len(cand)); G = g.max() + 1
    for _ in range(R):
        idx = np.concatenate([np.where(g == c)[0] for c in rng.integers(0, G, G)])
        frec += lasso(X[idx], y[idx], lam) != 0
    out = pd.DataFrame({"variable": cand, "coef_estandarizado": b0, "frecuencia_seleccion": frec / R})
    out.attrs["lam"] = lam; out.attrs["N"] = len(s)
    out.sort_values("frecuencia_seleccion", ascending=False).to_csv(os.path.join(x0.HERE, "f1_seleccion.csv"), index=False)
    print(f"\n   selección estable: N={len(s)}, {s['country'].nunique()} países, lambda={lam:.4f}")
    print(out.sort_values("frecuencia_seleccion", ascending=False).round(3).to_string(index=False))


def atenuacion(d):
    """corrección clásica por error de medición del riesgo de cola usando las 500 réplicas."""
    s = d.dropna(subset=["ln_EMBI", "J_c", "T_c", "D_ee_replicas"])
    yw, Xw, g = preparar(s, "ln_EMBI", ["J_c", "T_c"])
    b, se = x0.t_cluster(yw, Xw, 1, g)
    razon = s["D_ee_replicas"].mean() / Xw[:, 1].std()
    sd_pais = (s["D_l1"] - s.groupby("country")["D_l1"].transform("mean")).std()
    # la corrección clásica de atenuación solo tiene sentido si el error es menor que la señal (razón < 1)
    print(f"\n   error de estimación del riesgo de cola: N={len(s)}, b2={b:.4f}, ee medio entre réplicas={s['D_ee_replicas'].mean():.3f} pp; "
          f"d.e. de D dentro del país={sd_pais:.3f}; d.e. neta de efectos de país y tiempo={Xw[:, 1].std():.3f}; "
          f"razón error/señal identificadora={razon:.2f}")
    pd.Series({"N": len(s), "b2": b, "t": b / se, "ee_replicas_medio": s["D_ee_replicas"].mean(), "sd_D_dentro_pais": sd_pais,
               "sd_D_neto_EF": Xw[:, 1].std(), "razon_error_senal": razon}).to_csv(os.path.join(x0.HERE, "f1_atenuacion.csv"))


def main():
    assert not x0.NIV, "se corre en la forma logarítmica (los puntos básicos entran como variable dependiente alternativa)"
    d = cargar()
    assert len(d) == 765
    A, _ = x0.within(d, ["ln_EMBI", "J_c", "T_c", "JxT"]); b, _ = x0.ols(A[:, 0], A[:, 1:])
    assert abs(b[0] - 0.0985) < 5e-4 and abs(b[2] + 0.0112) < 5e-4, b
    print(f"f1: N={len(d)}; principal {b.round(4)}; B={B}, permutaciones={R_PERM}", flush=True)
    especificaciones(d)
    cerrar()
    atenuacion(d)
    seleccion(d)


if __name__ == "__main__":
    main()
