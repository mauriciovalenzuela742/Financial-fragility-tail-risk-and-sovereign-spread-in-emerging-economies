"""
extract_colombia.py — Inputs JLoss para Colombia desde la Superintendencia Financiera (SFC).

Fuente: portal de Envíos NIIF de la SFC (XBRL Individual/Separado), descargado con
download_sfc_niif.py y ensamblado a long-format con build_colombia_long.py -> colombia_long.csv.

Criterio del profesor (bonos vs resto): LP = deuda emitida (bonos + notas/debentures + subordinada
+ títulos en circulación); CP = resto (por residuo).

Limpieza de períodos (clean_colombia_long): el XBRL trae muchos contextos; aquí se deja SOLO el
cierre de trimestre real y se descartan:
  - balances de apertura (01-01, 04-01, 07-01, 10-01) del Estado de Cambios en el Patrimonio,
  - meses que no son de reporte (feb, nov, etc.),
  - fechas de último día hábil (06-28, 09-29, 12-30...) -> se mapean al cierre del trimestre,
  - periodos futuros.
Además, bancos sin emisión de deuda quedan con bonds=0 (no NaN), y se descartan filas sin
activos/patrimonio.

Uso:
    python extract_colombia.py --file colombia_long.csv --start 2000 --end 2026
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "colombia"

# 30 establecimientos bancarios vigilados por la SFC (los que descargaste). Sólo Bancolombia tiene
# precio fiable en yfinance (ADR CIB); el resto -> PD contable (book_pd). 'names' = subcadenas que
# identifican al banco en la etiqueta del long-format (coinciden con build_colombia_long).
BANKMAP = {
    "bancolombia":        {"ticker": "CIB", "names": ["BANCOLOMBIA", "BANCO DE COLOMBIA"]},
    "banco_de_bogota":    {"ticker": None,  "names": ["BANCO DE BOGOTA", "BANCO DE BOGOTÁ"]},
    "davivienda":         {"ticker": None,  "names": ["DAVIVIENDA"]},
    "bbva_colombia":      {"ticker": None,  "names": ["BILBAO VIZCAYA", "BBVA COLOMBIA"]},
    "banco_de_occidente": {"ticker": None,  "names": ["BANCO DE OCCIDENTE", "OCCIDENTE"]},
    "banco_popular":      {"ticker": None,  "names": ["BANCO POPULAR"]},
    "banco_caja_social":  {"ticker": None,  "names": ["CAJA SOCIAL"]},
    "banco_agrario":      {"ticker": None,  "names": ["BANCO AGRARIO", "BANAGRARIO"]},
    "av_villas":          {"ticker": None,  "names": ["AV VILLAS"]},
    "gnb_sudameris":      {"ticker": None,  "names": ["GNB SUDAMERIS", "SUDAMERIS"]},
    "citibank_colombia":  {"ticker": None,  "names": ["CITIBANK"]},
    "davibank":           {"ticker": None,  "names": ["DAVIBANK"]},
    "itau_colombia":      {"ticker": None,  "names": ["ITAU COLOMBIA", "ITAÚ COLOMBIA", "BANCO ITAU"]},
    "santander_colombia": {"ticker": None,  "names": ["SANTANDER"]},
    "pichincha":          {"ticker": None,  "names": ["BANCO PICHINCHA", "PICHINCHA"]},
    "falabella":          {"ticker": None,  "names": ["FALABELLA"]},
    "bancamia":           {"ticker": None,  "names": ["BANCAMIA"]},
    "bancien":            {"ticker": None,  "names": ["BANCIEN", "BAN100"]},
    "btg_pactual":        {"ticker": None,  "names": ["BTG PACTUAL"]},
    "contactar":          {"ticker": None,  "names": ["CONTACTAR"]},
    "coomeva":            {"ticker": None,  "names": ["COOMEVA"]},
    "coopcentral":        {"ticker": None,  "names": ["COOPCENTRAL"]},
    "finandina":          {"ticker": None,  "names": ["FINANDINA"]},
    "jp_morgan":          {"ticker": None,  "names": ["J.P. MORGAN", "JP MORGAN", "J P MORGAN"]},
    "lulo":               {"ticker": None,  "names": ["LULO"]},
    "mibanco":            {"ticker": None,  "names": ["MIBANCO"]},
    "mundo_mujer":        {"ticker": None,  "names": ["MUNDO MUJER"]},
    "serfinanza":         {"ticker": None,  "names": ["SERFINANZA"]},
    "banco_union":        {"ticker": None,  "names": ["BANCO UNION", "BANCO UNIÓN"]},
    "banco_w":            {"ticker": None,  "names": ["BANCO W"]},
}

# etiquetas que emite parse_sfc_xbrl.py -> campos v8 (substring, mayúsculas).
# La deuda se consolida ANTES (consolidate_colombia_debt) en una sola cuenta 'Bonos consolidado'
# para no doble-contar conceptos IFRS y extensiones SFC que se solapan.
ACCOUNT_MAP = {
    "bonds": ["BONOS CONSOLIDADO"],
    "tot_asset": ["TOTAL ACTIVOS"],
    "equity":    ["TOTAL PATRIMONIO"],
}

# Conceptos de deuda emitida del XBRL (etiquetas de parse_sfc_xbrl.py):
#  - IFRS, ADITIVOS (líneas distintas): se suman.
DEBT_IFRS = ["Bonos emitidos", "Notas y debentures emitidos", "Obligaciones subordinadas"]
#  - extensiones SFC, AGREGADOS que se solapan con lo anterior: solo respaldo si faltan los IFRS.
DEBT_FALLBACK = ["Titulos emitidos", "Bonos y titulos en circulacion"]


def clean_colombia_long(df):
    """Deja SOLO cierres de trimestre reales y deduplica por (banco, cuenta, trimestre)."""
    d = df.copy()
    d.columns = [str(c).strip().lower() for c in d.columns]
    d["_dt"] = pd.to_datetime(d["period"], errors="coerce")
    d = d.dropna(subset=["_dt"])
    # cierre de trimestre (incl. último día hábil): mes en {3,6,9,12} y día >= 20
    d = d[d["_dt"].dt.month.isin([3, 6, 9, 12]) & (d["_dt"].dt.day >= 20)]
    # descartar periodos futuros
    d = d[d["_dt"] <= pd.Timestamp.today().normalize()]
    if d.empty:
        return d[["bank", "account", "period", "value"]]
    # fecha canónica = fin de trimestre; una fila por (banco, cuenta, trimestre) la más cercana al cierre
    d["_qend"] = d["_dt"].dt.to_period("Q").dt.end_time.dt.normalize()
    d = d.sort_values("_dt").drop_duplicates(subset=["bank", "account", "_qend"], keep="last")
    return pd.DataFrame({
        "bank": d["bank"].values,
        "account": d["account"].values,
        "period": d["_qend"].dt.strftime("%Y-%m-%d").values,
        "value": d["value"].values,
    })


def consolidate_colombia_debt(d):
    """Colapsa los 5 conceptos de deuda en UNA cuenta 'Bonos consolidado' por (banco, periodo),
    evitando doble conteo y valores misscaled:
      bonds = sum(IFRS aditivos)  si hay alguno > 0
            = primer FALLBACK SFC disponible  en caso contrario
      Cualquier candidato de deuda > pasivos totales se descarta (error de escala en el XBRL)."""
    w = d.pivot_table(index=["bank", "period"], columns="account", values="value", aggfunc="first")
    for c in DEBT_IFRS + DEBT_FALLBACK + ["Total activos", "Total patrimonio"]:
        if c not in w.columns:
            w[c] = np.nan
    tot, eq = w["Total activos"], w["Total patrimonio"]
    tl = tot - eq
    # descartar candidatos de deuda claramente misscaled (> pasivos totales)
    for c in DEBT_IFRS + DEBT_FALLBACK:
        w.loc[w[c] > tl, c] = np.nan
    ifrs = w[DEBT_IFRS].sum(axis=1, min_count=1)
    fb = w[DEBT_FALLBACK[0]].fillna(w[DEBT_FALLBACK[1]])
    bonds = ifrs.where(ifrs.fillna(0) > 0, fb).fillna(0.0)
    base = pd.DataFrame({"bank": [i[0] for i in w.index], "period": [i[1] for i in w.index],
                         "Bonos consolidado": bonds.values,
                         "Total activos": tot.values, "Total patrimonio": eq.values})
    long = base.melt(id_vars=["bank", "period"], var_name="account", value_name="value")
    return long.dropna(subset=["value"])


def fetch_balances(export_file, start_year, end_year, col_code=None):
    df = pd.read_csv(export_file) if str(export_file).endswith(".csv") else pd.read_excel(export_file)
    df = clean_colombia_long(df)
    df = consolidate_colombia_debt(df)
    rows = jc.transform_long_generic(df, BANKMAP, ACCOUNT_MAP, COUNTRY,
                                     col_bank="bank", col_account="account",
                                     col_period="period", col_value="value", col_code=col_code)
    bal = jc.finalize_balance(rows)
    bal["bonds"] = bal["bonds"].fillna(0.0)
    bal = bal.dropna(subset=["tot_asset", "equity_book"])
    bal = bal[(bal["tot_asset"] > 0) & (bal["equity_book"] > 0)]
    bal = jc.derive_st_lt_bonds_vs_rest(bal)
    bal = bal[(bal["date"].dt.year >= start_year) & (bal["date"].dt.year <= end_year)]
    return bal.sort_values(["bankname", "date"]).reset_index(drop=True)


def flag_yoy_duplicates(bal):
    """Marca (banco, trimestre) cuyo tot_asset es idéntico al de exactamente 1 año antes
    (posible comparativo mal fechado / cierre no disponible en el XBRL)."""
    b = bal.copy()
    b["q"] = b["date"].dt.to_period("Q")
    cur = b[["bankname", "q", "date", "tot_asset"]]
    prev = b[["bankname", "q", "tot_asset"]].copy()
    prev["q"] = prev["q"] + 4  # +1 año
    prev = prev.rename(columns={"tot_asset": "ta_prev"})
    m = cur.merge(prev, on=["bankname", "q"], how="inner")
    return m.loc[m["tot_asset"] == m["ta_prev"], ["bankname", "date", "tot_asset"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="long-format colombia_long.csv (build_colombia_long.py)")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    a = ap.parse_args()
    bal = fetch_balances(a.file, a.start, a.end)
    bal.to_csv(f"balance_{COUNTRY}.csv", index=False)
    jc.coverage_report(bal).to_csv(f"coverage_{COUNTRY}.csv", index=False)
    rec = jc.reconcile_bonds_vs_rest(bal)
    neg = int((bal["st_borrow"] < 0).sum())
    dup = flag_yoy_duplicates(bal)
    print(f"balances={len(bal)} | bancos={bal['bankname'].nunique()} | "
          f"trimestres={bal['date'].dt.to_period('Q').nunique()}")
    print(f"reconcile: {rec} | st_borrow<0: {neg}")
    if len(dup):
        print(f"AVISO {len(dup)} (banco,trim) con tot_asset idéntico al de hace 1 año (revisar XBRL):")
        print(dup.to_string(index=False))
    try:
        mkt = jc.fetch_mktcap_yf(BANKMAP, COUNTRY, a.start, a.end)
        mkt.to_csv(f"mktcap_{COUNTRY}.csv", index=False)
        print(f"mktcap filas={len(mkt)}")
    except Exception as e:
        print(f"mktcap omitido ({e})")


if __name__ == "__main__":
    main()