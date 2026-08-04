"""
download_sfc_xbrl.py — Descarga masiva de XBRL Individual/Separado desde el portal de Envíos NIIF
de la Superintendencia Financiera de Colombia (SFC).

Replica el flujo manual del portal:
  Tipo de entidad = BC-Establecimiento Bancario
  Tipo de reporte = "Informes intermedios"  (meses 03/06/09)  -> columna Individual/Separado Intermedio (I-I)
                  = "Informes de cierre"     (mes  12)         -> columna Individual/Separado Cierre   (I-C)
  Periodo de corte = año (2015..2025) + mes
Para cada banco de la tabla de resultados, baja el XBRL Individual/Separado a:
    <out_root>/<carpeta_banco>/<carpeta_banco>_individual_<YYYY>-<MM>.<ext>
p.ej.  bancodeoccidente/bancodeoccidente_individual_2025-12.xbrl

Reanudable: si el archivo ya existe, lo salta. Robusto: esperas explícitas, try/except por banco,
log a sfc_download.log. Selectores ADAPTATIVOS (por texto de opción) + modo --debug para confirmarlos.

Requisitos (en tu venv):
    pip install selenium requests
    (Chrome instalado; Selenium 4 gestiona el driver automáticamente con Selenium Manager)

Uso típico:
    python download_sfc_xbrl.py --debug                  # 1) confirmar selectores (no descarga)
    python download_sfc_xbrl.py --years 2025 --headful   # 2) prueba un año mirando el navegador
    python download_sfc_xbrl.py --years 2015-2025        # 3) corrida completa (headless)

Si compartes UN link real de un icono XBRL (clic derecho -> copiar enlace), se puede hacer una
versión SOLO con requests (sin navegador), más rápida; este script ya intenta esa vía si el icono
es un <a href> directo, y cae a "clic + esperar descarga" si es un postback JS.
"""
import os, re, sys, time, glob, json, argparse, unicodedata, logging
from urllib.parse import urljoin

PORTAL = ("https://www.superfinanciera.gov.co/publicaciones/10084754/"
          "informes-y-cifrasestados-financieros-de-las-entidades-vigiladas-bajo-niif-10084754/")

# Texto de las opciones del formulario (confirmar/ajustar con --debug si difieren):
TIPO_ENTIDAD_OPT   = "Establecimiento Bancario"   # "BC-Establecimiento Bancario"
REPORTE_INTERMEDIO = "Informes intermedios"
REPORTE_CIERRE     = "Informes de cierre"

# Meses por tipo de reporte (nombre del mes como aparece en el desplegable)
MESES_INTERMEDIO = {"03": "Marzo", "06": "Junio", "09": "Septiembre"}
MESES_CIERRE     = {"12": "Diciembre"}

# carpeta_banco -> subcadenas (mayúsculas, SIN acentos) para identificar al banco en la tabla.
# Coincide con las carpetas que ya tienes creadas. Gana la coincidencia MÁS LARGA (más específica).
BANK_FOLDERS = {
    "banagrario":         ["BANCO AGRARIO", "BANAGRARIO", "AGRARIO"],
    "bancamia":           ["BANCAMIA", "MICROFINANZAS BANCAMIA"],
    "bancien":            ["BANCIEN", "BAN100", "BAN 100"],
    "bancoavvillas":      ["AV VILLAS"],
    "bancobogota":        ["BANCO DE BOGOTA"],
    "bancobtgpactualcol": ["BTG PACTUAL"],
    "bancocajasocial":    ["CAJA SOCIAL"],
    "bancocontactar":     ["CONTACTAR"],
    "bancodavivienda":    ["DAVIVIENDA"],
    "bancodeoccidente":   ["BANCO DE OCCIDENTE", "OCCIDENTE"],
    "bancofalabella":     ["FALABELLA"],
    "bancofinandinabic":  ["FINANDINA"],
    "bancognbsudameris":  ["GNB SUDAMERIS", "SUDAMERIS"],
    "bancojpmorgancol":   ["J.P. MORGAN", "JP MORGAN", "J P MORGAN"],
    "bancolombia":        ["BANCOLOMBIA"],
    "bancomundomujer":    ["MUNDO MUJER"],
    "bancoomeva":         ["COOMEVA", "BANCOOMEVA"],
    "bancoopcentral":     ["COOPCENTRAL"],
    "bancopichincha":     ["BANCO PICHINCHA", "PICHINCHA"],
    "bancopopular":       ["BANCO POPULAR"],
    "bancosantander":     ["SANTANDER"],
    "bancoserfinanza":    ["SERFINANZA"],
    "bancounion":         ["BANCO UNION"],
    "bancow":             ["BANCO W"],
    "bbvacolombia":       ["BILBAO VIZCAYA", "BBVA"],
    "citibankcolombia":   ["CITIBANK"],
    "davibank":           ["DAVIBANK"],
    "itaucolombia":       ["ITAU COLOMBIA", "BANCO ITAU", "ITAU"],
    "lulobank":           ["LULO"],
    "mibanco":            ["MIBANCO", "MICROEMPRESA DE COLOMBIA"],
}


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))


def norm(s):
    return re.sub(r"\s+", " ", strip_accents(s).upper()).strip()


def match_folder(entity_name):
    """Devuelve la carpeta cuyo nombre-substring más LARGO aparece en el nombre de la entidad."""
    u = norm(entity_name)
    best, best_len = None, 0
    for folder, keys in BANK_FOLDERS.items():
        for k in keys:
            ku = norm(k)
            if ku in u and len(ku) > best_len:
                best, best_len = folder, len(ku)
    return best


def parse_years(spec):
    """'2015-2025' o '2025' o '2018,2019' -> lista de años (int)."""
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-"); out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return sorted(set(out))


# ----------------------------------------------------------------------------
# Selenium
# ----------------------------------------------------------------------------
def build_driver(download_dir, headless=True):
    from selenium import webdriver
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,1000")
    opts.add_argument("--no-sandbox")
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True,
    }
    opts.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(90)
    return driver


def _select_by_option_text(driver, contains, set_to=None):
    """Encuentra el <select> que tenga una opción cuyo texto contenga `contains` y la selecciona.
    Si set_to se da, selecciona la opción cuyo texto contenga set_to (sirve para año/mes)."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    target = set_to if set_to is not None else contains
    for sel in driver.find_elements(By.TAG_NAME, "select"):
        texts = [o.text for o in sel.find_elements(By.TAG_NAME, "option")]
        if any(norm(contains) in norm(t) for t in texts):
            s = Select(sel)
            for o in sel.find_elements(By.TAG_NAME, "option"):
                if norm(target) in norm(o.text):
                    s.select_by_visible_text(o.text)
                    return True
    return False


def _click_buscar(driver):
    from selenium.webdriver.common.by import By
    for xp in ("//button[contains(., 'Buscar')]", "//input[@value='Buscar']",
               "//a[contains(., 'Buscar')]", "//*[contains(text(),'Buscar')]"):
        els = driver.find_elements(By.XPATH, xp)
        if els:
            driver.execute_script("arguments[0].click();", els[0]); return True
    return False


def _result_rows(driver):
    from selenium.webdriver.common.by import By
    # filas con al menos un nombre de banco; se filtran encabezados
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return [r for r in rows if r.find_elements(By.TAG_NAME, "td")]


def _xbrl_individual_link(row):
    """Dentro de una fila, devuelve el <a> del XBRL Individual/Separado DISPONIBLE (el primero),
    o None si no está disponible. Heurística: el primer enlace cuyo href/onclick apunte a xbrl."""
    from selenium.webdriver.common.by import By
    anchors = row.find_elements(By.XPATH, ".//a[@href or @onclick]")
    cands = []
    for a in anchors:
        h = (a.get_attribute("href") or "") + " " + (a.get_attribute("onclick") or "")
        img = a.find_elements(By.TAG_NAME, "img")
        alt = " ".join((i.get_attribute("alt") or "") + (i.get_attribute("src") or "") for i in img)
        blob = (h + " " + alt).lower()
        if "xbrl" in blob or ".xbrl" in blob or "xbrl" in (a.text or "").lower():
            cands.append(a)
    # el PRIMER xbrl de la fila = Individual/Separado (el segundo sería Consolidado)
    return cands[0] if cands else None


def _download_href(driver, url, dest):
    import requests
    sess = requests.Session()
    for c in driver.get_cookies():
        sess.cookies.set(c["name"], c["value"])
    ua = driver.execute_script("return navigator.userAgent;")
    r = sess.get(url, headers={"User-Agent": ua}, timeout=120)
    r.raise_for_status()
    ext = ".xbrl"
    cd = r.headers.get("Content-Disposition", "")
    m = re.search(r'filename="?([^";]+)"?', cd)
    if m and "." in m.group(1):
        ext = "." + m.group(1).rsplit(".", 1)[-1].lower()
    elif "." in url.split("/")[-1]:
        ext = "." + url.split("/")[-1].rsplit(".", 1)[-1].split("?")[0].lower()
    dest = dest + ext
    if os.path.exists(dest):
        return dest, True
    with open(dest, "wb") as f:
        f.write(r.content)
    return dest, False


def _download_click(driver, anchor, dest_base, download_dir, timeout=60):
    """Fallback: clic + esperar a que aparezca un archivo nuevo en download_dir, y renombrar."""
    before = set(os.listdir(download_dir))
    driver.execute_script("arguments[0].click();", anchor)
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(1)
        now = set(os.listdir(download_dir))
        new = [f for f in now - before if not f.endswith(".crdownload")]
        if new:
            src = os.path.join(download_dir, new[0])
            ext = os.path.splitext(src)[1] or ".xbrl"
            dest = dest_base + ext
            os.replace(src, dest)
            return dest, False
    raise TimeoutError("no se detectó descarga tras el clic")


def run(years, out_root, headless=True, debug=False, limit=None):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    tmp_dl = os.path.abspath(os.path.join(out_root, "_tmp_downloads"))
    os.makedirs(tmp_dl, exist_ok=True)
    driver = build_driver(tmp_dl, headless=headless)
    n_ok = n_skip = n_fail = 0
    try:
        plan = [(REPORTE_INTERMEDIO, MESES_INTERMEDIO), (REPORTE_CIERRE, MESES_CIERRE)]
        for year in years:
            for reporte, meses in plan:
                for mm, mes_nombre in meses.items():
                    logging.info(f"=== {year}-{mm} ({reporte}) ===")
                    driver.get(PORTAL)
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.TAG_NAME, "select")))
                    ok = (_select_by_option_text(driver, TIPO_ENTIDAD_OPT) and
                          _select_by_option_text(driver, reporte) and
                          _select_by_option_text(driver, str(year), set_to=str(year)) and
                          _select_by_option_text(driver, mes_nombre, set_to=mes_nombre))
                    if not ok:
                        logging.warning(f"no pude fijar el formulario para {year}-{mm}; revisa --debug")
                    _click_buscar(driver)
                    time.sleep(4)  # esperar resultados (ajustable)
                    try:
                        WebDriverWait(driver, 30).until(lambda d: len(_result_rows(d)) > 0)
                    except Exception:
                        logging.warning(f"sin filas de resultado para {year}-{mm}")
                    if debug:
                        _dump_debug(driver, out_root); driver.quit(); return
                    rows = _result_rows(driver)
                    count = 0
                    for row in rows:
                        tds = row.find_elements(By.TAG_NAME, "td")
                        name = tds[0].text.strip() if tds else ""
                        folder = match_folder(name)
                        if not folder:
                            continue
                        dest_dir = os.path.join(out_root, folder)
                        os.makedirs(dest_dir, exist_ok=True)
                        dest_base = os.path.join(dest_dir, f"{folder}_individual_{year}-{mm}")
                        if glob.glob(dest_base + ".*"):
                            n_skip += 1; continue
                        link = _xbrl_individual_link(row)
                        if link is None:
                            continue  # "Transmisión sin información" -> no disponible
                        try:
                            href = link.get_attribute("href")
                            if href and href.lower().startswith(("http", "/")):
                                url = urljoin(driver.current_url, href)
                                path, existed = _download_href(driver, url, dest_base)
                            else:
                                path, existed = _download_click(driver, link, dest_base, tmp_dl)
                            n_ok += 1; count += 1
                            logging.info(f"  OK {folder} {year}-{mm} -> {os.path.basename(path)}")
                        except Exception as e:
                            n_fail += 1
                            logging.error(f"  FALLO {folder} {year}-{mm}: {e}")
                        if limit and count >= limit:
                            break
        logging.info(f"FIN. descargados={n_ok} saltados={n_skip} fallidos={n_fail}")
    finally:
        driver.quit()


def _dump_debug(driver, out_root):
    """Vuelca opciones de los <select> y el HTML de las primeras filas para fijar selectores."""
    from selenium.webdriver.common.by import By
    print("\n===== DEBUG: <select> y sus opciones =====")
    for i, sel in enumerate(driver.find_elements(By.TAG_NAME, "select")):
        opts = [o.text for o in sel.find_elements(By.TAG_NAME, "option")][:12]
        print(f"select[{i}] id={sel.get_attribute('id')} name={sel.get_attribute('name')} :: {opts}")
    print("\n===== DEBUG: primeras filas de resultados =====")
    rows = _result_rows(driver)[:3]
    for r in rows:
        print("----")
        print(r.get_attribute("outerHTML")[:1500])
    path = os.path.join(out_root, "debug_page.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"\nHTML completo guardado en {path} (mándamelo si los selectores no calzan).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2015-2025", help="p.ej. 2015-2025 | 2025 | 2018,2019")
    ap.add_argument("--out", default=".", help="carpeta raíz donde están las carpetas por banco")
    ap.add_argument("--headful", action="store_true", help="mostrar el navegador (para observar/depurar)")
    ap.add_argument("--debug", action="store_true", help="solo volcar selectores y salir (no descarga)")
    ap.add_argument("--limit", type=int, default=None, help="máx. bancos por período (para pruebas)")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler("sfc_download.log", encoding="utf-8"),
                                  logging.StreamHandler()])
    run(parse_years(a.years), a.out, headless=not a.headful, debug=a.debug, limit=a.limit)


if __name__ == "__main__":
    main()
