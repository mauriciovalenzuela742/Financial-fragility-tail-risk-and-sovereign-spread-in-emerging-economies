# -*- coding: utf-8 -*-
"""
p7_iv_dolar_bis.py -- shock global mas fuerte para el IV shift-share: el tipo de
cambio efectivo nominal AMPLIO del dolar (BIS, canasta de 64 economias), el shock
estandar de la literatura del "dollar cycle" (Bruno-Shin 2015; Avdjiev et al. 2019)
para la fragilidad bancaria EM via descalce cambiario -- una apreciacion amplia del
dolar encarece el fondeo/deuda en dolares de los bancos EM y eleva JLoss.

Fuente: BIS Statistics API, dataflow WS_EER (Effective Exchange Rate Indices),
serie "United States - Nominal - Broad (64 economias)", mensual. Se agrega a
trimestral (promedio) y se expresa en log.

Salida -> usd_neer_bbg.csv (quarter, USD_NEER, USD_NEER_log)
        -> se mezcla en Panel_bloomberg.csv como columna adicional para causal_core.
"""
import os, io, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
URL = ("https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/M.N.B.US"
       "?format=csv&startPeriod=2003-01")


def fetch_bis_usd_neer(tries=4):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=30).read()
            df = pd.read_csv(io.BytesIO(raw))
            return df[["TIME_PERIOD", "OBS_VALUE"]].rename(
                columns={"TIME_PERIOD": "month", "OBS_VALUE": "USD_NEER"})
        except Exception as e:
            last = e
            print(f"  [BIS WS_EER] intento {k + 1}/{tries} fallo: {str(e)[:80]}")
    raise RuntimeError(f"No se pudo obtener BIS WS_EER: {last}")


def main():
    m = fetch_bis_usd_neer()
    m["month"] = pd.to_datetime(m["month"], format="%Y-%m")
    m["quarter"] = m["month"].dt.to_period("Q").astype(str)
    q = m.groupby("quarter", as_index=False)["USD_NEER"].mean()
    q["USD_NEER_log"] = np.log(q["USD_NEER"])
    q = q.sort_values("quarter")
    q.to_csv(os.path.join(HERE, "usd_neer_bbg.csv"), index=False)
    print(f"BIS USD NEER amplio: {q['quarter'].min()}..{q['quarter'].max()}, "
          f"{len(q)} trimestres")
    print(q.tail(3).to_string(index=False))

    # merge en Panel_bloomberg.csv (idempotente: reemplaza si ya existe)
    pcsv = os.path.join(HERE, "Panel_bloomberg.csv")
    p = pd.read_csv(pcsv)
    p = p.drop(columns=[c for c in ("USD_NEER", "USD_NEER_log") if c in p.columns])
    p = p.merge(q, on="quarter", how="left")
    p.to_csv(pcsv, index=False)
    print(f"\nMezclado en Panel_bloomberg.csv: {p['USD_NEER_log'].notna().sum()}/{len(p)} filas")


if __name__ == "__main__":
    main()
