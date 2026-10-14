# -*- coding: utf-8 -*-
"""
f0_construir_features.py -- EXPERIMENTO de ingeniería de variables: construye la tabla de variables.

Reconstruye cada regresor de la tesis desde sus ingredientes para que mida lo que la teoría dice que
debería medir. Todas las variables se construyen a nivel país-trimestre en la fecha t (sin rezagar);
el rezago de un trimestre lo aplica f1_evaluar.py, igual que la regresión principal.

Familias (ver REPORTE_features.md):
  F1  costo esperado del rescate frente al tamaño del país
  F2  fragilidad sin el piso de la malla de pérdidas
  F3  ingredientes de la fragilidad, banco por banco
  F4  fragilidad específica de la banca frente a la bolsa
  F5  riesgo de cola abierto: media, distancia a la baja y al alza
  F6  índice de condiciones financieras por bloques y sin la tasa local
  F7  riesgo de cola suavizado, propio del país, sorpresas y precisión
  F10 memoria y dinámica
(F8, simultaneidad, y F9, variable dependiente, se arman en f1 porque usan variables ya rezagadas.)

Salidas: experimentos/features_panel.csv y features_diccionario.md. No se integra a ningún documento.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy.stats import norm

import x0_comun as x0

warnings.filterwarnings("ignore")
COD = os.path.abspath(os.path.join(x0.BBG, "..", ".."))
sys.path.insert(0, os.path.join(COD, "JLoss_reconstruction"))
sys.path.insert(0, os.path.join(COD, "GaR"))
IND = os.path.join(COD, "GaR", "individuals")
PAISES = ["brazil", "chile", "china", "colombia", "india", "indonesia", "malaysia", "mexico", "peru",
          "philippines", "poland", "southafrica", "turkey"]
PISO = 2.16
DIC = []


def dic(var, familia, definicion, fuente):
    DIC.append((var, familia, definicion, fuente))


def leer2(path, nombre):
    """lector tolerante de los CSV de dos columnas (fecha, valor) de GaR/individuals."""
    g = pd.read_csv(path, sep=None, engine="python")
    g = g.iloc[:, :2]; g.columns = ["d", nombre]
    s = g["d"].astype(str)
    if s.str.fullmatch(r"\d{6}").all():
        g["d"] = pd.to_datetime(s, format="%Y%m") + pd.offsets.MonthEnd(0)
    else:
        g["d"] = pd.to_datetime(s, dayfirst=True, errors="coerce")
    g[nombre] = pd.to_numeric(g[nombre], errors="coerce")
    return g.dropna().sort_values("d").reset_index(drop=True)


def qn(q):
    p = pd.PeriodIndex(q, freq="Q")
    return p.year * 4 + p.quarter


def lag(df, col, k=1):
    """rezago k dentro del país, válido solo si el trimestre es consecutivo."""
    g = df.groupby("country")
    ok = (df["_qn"] - g["_qn"].shift(k)) == k
    return g[col].shift(k).where(ok)


def rolling(df, col, w, fn):
    """estadístico móvil de un solo lado sobre w trimestres consecutivos (incluye t)."""
    partes = [df[col]] + [lag(df, col, k) for k in range(1, w)]
    M = pd.concat(partes, axis=1)
    out = getattr(M, fn)(axis=1)
    return out.where(M.notna().all(axis=1))


# ---------------------------------------------------------------- base
def base():
    raw = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    raw = raw[raw["country"].isin(PAISES)].copy()
    raw["_qn"] = qn(raw["quarter"])
    raw = raw.sort_values(["country", "_qn"]).reset_index(drop=True)
    raw["lnJ"] = np.log(raw["JLoss"])
    raw["D"] = -raw["GaR"] * 100.0
    return raw


# ---------------------------------------------------------------- F1 tamaño
def f1_tamano(F):
    v9 = pd.read_csv(os.path.join(COD, "JLoss_reconstruction", "jloss_bloomberg", "Panel_JLoss_v9_bloomberg.csv"))
    v9 = v9.rename(columns={"countryname": "country"})[["country", "quarter", "sys_liab"]]
    F = F.merge(v9, on=["country", "quarter"], how="left")
    filas = []
    for c in PAISES:
        C = c.upper()
        g = leer2(os.path.join(IND, C, f"gGDP_{C}.csv"), "g")
        g["quarter"] = g["d"].dt.to_period("Q").astype(str)
        g = g.drop_duplicates("quarter").set_index("quarter")["g"]
        idx = pd.period_range(g.index.min(), g.index.max(), freq="Q").astype(str)
        g = g.reindex(idx)
        ln = np.zeros(len(g))                       # índice de PIB real por recursión a cuatro trimestres
        for i in range(len(g)):
            ln[i] = (ln[i - 4] if i >= 4 else 0.0) + (np.log1p(g.iloc[i]) if np.isfinite(g.iloc[i]) else np.nan)
        cpi = leer2(os.path.join(IND, C, f"CPI_{C}.csv"), "cpi")
        cpi["quarter"] = cpi["d"].dt.to_period("Q").astype(str)
        cq = cpi.groupby("quarter")["cpi"].mean()
        t = pd.DataFrame({"country": c, "quarter": idx, "ln_pib_real": ln, "g_real": g.to_numpy()})
        t["ln_cpi"] = np.log(t["quarter"].map(cq))
        filas.append(t)
    F = F.merge(pd.concat(filas), on=["country", "quarter"], how="left")
    F["ln_tamano"] = np.log(F["sys_liab"]) - F["ln_pib_real"] - F["ln_cpi"]
    F["ln_costo_pib"] = F["lnJ"] + F["ln_tamano"]
    F["ln_costo_reservas"] = F["ln_costo_pib"] - np.log(F["res_gdp"].where(F["res_gdp"] > 0))
    F["ln_costo_deuda"] = F["ln_costo_pib"] - np.log(F["debt_gdp"].where(F["debt_gdp"] > 0))
    F["ln_nbancos"] = np.log(F["n_banks"].where(F["n_banks"] > 0))
    dic("ln_tamano", "F1", "log de pasivos del sistema bancario / PIB nominal (PIB real por recursión del crecimiento interanual x IPC); definido hasta una constante por país", "Panel_JLoss_v9_bloomberg.csv; gGDP_*.csv; CPI_*.csv")
    dic("ln_costo_pib", "F1", "PRIMARIA. log de JLoss x pasivos del sistema / PIB: pérdida conjunta frente al tamaño de la economía", "ídem")
    dic("ln_costo_reservas", "F1", "pérdida conjunta frente a las reservas (reservas/PIB anual interpolado)", "ídem + panel")
    dic("ln_costo_deuda", "F1", "pérdida conjunta frente a la deuda pública", "ídem + panel")
    dic("ln_nbancos", "F1", "log del número de bancos con probabilidad válida (control: el tamaño salta cuando entra o sale un banco)", "panel")
    return F


# ---------------------------------------------------------------- F2 piso
def f2_piso(F):
    w = pd.read_csv(os.path.join(COD, "JLoss_reconstruction", "Panel_JLoss_wide.csv")).rename(
        columns={"countryname": "country", "JLoss": "JLoss_ancha"})[["country", "quarter", "JLoss_ancha"]]
    F = F.merge(w, on=["country", "quarter"], how="left")
    F["lnJ_ancha"] = np.log(F["JLoss_ancha"].where(F["JLoss_ancha"] > 0))
    F["J_exceso"] = np.log(np.maximum(F["JLoss"], PISO) / PISO)
    F["J_enpiso"] = (F["JLoss"] <= PISO * 1.02).astype(float)
    g = F.groupby("country")["lnJ"]
    F["J_z"] = (F["lnJ"] - g.transform("mean")) / g.transform("std")
    F["J_pct"] = g.rank(pct=True)
    racha = []
    for _, x in F.groupby("country"):
        n = 0; out = []
        for fuera, q, qprev in zip(1 - x["J_enpiso"], x["_qn"], x["_qn"].shift(1)):
            n = (n + 1 if (q - qprev) == 1 or n == 0 else 1) if fuera else 0
            out.append(n)
        racha += out
    F["J_racha_fuera"] = np.log1p(racha)
    dic("lnJ_ancha", "F2", "PRIMARIA. log del JLoss recalculado con malla de pérdidas ancha [0,01; 0,20] (sin India)", "Panel_JLoss_wide.csv")
    dic("J_exceso", "F2", "log del exceso sobre el piso: ln(max(JLoss; 2,16)/2,16); cero en el piso", "panel")
    dic("J_enpiso", "F2", "indicador de JLoss a menos de 2 % del piso", "panel")
    dic("J_z", "F2", "ln JLoss estandarizado dentro de cada país", "panel")
    dic("J_pct", "F2", "percentil de ln JLoss dentro de cada país", "panel")
    dic("J_racha_fuera", "F2", "log(1 + trimestres consecutivos fuera del piso)", "panel")
    return F


# ---------------------------------------------------------------- F3 y F4: datos banco por banco
def bancos():
    import jloss_engine as je
    out3, out4 = [], []
    for c in PAISES:
        d = os.path.join(COD, "Bloomberg_extraction", "output", c)
        bal = pd.read_csv(os.path.join(d, f"balance_{c}.csv")); mk = pd.read_csv(os.path.join(d, f"mktcap_{c}.csv"))
        dm = je.quarterly_inputs(bal, mk).dropna(subset=["D_star", "total_liab", "sigma_E_q", "mktcap_end"])
        dm = dm[(dm["D_star"] > 0) & (dm["mktcap_end"] > 0) & (dm["sigma_E_q"] > 0)].copy()
        E, Dd = dm["mktcap_end"], dm["D_star"]
        sE = dm["sigma_E_q"] * 2.0                                     # anualizada
        sV = E / (E + Dd) * sE + Dd / (E + Dd) * (0.05 + 0.25 * sE)    # Bharath y Shumway (2008)
        dm["dd"] = (np.log((E + Dd) / Dd) + (je.R_FREE - 0.5 * sV ** 2)) / sV
        dm["pd_ing"] = norm.cdf(-dm["dd"])
        dm["lev"] = dm["total_liab"] / E
        dm["sE"] = sE
        for q, x in dm.groupby("quarter"):
            w = x["total_liab"] / x["total_liab"].sum()
            out3.append(dict(country=c, quarter=str(q), ln_apalanc=np.log((w * x["lev"]).sum()),
                             ln_vol_banca=np.log((w * x["sE"]).sum()), dd_medio=(w * x["dd"]).sum(),
                             dd_min=x["dd"].min(), dd_disp=x["dd"].std() if len(x) > 1 else np.nan,
                             frac_estres=w[x["dd"] < 1.5].sum(), frac_estres_1=w[x["dd"] < 1.0].sum(),
                             frac_estres_2=w[x["dd"] < 2.0].sum(), pd_ing_pond=(w * x["pd_ing"]).sum(),
                             n_bancos_f3=len(x)))
        # F4: retorno diario de la banca (ponderado por capitalización del día previo) y de la bolsa
        mk["date"] = pd.to_datetime(mk["date"]); mk = mk[mk["mktcap"] > 0].sort_values(["bankname", "date"])
        mk["ret"] = mk.groupby("bankname")["mktcap"].pct_change()
        mk["w"] = mk.groupby("bankname")["mktcap"].shift(1)
        mk = mk.dropna(subset=["ret", "w"]); mk = mk[mk["ret"].abs() < 0.5]
        rb = mk.groupby("date").apply(lambda x: np.average(x["ret"], weights=x["w"]), include_groups=False).rename("rb")
        st = leer2(os.path.join(IND, c.upper(), f"STX_{c.upper()}.csv"), "stx").groupby("d")["stx"].last()
        st = st[st > 0]
        rm = st.pct_change().rename("rm"); rm = rm[rm.abs() < 0.5]
        dly = pd.concat([rb, rm], axis=1).dropna()
        dly["q"] = dly.index.to_period("Q")
        qs = sorted(dly["q"].unique())
        beta_full = np.cov(dly["rb"], dly["rm"])[0, 1] / dly["rm"].var()
        for i, q in enumerate(qs):
            x = dly[dly["q"] == q]
            prev = dly[dly["q"].isin(qs[max(0, i - 4):i])]
            beta = np.cov(prev["rb"], prev["rm"])[0, 1] / prev["rm"].var() if len(prev) >= 120 else beta_full
            idio = x["rb"] - beta * x["rm"]
            if len(x) < 20:
                continue
            out4.append(dict(country=c, quarter=str(q), banca_ret=x["rb"].sum(), bolsa_ret=x["rm"].sum(),
                             banca_ret_esp=idio.sum(), ln_banca_vol=0.5 * np.log((x["rb"] ** 2).sum()),
                             ln_bolsa_vol=0.5 * np.log((x["rm"] ** 2).sum()),
                             ln_banca_vol_esp=0.5 * np.log((idio ** 2).sum()), beta_banca=beta))
        print(f"   bancos: {c:12s} banco-trimestres {len(dm):5d}  días con retorno {len(dly):5d}", flush=True)
    dic("frac_estres", "F3", "PRIMARIA. fracción de los pasivos del sistema en bancos con distancia al incumplimiento ingenua < 1,5", "balance_*.csv, mktcap_*.csv (jloss_engine.quarterly_inputs)")
    dic("frac_estres_1 / frac_estres_2", "F3", "ídem con umbral 1,0 y 2,0", "ídem")
    dic("ln_apalanc", "F3", "log del apalancamiento a valor de mercado (pasivos / capitalización), ponderado por pasivos", "ídem")
    dic("ln_vol_banca", "F3", "log de la volatilidad accionaria anualizada de los bancos, ponderada por pasivos", "ídem")
    dic("dd_medio / dd_min / dd_disp", "F3", "distancia al incumplimiento ingenua (Bharath y Shumway, 2008): media ponderada, peor banco y dispersión entre bancos", "ídem")
    dic("pd_ing_pond", "F3", "probabilidad de incumplimiento ingenua ponderada por pasivos", "ídem")
    dic("ln_banca_vol_esp", "F4", "PRIMARIA. log de la volatilidad trimestral del retorno de la banca en exceso de la bolsa local (beta de los cuatro trimestres previos)", "mktcap_*.csv, STX_*.csv")
    dic("banca_ret_esp", "F4", "retorno trimestral de la banca en exceso de la bolsa", "ídem")
    dic("ln_bolsa_vol / bolsa_ret", "F4", "volatilidad y retorno trimestral del índice bursátil del país (componente de mercado)", "STX_*.csv")
    dic("ln_banca_vol / banca_ret", "F4", "volatilidad y retorno trimestral de la banca, sin depurar", "mktcap_*.csv")
    return pd.DataFrame(out3), pd.DataFrame(out4)


# ---------------------------------------------------------------- F5 cola abierta
def f5_cola(F):
    F["media_pp"] = F["gar_mean"] * 100.0
    F["D_media"] = -F["media_pp"]
    F["D_baja"] = (F["gar_mean"] - F["GaR"]) * 100.0
    F["D_alza"] = (F["GaR"] + F["iqr_05_95"] - F["gar_mean"]) * 100.0
    F["D_disp"] = F["std"] * 100.0
    F["D_asim"] = F["skew"]
    F["D_prof"] = (F["GaR"] - F["ES"]) * 100.0
    dic("D_baja", "F5", "PRIMARIA. distancia a la baja: media condicional menos cuantil 5 % (pp). D = D_media + D_baja", "panel (gar_mean, GaR)")
    dic("D_media", "F5", "menos la media condicional del crecimiento (pp)", "panel")
    dic("D_alza", "F5", "PLACEBO de simetría. distancia al alza: cuantil 95 % menos media (pp)", "panel (GaR + iqr_05_95)")
    dic("D_disp / D_asim / D_prof", "F5", "desviación estándar, asimetría y profundidad de la cola (cuantil 5 % menos pérdida esperada)", "panel")
    return F


# ---------------------------------------------------------------- F6 índice financiero por bloques
def f6_fci(F):
    import fci_engine as fe
    filas = []
    for c in PAISES:
        C = c.upper()
        try:
            x = fe.compute_fci(os.path.join(IND, C), C, os.path.join(IND, "US"), final="2026-06-30")
        except Exception as e:                                   # se reporta y se sigue
            print(f"   FCI {c}: no se pudo regenerar ({type(e).__name__}: {e})", flush=True)
            continue
        x["quarter"] = pd.to_datetime(x["DATES"]).dt.to_period("Q").astype(str)
        q = x.groupby("quarter")[["iSTX", "iRyr", "iEER", "FCI"]].mean().reset_index()
        q["country"] = c
        guard = leer2(os.path.join(IND, C, f"FCI_{C}.csv"), "fci0")
        guard["quarter"] = guard["d"].dt.to_period("Q").astype(str)
        q = q.merge(guard.groupby("quarter")["fci0"].mean().reset_index(), on="quarter", how="left")
        print(f"   FCI {c:12s} trimestres {len(q):3d}  corr con el guardado {q[['FCI', 'fci0']].corr().iloc[0, 1]:.3f}", flush=True)
        filas.append(q)
    if filas:
        q = pd.concat(filas).rename(columns={"FCI": "fci", "iSTX": "fci_bolsa", "iRyr": "fci_tasa", "iEER": "fci_cambio"})
        F = F.merge(q[["country", "quarter", "fci", "fci_bolsa", "fci_tasa", "fci_cambio"]], on=["country", "quarter"], how="left")
    carp = os.path.join(IND, "nlhpc_gar_all18")
    for lab, arch in (("D_ins", "gar_insample_base.csv"), ("D_ins_sintasa", "gar_insample_noCDIFF.csv"), ("D_ins_sinbolsa", "gar_insample_noSTX.csv")):
        g = pd.read_csv(os.path.join(carp, arch))[["country", "quarter", "GaR"]]
        g[lab] = -g["GaR"] * 100.0
        F = F.merge(g[["country", "quarter", lab]], on=["country", "quarter"], how="left")
    dic("D_ins_sintasa", "F6", "PRIMARIA. riesgo de cola (en muestra) con el índice financiero sin el diferencial de tasas reales local-EE.UU.", "gar_insample_noCDIFF.csv")
    dic("D_ins / D_ins_sinbolsa", "F6", "riesgo de cola en muestra, base y sin el bloque bursátil (comparación igual a igual)", "gar_insample_*.csv")
    dic("fci / fci_bolsa / fci_tasa / fci_cambio", "F6", "índice de condiciones financieras y sus tres bloques, promedio trimestral, regenerados con fci_engine.compute_fci", "STX/Ryr/CPI/rEER por país")
    return F


# ---------------------------------------------------------------- F7 y F10
def f7_f10(F):
    F["D_mm4"] = rolling(F, "D", 4, "mean")
    F["D_pct"] = F.groupby("country")["D"].rank(pct=True)
    F["D_propio"] = F["D"] - F.groupby("quarter")["D"].transform("mean")
    F["J_propio"] = F["lnJ"] - F.groupby("quarter")["lnJ"].transform("mean")
    F["sorpresa_crec"] = F["g_real"] * 100.0 - lag(F, "media_pp", 1)      # realizado menos media condicional previa
    F["cola_materializada"] = (F["g_real"] < lag(F, "GaR", 1)).astype(float).where(F["g_real"].notna() & lag(F, "GaR", 1).notna())
    rep = pd.read_csv(os.path.join(IND, "nlhpc_gar_all18", "gar_replicas_nlhpc.csv"), usecols=["country", "quarter", "GaR"])
    sd = (rep.groupby(["country", "quarter"])["GaR"].std() * 100.0).rename("D_ee_replicas").reset_index()
    F = F.merge(sd, on=["country", "quarter"], how="left")
    for v, n_ in (("lnJ", "J"), ("D", "D")):
        F[f"{n_}_d4"] = F[v] - lag(F, v, 4)
        F[f"{n_}_brecha8"] = F[v] - rolling(F, v, 8, "mean")
        F[f"{n_}_max4"] = rolling(F, v, 4, "max")
        F[f"{n_}_vol4"] = rolling(F, v, 4, "std")
    F["reer_ln"] = np.log(F["reer"].where(F["reer"] > 0))                  # placebo
    g = F.groupby("country")["reer_ln"]
    F["reer_z"] = (F["reer_ln"] - g.transform("mean")) / g.transform("std")
    F["reer_max4"] = rolling(F, "reer_ln", 4, "max")
    dic("D_mm4", "F7", "PRIMARIA. media móvil de un solo lado de 4 trimestres del riesgo de cola", "panel")
    dic("D_pct", "F7", "percentil del riesgo de cola dentro de cada país", "panel")
    dic("D_propio / J_propio", "F7", "riesgo menos el promedio de los 13 países en el trimestre (componente propio del país)", "panel")
    dic("sorpresa_crec", "F7", "crecimiento interanual realizado menos la media condicional del trimestre anterior (pp); la alineación de fechas es un supuesto", "gGDP_*.csv, panel")
    dic("cola_materializada", "F7", "indicador: el crecimiento realizado cayó bajo el cuantil 5 % previo", "ídem")
    dic("D_ee_replicas", "F7", "desviación estándar del riesgo de cola entre las 500 réplicas (error de estimación, pp)", "gar_replicas_nlhpc.csv")
    dic("J_max4", "F10", "PRIMARIA. máximo de ln JLoss en los últimos 4 trimestres", "panel")
    dic("J_d4 / J_brecha8 / J_vol4 (y D_*)", "F10", "cambio a 4 trimestres, brecha frente a la media móvil de 8 y desviación estándar de 4 trimestres", "panel")
    dic("reer_z / reer_max4", "placebo", "tipo de cambio real transformado igual que la fragilidad (no debería explicar el spread)", "panel")
    return F


def main():
    print("f0: construyendo variables", flush=True)
    F = base()
    n0 = len(F)
    F = f1_tamano(F)
    F = f2_piso(F)
    b3, b4 = bancos()
    F = F.merge(b3, on=["country", "quarter"], how="left").merge(b4, on=["country", "quarter"], how="left")
    F = f5_cola(F)
    F = f6_fci(F)
    F = f7_f10(F)
    assert len(F) == n0, (len(F), n0)
    # comprobación: la tabla reproduce el panel de estimación
    d = x0.datos()
    chk = d.merge(F[["country", "quarter", "lnJ", "D", "_qn"]], on=["country", "quarter"], how="left")
    F.to_csv(os.path.join(x0.HERE, "features_panel.csv"), index=False)
    cob = F[F["quarter"].isin(d["quarter"].unique())]
    with open(os.path.join(x0.HERE, "features_diccionario.md"), "w", encoding="utf-8") as f:
        f.write("# Diccionario de variables construidas (experimento, no integrado)\n\n")
        f.write("Todas a nivel país-trimestre en t; el rezago de un trimestre se aplica al evaluar.\n\n")
        f.write("| Variable | Familia | Definición | Fuente |\n|---|---|---|---|\n")
        for v, fa, de, fu in DIC:
            f.write(f"| `{v}` | {fa} | {de} | {fu} |\n")
        f.write("\n## Cobertura (fracción de país-trimestres con dato, 13 países)\n\n| Variable | Cobertura | Países |\n|---|---|---|\n")
        for c in F.columns:
            if c in ("country", "quarter", "_qn", "embi_source") or F[c].dtype == object:
                continue
            f.write(f"| `{c}` | {F[c].notna().mean():.2f} | {F.loc[F[c].notna(), 'country'].nunique()} |\n")
    print(f"-> features_panel.csv ({F.shape[0]} filas, {F.shape[1]} columnas) y features_diccionario.md", flush=True)
    print("   correlaciones de control (dentro de la tabla):")
    for a, b in (("lnJ", "lnJ_ancha"), ("lnJ", "frac_estres"), ("lnJ", "ln_apalanc"), ("lnJ", "ln_banca_vol"), ("lnJ", "ln_bolsa_vol"),
                 ("lnJ", "ln_costo_pib"), ("D", "D_media"), ("D", "D_baja"), ("D", "D_ins"), ("D_ins", "D_ins_sintasa"), ("D", "fci")):
        if a in F and b in F:
            print(f"     corr({a}, {b}) = {F[[a, b]].corr().iloc[0, 1]:+.3f}   n = {F[[a, b]].dropna().shape[0]}")


if __name__ == "__main__":
    main()
