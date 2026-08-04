"""
parse_sfc_xbrl.py — Convierte un Estado de Situación Financiera en XBRL (descargado de la SFC,
formato INDIVIDUAL/SEPARADO) a long-format (bank, account, period, value) para extract_colombia.py.

La instancia trae la taxonomía IFRS (conceptos en inglés) + extensiones SFC. Este parser:
  - lee contextos (NIT + fecha) y detecta cuáles tienen DIMENSIONES (miembros) para quedarse con el
    TOTAL sin dimensión de cada línea (evita tomar un desglose en vez del total);
  - mapea por nombre EXACTO de concepto (no subcadena) solo las líneas del balance que necesitamos
    bajo el criterio bonos-vs-resto; emite un CSV long-format con etiquetas en español que
    extract_colombia.py ya reconoce.

Criterio del profesor (bonos vs resto): LP = deuda emitida (bonos + notas/debentures + subordinada).
Se EXCLUYEN a propósito el papel comercial y los certificados de depósito (corto plazo -> "resto").

Uso:
    python parse_sfc_xbrl.py --file ./bancolombia_individual_2025-12.xbrl --bank "BANCOLOMBIA S.A." --list
    python parse_sfc_xbrl.py --file ./bancolombia_individual_2025-12.xbrl --bank "BANCOLOMBIA S.A." --out bancolombia_long.csv
"""
import argparse, glob, os, zipfile
import xml.etree.ElementTree as ET
import pandas as pd

# Concepto XBRL EXACTO -> etiqueta de salida (que extract_colombia.py reconoce)
CONCEPT_MAP = {
    "Assets": "Total activos",
    "Equity": "Total patrimonio",
    "Liabilities": "Total pasivos",
    "BondsIssued": "Bonos emitidos",
    "NotesAndDebenturesIssued": "Notas y debentures emitidos",
    "SubordinatedLiabilities": "Obligaciones subordinadas",
    # extensiones SFC (por si el banco etiqueta con estas en vez de las IFRS):
    "TitulosEmitidos": "Titulos emitidos",
    "BonosTitulosCirculacion": "Bonos y titulos en circulacion",
}
SKIP = {"context", "unit", "schemaRef", "linkbaseRef", "roleRef", "arcroleRef"}


def _iter_xbrl(path):
    if path.lower().endswith(".zip"):
        z = zipfile.ZipFile(path)
        for n in z.namelist():
            if n.lower().endswith((".xbrl", ".xml")) and "taxonomy" not in n.lower():
                yield n, z.read(n)
    else:
        with open(path, "rb") as f:
            yield os.path.basename(path), f.read()


def parse_instance(content):
    root = ET.fromstring(content)
    ctx = {}  # id -> (nit, period, is_dimensional)
    for c in root.iter():
        if c.tag.split("}")[-1] != "context":
            continue
        cid = c.get("id"); nit = per = None; dim = False
        for e in c.iter():
            t = e.tag.split("}")[-1]
            if t == "identifier" and e.text:
                nit = e.text.strip()
            elif t in ("instant", "endDate") and e.text:
                per = e.text.strip()
            elif t in ("explicitMember", "typedMember"):
                dim = True
        ctx[cid] = (nit, per, dim)
    facts = []
    for el in root.iter():
        cref = el.get("contextRef")
        if cref is None:
            continue
        local = el.tag.split("}")[-1]
        if local in SKIP or local not in CONCEPT_MAP:
            continue
        val = (el.text or "").strip()
        if val == "":
            continue
        nit, per, dim = ctx.get(cref, (None, None, False))
        facts.append({"concept": local, "value": val, "nit": nit, "period": per, "dim": dim})
    return facts


def list_all_concepts(content):
    root = ET.fromstring(content)
    out = set()
    for el in root.iter():
        if el.get("contextRef") is not None:
            out.add(el.tag.split("}")[-1])
    return out


def to_long(facts, bankname):
    """Por (etiqueta, período): preferir el fact SIN dimensión (el total); si no hay, max abs."""
    best = {}
    for f in facts:
        label = CONCEPT_MAP[f["concept"]]
        per = (f["period"] or "")[:10]
        try:
            v = float(f["value"])
        except ValueError:
            continue
        key = (label, per)
        cur = best.get(key)
        cand = (0 if f["dim"] else 1, abs(v))   # no-dim gana; luego mayor magnitud
        if cur is None or cand > cur[0]:
            best[key] = (cand, v)
    rows = [{"bank": bankname, "account": lab, "period": per, "value": val}
            for (lab, per), (_, val) in best.items()]
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="instancia XBRL (.xbrl/.xml/.zip)")
    ap.add_argument("--bank", help="nombre de la entidad (para el long-format)")
    ap.add_argument("--out", default="colombia_long.csv")
    ap.add_argument("--list", action="store_true", help="solo listar conceptos candidatos del balance")
    a = ap.parse_args()

    contents = [c for _, c in _iter_xbrl(a.file)]

    if a.list:
        allc = set()
        for c in contents:
            allc |= list_all_concepts(c)
        KEY = ["asset", "activ", "equity", "patrimon", "liabilit", "pasiv", "debt", "deuda",
               "bond", "bono", "issued", "emitid", "subordinat", "subordinad", "deposit", "titulo"]
        print(f"conceptos distintos: {len(allc)}\n--- candidatos (balance) ---")
        for c in sorted(allc):
            if any(k in c.lower() for k in KEY):
                print("  ", c)
        print("\n(los que el parser ya mapea:", list(CONCEPT_MAP.keys()), ")")
        return

    facts = []
    for c in contents:
        facts += parse_instance(c)
    df = to_long(facts, a.bank or "ENTIDAD")
    df.to_csv(a.out, index=False)
    print(f"guardado {a.out}: {len(df)} filas")
    if len(df):
        print(df.to_string(index=False))
    print("\nConcaténalo con los de otros bancos y corre: python extract_colombia.py --file <concat>.csv")


if __name__ == "__main__":
    main()


# --- Escala de presentación (miles/millones/pesos) -------------------------------------------
LEVEL_CONCEPT = "LevelOfRoundingUsedInFinancialStatements"

def level_of_rounding(content):
    import xml.etree.ElementTree as _ET
    root = _ET.fromstring(content)
    for el in root.iter():
        if el.tag.split("}")[-1] == LEVEL_CONCEPT and (el.text or "").strip():
            return el.text.strip()
    return ""

def scale_to_miles(level_text, override=None):
    """Factor para llevar los valores del archivo a MILES de COP (norma SFC).
    override: 'miles'|'millones'|'pesos' fuerza la escala (gana sobre el texto)."""
    if override:
        return {"miles": 1.0, "millones": 1000.0, "pesos": 0.001}.get(override, 1.0)
    t = (level_text or "").strip().upper()
    if t and len(t) < 40:                      # declaración corta y explícita
        if "MILLON" in t:  return 1000.0       # millones -> miles
        if "MILE" in t or t.startswith("MIL"): return 1.0
        if "PESO" in t and "MILLON" not in t:  return 0.001   # pesos -> miles
    return 1.0                                  # boilerplate/ausente -> asumir miles
