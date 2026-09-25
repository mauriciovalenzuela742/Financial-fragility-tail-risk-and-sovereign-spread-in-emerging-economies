# -*- coding: utf-8 -*-
"""
_fci_sin_ryr.py -- EXPLORATORIO, no vigente. Variante mas agresiva que
build_fci_no_cdiff.py: en vez de solo quitar CDIFF (dejando VRyr), elimina el
bloque tasa/Ryr COMPLETO (VRyr y CDIFF), reduciendo el FCI a una forma
cuadratica 2x2 sobre [iSTX, iEER] solamente. Esta es la unica variante que
sirve para Argentina, que no tiene archivo Ryr en absoluto (fci_engine.compute_fci
igual lo exige internamente incluso con drop_cdiff=True).

Uso:
  1) Validacion: aplicar a un pais que SI tiene Ryr (ej. BRASIL) y comparar
     contra su FCI oficial -- extiende la verificacion ya hecha para
     "quitar solo CDIFF" (build_fci_no_cdiff.py) a "quitar todo el bloque Ryr".
  2) Calculo para ARGENTINA (unico uso real: no tiene alternativa con Ryr).

No modifica fci_engine.py ni ningun CSV canonico. Salida a stdout + CSV en el
directorio del script (prefijo EXPLORATORIO).
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fci_engine as fe  # noqa: E402

IND = os.path.join(HERE, "individuals")


def compute_fci_no_ryr(country_dir, country, initial="1990-01-01",
                        final="2026-05-31", std_method="method_b_max",
                        lag_tilde=fe.LAG_TILDE):
    """Igual que fci_engine.compute_fci pero sin el bloque tasa/Ryr: no lee
    Ryr*.csv ni pais de referencia (Rbs/CPIbs), y agrega FCI = I'CI con
    I=[iSTX, iEER], C = [[1, cSE],[cSE, 1]] (2x2 en vez de 3x3).

    lag_tilde: ventana (dias habiles) de la desviacion estandar rolling de
    VSTX. Default = LAG_TILDE de fci_engine (~10 anios, parametro CEMLA usado
    para los 18 paises del pool). Se puede acortar explicitamente para paises
    cuyo CPI no cubre 10 anios (ej. ARGENTINA, CPI oficial desde dic-2016) --
    es una desviacion documentada del parametro canonico, no aplicable al
    pool sin volver a calibrar todos los paises."""
    def find(folder, prefix):
        f = glob.glob(os.path.join(folder, f"{prefix}*"))
        if not f:
            raise FileNotFoundError(f"Falta {prefix}* en {folder}")
        return f[0]

    grid = pd.DataFrame({"DATES": fe.business_days(initial, final)})
    STX = fe._read_daily(find(country_dir, "STX"), "STX")
    CPI = fe._read_daily(find(country_dir, "CPI"), "CPI")

    dd = grid.copy()
    for s, nm in [(STX, "STX"), (CPI, "CPI")]:
        dd = fe._join(dd, s, nm)
    dd = dd.sort_values("DATES", ascending=False).reset_index(drop=True)

    dd = fe.get_STX(dd, lagTilde=lag_tilde)
    ym = dd["DATES"].dt.year * 100 + dd["DATES"].dt.month
    eom = np.zeros(len(dd), bool); eom[0] = True
    eom[1:] = ym.to_numpy()[:-1] != ym.to_numpy()[1:]
    md_daily = dd.loc[eom, ["DATES", "VSTX", "CMAX"]].copy()
    md_daily["YM"] = md_daily["DATES"].dt.year * 100 + md_daily["DATES"].dt.month

    rEER = pd.read_csv(find(country_dir, "rEER"))
    rEER.columns = ["YM", "rEER"]
    rEER["DATES"] = pd.to_datetime(rEER["YM"].astype(int).astype(str),
                                    format="%Y%m") + pd.offsets.MonthEnd(0)
    mgrid = pd.DataFrame({"DATES": pd.date_range(initial, final, freq="ME")})
    md = mgrid.merge(rEER[["DATES", "rEER"]], on="DATES", how="left")
    md = md.sort_values("DATES", ascending=False).reset_index(drop=True)
    md["rEER"] = fe._interp_na(md["rEER"])
    md.loc[md["DATES"] < rEER["DATES"].min(), "rEER"] = np.nan
    md = fe.get_rEER(md)
    md["YM"] = md["DATES"].dt.year * 100 + md["DATES"].dt.month

    idx = md_daily.merge(md[["YM", "VEER", "CUMUL"]], on="YM", how="left")
    idx = idx.dropna(subset=["VSTX", "CMAX", "VEER", "CUMUL"])
    idx = idx.sort_values("DATES").reset_index(drop=True)  # ASCENDENTE

    std = fe.method_b_max if std_method == "method_b_max" else fe.method_a_cdf
    for col in ["VSTX", "CMAX", "VEER", "CUMUL"]:
        idx[col] = std(idx[col].to_numpy())

    idx["iSTX"] = (idx["VSTX"] + idx["CMAX"]) / 2
    idx["iEER"] = (idx["VEER"] + idx["CUMUL"]) / 2

    cSE = fe.corr_EWMA(idx["iSTX"], idx["iEER"])

    n = len(idx)
    fci = np.empty(n)
    iSTX = idx["iSTX"].to_numpy(); iEER = idx["iEER"].to_numpy()
    for k in range(n):
        C = np.array([[1, cSE[k]], [cSE[k], 1]])
        I = np.array([iSTX[k], iEER[k]])
        fci[k] = I @ C @ I
    idx["FCI"] = fci
    idx["country"] = country
    return idx[["DATES", "country", "iSTX", "iEER", "FCI"]]


def quarterly_from_monthly(fci_m):
    f = fci_m.copy()
    f["m"] = f["DATES"].dt.month
    f = f[f["m"].isin([3, 6, 9, 12])].copy()
    f["Date"] = pd.to_datetime(dict(year=f["DATES"].dt.year, month=f["m"], day=1))
    return f.set_index("Date")["FCI"]


def validate_on_brazil():
    print("=== Validacion: BRASIL, quitando el bloque Ryr completo ===")
    cdir = os.path.join(IND, "BRAZIL")
    official = pd.read_csv(os.path.join(cdir, "FCI_BRAZIL.csv"))
    official["DATES"] = pd.to_datetime(official["DATES"], dayfirst=True)

    noryr = compute_fci_no_ryr(cdir, "BRAZIL")
    j = official.merge(noryr[["DATES", "FCI"]], on="DATES", suffixes=("_oficial", "_noRyr"))
    j = j.dropna()
    r = j["FCI_oficial"].corr(j["FCI_noRyr"])
    top20 = j.loc[j["FCI_oficial"] > j["FCI_oficial"].quantile(0.80)]
    r_top = top20["FCI_oficial"].corr(top20["FCI_noRyr"])
    print(f"n={len(j)}  corr(FCI oficial, FCI sin-Ryr) = {r:.3f}  (cola 20% sup: {r_top:.3f})")
    print(f"media oficial={j['FCI_oficial'].mean():.4f}  media sin-Ryr={j['FCI_noRyr'].mean():.4f}")
    return r, r_top


def build_argentina():
    print("\n=== ARGENTINA: FCI sin bloque Ryr, ventana VSTX acortada (CPI oficial desde dic-2016) ===")
    cdir = os.path.join(IND, "ARGENTINA")
    cpi = pd.read_csv(os.path.join(cdir, "CPI_ARGENTINA.csv"))
    cpi["DATES"] = pd.to_datetime(cpi["DATES"], dayfirst=True)

    initial, final = "1990-01-01", "2026-05-31"
    grid = pd.DataFrame({"DATES": fe.business_days(initial, final)})
    cpi_daily = fe._read_daily(os.path.join(cdir, "CPI_ARGENTINA.csv"), "CPI")
    n_valid = fe._join(grid.copy(), cpi_daily, "CPI")["CPI"].notna().sum()
    # margen de seguridad: unos dias menos que el maximo estrictamente disponible,
    # para que el _roll_fwd principal (no solo el relleno de borde) tenga recorrido.
    lag_tilde_arg = int(n_valid) - 15
    print(f"CPI_ARGENTINA.csv: {cpi['DATES'].min().date()} .. {cpi['DATES'].max().date()} "
          f"({len(cpi)} obs mensuales) -> {n_valid} dias habiles con CPI valido en la grilla.")
    print(f"LAG_TILDE estandar (CEMLA, 18 paises) = {fe.LAG_TILDE} dias (~10.0 anios). "
          f"Insuficiente para Argentina (faltan {fe.LAG_TILDE - n_valid} dias).")
    print(f"LAG_TILDE usado para ARGENTINA (desviacion documentada) = {lag_tilde_arg} dias "
          f"(~{lag_tilde_arg/260:.1f} anios) -- unico ajuste metodologico, no aplicado a los "
          f"otros 18 paises del pool.")

    fci = compute_fci_no_ryr(cdir, "ARGENTINA", initial=initial, final=final,
                              lag_tilde=lag_tilde_arg)
    print(f"FCI_ARGENTINA (sin Ryr, ventana acortada): {fci['DATES'].min().date()} .. "
          f"{fci['DATES'].max().date()} ({len(fci)} obs mensuales)")
    out = os.path.join(HERE, "_FCI_ARGENTINA_sinRyr_EXPLORATORIO.csv")
    fci.to_csv(out, index=False)
    print(f"Guardado: {out}")
    return fci


if __name__ == "__main__":
    validate_on_brazil()
    build_argentina()
