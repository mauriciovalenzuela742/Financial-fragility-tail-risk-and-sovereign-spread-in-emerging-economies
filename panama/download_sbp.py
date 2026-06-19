"""
download_sbp.py — Descarga reportes individuales por banco de la SBP (Panamá).

URLs directas por plantilla (el filtro web es AJAX y no sirve por GET):
  .../reportes_estadisticos/{año}/{mm}/balance_individual_por_banco/RE-BALANCE-BANCO-en-{slug}.xlsx
  .../reportes_estadisticos/{año}/{mm}/estado_de_resultado_individual_por_banco/RE-ESTADO-BANCO-en-{slug}.xlsx

El archivo de un mes trae el año completo -> se prueba 12->01 y se baja el mes más reciente
que exista (cubre el año en curso, p.ej. 2026 sólo hasta abril). El régimen moderno NO cubre
años muy antiguos (2010 da 404); arranca el rango donde haya datos.

Slugs en sbp_parse.SLUGS (fuente única). Faltan por verificar: bac_panama, global_bank, aliado.

Uso:
    python download_sbp.py --years 2018-2026 --out ./sbp_raw
"""
import argparse, os, time, requests
from sbp_parse import SLUGS

BASE = "https://www.superbancos.gob.pa/documentos/financiera_y_estadistica/reportes_estadisticos"
UA = {"User-Agent": "Mozilla/5.0 (research)"}
FOLDERS = {"balance": ("balance_individual_por_banco", "RE-BALANCE-BANCO-en-"),
           "estado":  ("estado_de_resultado_individual_por_banco", "RE-ESTADO-BANCO-en-")}


def try_download(section, key, slug, year, out_dir):
    folder, prefix = FOLDERS[section]
    fn = f"{prefix}{slug}.xlsx"
    # Orden: Dic-mes primero (año completo en años recientes y de transición),
    # luego sin-mes (años viejos <=2018), luego meses descendentes (año en curso sin Dic).
    # Evita quedarse con el archivo sin-mes parcial en años de transición (2019 congelado en jul).
    urls = [f"{BASE}/{year}/12/{folder}/{fn}", f"{BASE}/{year}/{folder}/{fn}"]
    urls += [f"{BASE}/{year}/{mm:02d}/{folder}/{fn}" for mm in range(11, 0, -1)]
    for url in urls:
        try:
            r = requests.get(url, headers=UA, timeout=120)
        except Exception as e:
            print(f"  [err] {key} {section} {year}: {e}"); continue
        if r.status_code == 200 and r.content[:4] == b"PK\x03\x04":
            dest = os.path.join(out_dir, f"{section}_{key}_{year}.xlsx")
            with open(dest, "wb") as fh:
                fh.write(r.content)
            tag = url.split(f"/{year}/", 1)[1].split("/")[0]
            print(f"  [ok] {dest} ({len(r.content)} bytes, {slug}, {tag})")
            return True
        time.sleep(0.12)
    return False


def run(years, out_dir, only=None):
    os.makedirs(out_dir, exist_ok=True)
    for year in years:
        for key, slugs in SLUGS.items():
            if only and key not in only:
                continue
            cand = slugs if isinstance(slugs, list) else [slugs]
            for section in FOLDERS:
                if not any(try_download(section, key, s, year, out_dir) for s in cand):
                    print(f"  [404] {key} {section} {year} (sin datos ese año)")


def parse_years(spec):
    if "-" in spec:
        a, b = spec.split("-"); return list(range(int(a), int(b) + 1))
    return [int(x) for x in spec.split(",")]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2018-2026")
    ap.add_argument("--out", default="./sbp_raw")
    ap.add_argument("--banks", default=None, help="keys separadas por coma (ej. bac_panama)")
    a = ap.parse_args()
    only = set(a.banks.split(",")) if a.banks else None
    run(parse_years(a.years), a.out, only=only)