"""
jloss_common.py — utilidades compartidas por los extractores LatAm de inputs JLoss.

Esquema v8 (idéntico al panel actual):
  BALANCE: countryname, bankname, date, lt_borrow, st_borrow, tot_asset,
           cash_and_st_investments, net_income, net_rev, prof_margin   (+ equity_book aux)
  MKTCAP : countryname, bankname, date, mktcap

La estimacion de rho (doble: 0.4 plano y rho estimado por factor comun) NO ocurre aqui;
es parte de la capa de metrica (compute_jloss / calibracion). Los extractores son
rho-agnosticos: solo entregan E (mktcap), insumos de sigma (precios), deuda CP/LP y
pasivos totales.

EJECUTAR EN ENTORNO CON RED ABIERTA. No corre dentro del sandbox de Claude.
"""
import re
import time
import numpy as np
import pandas as pd

_RE_LATAM = re.compile(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$")   # 1.234.567,89  (miles '.', dec ',')
_RE_EN    = re.compile(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$")    # 1,234,567.89  (miles ',', dec '.')
_RE_DECCO = re.compile(r"^-?\d+,\d+$")                      # 1234,5        (dec ',')

BALANCE_COLS = ["countryname", "bankname", "date", "lt_borrow", "st_borrow", "tot_asset",
                "cash_and_st_investments", "net_income", "net_rev", "prof_margin",
                "equity_book", "bonds", "total_liab"]
MKTCAP_COLS = ["countryname", "bankname", "date", "mktcap"]


def empty_balance_row(country, bankname, date):
    return {"countryname": country, "bankname": bankname, "date": date,
            "lt_borrow": np.nan, "st_borrow": np.nan, "tot_asset": np.nan,
            "cash_and_st_investments": np.nan, "net_income": np.nan, "net_rev": np.nan,
            "prof_margin": np.nan, "equity_book": np.nan, "bonds": np.nan, "total_liab": np.nan}


def derive_st_lt_bonds_vs_rest(df, lt_weight=0.5):
    """Criterio del profesor (bonos vs resto): LP = bonos (deuda emitida), CP = resto.
    Requiere columnas 'bonds', 'tot_asset', 'equity_book'. Calcula:
        total_liab = tot_asset - equity_book
        lt_borrow  = bonds
        st_borrow  = total_liab - bonds        (el 'resto', por residuo -> reconcilia por construccion)
    El punto de default es DP = st_borrow + lt_weight*lt_borrow = total_liab - (1-lt_weight)*bonds.
    Devuelve el df con st_borrow, lt_borrow, total_liab, DP completados."""
    df = df.copy()
    df["total_liab"] = df["tot_asset"] - df["equity_book"]
    df["lt_borrow"] = df["bonds"]
    df["st_borrow"] = df["total_liab"] - df["bonds"]
    df["DP"] = df["st_borrow"] + lt_weight * df["lt_borrow"]
    return df


def reconcile_bonds_vs_rest(df, tol=1e-6):
    """Chequeo de consistencia contable del criterio bonos-vs-resto (lo que pide el profesor:
    'que cuadren'). Devuelve un resumen con la tasa de filas que reconcilian.
    Compatible con el esquema v8 (columna 'bonds') y con extractores antiguos (Peru/Mexico)
    que solo traen 'lt_borrow': en el criterio bonos-vs-resto, lt_borrow == bonds."""
    df = df.copy()
    if "bonds" not in df.columns:
        if "lt_borrow" not in df.columns:
            raise KeyError("Falta 'bonds' y 'lt_borrow'; no se puede reconciliar.")
        df["bonds"] = df["lt_borrow"]          # en bonos-vs-resto, los bonos son el LP
    d = df.dropna(subset=["st_borrow", "lt_borrow", "total_liab", "bonds"]).copy()
    if len(d) == 0:
        return {"n": 0, "ok_rate": np.nan}
    sum_ok = np.isclose(d["st_borrow"] + d["lt_borrow"], d["total_liab"], rtol=tol, atol=tol)
    bonds_ok = (d["bonds"] >= -tol) & (d["bonds"] <= d["total_liab"] * (1 + tol))
    st_ok = d["st_borrow"] >= -tol
    ok = sum_ok & bonds_ok & st_ok
    return {"n": int(len(d)), "ok_rate": float(ok.mean()),
            "fail_sum": int((~sum_ok).sum()), "fail_bonds": int((~bonds_ok).sum()),
            "fail_neg_st": int((~st_ok).sum()),
            "bonds_share_median": float((d["bonds"] / d["total_liab"]).median())}


def apply_residual_maturity(df, lt_amount_col, st_amount_col):
    """Mejora opcional (intencion de la duration, version ACCESIBLE): usar el desglose por
    vencimiento RESIDUAL que publican algunos supervisores en sus reportes de calce de plazos.
    lt_amount_col / st_amount_col son columnas ya extraidas con los montos a >1 anio y <=1 anio.
    Sobreescribe lt_borrow/st_borrow con el corte por vencimiento real (mas preciso que bonos-vs-resto)."""
    df = df.copy()
    df["lt_borrow"] = df[lt_amount_col]
    df["st_borrow"] = df[st_amount_col]
    df["total_liab"] = df["st_borrow"] + df["lt_borrow"]
    return df


def to_float_latam(x):
    """Convierte numeros con separador de miles '.' y decimal ',' (es-LATAM) o formato plano."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace("\xa0", "").replace(" ", "")
    if s in ("", "-", "n/d", "N/D", "ND", "nan", "NaN"):
        return np.nan
    if _RE_LATAM.match(s):                       # miles '.', decimal ','
        s = s.replace(".", "").replace(",", ".")
    elif _RE_EN.match(s):                        # miles ',', decimal '.'
        s = s.replace(",", "")
    elif _RE_DECCO.match(s):                      # solo decimal ','
        s = s.replace(",", ".")
    else:                                         # entero/decimal plano o con coma de miles suelta
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


def finalize_balance(rows):
    df = pd.DataFrame(rows)
    for c in BALANCE_COLS:
        if c not in df.columns:
            df[c] = np.nan
    df = df[BALANCE_COLS].copy()
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["bankname", "date"]).reset_index(drop=True)


def coverage_report(balance_df):
    """Fraccion de activos del sistema cubierta por trimestre (QA de representatividad)."""
    b = balance_df.dropna(subset=["tot_asset"]).copy()
    b["quarter"] = b["date"].dt.to_period("Q")
    g = b.groupby("quarter").agg(n_banks=("bankname", "nunique"),
                                 sys_assets=("tot_asset", "sum")).reset_index()
    return g


def fetch_mktcap_yf(bankmap, country, start_year, end_year):
    """Market cap diario via yfinance. bankmap: {bankname: {'ticker': 'XXX.SA', ...}}.
    mktcap = precio de cierre * acciones en circulacion (get_shares_full)."""
    import yfinance as yf
    frames = []
    for bankname, meta in bankmap.items():
        ticker = meta.get("ticker")
        if not ticker:
            continue
        tk = yf.Ticker(ticker)
        px = tk.history(start=f"{start_year}-01-01", end=f"{end_year}-12-31", interval="1d")
        if px.empty:
            continue
        px = px[["Close"]].reset_index().rename(columns={"Date": "date", "Close": "price"})
        px["date"] = pd.to_datetime(px["date"]).dt.tz_localize(None)
        try:
            sh = tk.get_shares_full(start=f"{start_year}-01-01")
        except Exception:
            sh = None
        if sh is not None and len(sh):
            sh = sh.reset_index(); sh.columns = ["date", "shares"]
            sh["date"] = pd.to_datetime(sh["date"]).dt.tz_localize(None)
            px = pd.merge_asof(px.sort_values("date"), sh.sort_values("date"), on="date")
            px["mktcap"] = px["price"] * px["shares"]
        else:
            px["mktcap"] = px["price"]   # fallback: precio (escala se corrige en el modelo)
        px["countryname"] = country; px["bankname"] = bankname
        frames.append(px[MKTCAP_COLS])
        time.sleep(0.2)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=MKTCAP_COLS)


# =========================================================================
# Helpers genericos para extractores long-format (bonos-vs-resto)
# Reutilizados por las configuraciones delgadas de los paises del Hito 4.
# =========================================================================
def match_bank_generic(entity, bankmap, code=None, code_key="code"):
    if code is not None:
        for b, meta in bankmap.items():
            if str(code).strip() == str(meta.get(code_key, "")).strip() and meta.get(code_key):
                return b
    u = str(entity).upper()
    # match mas ESPECIFICO: la subcadena coincidente mas larga gana (evita que un nombre
    # generico como "BANK OF CHINA" capture "POSTAL SAVINGS BANK OF CHINA", etc.)
    best, best_len = None, 0
    for b, meta in bankmap.items():
        for n in meta.get("names", []):
            nu = n.upper()
            if nu in u and len(nu) > best_len:
                best, best_len = b, len(nu)
    return best


def classify_generic(name, account_map):
    c = str(name).upper()
    for field, keys in account_map.items():
        if any(k.upper() in c for k in keys):
            return field
    return None


def parse_period_generic(p):
    s = str(p).strip()
    for fmt in ("%Y%m", "%Y-%m", "%Y/%m", "%Y-%m-%d", "%d/%m/%Y", "%Y"):
        try:
            return pd.to_datetime(s, format=fmt).replace(day=1)
        except ValueError:
            continue
    return pd.to_datetime(s).normalize().replace(day=1)


def transform_long_generic(df, bankmap, account_map, country,
                           col_bank="bank", col_account="account",
                           col_period="period", col_value="value", col_code=None):
    """Export long-format (banco, cuenta, periodo, valor) -> filas v8 con bonds/tot_asset/equity_book.
    El llamador aplica derive_st_lt_bonds_vs_rest. 'bonds' acumula todas las cuentas mapeadas a 'bonds'
    (p.ej. titulos emitidos + deuda subordinada)."""
    acc = {}
    for _, rec in df.iterrows():
        code = rec.get(col_code) if col_code else None
        bankname = match_bank_generic(rec.get(col_bank, ""), bankmap, code=code)
        if bankname is None:
            continue
        field = classify_generic(rec.get(col_account, ""), account_map)
        if field is None:
            continue
        val = to_float_latam(rec.get(col_value))
        if np.isnan(val):
            continue
        date = parse_period_generic(rec.get(col_period))
        key = (bankname, date)
        acc.setdefault(key, {})
        acc[key][field] = acc[key].get(field, 0.0) + val
    rows = []
    for (bankname, date), f in acc.items():
        row = empty_balance_row(country, bankname, date)
        row.update({"bonds": f.get("bonds", np.nan),
                    "tot_asset": f.get("tot_asset", np.nan), "equity_book": f.get("equity", np.nan)})
        rows.append(row)
    return rows


# --- Normalizacion de nombres de banco (Mexico) -------------------------------
# La CNBV cambia/typea nombres en el tiempo, generando varios slugs para un mismo
# banco. Mapa variante -> canonico (confirmado: periodos disjuntos + empalme de
# activos). Aplicar jc.canonical_bankname() al asignar el bankname en CUALQUIER
# extractor de Mexico para no fragmentar series.
BANK_ALIASES_MX = {
    "bicentenario": "banco_bicentenario", "bicentenrio": "banco_bicentenario",
    "banco_bicentenario": "banco_bicentenario",
    "donde": "banco_donde", "donde_banco": "banco_donde", "banco_donde": "banco_donde",
    "uala": "banco_uala", "banco_uala": "banco_uala",
    "covalto": "banco_covalto", "banco_covalto": "banco_covalto",
    "forjadores": "banco_forjadores", "banco_forjadores": "banco_forjadores",
    "banfeliz_antes_forjadores": "banco_forjadores",
    "finterra": "banco_finterra", "banco_finterra": "banco_finterra",
    "intercam": "intercam_banco", "inter_banco": "intercam_banco",
    "keb_hana_bank": "keb_hana_mexico", "keb_hana_mexico": "keb_hana_mexico",
    "ubs": "ubs_bank", "ubs_bank": "ubs_bank",
    "bank_of_tokio_mitsubishi_ufj": "bank_of_tokyo_mitsubishi_ufj",
    "bank_of_tokyo_mitsubishi_ufj": "bank_of_tokyo_mitsubishi_ufj",
}


def canonical_bankname(name, country="mexico"):
    """Unifica variantes/typos de un mismo banco a un slug canonico (idempotente)."""
    s = str(name).strip()
    if country == "mexico":
        return BANK_ALIASES_MX.get(s, s)
    return s