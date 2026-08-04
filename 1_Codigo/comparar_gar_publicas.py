#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comparar_gar_publicas.py
Compara la serie GaR (métrica oficial, panel de 17 economías) contra métricas
de predicción de riesgo PÚBLICAS e independientes, en nivel y en variación.

GaR = percentil 5% del crecimiento interanual (mayor = piso más alto = MENOS
riesgo). Una métrica de estrés/riesgo que SUBE con el riesgo debe correlacionar
NEGATIVO con el GaR.

Métricas públicas soportadas:
  Locales (ya en tu panel):
    - US_HY_spread : ICE BofA US HY OAS (crédito, familia 'credit spread' Tabla A.3)
    - VIX          : volatilidad implícita S&P500 (nota: entra en el GaR)
  Descargables (--download, corre en tu máquina con red):
    - OFR_FSI      : OFR Financial Stress Index, total  (global)
    - OFR_FSI_EM   : OFR FSI, contribución 'Emerging markets'
    - EM_OAS       : FRED ICE BofA EM Corporate OAS (BAMLEMCBPIOAS)
  Externa por país (--vlab archivo.csv):
    - SRISK        : NYU Stern V-Lab, riesgo sistémico por país (capital shortfall)

Uso:
    python comparar_gar_publicas.py --panel .                         # locales
    python comparar_gar_publicas.py --panel . --download              # + OFR/FRED
    python comparar_gar_publicas.py --panel . --vlab vlab_srisk.csv   # + SRISK por país
    python comparar_gar_publicas.py --selftest                        # prueba con fixtures

Salidas:
    comparacion_gar_publicas.csv       (correlaciones por país y pooled)
    fig_gar_vs_publicas_overlay.png    (overlays por país, métrica mejor cubierta)
    fig_gar_vs_publicas_corr.png       (correlaciones por país y métrica)
Dependencias: pandas, numpy, matplotlib
"""
import argparse
import os
import numpy as np
import pandas as pd

SOURCES = {
    "OFR_FSI":     "https://www.financialresearch.gov/financial-stress-index/data/fsi.csv",
    "FRED_EM_OAS": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLEMCBPIOAS",
    "FRED_US_HY":  "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2",
    # IMF GaR: GFSR (descarga manual, sin API de serie limpia).
    # V-Lab SRISK por país: https://vlab.stern.nyu.edu/srisk  (--vlab con el CSV exportado).
}
# métrica -> signo esperado de la correlación con el GaR
EXPECTED_SIGN = {"US_HY_spread": -1, "VIX": -1, "OFR_FSI": -1, "OFR_FSI_EM": -1,
                 "EM_OAS": -1, "SRISK": -1}


def zscore(s):
    s = pd.to_numeric(s, errors="coerce")
    sd = s.std()
    return (s - s.mean()) / sd if sd else s * np.nan


def to_q(dtser, fmt=None):
    return pd.PeriodIndex(pd.to_datetime(dtser, format=fmt, errors="coerce"), freq="Q")


def norm_country(x):
    """Normaliza etiquetas de país al código del panel (upper, sin espacios/puntos)."""
    return (str(x).strip().upper().replace(".", "")
            .replace("SOUTH ", "SOUTH").replace(" ", ""))


# ---------------- CARGA GaR ----------------
def load_gar(panel_dir):
    for name in ("gar_panel_all17.csv", "gar_panel_all15.csv", "gar_panel_latam.csv"):
        p = os.path.join(panel_dir, name)
        if os.path.exists(p):
            df = pd.read_csv(p); break
    else:
        raise SystemExit("No encuentro gar_panel_*.csv en " + panel_dir)
    df = df.rename(columns={"countryname": "country"})
    df["country"] = df["country"].map(norm_country)
    df["q"] = pd.PeriodIndex(df["quarter"].astype(str).str.upper(), freq="Q")
    df["GaR"] = pd.to_numeric(df["GaR"], errors="coerce")
    return df[["country", "q", "GaR"]].dropna()


# ---------------- MÉTRICAS PÚBLICAS ----------------
def load_local_public(panel_dir):
    """Series públicas globales ya disponibles en tu panel."""
    series = {}
    gc = os.path.join(panel_dir, "global_controls_quarterly.csv")
    if os.path.exists(gc):
        g = pd.read_csv(gc)
        g["q"] = pd.PeriodIndex(g["quarter"].astype(str), freq="Q")
        if "US_HY_spread" in g:
            series["US_HY_spread"] = g.set_index("q")["US_HY_spread"]
    vix = os.path.join(panel_dir, "VIX_History.csv")
    if os.path.exists(vix):
        v = pd.read_csv(vix)
        v["q"] = to_q(v["DATE"], fmt="%m/%d/%Y")
        series["VIX"] = v.dropna(subset=["q"]).groupby("q")["CLOSE"].mean()
    out = pd.DataFrame(series)
    return out.apply(pd.to_numeric, errors="coerce")


def parse_ofr(path_or_url):
    """OFR FSI: columnas reales Date, 'OFR FSI', ..., 'Emerging markets' (diario)."""
    o = pd.read_csv(path_or_url)
    o.columns = [c.strip() for c in o.columns]
    dcol = [c for c in o.columns if c.lower() == "date"][0]
    o["q"] = to_q(o[dcol])
    got = {}
    if "OFR FSI" in o.columns:
        got["OFR_FSI"] = o.groupby("q")["OFR FSI"].mean()
    em = [c for c in o.columns if "emerg" in c.lower()]
    if em:
        got["OFR_FSI_EM"] = o.groupby("q")[em[0]].mean()
    return pd.DataFrame(got)


def parse_fred(url, name):
    f = pd.read_csv(url)
    f.columns = ["date", name]
    f["q"] = to_q(f["date"])
    return pd.to_numeric(f[name], errors="coerce").groupby(f["q"]).mean().to_frame(name)


def try_download():
    got = []
    for fn, args in [(parse_ofr, (SOURCES["OFR_FSI"],)),
                     (parse_fred, (SOURCES["FRED_EM_OAS"], "EM_OAS"))]:
        try:
            got.append(fn(*args)); print("descargado:", list(got[-1].columns))
        except Exception as e:
            print("no disponible:", str(e)[:90])
    return pd.concat(got, axis=1) if got else pd.DataFrame()


COUNTRY_HINTS = {"BRAZIL", "MEXICO", "CHILE", "COLOMBIA", "PERU", "TURKEY", "POLAND",
                 "INDONESIA", "MALAYSIA", "PAKISTAN", "PHILIPPINES", "RUSSIA", "INDIA",
                 "CHINA", "SOUTHAFRICA", "SOUTHKOREA", "HUNGARY", "BULGARIA"}


def load_vlab(path):
    """NYU V-Lab SRISK. Detecta automaticamente el formato:
      - GLOBAL:   fecha + una sola columna agregada (p.ej. 'World Financials -
                  Total SRISK') -> devuelve ('global', Serie trimestral 'SRISK').
      - POR PAIS: columna 'country' (largo) o varias columnas de paises (ancho)
                  -> devuelve ('panel', DataFrame largo country/q/SRISK).
    SRISK es un stock: se agrega al ultimo dato del trimestre."""
    v = pd.read_csv(path)
    cols = list(v.columns)
    low = {c.lower(): c for c in cols}
    dcol = next((low[k] for k in low if "date" in k or k in ("period", "month")), cols[0])
    v["q"] = to_q(v[dcol])
    ccol = next((low[k] for k in low if k in ("country", "economy", "name")), None)
    val_cols = [c for c in cols if c != dcol]

    if ccol:  # largo explicito
        scol = next((low[k] for k in low if "srisk" in k or k == "value"), val_cols[0])
        long = v[[ccol, "q", scol]].rename(columns={ccol: "country", scol: "SRISK"})
    elif len(val_cols) == 1:  # una sola serie
        col = val_cols[0]
        if norm_country(col) in COUNTRY_HINTS:  # es un pais
            long = v[["q", col]].rename(columns={col: "SRISK"}).assign(country=col)
        else:  # agregado GLOBAL (World / Total)
            s = (pd.to_numeric(v[col], errors="coerce").groupby(v["q"]).last().rename("SRISK_world"))
            return ("global", s)
    else:  # ancho: columnas = paises
        keep = [c for c in val_cols if norm_country(c) in COUNTRY_HINTS] or val_cols
        long = v.melt(id_vars="q", value_vars=keep, var_name="country", value_name="SRISK")

    long["country"] = long["country"].map(norm_country)
    long["SRISK"] = pd.to_numeric(long["SRISK"], errors="coerce")
    long = (long.dropna(subset=["SRISK"]).sort_values("q")
            .groupby(["country", "q"], as_index=False)["SRISK"].last())
    return ("panel", long)


# ---------------- COMPARACIÓN ----------------
def correlate(gar, pub_global, vlab_long=None):
    rows = []
    metrics = list(pub_global.columns)
    for c, g in gar.groupby("country"):
        s = g.set_index("q")["GaR"].sort_index()
        # métricas globales (misma serie para todos los países)
        for m in metrics:
            j = pd.concat([s, pub_global[m]], axis=1, join="inner").dropna()
            if len(j) < 8:
                continue
            j.columns = ["GaR", m]
            lvl = j["GaR"].corr(j[m]); chg = j["GaR"].diff().corr(j[m].diff())
            exp = EXPECTED_SIGN.get(m, -1)
            rows.append(dict(country=c, metrica=m, n=len(j),
                             corr_nivel=round(lvl, 3), corr_cambio=round(chg, 3),
                             signo_esperado=exp,
                             flag="ok" if np.sign(lvl) == np.sign(exp) else "REVISAR"))
        # SRISK: serie específica del país
        if vlab_long is not None:
            sub = vlab_long[vlab_long["country"] == c].set_index("q")["SRISK"]
            j = pd.concat([s, sub], axis=1, join="inner").dropna()
            if len(j) >= 8:
                j.columns = ["GaR", "SRISK"]
                lvl = j["GaR"].corr(j["SRISK"]); chg = j["GaR"].diff().corr(j["SRISK"].diff())
                rows.append(dict(country=c, metrica="SRISK", n=len(j),
                                 corr_nivel=round(lvl, 3), corr_cambio=round(chg, 3),
                                 signo_esperado=-1,
                                 flag="ok" if lvl < 0 else "REVISAR"))
    res = pd.DataFrame(rows)
    # POOL within (demean por país) para cada métrica global
    pool = []
    for m in metrics:
        big = gar.merge(pub_global[m].rename("M").reset_index(), on="q").dropna(subset=["GaR", "M"])
        if len(big) < 20:
            continue
        gw = big["GaR"] - big.groupby("country")["GaR"].transform("mean")
        mw = big["M"] - big.groupby("country")["M"].transform("mean")
        r = gw.corr(mw)
        pool.append(dict(country="POOL(within)", metrica=m, n=len(big),
                         corr_nivel=round(r, 3), corr_cambio=np.nan,
                         signo_esperado=EXPECTED_SIGN.get(m, -1),
                         flag="ok" if r < 0 else "REVISAR"))
    if vlab_long is not None and not res[res.metrica == "SRISK"].empty:
        big = gar.merge(vlab_long, on=["country", "q"]).dropna(subset=["GaR", "SRISK"])
        if len(big) >= 20:
            gw = big["GaR"] - big.groupby("country")["GaR"].transform("mean")
            mw = big["SRISK"] - big.groupby("country")["SRISK"].transform("mean")
            r = gw.corr(mw)
            pool.append(dict(country="POOL(within)", metrica="SRISK", n=len(big),
                             corr_nivel=round(r, 3), corr_cambio=np.nan,
                             signo_esperado=-1, flag="ok" if r < 0 else "REVISAR"))
    return pd.concat([res, pd.DataFrame(pool)], ignore_index=True)


def plot_overlay(gar, pub_global, outfile, countries=None):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if pub_global.empty:
        return
    m = pub_global.notna().sum().idxmax()
    cs = countries or sorted(gar["country"].unique())[:6]
    n = len(cs); fig, axes = plt.subplots((n + 1) // 2, 2, figsize=(13, 2.4 * ((n + 1) // 2)))
    axes = np.atleast_1d(axes).ravel()
    for ax, c in zip(axes, cs):
        s = gar[gar["country"] == c].set_index("q")["GaR"].sort_index()
        j = pd.concat([s, pub_global[m]], axis=1, join="inner").dropna()
        if j.empty:
            ax.set_visible(False); continue
        t = j.index.to_timestamp()
        ax.plot(t, zscore(j["GaR"]), color="#1F3864", lw=1.8, label="GaR (z)")
        ax.plot(t, zscore(j[m]), color="#C00000", lw=1.4, alpha=0.85, label=f"{m} (z)")
        ax.axhline(0, color="0.8", lw=0.6); ax.set_title(c, fontsize=10)
    for ax in axes[len(cs):]:
        ax.set_visible(False)
    axes[0].legend(fontsize=8, loc="upper right")
    fig.suptitle(f"GaR vs {m} (estandarizados) — co-movimiento esperado inverso", y=1.0)
    fig.tight_layout(); fig.savefig(outfile, dpi=160, bbox_inches="tight"); plt.close(fig)
    print("ok:", outfile)


def plot_corr(res, outfile):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = res[~res["country"].str.startswith("POOL")]
    metrics = list(d["metrica"].unique())
    piv = d.pivot_table(index="country", columns="metrica", values="corr_nivel")
    fig, ax = plt.subplots(figsize=(8.5, 6))
    y = np.arange(len(piv)); w = 0.8 / max(1, len(metrics))
    colors = {"US_HY_spread": "#C00000", "VIX": "#1F3864", "OFR_FSI": "#2E7D32",
              "OFR_FSI_EM": "#7CB342", "EM_OAS": "#8E44AD", "SRISK": "#E67E22"}
    for i, m in enumerate(metrics):
        ax.barh(y + i * w, piv[m].reindex(piv.index).values, height=w, label=m,
                color=colors.get(m))
    ax.axvline(0, color="0.4", lw=0.8)
    ax.set_yticks(y + w * (len(metrics) - 1) / 2); ax.set_yticklabels(piv.index, fontsize=8)
    ax.set_xlabel("Correlación de nivel con el GaR (esperada < 0)")
    ax.set_title("GaR vs métricas públicas de riesgo — correlación por país")
    ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(outfile, dpi=160, bbox_inches="tight"); plt.close(fig)
    print("ok:", outfile)


# ---------------- SELF-TEST (fixtures con el esquema real) ----------------
def selftest(out):
    rng = np.random.default_rng(1)
    qs = pd.period_range("2005Q1", "2024Q4", freq="Q")
    countries = ["BRAZIL", "MEXICO", "TURKEY", "POLAND", "INDONESIA", "SOUTHAFRICA"]
    # GaR sintético que cae cuando sube el estrés global
    stress = pd.Series(np.cumsum(rng.normal(0, 1, len(qs))) * 0.2, index=qs)
    gar_rows = []
    for c in countries:
        g = -stress + rng.normal(0, 0.3, len(qs))          # corr negativa con estrés
        for q, val in zip(qs, g):
            gar_rows.append(dict(country=c, quarter=str(q), GaR=val))
    pd.DataFrame(gar_rows).to_csv(os.path.join(out, "_st_gar.csv"), index=False)
    # OFR fixture con columnas REALES
    days = pd.date_range("2005-01-01", "2024-12-31", freq="B")
    ofr = pd.DataFrame({"Date": days})
    base = stress.reindex(to_q(pd.Series(days))).values
    ofr["OFR FSI"] = base + rng.normal(0, 0.1, len(days))
    ofr["Credit"] = 0; ofr["Emerging markets"] = base * 0.4 + rng.normal(0, 0.1, len(days))
    ofr.to_csv(os.path.join(out, "_st_ofr.csv"), index=False)
    # V-Lab SRISK fixture (formato largo)
    vl = []
    for c in countries:
        s = (stress.reindex(qs).values * 50 + 100 + rng.normal(0, 5, len(qs)))
        for q, val in zip(qs, s):
            vl.append(dict(country=c.title(), date=q.to_timestamp(how="end").date(), SRISK=val))
    pd.DataFrame(vl).to_csv(os.path.join(out, "_st_vlab.csv"), index=False)

    gar = load_gar_from(os.path.join(out, "_st_gar.csv"))
    pub = parse_ofr(os.path.join(out, "_st_ofr.csv"))
    kind, vlab = load_vlab(os.path.join(out, "_st_vlab.csv"))
    res = correlate(gar, pub, vlab if kind == "panel" else None)
    print(res.to_string(index=False))
    assert (res[res.metrica == "OFR_FSI"]["flag"] == "ok").all(), "OFR signo"
    assert (res[res.metrica == "SRISK"]["flag"] == "ok").all(), "SRISK signo"
    print("\nSELFTEST OK: parsers OFR (total+EM) y V-Lab SRISK correctos.")


def load_gar_from(path):
    df = pd.read_csv(path)
    df["country"] = df["country"].map(norm_country)
    df["q"] = pd.PeriodIndex(df["quarter"].astype(str).str.upper(), freq="Q")
    df["GaR"] = pd.to_numeric(df["GaR"], errors="coerce")
    return df[["country", "q", "GaR"]].dropna()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default=".")
    ap.add_argument("--download", action="store_true", help="baja OFR/FRED (requiere red)")
    ap.add_argument("--vlab", help="CSV de NYU V-Lab SRISK por país")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    if args.selftest:
        selftest(args.out); return

    gar = load_gar(args.panel)
    pub = load_local_public(args.panel)
    if args.download:
        pub = pd.concat([pub, try_download()], axis=1)
    vlab_long = None
    if args.vlab:
        kind, data = load_vlab(args.vlab)
        if kind == "global":                       # SRISK agregado mundial -> métrica global
            pub = pd.concat([pub, data.to_frame()], axis=1)
            EXPECTED_SIGN["SRISK_world"] = -1
            print("V-Lab: SRISK GLOBAL (World Financials) como métrica global.")
        else:                                       # SRISK por país
            vlab_long = data
            print("V-Lab: SRISK por país,", data["country"].nunique(), "economías.")
    pub = pub.reindex(sorted(pub.index)).dropna(how="all")
    print("Globales:", list(pub.columns), "| países GaR:", gar["country"].nunique())

    res = correlate(gar, pub, vlab_long)
    outcsv = os.path.join(args.out, "comparacion_gar_publicas.csv")
    res.to_csv(outcsv, index=False)
    print(res.to_string(index=False)); print("->", outcsv)

    reps = [c for c in ["BRAZIL", "MEXICO", "TURKEY", "SOUTHAFRICA", "INDONESIA", "POLAND"]
            if c in gar["country"].unique()] or None
    plot_overlay(gar, pub, os.path.join(args.out, "fig_gar_vs_publicas_overlay.png"), reps)
    plot_corr(res, os.path.join(args.out, "fig_gar_vs_publicas_corr.png"))


if __name__ == "__main__":
    main()
