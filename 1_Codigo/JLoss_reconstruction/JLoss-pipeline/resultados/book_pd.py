"""
book_pd.py — PD contable (z-score) para bancos NO listados, y fusion con la PD de mercado.

Para no listados no hay E de mercado ni sigma de equity, asi que la PD de Merton/KMV no es
estimable. Se usa la distancia a la insolvencia contable (bank z-score), el analogo de la
distancia a default basado en estados financieros:

    CAR_t   = equity_book_t / tot_asset_t                 (colchon de capital)
    ROA_t   = net_income_t  / tot_asset_t                 (rentabilidad sobre activos)
    z_t     = (CAR_t + media_movil(ROA)) / sigma_movil(ROA)
    EDF_book= Phi(-z_t)

sigma_movil(ROA) es la VOLATILIDAD DE ACTIVOS IMPUTADA (contable). Requiere serie temporal
por banco; usar ventana movil (default 8 trimestres, min 6 obs).

ADVERTENCIA DE CONSISTENCIA (para el comite): mezclar PD de mercado (listados) y PD contable
(no listados) en el mismo portafolio introduce heterogeneidad de metodo. Reportar el flag
'pd_source' por banco-trimestre y correr un chequeo de robustez (p.ej. JLoss sobre solo-listados
vs panel completo).
"""
import numpy as np
import pandas as pd
from scipy.stats import norm


def ytd_to_quarterly_flow(df, value_col="net_income", by=("countryname", "bankname"),
                          date_col="date"):
    """Convierte una serie acumulada YTD (resetea cada anio) a flujo trimestral.
    Muchos reguladores publican net_income acumulado en el anio; diferenciar dentro del anio."""
    df = df.sort_values(list(by) + [date_col]).copy()
    df["_year"] = pd.to_datetime(df[date_col]).dt.year
    df[value_col + "_flow"] = (df.groupby(list(by) + ["_year"])[value_col]
                               .transform(lambda s: s.diff().fillna(s)))
    return df.drop(columns="_year")


def compute_book_pd(balance_df, window=8, min_obs=6, annualize=4, sd_floor=1e-4,
                    net_income_is_ytd=False):
    """Calcula EDF_book por banco-trimestre a partir del panel de balance.

    balance_df debe tener: countryname, bankname, date, equity_book, tot_asset, net_income.
    Devuelve columnas extra: CAR, ROA, mu_ROA, sd_ROA, zscore, PD (=EDF_book), pd_source.
    """
    df = balance_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["countryname", "bankname", "date"]).reset_index(drop=True)

    if net_income_is_ytd:
        df = ytd_to_quarterly_flow(df, "net_income")
        ni = df["net_income_flow"]
    else:
        ni = df["net_income"]

    df["ROA"] = (ni * annualize) / df["tot_asset"]          # ROA anualizado
    df["CAR"] = df["equity_book"] / df["tot_asset"]

    g = df.groupby(["countryname", "bankname"])["ROA"]
    df["mu_ROA"] = g.transform(lambda s: s.rolling(window, min_periods=min_obs).mean())
    df["sd_ROA"] = g.transform(lambda s: s.rolling(window, min_periods=min_obs).std())

    sd = df["sd_ROA"].clip(lower=sd_floor)
    df["zscore"] = (df["CAR"] + df["mu_ROA"]) / sd
    df["PD"] = norm.cdf(-df["zscore"])
    df["pd_source"] = "book_zscore"
    # invalidar donde falta historia suficiente o inputs
    bad = df[["CAR", "mu_ROA", "sd_ROA"]].isna().any(axis=1) | (df["tot_asset"] <= 0)
    df.loc[bad, ["PD", "zscore"]] = np.nan
    return df


def pd_distribution_free(zscore):
    """Cota de Cantelli/Chebyshev: PD <= 1/(2 z^2) para z>0. Alternativa sin supuesto normal,
    evita el underflow de Phi(-z) con z grandes. Devuelve la cota como PD."""
    z = np.asarray(zscore, float)
    out = np.where(z > 0, 1.0 / (2.0 * z**2), 0.5)
    return np.clip(out, 0.0, 1.0)


def calibrate_book_to_market(listed_z, listed_edf_market):
    """Puente de escala: ajusta Phi^{-1}(EDF_market) = a + b*z sobre los bancos LISTADOS
    (que tienen z contable Y EDF de mercado). Devuelve (a, b) para mapear z de no listados:
        EDF_book_cal = Phi(a + b*z).
    Esto pone el riesgo contable en la MISMA escala que el riesgo de mercado y elimina el
    underflow del z-score crudo. Se espera b<0 (mayor z -> menor PD)."""
    z = np.asarray(listed_z, float)
    e = np.asarray(listed_edf_market, float)
    m = np.isfinite(z) & np.isfinite(e) & (e > 1e-12) & (e < 1 - 1e-12)
    if m.sum() < 10:
        return None                       # muestra insuficiente para calibrar
    y = norm.ppf(e[m])                    # threshold de default implícito en EDF de mercado
    b, a = np.polyfit(z[m], y, 1)         # y = b*z + a
    return float(a), float(b)


def apply_book_calibration(book_df, ab):
    """Aplica EDF_book_cal = Phi(a + b*z) y lo deja en columna 'PD_cal'."""
    df = book_df.copy()
    if ab is None:
        df["PD_cal"] = pd_distribution_free(df["zscore"])   # fallback sin calibración
        df["pd_source"] = "book_chebyshev"
    else:
        a, b = ab
        df["PD_cal"] = norm.cdf(a + b * df["zscore"])
        df["pd_source"] = "book_zscore_cal"
    df.loc[~np.isfinite(df["zscore"]), "PD_cal"] = np.nan
    return df


def merge_pds(market_pd_df, book_pd_df, keys=("countryname", "bankname", "date"),
              book_pd_col="PD"):
    """Une PD de mercado (listados) y PD contable (no listados).
    Prioriza la PD de mercado cuando existe; rellena con la contable.
    Ambos df deben tener las columnas keys + 'PD' (+ 'pd_source' opcional)."""
    keys = list(keys)
    m = market_pd_df[keys + ["PD"]].dropna(subset=["PD"]).copy()
    m["pd_source"] = "market_merton"
    b = book_pd_df[keys + [book_pd_col]].dropna(subset=[book_pd_col]).copy()
    b = b.rename(columns={book_pd_col: "PD"})
    b["pd_source"] = "book"
    # left = mercado; agregar contable solo para (banco,fecha) sin PD de mercado
    merged = m.set_index(keys)
    add = b.set_index(keys)
    add = add[~add.index.isin(merged.index)]
    out = pd.concat([merged, add]).reset_index()
    return out.sort_values(keys).reset_index(drop=True)
