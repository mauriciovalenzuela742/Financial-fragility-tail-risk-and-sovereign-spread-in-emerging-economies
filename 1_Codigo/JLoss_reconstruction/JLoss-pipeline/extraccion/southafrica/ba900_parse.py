"""
ba900_parse.py — Parser de los retornos BA900 del SARB (Sudáfrica).

Formato (CSV por institución, R'000): cabecera con 'Date'/'Institution', luego varias
'Table N' cada una con fila 'Description,Item Number,<bandas de madurez...>,TOTAL,...'.
Se extrae item_number -> valor de la columna TOTAL de cada tabla.

Ítems validados (BA900, abr-2026):
  277 = TOTAL ASSETS (columna 'TOTAL ASSETS (Col 1 plus col 3)')
   95 = TOTAL LIABILITIES (= 78+79+80)
   96 = TOTAL EQUITY (= 97 capital + 101 reservas)
   68 = Debt securities (deuda emitida) -> LP en bonos-vs-resto
Identidad validada: item277 == item95 + item96 (exacta).

Nota: la granularidad de madurez de depósitos llega solo a '>6 meses' -> NO hay corte
limpio a 1 año, por eso se usa bonos-vs-resto (homogéneo con el resto del panel), no
residual-maturity.
"""
import csv
import io
import datetime as dt

_MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}

ITEM_TOTAL_ASSET = 277
ITEM_TOTAL_LIAB = 95
ITEM_EQUITY = 96
ITEMS_BONDS = [68]      # Debt securities issued (bonos-vs-resto)


def _to_float(s):
    s = (s or "").strip().replace(",", "").replace(" ", "")
    if s in ("", "-", "."):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_date(s):
    s = (s or "").strip()
    parts = s.split()
    if len(parts) == 2 and parts[0].lower() in _MONTHS:
        return dt.date(int(parts[1]), _MONTHS[parts[0].lower()], 1)
    return None


def parse_ba900_csv(path):
    """Devuelve (date, institution, items{item_number: total_value}) desde un archivo."""
    with open(path, newline="", encoding="latin-1") as f:
        return _parse_rows(list(csv.reader(f)))


def parse_ba900_text(text):
    """Igual que parse_ba900_csv pero desde el contenido en memoria (miembro de zip)."""
    return _parse_rows(list(csv.reader(io.StringIO(text))))


def parse_ba900_xml(text):
    """Parsea el XMLData del SARB (campo XMLData de la API GetInstitutionData).
    Estructura: SARBForms[@TheYear,@TheMonth] -> Table -> ColumnHeader/Row -> Column[@Value].
    Devuelve (date, institution, items, mat) igual que el parser CSV."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(text)
    yr, mo = root.get("TheYear"), root.get("TheMonth")
    date = dt.date(int(yr), int(mo), 1) if yr and mo else None
    inst = root.get("InstitutionDescription")
    items, mat = {}, {}
    for table in root.iter("Table"):
        cols = {ch.get("ColumnNumber"): (ch.get("ColumnDescription") or "").strip().upper()
                for ch in table.findall("ColumnHeader")}
        total_cn = next((cn for cn, d in cols.items() if d.startswith("TOTAL")), None)
        st_cn = next((cn for cn, d in cols.items() if d == "SHORT-TERM"), None)
        mt_cn = next((cn for cn, d in cols.items() if d == "MEDIUM-TERM"), None)
        lt_cn = next((cn for cn, d in cols.items() if d == "LONG-TERM"), None)
        for row in table.findall("Row"):
            it = row.get("ItemNumber")
            if not it or not it.isdigit():
                continue
            it = int(it)
            cv = {c.get("ColumnNumber"): _to_float(c.get("Value")) for c in row.findall("Column")}
            if total_cn is not None and cv.get(total_cn) is not None:
                items[it] = cv[total_cn]
            if st_cn and mt_cn and lt_cn:
                st, m_, lt = cv.get(st_cn), cv.get(mt_cn), cv.get(lt_cn)
                if None not in (st, m_, lt):
                    mat[it] = (st, m_, lt)
    return date, inst, items, mat


def parse_ba900_any(text):
    """Detecta XML (API) vs CSV (zip/export) por el primer caracter."""
    return parse_ba900_xml(text) if text.lstrip()[:1] == "<" else parse_ba900_text(text)


def _parse_rows(rows):
    date = institution = None
    items = {}
    mat = {}            # item -> (short, medium, long) para tablas con cabecera Short-term
    total_col = None
    mat_cols = None     # (st_idx, mt_idx, lt_idx) si la tabla trae Short/Medium/Long-term
    for r in rows:
        if not r:
            continue
        c0 = r[0].strip()
        if c0 == "Date" and len(r) > 1:
            date = _parse_date(r[1])
        elif c0 == "Institution" and len(r) > 1:
            institution = r[1].strip()
        elif c0 == "Description" and len(r) > 1 and "Item" in r[1]:
            hdr = [c.strip().upper() for c in r]
            total_col = next((j for j, c in enumerate(hdr) if c.startswith("TOTAL")), None)
            try:
                mat_cols = (hdr.index("SHORT-TERM"), hdr.index("MEDIUM-TERM"), hdr.index("LONG-TERM"))
            except ValueError:
                mat_cols = None
        elif total_col is not None and len(r) > 1 and r[1].strip().isdigit():
            it = int(r[1])
            val = _to_float(r[total_col]) if total_col < len(r) else None
            if val is not None:
                items[it] = val
            if mat_cols is not None and all(i < len(r) for i in mat_cols):
                st, mt, lt = (_to_float(r[mat_cols[0]]), _to_float(r[mat_cols[1]]), _to_float(r[mat_cols[2]]))
                if None not in (st, mt, lt):
                    mat[it] = (st, mt, lt)
    return date, institution, items, mat


def extract_fields(items, mat=None, mode="bonds"):
    """tot_asset, total_liab, equity, st_borrow, lt_borrow, bonds.
    mode='bonds': LP = item 68 (deuda emitida), CP = total_liab - LP (homogéneo con el panel).
    mode='maturity': usa columnas Short/Medium/Long-term del item 95 (vencimiento residual):
        CP = Short-term, LP = Medium-term + Long-term."""
    mat = mat or {}
    ta = items.get(ITEM_TOTAL_ASSET)
    tl = items.get(ITEM_TOTAL_LIAB)
    eq = items.get(ITEM_EQUITY)
    bonds = sum(items.get(i, 0.0) for i in ITEMS_BONDS)
    out = {"tot_asset": ta, "total_liab": tl, "equity": eq, "bonds": bonds,
           "st_borrow": None, "lt_borrow": None}
    if mode == "maturity" and ITEM_TOTAL_LIAB in mat:
        st, mt, lt = mat[ITEM_TOTAL_LIAB]
        out["st_borrow"] = st
        out["lt_borrow"] = mt + lt
    elif tl is not None:                       # bonds-vs-rest
        out["lt_borrow"] = bonds
        out["st_borrow"] = tl - bonds
    return out


if __name__ == "__main__":
    import sys, glob, os
    d = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ba900"
    print(f"{'code':>8} {'bank':32} {'asset':>16} {'liab':>16} {'equity':>14} {'bonds':>14} idOK")
    for p in sorted(glob.glob(os.path.join(d, "*.csv"))):
        code = os.path.splitext(os.path.basename(p))[0]
        if code == "TOTAL":
            continue
        date, inst, items, mat = parse_ba900_csv(p)
        f = extract_fields(items, mat)
        ta, tl, eq = f["tot_asset"], f["total_liab"], f["equity"]
        idok = (ta is not None and tl is not None and eq is not None
                and abs(ta - (tl + eq)) < 1.0)
        print(f"{code:>8} {(inst or '')[:32]:32} {ta or 0:16.0f} {tl or 0:16.0f} "
              f"{eq or 0:14.0f} {f['bonds']:14.0f} {idok}")