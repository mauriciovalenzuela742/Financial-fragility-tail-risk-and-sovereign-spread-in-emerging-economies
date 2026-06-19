"""
download_sbs.py — Descarga masiva de los boletines SBS (Banca Múltiple) por período.

Hallazgo clave (corrige la confusión del F12):
    La descarga NO pasa por los beacons `collect?v=2&tid=...` de Google Analytics
    (eso es solo tracking; por eso veías 2 "cargas útiles" irrelevantes). El archivo
    real es un GET estático directo al servidor de estadística de la SBS:

        https://intranet2.sbs.gob.pe/estadistica/financiera/{AÑO}/{MesEspañol}/{CODE}-{mm}{yyyy}.XLS

    Patrón verificado en el mismo host:
        .../2025/Enero/B-2201-en2025.XLS      (objetivo de este proyecto)
        .../2026/Febrero/B-2201-fe2026.XLS
        .../2020/Diciembre/BM-00101-di2020.XLS
        .../2001/Julio/B-2101-jl2001.DOC

    No hay API REST: se itera período a período y se verifica HTTP 200.

Uso:
    python download_sbs.py --code B-2201 --start 2010 --end 2026 --out ./sbs_xlsx
    # luego:  python extract_peru.py --dir ./sbs_xlsx --start 2010 --end 2026
"""
import argparse
import os
import time
import sys

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Mes -> (nombre de carpeta en el path, abreviatura de 2 letras del nombre de archivo).
# Confirmadas por ejemplos reales: en, fe, jl, di. El resto sigue el esquema SBS estándar.
MESES = {
    1:  ("Enero",      "en"),
    2:  ("Febrero",    "fe"),
    3:  ("Marzo",      "ma"),
    4:  ("Abril",      "ab"),
    5:  ("Mayo",       "my"),   # 'my' para distinguir de marzo 'ma'
    6:  ("Junio",      "jn"),   # 'jn' para distinguir de julio 'jl'
    7:  ("Julio",      "jl"),
    8:  ("Agosto",     "ag"),
    9:  ("Setiembre", "se"),
    10: ("Octubre",    "oc"),
    11: ("Noviembre",  "no"),
    12: ("Diciembre",  "di"),
}

HOSTS = ["intranet2.sbs.gob.pe", "intranet1.sbs.gob.pe"]  # fallback al segundo si el primero falla
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def build_url(host, code, year, month, ext):
    mes_dir, abbr = MESES[month]
    fname = f"{code}-{abbr}{year}.{ext}"
    url = f"https://{host}/estadistica/financiera/{year}/{mes_dir}/{fname}"
    return url, fname


def try_download(code, year, month, ext, out_dir, session, timeout=30):
    """Devuelve (status, ruta_o_url). status ∈ {'ok','skip','404','err'}."""
    _, abbr = MESES[month][0], MESES[month][1]
    _, fname = build_url(HOSTS[0], code, year, month, ext)
    dest = os.path.join(out_dir, fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return "skip", dest

    for host in HOSTS:
        url, _ = build_url(host, code, year, month, ext)
        try:
            r = session.get(url, headers=HEADERS, timeout=timeout, verify=False, stream=True)
        except requests.RequestException:
            continue
        ct = r.headers.get("Content-Type", "").lower()
        # Un 200 con HTML suele ser una página de error camuflada -> rechazar.
        if r.status_code == 200 and "text/html" not in ct:
            with open(dest, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            if os.path.getsize(dest) > 1024:
                return "ok", dest
            os.remove(dest)  # archivo basura
        r.close()
    return "404", url


def main():
    ap = argparse.ArgumentParser(description="Descarga boletines SBS por período.")
    ap.add_argument("--code", default="B-2201", help="código de reporte SBS (p.ej. B-2201)")
    ap.add_argument("--start", type=int, default=2010)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--ext", default="XLS")
    ap.add_argument("--out", default="./sbs_xlsx")
    ap.add_argument("--pause", type=float, default=0.4, help="segundos entre descargas")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    session = requests.Session()
    got, missing = [], []

    for year in range(a.start, a.end + 1):
        for month in range(1, 13):
            status, ref = try_download(a.code, year, month, a.ext, a.out, session)
            tag = f"{year}-{month:02d}"
            if status in ("ok", "skip"):
                got.append(tag)
                print(f"[{status:4}] {tag}  {os.path.basename(ref)}")
            else:
                missing.append(tag)
                print(f"[MISS] {tag}  {ref}", file=sys.stderr)
            time.sleep(a.pause)

    print(f"\nResumen: {len(got)} descargados/presentes | {len(missing)} faltantes")
    if missing:
        print("Faltantes (revisar abreviatura de mes o disponibilidad):")
        print("  " + ", ".join(missing))


if __name__ == "__main__":
    main()