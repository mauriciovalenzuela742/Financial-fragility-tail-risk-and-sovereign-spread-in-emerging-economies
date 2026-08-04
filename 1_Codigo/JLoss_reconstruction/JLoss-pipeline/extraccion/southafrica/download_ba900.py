"""
download_ba900.py — Descarga los retornos BA900 del SARB vía su API REST.

API (custom.resbank.co.za/SarbWebApi/SarbData/IFData):
  GetInstitutions/BA900/{YYYY-MM-01}              -> lista [{Id, Name, ...}] del mes
  GetInstitutionData/BA900/{YYYY-MM-01}/{code}    -> [{..., "XMLData": "<SARBForms...>"}]

Guarda el XMLData de cada banco-mes como {code}_{YYYY-MM-01}.xml (lo consume extract_southafrica).
Por defecto solo el núcleo (6 grandes listados); --all baja todas las instituciones del mes.

Uso:
    python download_ba900.py --start 2008 --end 2026 --out ./ba900_raw
"""
import argparse, calendar, datetime as dt, json, os, time
import requests
from extract_southafrica import BANKMAP

API = "https://custom.resbank.co.za/SarbWebApi/SarbData/IFData"
UA = {"User-Agent": "Mozilla/5.0 (research)", "Accept": "application/json"}
CORE_CODES = {m["code"] for m in BANKMAP.values()}
API_MIN_DATE = dt.date(2017, 5, 1)  # earliest period with data in SARB API


def months(start_year, end_year):
    today = dt.date.today()
    for y in range(start_year, end_year + 1):
        for mo in range(1, 13):
            d = dt.date(y, mo, 1)
            if d < API_MIN_DATE or d > today:
                continue
            yield d.isoformat()


def get_codes(period, only_core):
    if only_core:
        return sorted(CORE_CODES)
    try:
        r = requests.get(f"{API}/GetInstitutions/BA900/{period}", headers=UA, timeout=60)
        r.raise_for_status()
        return [x["Id"] for x in r.json() if str(x.get("Id", "")).isdigit()]
    except Exception as e:
        print(f"  [err] GetInstitutions {period}: {e}")
        return []


def download_one(period, code, out_dir, verbose=False):
    url = f"{API}/GetInstitutionData/BA900/{period}/{code}"
    try:
        r = requests.get(url, headers=UA, timeout=120)
    except Exception as e:
        print(f"  [err] {code} {period}: {e}"); return False
    if r.status_code != 200:
        print(f"  [err] {code} {period}: HTTP {r.status_code}")
        return False
    try:
        data = r.json()
    except json.JSONDecodeError:
        print(f"  [err] {code} {period}: respuesta no es JSON — {r.text[:120]!r}")
        return False
    if not data:
        if verbose:
            print(f"  [skip] {code} {period}: lista vacía")
        return False
    if not data[0].get("XMLData"):
        if verbose:
            print(f"  [skip] {code} {period}: sin XMLData — claves={list(data[0].keys())}")
        return False
    dest = os.path.join(out_dir, f"{code}_{period}.xml")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(data[0]["XMLData"])
    return True


def run(start, end, out_dir, only_core=True, verbose=False):
    os.makedirs(out_dir, exist_ok=True)
    for period in months(start, end):
        codes = get_codes(period, only_core)
        n = sum(download_one(period, c, out_dir, verbose=verbose) for c in codes)
        print(f"  [{period}] {n}/{len(codes)} bancos")
        time.sleep(0.2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2017)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--out", default="./ba900_raw")
    ap.add_argument("--all", action="store_true", help="todas las instituciones (no solo el núcleo)")
    ap.add_argument("--verbose", "-v", action="store_true", help="mostrar detalle de cada fallo")
    a = ap.parse_args()
    run(a.start, a.end, a.out, only_core=not a.all, verbose=a.verbose)