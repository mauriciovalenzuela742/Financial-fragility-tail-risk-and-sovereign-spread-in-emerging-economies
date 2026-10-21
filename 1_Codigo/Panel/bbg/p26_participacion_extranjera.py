# -*- coding: utf-8 -*-
"""
p26_participacion_extranjera.py -- moderador ex ante: quién tiene la deuda soberana.

Objeción de árbitro: el grupo "núcleo de 11 economías vs. Polonia e India" (p16) se definió ex post.
El contraste limpio usa un moderador continuo y medido de forma independiente: la participación de
no residentes en la deuda del gobierno (Arslanalp y Tsuda, FMI, "Tracking Global Demand for Emerging
Market Sovereign Debt", base trimestral, versión de mayo de 2026).

Datos: 2_Datos/Database_For_Posting_EM_Frozen.xlsx. De las hojas "Table 2. Foreign", "Table 2.1
ForeignOfficial", "Table 2.2 ForeignBank" y "Table 2.3 ForeignNonbank" se lee el bloque "Percent of
Total Debt" (fracción de la deuda total del gobierno general; se multiplica por 100). El script
escribe 2_Datos/participacion_extranjera.csv (formato largo, 13 países del panel) y luego estima.

    ln EMBI = a_i + d_t + b1 J + b2 D + b3 JxD + f F + h1 J*F + h2 D*F + h3 JxD*F + e

=========================== PRE-ESPECIFICACIÓN (2026-10-13) ===========================
Escrita ANTES del código de estimación y antes de ver ningún resultado. No se agregan pruebas después.

 - Moderador PRIMARIO F = participación de los tenedores extranjeros NO BANCARIOS en la deuda total
   del gobierno (el inversionista marginal sensible al riesgo), rezagada 4 trimestres y
   estandarizada sobre la muestra de estimación.
 - Familia PRIMARIA: en ln EMBI = EF + b1 J + b2 D + b3 JxD + f F + h1 J·F + h2 D·F + h3 JxD·F, los
   tres coeficientes h1, h2, h3; signo predicho positivo; corrección de Holm sobre los tres; el
   veredicto lo da el wild cluster bootstrap por país (Webb, B=1999); los p de Driscoll-Kraay y de
   cluster por país se reportan al lado. Logs es la forma primaria; se reporta la gemela en pb.
 - SECUNDARIAS (rotuladas como tales, sin Holm): participación extranjera total; F ex ante
   invariante en el tiempo (media del país 2004-2007) con su efecto directo absorbido por los
   efectos fijos de país; rezago de 8 trimestres; muestra sin trimestres de crisis; descomposición
   entre/dentro de F (media del país vs. desviación).
 - Consecuencia declarada de antemano: si h3 no es significativo bajo la prueba primaria, el
   resultado previo de heterogeneidad del "núcleo de 11 economías" se degrada a exploratorio.
=======================================================================================

Además, como HECHOS DESCRIPTIVOS (sin prueba): media por país de la participación total y no bancaria
en la muestra y en 2004-2007, ordenadas; si el grupo de contraste usado hasta ahora (Polonia e India,
descrito como de "mercados de deuda local profundos") coincide con baja participación extranjera;
pérdida de observaciones por el rezago y proporción de la varianza de F que es entre países.

Salida: bbg/paper_participacion_numeros.csv (o _nivlag) y fig_participacion_extranjera. Reutiliza
p13, p14 y p16; no modifica ningún archivo canónico.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

D2 = os.path.abspath(os.path.join(HERE, "..", "..", "..", "2_Datos"))
XLSX = os.path.join(D2, "Database_For_Posting_EM_Frozen.xlsx")
DATOS = os.path.join(D2, "participacion_extranjera.csv")
HOJAS = {"foreign_share": "Table 2. Foreign", "foreign_nonbank_share": "Table 2.3 ForeignNonbank",
         "foreign_official_share": "Table 2.1 ForeignOfficial", "foreign_bank_share": "Table 2.2 ForeignBank"}
PAISES = {"Brazil": "brazil", "Chile": "chile", "China": "china", "Colombia": "colombia", "India": "india",
          "Indonesia": "indonesia", "Malaysia": "malaysia", "Mexico": "mexico", "Peru": "peru",
          "Philippines": "philippines", "Poland": "poland", "South Africa": "southafrica", "Turkey": "turkey"}
NUM = {}
CLU = dict(cov_type="clustered", cluster_entity=True)
B_PRIM, B_SEC = 1999, 999


def num(k, v):
    NUM[k] = float(v)
    return v


# ================================================================ datos
def _bloque(hoja):
    """bloque "Percent of Total Debt" de una hoja: fila de encabezado ubicada por su texto, 22 países."""
    x = pd.read_excel(XLSX, sheet_name=hoja, header=None)
    fila = [i for i in range(len(x)) if isinstance(x.iat[i, 0], str) and x.iat[i, 0].strip() == "Percent of Total Debt"]
    assert len(fila) == 1, (hoja, fila)
    h = fila[0]
    trim = [str(v) for v in x.iloc[h, 1:] if isinstance(v, str) and len(v) == 6 and v[4] == "Q"]
    assert trim[0] == "2004Q1" and trim[-1] == "2025Q4" and len(trim) == 88, (hoja, trim[:2], trim[-2:])
    b = x.iloc[h + 1:h + 23, :len(trim) + 1].copy()
    b.columns = ["pais"] + trim
    b["pais"] = b["pais"].astype(str).str.strip()
    assert b["pais"].nunique() == 22 and set(PAISES) <= set(b["pais"]), (hoja, sorted(b["pais"]))
    b = b[b["pais"].isin(PAISES)].melt(id_vars="pais", var_name="quarter", value_name="v")
    b["country"] = b["pais"].map(PAISES)
    b["v"] = pd.to_numeric(b["v"], errors="coerce") * 100.0
    return b[["country", "quarter", "v"]], h


def construir_datos():
    out = None
    for col, hoja in HOJAS.items():
        b, h = _bloque(hoja)
        print(f"   {hoja}: encabezado 'Percent of Total Debt' en la fila {h} (base 0) = {h + 1} (base 1)")
        b = b.rename(columns={"v": col})
        out = b if out is None else out.merge(b, on=["country", "quarter"], how="outer")
    out = out.sort_values(["country", "quarter"]).reset_index(drop=True)
    g = out.set_index(["country", "quarter"])["foreign_share"]
    for (c, q), ref in ((("brazil", "2010Q4"), 11.96), (("poland", "2015Q4"), 54.05), (("indonesia", "2025Q4"), 37.23)):
        assert abs(g[(c, q)] - ref) < 0.01, (c, q, g[(c, q)])
        num(f"dato_{c}_{q}", g[(c, q)])
    suma = out[["foreign_nonbank_share", "foreign_official_share", "foreign_bank_share"]].sum(axis=1, min_count=3)
    num("dato_max_dif_suma_partes", (suma - out["foreign_share"]).abs().max())
    num("dato_n_filas", len(out)); num("dato_n_faltantes_total", out["foreign_share"].isna().sum())
    num("dato_n_faltantes_nobanc", out["foreign_nonbank_share"].isna().sum())
    out.to_csv(DATOS, index=False)
    print("   ->", DATOS, out.shape)
    return out


def rezagar(d, f, col, k, nombre):
    """agrega a d el valor de `col` k trimestres antes."""
    x = f[["country", "quarter", col]].copy()
    x["quarter"] = (pd.PeriodIndex(x["quarter"], freq="Q") + k).astype(str)
    return d.merge(x.rename(columns={col: nombre}), on=["country", "quarter"], how="left")


# ================================================================ estimación
def holm(ps):
    """p ajustados de Holm, en el orden original."""
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0.0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1.0, run)
    return adj


def _centrar(d, cols):
    dd = d.dropna(subset=["ln_EMBI", "ln_JLoss_l1", "D_l1"] + cols).copy()
    dd["J_c"] = dd["ln_JLoss_l1"] - dd["ln_JLoss_l1"].mean()
    dd["T_c"] = dd["D_l1"] - dd["D_l1"].mean()
    dd["JxT"] = dd["J_c"] * dd["T_c"]
    return dd


def _ajustar(dd, rhs, pares, pref, B):
    import p14_arbitro_lnlag as p14
    idx = dd.set_index(["country", "t"])
    f = "ln_EMBI ~ " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, idx).fit(**p14.DK); mc = PanelOLS.from_formula(f, idx).fit(**CLU)
    num(f"{pref}_N", m.nobs); num(f"{pref}_paises", dd["country"].nunique())
    for n_, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"{pref}_{lab}", m.params[n_]); num(f"{pref}_{lab}_p_dk", m.pvalues[n_])
    for n_, lab in pares:
        num(f"{pref}_{lab}", m.params[n_]); num(f"{pref}_{lab}_se_dk", m.std_errors[n_])
        num(f"{pref}_{lab}_p_dk", m.pvalues[n_]); num(f"{pref}_{lab}_p_pais", mc.pvalues[n_])
        if n_ != "F":
            p, _ = p14.wild_boot(dd, "ln_EMBI", rhs, n_, B=B, weights="webb")
            num(f"{pref}_{lab}_p_wild", p)
    print(f"   {pref}: N={int(m.nobs)}", flush=True)
    return m


def estimar(d, col, pref, B=B_SEC, absorbido=False):
    """especificación con F (columna `col`, estandarizada sobre la muestra) y sus tres interacciones.
    Si `absorbido`, F no varía en el tiempo y su efecto directo queda en los efectos fijos de país."""
    dd = _centrar(d, [col])
    dd["F"] = (dd[col] - dd[col].mean()) / dd[col].std()
    dd["JxF"] = dd["J_c"] * dd["F"]; dd["TxF"] = dd["T_c"] * dd["F"]; dd["JxTxF"] = dd["JxT"] * dd["F"]
    rhs = ["J_c", "T_c", "JxT"] + ([] if absorbido else ["F"]) + ["JxF", "TxF", "JxTxF"]
    pares = ([] if absorbido else [("F", "f")]) + [("JxF", "h1"), ("TxF", "h2"), ("JxTxF", "h3")]
    num(f"{pref}_F_media", dd[col].mean()); num(f"{pref}_F_de", dd[col].std())
    _ajustar(dd, rhs, pares, pref, B)
    return dd


def entre_dentro(d, col, pref, B=B_SEC):
    """F = media del país (entre) + desviación (dentro), ambas en unidades de la d.e. total de F."""
    dd = _centrar(d, [col])
    s = dd[col].std()
    mp = dd.groupby("country")[col].transform("mean")
    dd["Fb"] = (mp - dd[col].mean()) / s; dd["Fw"] = (dd[col] - mp) / s
    for a in ("b", "w"):
        dd[f"JxF{a}"] = dd["J_c"] * dd[f"F{a}"]; dd[f"TxF{a}"] = dd["T_c"] * dd[f"F{a}"]
        dd[f"JxTxF{a}"] = dd["JxT"] * dd[f"F{a}"]
    rhs = ["J_c", "T_c", "JxT", "JxFb", "TxFb", "JxTxFb", "Fw", "JxFw", "TxFw", "JxTxFw"]
    pares = [("JxFb", "h1_entre"), ("TxFb", "h2_entre"), ("JxTxFb", "h3_entre"),
             ("JxFw", "h1_dentro"), ("TxFw", "h2_dentro"), ("JxTxFw", "h3_dentro")]
    _ajustar(dd, rhs, pares, pref, B)


# ================================================================ hechos descriptivos
def descriptivos(d, f, dd_prim):
    import p16_heterogeneidad as p16
    paises = sorted(d["country"].unique())
    cont = d.merge(f, on=["country", "quarter"], how="left")           # participación contemporánea en la muestra
    pre = f[(f["quarter"] >= "2004Q1") & (f["quarter"] <= "2007Q4")]
    filas = []
    for c in paises:
        g = cont[cont["country"] == c]; gp = pre[pre["country"] == c]; gf = f[f["country"] == c]
        filas.append(dict(country=c, total_muestra=g["foreign_share"].mean(), nobanc_muestra=g["foreign_nonbank_share"].mean(),
                          total_0407=gp["foreign_share"].mean(), nobanc_0407=gp["foreign_nonbank_share"].mean(),
                          total_min=gf["foreign_share"].min(), total_max=gf["foreign_share"].max(),
                          oficial_muestra=g["foreign_official_share"].mean(), banc_muestra=g["foreign_bank_share"].mean()))
    t = pd.DataFrame(filas).set_index("country")
    for col in ("total_muestra", "nobanc_muestra", "total_0407", "nobanc_0407"):
        t["rk_" + col] = t[col].rank(ascending=False).astype(int)          # 1 = mayor participación extranjera
    for c in paises:
        for col in t.columns:
            num(f"desc_{c}_{col}", t.loc[c, col])
    con = t.loc[p16.CONV]; nuc = t.drop(index=p16.CONV)
    for col in ("total_muestra", "nobanc_muestra", "total_0407", "nobanc_0407"):
        num(f"desc_contraste_media_{col}", con[col].mean()); num(f"desc_nucleo_media_{col}", nuc[col].mean())
        num(f"desc_mediana13_{col}", t[col].median())
    # varianza de F (primario, rezago 4, muestra de estimación): entre vs. dentro de países
    x = dd_prim["F_nb_l4"]; mp = dd_prim.groupby("country")["F_nb_l4"].transform("mean")
    num("var_entre_share", ((mp - x.mean()) ** 2).sum() / ((x - x.mean()) ** 2).sum())
    num("var_dentro_share", ((x - mp) ** 2).sum() / ((x - x.mean()) ** 2).sum())
    num("corr_total_nobanc_l4", dd_prim[["F_nb_l4", "F_tot_l4"]].corr().iloc[0, 1])
    num("corr_F_J", dd_prim[["F", "J_c"]].corr().iloc[0, 1]); num("corr_F_T", dd_prim[["F", "T_c"]].corr().iloc[0, 1])
    print(t.round(2).sort_values("total_muestra", ascending=False).to_string())
    return t


def figura(t):
    import matplotlib.pyplot as plt
    import p13_figuras_paper as p13
    import p16_heterogeneidad as p16
    s = t.sort_values("total_muestra")
    y = np.arange(len(s))
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    col = [p13.RED if c in p16.CONV else p13.BLUE for c in s.index]
    ax.barh(y + 0.2, s["total_muestra"], height=0.38, color=col, label="total no residentes")
    ax.barh(y - 0.2, s["nobanc_muestra"], height=0.38, color=col, alpha=0.45, label="no residentes no bancarios")
    ax.plot(s["total_0407"], y + 0.2, "|", color=p13.INK, ms=9, mew=1.6, label="total, media 2004–2007")
    ax.set_yticks(y); ax.set_yticklabels([p13.NOMBRE.get(c, c) for c in s.index])
    for lab, c in zip(ax.get_yticklabels(), s.index):
        if c in p16.CONV:
            lab.set_color(p13.RED); lab.set_fontweight("bold")
    ax.set_xlabel("participación en la deuda total del gobierno general (%), media en la muestra de estimación")
    ax.set_title("Participación de no residentes en la deuda del gobierno (Arslanalp y Tsuda, FMI)\n"
                 "en rojo: grupo de contraste usado hasta ahora (Polonia e India)", fontsize=9.5)
    ax.legend(fontsize=8, loc="lower right")
    p13.save(fig, "fig_participacion_extranjera")


# ================================================================ main
def main():
    if not os.path.exists(XLSX) and not os.path.exists(DATOS):
        print("p26: falta", XLSX)
        return
    import p13_figuras_paper as p13
    NIV = p13.NIV
    SFX = "_nivlag" if NIV else ""
    print("p26: panel", os.path.basename(os.environ["JLOSS_PANEL_CSV"]), "| forma", "niveles" if NIV else "logs")
    f = construir_datos() if os.path.exists(XLSX) else pd.read_csv(DATOS)
    d = p13.datos()
    m0, _ = p13.fit(d)
    ref = 0.2464 if NIV else -0.0112
    assert int(m0.nobs) == 765 and abs(m0.params["JxT"] - ref) < 5e-4, (m0.nobs, m0.params["JxT"])
    num("principal_N", m0.nobs)
    for n_, lab in (("J_c", "b1"), ("T_c", "b2"), ("JxT", "b3")):
        num(f"principal_{lab}", m0.params[n_])
    assert set(d["country"].unique()) == set(PAISES.values())
    for col, nom in (("foreign_nonbank_share", "F_nb"), ("foreign_share", "F_tot")):
        d = rezagar(d, f, col, 4, nom + "_l4")
    d = rezagar(d, f, "foreign_nonbank_share", 8, "F_nb_l8")
    pre = f[(f["quarter"] >= "2004Q1") & (f["quarter"] <= "2007Q4")].groupby("country")["foreign_nonbank_share"].mean()
    assert pre.notna().all() and len(pre) == 13
    d["F_nb_exante"] = d["country"].map(pre)

    # ---- cobertura: qué se pierde con el rezago de cuatro trimestres
    perd = d[d["F_nb_l4"].isna()]
    num("perdidas_l4", len(perd)); num("perdidas_l8", d["F_nb_l8"].isna().sum())
    print("   perdidas por el rezago 4:", perd.groupby("country")["quarter"].apply(list).to_dict())

    # ---- PRIMARIA: no bancarios, rezago 4; h1, h2, h3 con Holm sobre el wild bootstrap
    dd = estimar(d, "F_nb_l4", "prim", B=B_PRIM)
    for tipo in ("wild", "dk", "pais"):
        adj = holm([NUM[f"prim_{h}_p_{tipo}"] for h in ("h1", "h2", "h3")])
        for h, a in zip(("h1", "h2", "h3"), adj):
            num(f"prim_{h}_p_{tipo}_holm", a)
    num("prim_h3_significativo_5pct", float(NUM["prim_h3"] > 0 and NUM["prim_h3_p_wild_holm"] < 0.05))
    num("prim_alguno_significativo_5pct", float(any(NUM[f"prim_{h}"] > 0 and NUM[f"prim_{h}_p_wild_holm"] < 0.05
                                                     for h in ("h1", "h2", "h3"))))

    # ---- SECUNDARIAS (sin Holm)
    estimar(d, "F_tot_l4", "sec_total")
    estimar(d, "F_nb_exante", "sec_exante", absorbido=True)
    estimar(d, "F_nb_l8", "sec_l8")
    estimar(d[~d["quarter"].isin(p13.CRISIS_BAT)], "F_nb_l4", "sec_sincrisis")
    entre_dentro(d, "F_nb_l4", "sec_ed")

    # ---- hechos descriptivos y figura
    dd["F_tot_l4"] = dd["F_tot_l4"].astype(float)
    t = descriptivos(d, f, dd)
    if not NIV:                                   # la figura no depende de la forma funcional
        figura(t)

    out = os.path.join(HERE, f"paper_participacion_numeros{SFX}.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        if not k.startswith("desc_") or "contraste" in k or "nucleo" in k or "mediana" in k:
            print(f"  {k:38s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
