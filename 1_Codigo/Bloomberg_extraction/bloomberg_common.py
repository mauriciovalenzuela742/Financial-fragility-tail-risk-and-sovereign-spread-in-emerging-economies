"""
bloomberg_common.py — utilidades compartidas para extraer, via Bloomberg Terminal (xbbg),
los insumos del panel JLoss (riesgo bancario) y GaR/FCI (riesgo soberano) para la tesis
"Financial fragility, tail risk and sovereign spread in emerging economies".

Contrato de salida (tomado de jloss_common.py del repo — ver reference/jloss_common.py):
  BALANCE_COLS = countryname, bankname, date, lt_borrow, st_borrow, tot_asset,
                 cash_and_st_investments, net_income, net_rev, prof_margin,
                 equity_book, bonds, total_liab
  MKTCAP_COLS  = countryname, bankname, date, mktcap
  Regla LP/CP (bonos vs resto, "criterio del profesor"):
    total_liab = tot_asset - equity_book
    lt_borrow  = bonds
    st_borrow  = total_liab - bonds
  (DP no se guarda en el CSV — se calcula aguas abajo en el motor JLoss.)

Formato GaR/FCI (tomado de reference/GaR_extraction_individuals/*.py):
  CPI_<PAIS>.csv, GDP_<PAIS>.csv, Ryr_<PAIS>.csv, STX_<PAIS>.csv: columnas DATES,<nombre>,
  fecha DD/MM/YYYY, orden descendente (mas reciente primero, igual que el resto del panel).
  rEER_<PAIS>.csv: fecha AAAAMM, mensual (no se cubre aqui — fuente es BIS/IFS, no Bloomberg).

EJECUTAR EN PYCHARM CON EL TERMINAL BLOOMBERG ABIERTO (BBComm activo). Este modulo NO corre
dentro del sandbox del agente — requiere xbbg + una sesion Bloomberg local real:
    pip install xbbg

Todo lo que este archivo produce son DataFrames/CSVs de series de mercado, balance contable
publico y variables macro agregadas (spreads soberanos, ratings, indices) — nada de datos
bancarios personales o de cuentas.
"""
from __future__ import annotations

import time
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Schema (copiado literal de jloss_common.py — "informacion de cabecera")
# ---------------------------------------------------------------------------
BALANCE_COLS = ["countryname", "bankname", "date", "lt_borrow", "st_borrow", "tot_asset",
                "cash_and_st_investments", "net_income", "net_rev", "prof_margin",
                "equity_book", "bonds", "total_liab"]
MKTCAP_COLS = ["countryname", "bankname", "date", "mktcap"]

# Nota (a) del runbook — escala de rating S&P, notch -> numero (21=AAA ... 1=SD/D)
RATING_SCALE = {
    "AAA": 21, "AA+": 20, "AA": 19, "AA-": 18, "A+": 17, "A": 16, "A-": 15,
    "BBB+": 14, "BBB": 13, "BBB-": 12, "BB+": 11, "BB": 10, "BB-": 9,
    "B+": 8, "B": 7, "B-": 6, "CCC+": 5, "CCC": 4, "CCC-": 3, "CC": 2, "C": 2,
    "SD": 1, "D": 1,
}


def rating_to_score(notch) -> float:
    """Notch de S&P -> escala 21-1 de RATING_SCALE, limpiando los sufijos que agrega
    Bloomberg: 'u' = unsolicited (Turquia devuelve 'BB-u'), 'pi' = public information,
    'NR'/'WD' = sin rating (Rusia devuelve 'NR' desde que S&P retiro la calificacion).
    Devuelve NaN en vez de romper cuando el notch no es calificable."""
    if notch is None:
        return np.nan
    s = str(notch).strip().upper().replace("*", "").strip()
    if s in ("", "NR", "WD", "WR", "NAN", "NONE"):
        return np.nan
    for suf in ("PI", "U"):
        if s.endswith(suf) and len(s) > len(suf):
            s = s[: -len(suf)]
            break
    val = RATING_SCALE.get(s)
    return float(val) if val is not None else np.nan


def derive_st_lt_bonds_vs_rest(df: pd.DataFrame, lt_weight: float = 0.5) -> pd.DataFrame:
    """Identica a jloss_common.derive_st_lt_bonds_vs_rest — criterio bonos-vs-resto.
    Requiere columnas 'bonds', 'tot_asset', 'equity_book'."""
    df = df.copy()
    df["total_liab"] = df["tot_asset"] - df["equity_book"]
    df["lt_borrow"] = df["bonds"]
    df["st_borrow"] = df["total_liab"] - df["bonds"]
    df["DP"] = df["st_borrow"] + lt_weight * df["lt_borrow"]
    return df


def finalize_balance(rows: list[dict]) -> pd.DataFrame:
    """Arma el DataFrame final en el orden/columnas exacto de BALANCE_COLS."""
    df = pd.DataFrame(rows)
    for c in BALANCE_COLS:
        if c not in df.columns:
            df[c] = np.nan
    df = df[BALANCE_COLS].copy()
    df["date"] = pd.to_datetime(df["date"])
    # Blindaje: cualquier partida que Bloomberg no reporte llega como object/None y
    # rompe derive_st_lt_bonds_vs_rest. Todo lo que no es etiqueta debe ser float.
    for c in BALANCE_COLS:
        if c not in ("countryname", "bankname", "date"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # Bloomberg devuelve ocasionalmente 0.0 en vez de vacio cuando falta el reporte del
    # trimestre (verificado 2026-08-27: UBL PA en 2025-02-27, tot_asset=0 con equity_book
    # de 275.289 y bonds de 3.002.946). Un banco con activos exactamente cero no existe, y
    # dejarlo pasar propaga total_liab y st_borrow negativos a la regla LP/CP. Se marca
    # como faltante. Ojo: bonds == 0 SI es legitimo (banco sin deuda LP emitida) y no se toca.
    cero = df["tot_asset"] == 0
    if int(cero.sum()):
        for _, r in df[cero].iterrows():
            print(f"  [finalize_balance] {r['bankname']} {pd.Timestamp(r['date']).date()}: "
                  f"tot_asset == 0 -> NaN (dato invalido de Bloomberg)")
        df.loc[cero, "tot_asset"] = np.nan
    return df.sort_values(["bankname", "date"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Wrappers Bloomberg (xbbg)
# ---------------------------------------------------------------------------
def _get_blp():
    try:
        from xbbg import blp
    except ImportError as e:
        raise ImportError(
            "xbbg no esta instalado en este entorno. Correr:  pip install xbbg\n"
            "y tener el Bloomberg Terminal abierto (BBComm activo) en esta misma maquina."
        ) from e
    return blp


# xbbg 1.0 rompio la API de 0.7: ya no devuelve un DataFrame pandas ancho (indice=fecha,
# columnas MultiIndex ticker/campo) sino un frame *largo* de narwhals sobre pyarrow
# (ticker, [date,] field, value) con los valores como string. Se le pide backend pandas +
# formato tipado, y el formato ancho se re-arma aca (_to_wide) para que el resto del
# pipeline siga viendo el contrato de siempre: una columna 'date' + una columna por campo.
_XBBG_CALL = {"backend": "pandas", "format": "long_typed", "validate_fields": False}
_VALUE_COLS = ["value_f64", "value_i64", "value_str", "value_bool", "value_date", "value_ts"]

# freq del pipeline -> (periodicitySelection, periodicityAdjustment) de la
# HistoricalDataRequest de blpapi (el viejo kwarg Per= de xbbg 0.7 ya no existe).
# ACTUAL para fundamentales trimestrales: usa las fechas de reporte reales y da mejor
# cobertura que CALENDAR (verificado 2026-08-27: BS_LT_BORROW de BDO Unibank pasa de
# 29 a 46 trimestres). 'SA' es el fallback para bancos que reportan semestralmente.
_PERIODICITY = {
    "D":  ("DAILY", "ACTUAL"),
    "W":  ("WEEKLY", "ACTUAL"),
    "M":  ("MONTHLY", "ACTUAL"),
    "Q":  ("QUARTERLY", "ACTUAL"),
    "CQ": ("QUARTERLY", "ACTUAL"),
    "SA": ("SEMI_ANNUALLY", "FISCAL"),
    "A":  ("YEARLY", "ACTUAL"),
    "Y":  ("YEARLY", "ACTUAL"),
    "CY": ("YEARLY", "ACTUAL"),
}


def _coalesce_value(df: pd.DataFrame) -> pd.Series:
    """Junta las columnas value_* del formato long_typed en una sola serie de valores."""
    out = pd.Series(np.nan, index=df.index, dtype=object)
    for c in _VALUE_COLS:
        if c in df.columns:
            out = out.where(out.notna(), df[c])
    return out


def _to_wide(df) -> pd.DataFrame:
    """Frame largo de xbbg 1.0 -> ancho. Con columna 'date' (bdh) la clave es la fecha;
    sin ella (bdp) la clave es el ticker. Las columnas convertibles a numero quedan
    numericas; las de texto (ej. rating S&P) se dejan como string."""
    if df is None:
        return pd.DataFrame()
    if hasattr(df, "to_pandas"):          # narwhals / polars / pyarrow
        df = df.to_pandas()
    if len(df) == 0 or "field" not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    if "value" not in df.columns:
        df["value"] = _coalesce_value(df)
    keys = ["date"] if "date" in df.columns else ["ticker"]
    wide = df.groupby(keys + ["field"])["value"].first().unstack("field").reset_index()
    wide.columns.name = None
    if "date" in wide.columns:
        wide["date"] = pd.to_datetime(wide["date"])
    for c in wide.columns:
        if c in ("date", "ticker"):
            continue
        conv = pd.to_numeric(wide[c], errors="coerce")
        # Una columna enteramente vacia tiene que quedar float NaN y no object: si se
        # queda en object, la aritmetica aguas abajo (total_liab = tot_asset - equity_book)
        # revienta con TypeError en vez de propagar NaN.
        if conv.notna().any() or not wide[c].notna().any():
            wide[c] = conv
    return wide


def verify_fields(sample_ticker: str, flds: list[str]) -> dict:
    """Equivalente a FLDS<GO> del terminal: confirma que un campo existe/devuelve algo
    para un ticker de prueba ANTES de tirar el historial completo de 15 anios.
    Usar sobre los campos marcados 'verificar' en el runbook (rating S&P, HY spread
    propietario JPM, bonos soberanos ilíquidos). Imprime advertencia, no aborta."""
    blp = _get_blp()
    out = {}
    try:
        res = _to_wide(blp.bdp(tickers=sample_ticker, flds=flds, **_XBBG_CALL))
    except Exception as e:
        print(f"  [verify_fields] ERROR consultando {sample_ticker} {flds}: {e}")
        return {f: False for f in flds}
    for f in flds:
        ok = (not res.empty) and (f in res.columns) and res[f].notna().any()
        out[f] = bool(ok)
        if not ok:
            print(f"  [verify_fields] AVISO: campo '{f}' vacio/no encontrado para {sample_ticker} "
                  f"— confirmar mnemonico exacto en FLDS<GO> antes de automatizar el pull.")
    return out


def bdh_pull(tickers, flds, start_date, end_date, freq="D", max_retries=3, pause=1.5):
    """Wrapper sobre xbbg.blp.bdh con reintentos. freq: 'D' diario, 'CQ' trimestral.
    Un ticker con error/vacio no debe tumbar el batch completo: se pide de a un ticker
    y se acumulan resultados parciales.
    Devuelve {ticker: DataFrame ancho con columna 'date' + una columna por campo}."""
    blp = _get_blp()
    if isinstance(tickers, str):
        tickers = [tickers]
    per, adj = _PERIODICITY.get(str(freq).upper(), ("DAILY", "ACTUAL"))
    frames = {}
    for tk in tickers:
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                df = _to_wide(blp.bdh(tickers=tk, flds=flds,
                                      start_date=start_date, end_date=end_date,
                                      periodicitySelection=per,
                                      periodicityAdjustment=adj,
                                      **_XBBG_CALL))
                if not df.empty:
                    frames[tk] = df
                else:
                    print(f"  [bdh_pull] sin datos para {tk} {flds} ({start_date}..{end_date})")
                break
            except Exception as e:
                last_err = e
                print(f"  [bdh_pull] intento {attempt}/{max_retries} fallo para {tk}: {e}")
                time.sleep(pause)
        else:
            print(f"  [bdh_pull] {tk} fallo tras {max_retries} intentos: {last_err}")
    return frames


def bdp_pull(tickers, flds, max_retries=3, pause=1.5):
    """Wrapper sobre xbbg.blp.bdp (estaticos: rating, acciones en circulacion, etc.).
    Devuelve un DataFrame ancho: una fila por ticker, una columna por campo."""
    blp = _get_blp()
    if isinstance(tickers, str):
        tickers = [tickers]
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            return _to_wide(blp.bdp(tickers=tickers, flds=flds, **_XBBG_CALL))
        except Exception as e:
            last_err = e
            print(f"  [bdp_pull] intento {attempt}/{max_retries} fallo: {e}")
            time.sleep(pause)
    print(f"  [bdp_pull] fallo definitivo para {tickers} {flds}: {last_err}")
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Market cap / balance por banco (contraparte Bloomberg de fetch_mktcap_yf)
# ---------------------------------------------------------------------------
def fetch_mktcap_bloomberg(bankmap: dict, country: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Contraparte de jloss_common.fetch_mktcap_yf pero via Bloomberg.
    bankmap: {bankname: {'ticker': 'GGAL AR Equity', ...}} (ticker=None si no cotiza).
    mktcap = CUR_MKT_CAP diario si esta disponible; si no, PX_LAST * BS_SH_OUT."""
    frames = []
    for bankname, meta in bankmap.items():
        ticker = meta.get("ticker")
        if not ticker:
            continue
        res = bdh_pull(ticker, ["CUR_MKT_CAP", "PX_LAST"], start_date, end_date, freq="D")
        df = res.get(ticker)
        if df is None or df.empty:
            continue
        df = df.copy()   # bdh_pull ya devuelve ancho, con 'date' como columna
        if "CUR_MKT_CAP" in df.columns and df["CUR_MKT_CAP"].notna().any():
            df["mktcap"] = df["CUR_MKT_CAP"]
        elif "PX_LAST" in df.columns:
            # BS_SH_OUT como serie trimestral (no un unico snapshot estatico) + merge_asof,
            # igual que jloss_common.fetch_mktcap_yf — evita sesgo por splits/aumentos de capital.
            sh_res = bdh_pull(ticker, ["BS_SH_OUT"], start_date, end_date, freq="CQ")
            sh_df = sh_res.get(ticker)
            if sh_df is not None and not sh_df.empty:
                sh_df = sh_df.copy()
                sh_df["date"] = pd.to_datetime(sh_df["date"])
                df["date"] = pd.to_datetime(df["date"])
                df = pd.merge_asof(df.sort_values("date"), sh_df[["date", "BS_SH_OUT"]].sort_values("date"),
                                    on="date")
                df["mktcap"] = df["PX_LAST"] * df["BS_SH_OUT"]
            else:
                # fallback: snapshot estatico unico (mejor que nada, pero no ajusta por splits)
                sh = bdp_pull(ticker, ["BS_SH_OUT"])
                shares = sh["BS_SH_OUT"].iloc[0] if not sh.empty and "BS_SH_OUT" in sh.columns else np.nan
                df["mktcap"] = df["PX_LAST"] * shares
        else:
            continue
        df["countryname"] = country
        df["bankname"] = bankname
        frames.append(df[MKTCAP_COLS])
        time.sleep(0.2)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=MKTCAP_COLS)


def _has_data(df: pd.DataFrame, flds: list[str]) -> bool:
    """True si al menos un campo fundamental trae algun valor no nulo."""
    if df is None or df.empty:
        return False
    return any(pd.to_numeric(df[f], errors="coerce").notna().any()
               for f in flds if f in df.columns)


def _pull_fundamentals(ticker: str, bankname: str, flds: list[str],
                       start_date: str, end_date: str) -> pd.DataFrame | None:
    """Trimestral primero; si el banco no reporta trimestralmente (Sudafrica es el caso
    tipico: SBK/FSR devuelven las fechas de fin de trimestre pero todas vacias) se
    reintenta semestral. Devuelve None si ninguna frecuencia trae dato."""
    res = bdh_pull(ticker, flds, start_date, end_date, freq="CQ")
    df = res.get(ticker)
    if _has_data(df, flds):
        return df.copy()

    print(f"  [{bankname}] sin fundamentales trimestrales en {ticker} — "
          f"reintento en frecuencia semestral")
    res = bdh_pull(ticker, flds, start_date, end_date, freq="SA")
    df = res.get(ticker)
    if _has_data(df, flds):
        print(f"  [{bankname}] OK en semestral ({len(df)} periodos) — el panel de este "
              f"banco queda a frecuencia semestral, no trimestral.")
        return df.copy()

    print(f"  [{bankname}] AVISO: sin fundamentales en ninguna frecuencia para {ticker} "
          f"— el banco queda fuera del balance.")
    return None


def fetch_balance_bloomberg(bankmap: dict, country: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Pull trimestral (Per=CQ) de las 3 partidas que JLoss realmente necesita por banco:
    activos totales (BS_TOT_ASSET), patrimonio total (TOTAL_EQUITY), deuda emitida (bonds,
    campo BS_LT_BORROW = "Long Term Debt" de Balance Sheet/Liabilities; verificado 2026-08-27
    contra el Terminal — el viejo "LT_DEBT" no es un mnemonico valido y volvia vacio), mas
    net_income/net_rev si estan disponibles. Devuelve columnas ya alineadas a BALANCE_COLS
    (lt_borrow/st_borrow/total_liab se completan despues con derive_st_lt_bonds_vs_rest)."""
    flds = ["BS_TOT_ASSET", "TOTAL_EQUITY", "BS_LT_BORROW", "NET_INCOME", "SALES_REV_TURN",
            "BS_CASH_NEAR_CASH_ITEM"]
    rows = []
    for bankname, meta in bankmap.items():
        ticker = meta.get("ticker")
        if not ticker:
            continue
        df = _pull_fundamentals(ticker, bankname, flds, start_date, end_date)
        if df is None:
            continue
        for _, r in df.iterrows():
            rows.append({
                "countryname": country, "bankname": bankname, "date": r.get("date"),
                "tot_asset": r.get("BS_TOT_ASSET", np.nan),
                "equity_book": r.get("TOTAL_EQUITY", np.nan),
                "bonds": r.get("BS_LT_BORROW", np.nan),
                "net_income": r.get("NET_INCOME", np.nan),
                "net_rev": r.get("SALES_REV_TURN", np.nan),
                "cash_and_st_investments": r.get("BS_CASH_NEAR_CASH_ITEM", np.nan),
                "prof_margin": np.nan,  # se completa despues: net_income/net_rev agregado
                "lt_borrow": np.nan, "st_borrow": np.nan, "total_liab": np.nan,
            })
        time.sleep(0.2)
    return finalize_balance(rows) if rows else finalize_balance([])


# ---------------------------------------------------------------------------
# Variables macro/globales y de pais (runbook §1 y §3)
# ---------------------------------------------------------------------------
def daily_fx_vol_quarterly(ccy_ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Volatilidad cambiaria trimestral: std de retornos diarios de USD<CCY> Curncy x sqrt(63)."""
    res = bdh_pull(ccy_ticker, ["PX_LAST"], start_date, end_date, freq="D")
    df = res.get(ccy_ticker)
    if df is None or df.empty:
        return pd.DataFrame(columns=["quarter", "fx_vol"])
    df = df.copy()   # bdh_pull ya devuelve ancho, con 'date' como columna
    df["date"] = pd.to_datetime(df["date"])
    df["ret"] = np.log(df["PX_LAST"]).diff()
    df["quarter"] = df["date"].dt.to_period("Q")
    g = df.groupby("quarter")["ret"].std().reset_index()
    g["fx_vol"] = g["ret"] * np.sqrt(63)
    return g[["quarter", "fx_vol"]]


def write_dates_series_csv(df: pd.DataFrame, date_col: str, value_col: str, out_path: str,
                           value_name: str, date_fmt: str = "%d/%m/%Y", descending: bool = True):
    """Escribe un CSV en el formato DATES,<value_name> ya usado por download_STX.py /
    download_Ryr.py (mismo esquema que Chile) — para que entre directo al pipeline GaR."""
    out = df[[date_col, value_col]].copy()
    out[date_col] = pd.to_datetime(out[date_col])
    out = out.sort_values(date_col, ascending=not descending)
    out["DATES"] = out[date_col].dt.strftime(date_fmt)
    out = out.rename(columns={value_col: value_name})[["DATES", value_name]]
    out.to_csv(out_path, index=False)
    print(f"  escrito {out_path} ({len(out)} filas)")
