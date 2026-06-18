"""
download_sfc_niif.py — Descarga masiva de XBRL Individual/Separado desde la app JSF/PrimeFaces de
Envíos NIIF de la Superintendencia Financiera de Colombia (SFC), en PURO requests (sin navegador).

Protocolo (descubierto del tráfico real):
  App: https://www.superfinanciera.gov.co/SuperfinancieraNIIF/generic/SendingNiifAllList2.xhtml
  1) GET la página -> cookie de sesión + javax.faces.ViewState inicial.
  2) POST búsqueda (PrimeFaces partial/ajax) con:
        entityType_input=1 (Establecimiento Bancario), reportType_input=intermedio|cierre,
        cutOffYear_input=YYYY, cutOffMonth_input=MM
     -> <partial-response> con la tabla (filas, nombre, disponibilidad XBRL I-I/I-C).
  3) Por cada fila con XBRL Individual disponible, POST el AJAX del diálogo (sus parámetros s/p/u
     se leen del onclick del enlace) -> trae <a href="downloadServlet.do?path=BASE64">.
  4) GET downloadServlet.do?path=BASE64 -> el archivo XBRL.

Guarda en  <out>/<carpeta_banco>/<carpeta_banco>_individual_<YYYY>-<MM>.xbrl  (reanudable).

Requisitos:  pip install requests
Uso:
    python download_sfc_niif.py --probe                 # 1 búsqueda de prueba (2025-03), no descarga
    python download_sfc_niif.py --years 2025            # un año
    python download_sfc_niif.py --years 2015-2025       # corrida completa
"""
import os, re, sys, time, glob, html, argparse, logging
import requests

from download_sfc_xbrl import BANK_FOLDERS, match_folder, parse_years

BASE = "https://www.superfinanciera.gov.co/SuperfinancieraNIIF/generic/"
URL = BASE + "SendingNiifAllList2.xhtml"

ENTITY_TYPE_INPUT = "1"            # 1 = Establecimiento Bancario
SEARCH_SOURCE = "j_idt57"         # botón Buscar (id JSF; override con --search-source)
# tipo de reporte -> (valor de reportType_input, etiqueta, meses)
REPORTTYPES = {
    "intermedio": ("intermedio", "I-I", ["03", "06", "09"]),
    "cierre":     ("cierre",     "I-C", ["12"]),
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36")

_VS_HTML = re.compile(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"')
_VS_PART = re.compile(r'<update id="[^"]*ViewState[^"]*"><!\[CDATA\[(.*?)\]\]></update>', re.S)
_CDATA_RESULT = re.compile(r'<update id="resultForm"><!\[CDATA\[(.*?)\]\]></update>', re.S)
_DL_PATH = re.compile(r'downloadServlet\.do\?path=([^"&]+)')


def _viewstate(text):
    m = _VS_PART.search(text) or _VS_HTML.search(text)
    return m.group(1) if m else None


class SFC:
    def __init__(self, search_source=SEARCH_SOURCE):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA})
        self.vs = None
        self.search_source = search_source

    def init(self):
        r = self.s.get(URL, timeout=60)
        r.raise_for_status()
        self.vs = _viewstate(r.text)
        # intentar autodetectar el id del botón Buscar
        m = re.search(r'id="([^"]+)"[^>]*>\s*(?:<[^>]+>\s*)*Buscar', r.text)
        if m:
            self.search_source = m.group(1)
        if not self.vs:
            logging.warning("no encontré ViewState inicial; el portal pudo cambiar.")
        return self

    def _post(self, data):
        headers = {"Faces-Request": "partial/ajax", "X-Requested-With": "XMLHttpRequest",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Origin": "https://www.superfinanciera.gov.co", "Referer": URL}
        r = self.s.post(URL, data=data, headers=headers, timeout=90)
        r.raise_for_status()
        nv = _viewstate(r.text)
        if nv:
            self.vs = nv
        return r.text

    def search(self, year, month, reporttype_value):
        data = {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": self.search_source,
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "resultForm",
            self.search_source: self.search_source,
            "searchForm": "searchForm",
            "entityType_focus": "", "entityType_input": ENTITY_TYPE_INPUT,
            "entityTypeCode_input": "", "entityTypeCode_hinput": "",
            "reportType_focus": "", "reportType_input": reporttype_value,
            "cutOffYear_focus": "", "cutOffYear_input": str(year),
            "cutOffMonth_focus": "", "cutOffMonth_input": str(month),
            "j_idt19_collapsed": "false",
            "javax.faces.ViewState": self.vs or "",
        }
        return self._post(data)

    def open_dialog(self, s, p, u):
        data = {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": s,
            "javax.faces.partial.execute": p,
            "javax.faces.partial.render": u,
            s: s, "resultForm": "resultForm",
            "javax.faces.ViewState": self.vs or "",
        }
        return self._post(data)

    def download(self, path, dest_base):
        url = BASE + "downloadServlet.do?path=" + path
        r = self.s.get(url, timeout=180)
        r.raise_for_status()
        content = r.content
        ext = ".zip" if content[:4] == b"PK\x03\x04" else ".xbrl"
        dest = dest_base + ext
        with open(dest, "wb") as f:
            f.write(content)
        return dest, len(content)


def parse_rows(search_xml):
    """Devuelve [(data_ri, nombre, (s,p,u) | None)] por fila; (s,p,u)=None si XBRL Individual no disponible."""
    m = _CDATA_RESULT.search(search_xml)
    body = m.group(1) if m else search_xml
    # cortar en filas por data-ri
    parts = re.split(r'(data-ri="\d+")', body)
    rows = []
    for i in range(1, len(parts), 2):
        ri = re.search(r'\d+', parts[i]).group(0)
        chunk = parts[i + 1] if i + 1 < len(parts) else ""
        mn = re.search(rf'id="sendingNIIFTable:{ri}:code">([^<]+)<', chunk)
        name = html.unescape(mn.group(1).strip()) if mn else ""
        # enlace XBRL Individual disponible: <a ... onclick="PrimeFaces.ab({s:..,p:..,u:..})" ...PF('XBRLDialog(II|IC)')
        spu = None
        for a in re.finditer(r'onclick="PrimeFaces\.ab\(\{s:&quot;([^&]+)&quot;,f:&quot;resultForm&quot;,'
                             r'p:&quot;([^&]+)&quot;,u:&quot;([^&]+)&quot;[^X]*?(XBRLDialog(?:II|IC))',
                             chunk):
            spu = (html.unescape(a.group(1)), html.unescape(a.group(2)), html.unescape(a.group(3)))
            break
        rows.append((ri, name, spu))
    return rows


def download_path_from_dialog(dialog_xml):
    m = _DL_PATH.search(dialog_xml)
    return m.group(1) if m else None


def run(years, out_root, probe=False, search_source=SEARCH_SOURCE, limit=None, report_type="both"):
    sfc = SFC(search_source=search_source).init()
    logging.info(f"sesión iniciada. ViewState={'ok' if sfc.vs else 'NO'} | buscar_id={sfc.search_source}")
    n_ok = n_skip = n_fail = 0
    years = [years[0]] if probe else years
    if probe:
        rt_list = ["intermedio"]
    elif report_type == "both":
        rt_list = list(REPORTTYPES)
    else:
        rt_list = [report_type]
    logging.info(f"tipos de reporte a descargar: {rt_list}")
    for year in years:
        for rt in rt_list:
            rt_value, tag, months = REPORTTYPES[rt]
            for mm in (["03"] if probe else months):
                logging.info(f"=== buscar {year}-{mm} ({rt}) ===")
                try:
                    xml = sfc.search(year, mm, rt_value)
                except Exception as e:
                    logging.error(f"búsqueda falló {year}-{mm}: {e}"); continue
                rows = parse_rows(xml)
                avail = [r for r in rows if r[2]]
                logging.info(f"  filas={len(rows)} con XBRL Individual disponible={len(avail)}")
                if probe:
                    for ri, name, spu in rows[:8]:
                        logging.info(f"    ri={ri} '{name[:40]}' folder={match_folder(name)} xbrl={'sí' if spu else 'no'}")
                    if avail:
                        ri, name, spu = avail[0]
                        dlg = sfc.open_dialog(*spu)
                        path = download_path_from_dialog(dlg)
                        logging.info(f"  PRUEBA diálogo '{name[:30]}': path={'OK' if path else 'NO'} -> {str(path)[:60]}")
                    return
                count = 0
                for ri, name, spu in avail:
                    folder = match_folder(name)
                    if not folder:
                        continue
                    dest_dir = os.path.join(out_root, folder); os.makedirs(dest_dir, exist_ok=True)
                    dest_base = os.path.join(dest_dir, f"{folder}_individual_{year}-{mm}")
                    if glob.glob(dest_base + ".*"):
                        n_skip += 1; continue
                    try:
                        dlg = sfc.open_dialog(*spu)
                        path = download_path_from_dialog(dlg)
                        if not path:
                            n_fail += 1; logging.warning(f"  sin link de descarga: {folder} {year}-{mm}"); continue
                        dest, size = sfc.download(path, dest_base)
                        n_ok += 1; count += 1
                        logging.info(f"  OK {folder} {year}-{mm} -> {os.path.basename(dest)} ({size} bytes)")
                        time.sleep(0.4)
                    except Exception as e:
                        n_fail += 1; logging.error(f"  FALLO {folder} {year}-{mm}: {e}")
                    if limit and count >= limit:
                        break
    logging.info(f"FIN. descargados={n_ok} saltados={n_skip} fallidos={n_fail}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="1995-2026")
    ap.add_argument("--out", default=".")
    ap.add_argument("--probe", action="store_true", help="una búsqueda de prueba (2025-03), sin descargar")
    ap.add_argument("--search-source", default=SEARCH_SOURCE, help="id del botón Buscar si difiere")
    ap.add_argument("--report-type", choices=["both", "intermedio", "cierre"], default="both",
                    help="qué descargar: ambos (def.), solo intermedios (03/06/09) o solo cierres (12)")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler("sfc_niif.log", encoding="utf-8"),
                                  logging.StreamHandler()])
    run(parse_years(a.years), a.out, probe=a.probe, search_source=a.search_source,
        limit=a.limit, report_type=a.report_type)


if __name__ == "__main__":
    main()