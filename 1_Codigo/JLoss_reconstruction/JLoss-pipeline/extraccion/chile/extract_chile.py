"""
extract_chile.py — Extracción de inputs JLoss para Chile desde fuentes públicas.

Produce DOS archivos con el MISMO esquema que el panel v8:
  - mktcap_chile.csv      : [countryname, bankname, date, mktcap]      (precios * acciones)
  - balance_chile.csv     : [countryname, bankname, date, lt_borrow, st_borrow,
                             tot_asset, cash_and_st_investments, net_income, net_rev, prof_margin]

Fuentes:
  - Balances: API CMF Bancos (https://api.cmfchile.cl).  Requiere API key gratuita.
  - Precios : proveedor público de equity configurable (yfinance por defecto, tickers .SN).

EJECUTAR EN UN ENTORNO CON RED ABIERTA. Este modulo NO corre dentro del sandbox de Claude.

Uso:
    export CMF_API_KEY=xxxxxxxx
    python extract_chile.py --start 1999 --end 2026

Notas de modelado (decidir con el comité):
  * El esquema original 'st_borrow'/'lt_borrow' venia de un proveedor con plantilla
    estandarizada por madurez. La CMF clasifica las obligaciones por INSTRUMENTO, no por
    madurez estricta. El mapeo por defecto (ACCOUNT_MAP) es una aproximacion defendible;
    confirmela ejecutando `discover_accounts()` y revisando los nombres de cuenta.
  * Las cifras CMF estan en millones de pesos (MM$). El modelo de Merton es invariante a
    escala dentro de cada banco-trimestre (usa E, sigma, D en la misma unidad), pero E
    (market cap) debe quedar en la MISMA moneda/unidad que D (pasivos). Ver to_common_units().
"""
import os, time, argparse, json, random
import requests
import pandas as pd
import numpy as np
import jloss_common as jc

CMF_BASE = "https://api.cmfchile.cl/api-sbifv3/recursos_api"
COUNTRY = "chile"

# --- Universo de bancos (codigos CMF verificados con --discover-banks) ---
# bankname sigue la convencion del panel (minusculas, sin espacios) para empatar con v8.
# ticker=None -> no transa en bolsa -> entra con PD CONTABLE (book_pd.py) en el motor JLoss.
BANKS = {
    # --- LISTADOS (PD de mercado via yfinance, .SN) ---
    "banco_de_chile":   {"cmf": "001", "ticker": "CHILE.SN"},
    "bci":              {"cmf": "016", "ticker": "BCI.SN"},
    "santander_chile":  {"cmf": "037", "ticker": "BSANTANDER.SN"},
    "itau_corpbanca":   {"cmf": "039", "ticker": "ITAUCL.SN"},   # ex ITAUCORP.SN (renombrado 04/2023)
    "banco_bice":       {"cmf": "028", "ticker": None},          # holding BICECORP sin cobertura yf -> PD contable
    "banco_security":   {"cmf": "049", "ticker": None},          # Grupo Security fusionado con BICECORP 2025 -> PD contable
    # --- NO LISTADOS (PD contable) -- amplian la cobertura del sistema para JLoss ---
    # Comenta los que no quieras incluir en el agregado sistemico.
    "bancoestado":         {"cmf": "012", "ticker": None},   # estatal
    "scotiabank_chile":    {"cmf": "014", "ticker": None},
    "banco_internacional": {"cmf": "009", "ticker": None},
    "banco_falabella":     {"cmf": "051", "ticker": None},
    "banco_ripley":        {"cmf": "053", "ticker": None},
    "banco_consorcio":     {"cmf": "055", "ticker": None},
    "bbva_chile":          {"cmf": "504", "ticker": None},   # BBVA Chile (absorbido por Scotiabank 2018)
    "btg_pactual_chile":   {"cmf": "059", "ticker": None},
}
LISTED_BANKS = {k: v for k, v in BANKS.items() if v["ticker"]}   # subconjunto con precio de mercado
# --- Mapeo de cuentas del Balance Mensual CMF -> campos del esquema v8 ---
# Codigos CONFIRMADOS con --discover-accounts. El plan de cuentas es comun para
# periodo2 (2008) y periodo3 (2009-hoy); el periodo1 (1995-2007) usa OTRO plan
# (codigos de 10 digitos) SIN lineas de total limpias -> no soportado por esta via.
#   1000000 ACTIVOS  |  3000000 PATRIMONIO  |  2400000 INSTRUMENTOS DE DEUDA EMITIDOS
# 2400000 = LETRAS DE CREDITO (2401000) + BONOS (2402000); es la "deuda emitida" total
# (criterio del profesor: deuda emitida = LP). Alternativa mas estricta: solo 2402000 BONOS.
CODE_MAP_MODERN = {
    "1000000": "tot_asset",   # ACTIVOS (total)
    "3000000": "equity",      # PATRIMONIO (atribuible a tenedores; minoritario 3200000 se omite)
    "2400000": "bonds",       # INSTRUMENTOS DE DEUDA EMITIDOS (letras + bonos) -> LP
}
# 2022+ : nuevo Compendio de Normas Contables (IFRS9/Basilea III, rige 01-01-2022).
# El plan de cuentas cambio -> los codigos de arriba dan 404. Completar con los codigos
# reales corriendo:  python extract_chile.py --discover-accounts 2022 06
# Mapear: total activos -> tot_asset ; total patrimonio -> equity ; deuda emitida (bonos/
# instrumentos de deuda emitidos) -> bonds.
CODE_MAP_2022 = {
    "100000000": "tot_asset",   # TOTAL ACTIVOS
    "380000000": "equity",      # PATRIMONIO DE LOS PROPIETARIOS (excluye 390000000 interes no controlador)
    "245000000": "bonds",       # Instrumentos financieros de deuda emitidos (letras + bonos) -> LP
    # Nota: los bonos subordinados/perpetuos pasaron a 255000000 (capital regulatorio) y NO se
    # incluyen aqui; son loss-absorbing capital, no funding senior, y su peso es marginal.
}
# Respaldo por DESCRIPCION EXACTA (match en MAYUSCULAS, sin sub-cuentas).
ACCOUNT_MAP = {
    "tot_asset": ["ACTIVOS"],
    "equity":    ["PATRIMONIO"],
    "bonds":     ["INSTRUMENTOS DE DEUDA EMITIDOS"],
}
FIRST_SUPPORTED_YEAR = 2008   # antes de 2008 el plan de cuentas no tiene totales limpios
REGIME_2022 = 2022            # nuevo Compendio (IFRS9/Basilea III)


def _code_map_for_year(year):
    """Devuelve el mapa de codigos vigente para el anio, o None si no esta soportado/mapeado."""
    y = int(year)
    if y < FIRST_SUPPORTED_YEAR:
        return None                              # 1995-2007: plan antiguo sin totales limpios
    if y >= REGIME_2022:
        return CODE_MAP_2022 or None             # 2022+: requiere completar CODE_MAP_2022
    return CODE_MAP_MODERN                        # 2008-2021


# =========================================================================
# Cliente CMF minimo (sin dependencias externas mas alla de requests)
# =========================================================================
class CMF:
    def __init__(self, api_key, timeout=45, pause=1.5, retries=6):
        if not api_key:
            raise ValueError("Falta CMF_API_KEY (registro gratuito en api.cmfchile.cl)")
        self.key = api_key; self.timeout = timeout; self.pause = pause; self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JLoss-research/1.0",
            "Accept": "application/json",
            # Sin keep-alive: conexion TCP nueva por request. Evita el RemoteDisconnected
            # que ocurre cuando el servidor CMF cierra una conexion keep-alive en reposo.
            "Connection": "close",
        })

    def _get(self, path, **params):
        params.update({"apikey": self.key, "formato": "json"})
        url = f"{CMF_BASE}/{path}"
        last = None
        for attempt in range(self.retries):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)
                r.raise_for_status()
                time.sleep(self.pause)        # cortesia con el rate limit de la CMF
                return r.json()
            except requests.HTTPError as e:
                sc = e.response.status_code if e.response is not None else None
                # 429/408 = rate limit / timeout del servidor -> reintentar con espera larga
                if sc in (408, 429):
                    last = e
                    time.sleep(min(8.0 * (attempt + 1), 40.0) + random.uniform(0, 2.0))
                    continue
                # otros 4xx (p.ej. cuenta inexistente) no se reintentan
                if sc is not None and 400 <= sc < 500:
                    raise
                last = e                           # 5xx -> reintentar
            except (requests.ConnectionError, requests.Timeout) as e:
                last = e                           # caída transitoria -> reintentar con backoff
            # backoff exponencial con tope y jitter (evita sincronizar reintentos)
            time.sleep(min(2.0 * (2 ** attempt), 20.0) + random.uniform(0, 1.0))
        raise last

    def instituciones(self, year, month):
        # listado de instituciones con datos en ese mes/año
        return self._get(f"balances/{year}/{month}/instituciones")

    def lista_cuentas(self, year, month):
        return self._get(f"balances/{year}/{month}/cuentas")

    def balance_institucion(self, year, inst):
        # balance de la institucion (codigo en la RUTA) para todos los meses del año
        return self._get(f"balances/{year}/instituciones/{inst}")

    def cuenta_anual_todas(self, year, codigo_cuenta):
        # UNA cuenta para TODAS las instituciones, todos los meses del año (respuesta chica)
        return self._get(f"balances/{year}/cuentas/{codigo_cuenta}")


def discover_accounts(api_key, year="2024", month="06"):
    """Imprime CodigoCuenta | DescripcionCuenta para fijar CODE_MAP/ACCOUNT_MAP con valores reales."""
    cli = CMF(api_key)
    data = cli.lista_cuentas(year, month)
    for row in _records(data):
        print(row.get("CodigoCuenta", "?"), "|", row.get("DescripcionCuenta", "?"))


def discover_banks(api_key, year="2024", month="06"):
    """Imprime CodigoInstitucion | NombreInstitucion (para elegir qué bancos agregar)."""
    cli = CMF(api_key)
    data = cli.instituciones(year, month)
    for row in _records(data):
        print(row.get("CodigoInstitucion", "?"), "|", row.get("NombreInstitucion", "?"))


def _records(payload):
    """La API CMF anida los registros bajo claves variables (CodigosBalances, etc.).
    Devuelve la primera lista de registros que encuentre, recursivamente."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for v in payload.values():
            r = _records(v)
            if r:
                return r
    return []


# =========================================================================
# Extraccion de balances -> esquema v8
# =========================================================================
def _classify(code, desc, code_map):
    """Mapea un registro de balance a un campo del esquema v8.
    Prioriza el CODIGO de cuenta (estable); respaldo: descripcion EXACTA en mayusculas."""
    if code and str(code) in code_map:
        return code_map[str(code)]
    u = (desc or "").strip().upper()
    for field, names in ACCOUNT_MAP.items():
        if u in [n.upper() for n in names]:
            return field
    return None


def fetch_balances(api_key, start_year, end_year, out_dir=".", all_banks=False):
    """Extrae solo las 3 cuentas necesarias usando el endpoint
    balances/{año}/cuentas/{codigo} (una cuenta, TODAS las instituciones, todo el año).
    Cachea cada (año, cuenta) en disco: re-correr completa lo que falto sin re-bajar lo que ya tiene.
    all_banks=True -> incluye TODO el sistema bancario (excepto el agregado 999), no solo los de BANKS."""
    cli = CMF(api_key)
    field_for_code = {**CODE_MAP_MODERN, **CODE_MAP_2022}  # codigo -> campo (ambos regimenes)
    bank_by_cmf = {meta["cmf"]: name for name, meta in BANKS.items()}
    skipped_old = False
    skipped_new = False

    # --- cache en disco: {"year|code": [ [inst, nombre, anho, mes, montototal], ... ]} ---
    # (formato nuevo de 5 campos guarda TODAS las instituciones; el viejo de 4 solo los 14 de BANKS)
    cache_path = os.path.join(out_dir, ".chile_cmf_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as fh:
                cache = json.load(fh)
            print(f"  cache: {len(cache)} (anio,cuenta) ya descargados en corridas previas")
        except Exception:
            cache = {}

    def _save_cache():
        tmp = cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh)
        os.replace(tmp, cache_path)

    def _is_cached(key):
        if key not in cache:
            return False
        recs = cache[key]
        if not all_banks:
            return True                                    # default: cualquier formato sirve
        # all_banks requiere formato nuevo (5 campos = todas las instituciones)
        return (len(recs) == 0) or (len(recs[0]) >= 5)

    tasks = []                                             # (year, codigo_cuenta) que faltan
    for year in range(start_year, end_year + 1):
        cm = _code_map_for_year(year)
        if cm is None:
            if year >= REGIME_2022:
                skipped_new = True
            else:
                skipped_old = True
            continue
        for code in cm:                                    # codigos del regimen de ESE anio
            if not _is_cached(f"{year}|{code}"):
                tasks.append((year, code))

    def _run(task_list, label):
        still = []
        for year, code in task_list:
            try:
                payload = cli.cuenta_anual_todas(year, code)
            except requests.RequestException as e:
                detail = type(e).__name__
                if isinstance(e, requests.HTTPError) and e.response is not None:
                    detail += f" {e.response.status_code}"
                print(f"  aviso{label}: cuenta {code} {year} omitida ({detail})")
                still.append((year, code))
                continue
            recs = []
            for rec in _records(payload):
                inst = str(rec.get("CodigoInstitucion", "")).strip().zfill(3)
                # excluir agregados: 999 (sistema) y subtotales 900/970/980... (codigos >= 900)
                if not inst.isdigit() or int(inst) >= 900:
                    continue
                recs.append([inst, rec.get("NombreInstitucion", ""),
                             rec.get("Anho", year), rec.get("Mes"), rec.get("MonedaTotal")])
            cache[f"{year}|{code}"] = recs                  # guarda TODAS las instituciones
            _save_cache()
            print(f"  ok{label}: cuenta {code} {year} -> {len(recs)} registros (cacheado)")
        return still

    if tasks:
        failed = _run(tasks, "")
        if failed:                                         # 2da pasada solo sobre lo que cayo
            print(f"  reintentando {len(failed)} (anio,cuenta) que fallaron...")
            time.sleep(8)
            failed = _run(failed, " [2da pasada]")
        if failed:
            print(f"  quedaron {len(failed)} (anio,cuenta) sin obtener; VUELVE A CORRER el mismo "
                  "comando para completarlos (la caché conserva lo ya bajado).")
    else:
        print("  todo en cache; nada que descargar.")

    if skipped_old:
        print(f"  nota: se omitieron los anios < {FIRST_SUPPORTED_YEAR} (plan de cuentas antiguo "
              "sin totales limpios). Para 1995-2007 usa la fuente legada (Bloomberg .xls).")
    if skipped_new:
        print(f"  nota: se omitieron los anios >= {REGIME_2022} (nuevo Compendio IFRS9/Basilea III, "
              "plan de cuentas distinto). Corre  --discover-accounts 2022 06  y completa CODE_MAP_2022.")

    # --- ensamblar el balance desde TODA la cache (corrida actual + previas) ---
    store = {}                                             # (bankname, year, month) -> {campo: valor}
    names_seen = {}                                        # bankname -> codigo CMF (para reporte)
    for key, recs in cache.items():
        _, code = key.split("|")
        if code not in field_for_code:
            continue
        for r in recs:
            if len(r) >= 5:                                # formato nuevo (con nombre)
                inst, nombre, anho, mes, monto = r[0], r[1], r[2], r[3], r[4]
            else:                                          # formato viejo (solo codigos de BANKS)
                inst, anho, mes, monto = r[0], r[1], r[2], r[3]
                nombre = None
            if not str(inst).isdigit() or int(inst) >= 900:  # agregados 900/970/980/999
                continue
            if not all_banks and inst not in bank_by_cmf:  # modo default -> solo los de BANKS
                continue
            if inst in bank_by_cmf:                         # nombre canonico (mantiene link de ticker)
                bname = bank_by_cmf[inst]
            else:
                bname = _slug(nombre) if nombre else f"banco_{inst}"
            val = _to_float(monto)
            if mes is None or val is None:
                continue
            store.setdefault((bname, int(anho), int(mes)), {}).setdefault(field_for_code[code], val)
            names_seen[bname] = inst

    rows = []
    for (bankname, yr, month), fields in store.items():
        rows.append({
            "countryname": COUNTRY, "bankname": bankname,
            "date": pd.Timestamp(yr, month, 1),
            "bonds": fields.get("bonds", np.nan),    # Instrumentos de deuda emitidos -> LP
            "tot_asset": fields.get("tot_asset", np.nan),
            "cash_and_st_investments": np.nan,
            "net_income": np.nan, "net_rev": np.nan, "prof_margin": np.nan,
            "equity_book": fields.get("equity", np.nan),
        })
    if not rows:
        print("  ATENCION: no se obtuvo ningun balance. Revisa CMF_API_KEY y los rangos de anios. "
              "No se escribira balance.")
        return pd.DataFrame(columns=["countryname", "bankname", "date",
                                     "bonds", "tot_asset", "equity_book"])
    if all_banks:
        print(f"  sistema: {len(names_seen)} bancos incluidos -> "
              f"{', '.join(sorted(names_seen))}")
    return jc.derive_st_lt_bonds_vs_rest(pd.DataFrame(rows))   # CP = pasivo total - bonos ; LP = bonos


def _slug(s):
    """Normaliza un nombre de institucion a bankname (minusculas, sin acentos ni simbolos)."""
    import unicodedata, re
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return s or "banco"


def _to_float(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(".", "").replace(",", ".")   # formato CL: 1.234.567,89
    try:
        return float(s)
    except ValueError:
        return None


# =========================================================================
# Extraccion de precios -> market cap (esquema v8)
# =========================================================================
def fetch_mktcap(start_year, end_year, source="yfinance"):
    """Devuelve [countryname, bankname, date, mktcap]. mktcap = precio * acciones en circulacion."""
    if source != "yfinance":
        raise NotImplementedError("Implementar backend Bolsa de Santiago / Stooq segun acceso.")
    import yfinance as yf
    frames = []
    for bankname, meta in LISTED_BANKS.items():
        tk = yf.Ticker(meta["ticker"])
        px = tk.history(start=f"{start_year}-01-01", end=f"{end_year}-12-31", interval="1d")
        if px.empty:
            continue
        shares = tk.get_shares_full(start=f"{start_year}-01-01")     # acciones en circulacion
        px = px[["Close"]].reset_index().rename(columns={"Date": "date", "Close": "price"})
        px["date"] = pd.to_datetime(px["date"]).dt.tz_localize(None)
        if shares is not None and len(shares):
            sh = shares.reset_index(); sh.columns = ["date", "shares"]
            sh["date"] = pd.to_datetime(sh["date"]).dt.tz_localize(None)
            px = pd.merge_asof(px.sort_values("date"), sh.sort_values("date"), on="date")
            px["mktcap"] = px["price"] * px["shares"]
        else:
            px["mktcap"] = px["price"]      # fallback: usar precio (escala se corrige en el modelo)
        px["countryname"] = COUNTRY; px["bankname"] = bankname
        frames.append(px[["countryname", "bankname", "date", "mktcap"]])
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# =========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2008)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--price-source", default="yfinance")
    ap.add_argument("--out", default=".")
    ap.add_argument("--all-banks", action="store_true",
                    help="Incluye TODO el sistema bancario (excepto el agregado 999), no solo los listados.")
    ap.add_argument("--discover-accounts", nargs="*", metavar="YEAR MONTH",
                    help="Lista CodigoCuenta|DescripcionCuenta (def. 2024 06) y termina.")
    ap.add_argument("--discover-banks", nargs="*", metavar="YEAR MONTH",
                    help="Lista CodigoInstitucion|NombreInstitucion (def. 2024 06) y termina.")
    args = ap.parse_args()
    key = os.getenv("CMF_API_KEY")

    if args.discover_accounts is not None:
        y, m = (args.discover_accounts + ["2024", "06"])[:2]
        discover_accounts(key, y, m); return
    if args.discover_banks is not None:
        y, m = (args.discover_banks + ["2024", "06"])[:2]
        discover_banks(key, y, m); return

    print("1/2 Balances CMF...")
    bal = fetch_balances(key, args.start, args.end, out_dir=args.out, all_banks=args.all_banks)
    if bal.empty:
        print("   balance vacio -> revisa los avisos de arriba. No se continua con market cap.")
        return
    bal.to_csv(f"{args.out}/balance_chile.csv", index=False)
    print(f"   {len(bal)} filas, {bal['bankname'].nunique()} bancos, "
          f"{bal['date'].min().date()} a {bal['date'].max().date()}")

    print("2/2 Market cap...")
    mkt = fetch_mktcap(args.start, args.end, args.price_source)
    mkt.to_csv(f"{args.out}/mktcap_chile.csv", index=False)
    print(f"   {len(mkt)} filas, {mkt['bankname'].nunique() if len(mkt) else 0} bancos")


if __name__ == "__main__":
    main()