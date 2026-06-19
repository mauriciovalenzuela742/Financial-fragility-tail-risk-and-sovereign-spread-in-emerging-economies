"""
sbp_parse.py — Parser de reportes individuales por banco de la SBP (Panamá) + mapa de slugs.

Hechos validados (Banco Nacional y bancos privados, 2024-2026):
  - Cabecera de meses en fila ~9; 13 ranuras: Dic(año previo) + Ene..Dic(año fin).
  - El archivo de un mes trae el ejercicio del año-fin; meses NO reportados = 0.0 (no vacío).
  - Año del ejercicio = año-fin del título ('... A <MES> <AÑO>').
  - Balance: ACTIVO == PASIVO+PATRIMONIO y DEP+OBLIG+OTROS+PATRIM == ACTIVO (residual 0).
  - Estado de Resultado de-acumulado: net_income mensual = flujo del mes; última col 'ACUMULADO'.
  - No hay renglón de bonos (ni en privados): LP = OBLIGACIONES; CP = DEPOSITOS + OTROS PASIVOS.
"""
import re
import unicodedata
import datetime as dt
import pandas as pd

# --- Mapa key canónica -> slug SBP (fuente única; download_sbp y extract_panama lo importan).
# Confirmados por nombre de archivo descargado. bac/global/aliado pendientes de verificar.
SLUGS = {
    "banco_nacional": "Nacional",
    "caja_ahorros":   "Cajahorros",
    "banco_general":  "General",
    "banistmo":       "Banistmosa",
    "banesco":        "Banescosa",
    "bancolombia_pa": "Bancolopanama",
    "multibank":      ["Multibanksub", "Multibank"],  # slug cambió: Multibanksub (2016+), Multibank (<=2015)
    "credicorp_bank": "Credicorp",
    "mercantil":      "MercantilPanama",
    "metrobank":      "Metrobank",
    "towerbank":      "Tower",
    "st_george":      "Stgeorge",
    "unibank":        "Unibank",
    "bct_bank":       "BCTBankIntSA",
    "bac_panama":     ["Bac", "BacPanama"],   # slug cambió: Bac (2016+), BacPanama (<=2015)
    "global_bank":    "Global",
    "aliado":         "Aliado",
}
SLUG2KEY = {s.lower(): k for k, v in SLUGS.items()
            for s in (v if isinstance(v, list) else [v])}

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MONTH_IDX = {m: i + 1 for i, m in enumerate(MONTHS)}

BAL_LINES = {
    "total de activos":    "tot_asset",
    "depositos":           "deposits",
    "obligaciones":        "obligaciones",   # -> LP
    "otros pasivos":       "otros_pasivos",
    "patrimonio":          "equity",
    "pasivo y patrimonio": "pas_y_pat",
}
PNL_NETINCOME = "utilidad del periodo"
_YEAR_RE = re.compile(r"\ba\s+[a-z]+\s+(\d{4})")


def _norm(s):
    if s is None:
        return ""
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def _detect_engine(path):
    with open(path, "rb") as fh:
        magic = fh.read(8)
    if magic[:4] == b"\xd0\xcf\x11\xe0":
        return "xlrd"
    if magic[:4] == b"PK\x03\x04":
        return "openpyxl"
    raise ValueError(f"Formato no reconocido: {path}")


def _read_rows(path):
    df = pd.read_excel(path, header=None, engine=_detect_engine(path))
    return df.values.tolist()


def _detect_year(rows):
    for r in rows[:8]:
        for c in r:
            m = _YEAR_RE.findall(_norm(c))
            if m:
                return int(m[-1])
    return None


def _find_month_header(rows):
    for i, r in enumerate(rows):
        if sum(1 for c in r if _norm(c) in MONTH_IDX) >= 4:
            return i
    raise ValueError("No se encontró fila de cabecera de meses.")


def _current_year_month_cols(header_row):
    seq = [(j, _norm(c)) for j, c in enumerate(header_row) if _norm(c) in MONTH_IDX]
    return [(MONTH_IDX[m], j) for j, m in seq[1:13]]   # descarta Dic(año previo)


def _row_label(r):
    for c in r:
        if isinstance(c, str) and _norm(c):
            return _norm(c)
    return ""


def _line(rows, label_norm):
    for r in rows:
        if _row_label(r) == label_norm:
            return r
    return None


def parse_balance(path, year=None, bank_key=None, tol=1.0):
    rows = _read_rows(path)
    year = year or _detect_year(rows)
    if year is None:
        raise ValueError(f"No pude detectar el año en {path}")
    cols = _current_year_month_cols(rows[_find_month_header(rows)])
    lines = {field: _line(rows, lbl) for lbl, field in BAL_LINES.items()}
    out = []
    for mnum, j in cols:
        rec = {"bankname": bank_key, "country": "panama", "date": dt.date(year, mnum, 1)}
        for field, r in lines.items():
            rec[field] = (r[j] if r is not None and j < len(r) else None)
        out.append(rec)
    bal = pd.DataFrame(out)
    # Meses NO reportados vienen como 0.0 -> descartar por activo nulo/cero.
    bal = bal[bal["tot_asset"].fillna(0) > 0].copy()
    if bal.empty:
        return bal
    bal["lt_debt"] = bal["obligaciones"]
    bal["st_debt"] = bal["deposits"].fillna(0) + bal["otros_pasivos"].fillna(0)
    bal["tot_liab"] = bal["st_debt"] + bal["lt_debt"]
    id1 = (bal["tot_asset"] - bal["pas_y_pat"]).abs()
    id2 = (bal["tot_liab"] + bal["equity"] - bal["tot_asset"]).abs()
    bal["id_fail"] = (id1 > tol) | (id2 > tol)
    if int(bal["id_fail"].sum()):
        print(f"[WARN] {bank_key} {year}: {int(bal['id_fail'].sum())} meses con identidad > tol={tol}")
    return bal[["bankname", "country", "date", "tot_asset", "tot_liab", "st_debt",
                "lt_debt", "equity", "deposits", "obligaciones", "otros_pasivos", "id_fail"]]


def parse_netincome(path, year=None, bank_key=None):
    rows = _read_rows(path)
    year = year or _detect_year(rows)
    if year is None:
        return None
    cols = _current_year_month_cols(rows[_find_month_header(rows)])
    ni = _line(rows, PNL_NETINCOME)
    if ni is None:
        return None
    recs = []
    for mnum, j in cols:
        v = ni[j] if j < len(ni) else None
        recs.append({"bankname": bank_key, "country": "panama",
                     "date": dt.date(year, mnum, 1), "net_income_flow": v})
    df = pd.DataFrame(recs)
    return df  # meses futuros (0.0) se descartan via merge contra balance


if __name__ == "__main__":
    import sys, glob, os
    base = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads"
    for p in sorted(glob.glob(os.path.join(base, "RE-BALANCE-BANCO-en-*.xlsx"))):
        slug = re.match(r"RE-BALANCE-BANCO-en-(.+)\.xlsx", os.path.basename(p)).group(1)
        key = SLUG2KEY.get(slug.lower(), f"?{slug}")
        b = parse_balance(p, bank_key=key)
        if b.empty:
            print(f"{key:16s} sin meses reportados"); continue
        print(f"{key:16s} {b['date'].min()}..{b['date'].max()} | meses={len(b)} | id_fails={int(b['id_fail'].sum())}")