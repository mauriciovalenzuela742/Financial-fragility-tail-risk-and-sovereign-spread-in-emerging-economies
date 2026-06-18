"""
build_colombia_long.py — Recorre las carpetas por banco con los XBRL descargados de la SFC
(download_sfc_xbrl.py) y construye UN solo long-format `colombia_long.csv` para extract_colombia.py.

Flujo completo de Colombia:
    1) python download_sfc_xbrl.py --years 2015-2025      # baja los XBRL a <banco>/<banco>_individual_YYYY-MM.xbrl
    2) python build_colombia_long.py --root .             # parsea TODO -> colombia_long.csv
    3) python extract_colombia.py --file colombia_long.csv --start 2015 --end 2026

Usa el parser exacto de parse_sfc_xbrl.py (mapeo de conceptos XBRL, total sin dimensión, bonos-vs-resto)
y el mapa de carpetas->banco de download_sfc_xbrl.py.
"""
import os, re, glob, argparse
import numpy as np
import pandas as pd
from parse_sfc_xbrl import _iter_xbrl, parse_instance, to_long, level_of_rounding, scale_to_miles
from download_sfc_xbrl import BANK_FOLDERS

# Forzar la escala de un banco si el auto-detector (LevelOfRoundingUsedInFinancialStatements)
# fallara. Valores: 'miles' | 'millones' | 'pesos'. Ej: {"bancosantander": "millones"}
SCALE_OVERRIDE = {}


def fix_within_bank_scale(df):
    """Red de seguridad: corrige períodos cuya escala difiere ~1000x de la magnitud DOMINANTE
    del propio banco (p.ej. archivos en pesos mezclados con archivos en miles). Usa 'Total activos'
    para detectar, y aplica el factor a TODAS las cuentas de ese (banco, período)."""
    ta = df[(df["account"] == "Total activos") & (df["value"] > 0)][["bank", "period", "value"]].copy()
    if ta.empty:
        return df, pd.DataFrame()
    ta["mag"] = np.floor(np.log10(ta["value"]))
    dom = ta.groupby("bank")["mag"].agg(lambda s: s.mode().iloc[0]).rename("dom")
    ta = ta.merge(dom, on="bank")
    diff = ta["dom"] - ta["mag"]
    ta["factor"] = np.where(diff >= 2.5, 1000.0, np.where(diff <= -2.5, 0.001, 1.0))
    corr = ta.loc[ta["factor"] != 1.0, ["bank", "period", "factor"]]
    if len(corr):
        df = df.merge(corr, on=["bank", "period"], how="left")
        df["factor"] = df["factor"].fillna(1.0)
        df["value"] = df["value"] * df["factor"]
        df = df.drop(columns="factor")
    return df, corr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="carpeta raíz con las subcarpetas por banco")
    ap.add_argument("--out", default="colombia_long.csv")
    a = ap.parse_args()

    frames = []
    scale_log = {}
    for folder, keys in BANK_FOLDERS.items():
        bank_label = keys[0]   # nombre representativo del banco (lo reconoce extract_colombia.BANKMAP)
        d = os.path.join(a.root, folder)
        if not os.path.isdir(d):
            continue
        files = []
        for ext in ("*.xbrl", "*.zip", "*.xml"):
            files += glob.glob(os.path.join(d, ext))
        for fpath in sorted(files):
            try:
                facts, level = [], ""
                for _, content in _iter_xbrl(fpath):
                    facts += parse_instance(content)
                    if not level:
                        level = level_of_rounding(content)
                df = to_long(facts, bank_label)
                # GUARDIA: el año del nombre del archivo debe aparecer en el contenido.
                # (La SFC devuelve la última transmisión para años sin NIIF -> archivos mal etiquetados.)
                m = re.search(r"_(\d{4})-(\d{2})", os.path.basename(fpath))
                if m and len(df):
                    fname_year = m.group(1)
                    if not df["period"].astype(str).str.startswith(fname_year).any():
                        print(f"  OMITIDO (nombre {fname_year} no coincide con el contenido): "
                              f"{os.path.basename(fpath)}")
                        continue
                if len(df):
                    factor = scale_to_miles(level, override=SCALE_OVERRIDE.get(folder))
                    df["value"] = df["value"] * factor          # -> MILES de COP (escala común)
                    scale_log[folder] = (factor, level[:38])
                    frames.append(df)
            except Exception as e:
                print(f"  aviso: no pude parsear {fpath}: {e}")

    if not frames:
        print("No encontré XBRL parseables. ¿Corriste download_sfc_niif.py y están las carpetas?")
        return
    out = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["bank", "account", "period"])
    out, corr = fix_within_bank_scale(out)
    out.to_csv(a.out, index=False)
    print(f"{a.out}: {len(out)} filas | bancos={out['bank'].nunique()} | períodos={out['period'].nunique()}")
    print("escala detectada por banco (factor a MILES de COP; revisa los reescalados):")
    for folder, (factor, lvl) in sorted(scale_log.items()):
        flag = "" if factor == 1.0 else "  <-- reescalado (texto)"
        print(f"  {folder:22s} x{factor:<8g}{flag}  [{lvl}]")
    if len(corr):
        print(f"\nred de seguridad intra-banco: corregí {len(corr)} (banco,período) con salto de escala ~1000x:")
        print(corr.to_string(index=False))
    print(f"\nAhora: python extract_colombia.py --file {a.out} --start 2015 --end 2026")


if __name__ == "__main__":
    main()