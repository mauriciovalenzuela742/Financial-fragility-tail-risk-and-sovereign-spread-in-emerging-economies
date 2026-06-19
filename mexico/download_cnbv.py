"""
download_cnbv.py — Descarga masiva de los Boletines Estadísticos de Banca Múltiple (CNBV).

URL estática directa (verificada en portafolioinfo.cnbv.gob.mx):
    https://portafolioinfo.cnbv.gob.mx/PortafolioInformacion/BE_BM_{YYYY}{MM}.{ext}
Ejemplos reales: BE_BM_201302.xls, BE_BM_201505.xls, BE_BM_202511.xlsx, BE_BM_201802.pdf
Sin carpetas de mes ni API: se itera período a período. El Excel es .xls (histórico) o
.xlsx (reciente); se intenta .xlsx y luego .xls, y se verifica HTTP 200 (no HTML de error).

Uso:
    python download_cnbv.py --start 2010 --end 2026 --out ./cnbv_xls
    python extract_mexico.py --dir ./cnbv_xls --start 2010 --end 2026 --out ./out_mexico
"""
import argparse
import os
import sys
import time

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://portafolioinfo.cnbv.gob.mx/PortafolioInformacion"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
EXTS = ("xlsx", "xlsm", "xls") # recientes en xlsx, históricos en xls, # algunos vienen con macros


def try_download(year, month, out_dir, session, timeout=60, retries=4):
    stem = f"BE_BM_{year}{month:02d}"
    for ext in EXTS:
        dest = os.path.join(out_dir, f"{stem}.{ext}")
        if os.path.exists(dest) and os.path.getsize(dest) > 4096:
            return "skip", dest
    for ext in EXTS:
        url = f"{BASE}/{stem}.{ext}"
        for attempt in range(retries):
            try:
                r = session.get(url, headers=HEADERS, timeout=timeout,
                                verify=False, stream=True)
            except requests.RequestException:
                time.sleep(2 ** attempt)          # backoff ante caída de conexión
                continue
            ct = r.headers.get("Content-Type", "").lower()
            if r.status_code == 200 and "text/html" not in ct:
                dest = os.path.join(out_dir, f"{stem}.{ext}")
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                r.close()
                if os.path.getsize(dest) > 4096:
                    return "ok", dest
                os.remove(dest)
            elif r.status_code in (429, 500, 502, 503, 504):
                r.close()
                time.sleep(2 ** attempt)          # backoff ante throttling
                continue
            r.close()
            break                                  # 404 real -> no insistir con este ext
    return "404", f"{BASE}/{stem}.(xlsx|xls)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2010)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--out", default="./cnbv_xls")
    ap.add_argument("--pause", type=float, default=0.4)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    session = requests.Session()
    got, missing = [], []
    for year in range(a.start, a.end + 1):
        for month in range(1, 13):
            status, ref = try_download(year, month, a.out, session)
            tag = f"{year}-{month:02d}"
            if status in ("ok", "skip"):
                got.append(tag)
                print(f"[{status:4}] {tag}  {os.path.basename(ref)}")
            else:
                missing.append(tag)
                print(f"[MISS] {tag}  {ref}", file=sys.stderr)
            time.sleep(a.pause)

    print(f"\nResumen: {len(got)} presentes | {len(missing)} faltantes")
    if missing:
        print("Faltantes:", ", ".join(missing))


if __name__ == "__main__":
    main()