"""
extract_brazil.py — Inputs JLoss para Brasil desde la API OData IFData del Banco Central.

Fuente balances: https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/
  Recurso de FUNCION (los parametros van en la ruta con alias @):
    IfDataValores(AnoMes=@AnoMes,TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)
      ?@AnoMes=YYYYMM&@TipoInstituicao=1&@Relatorio='1'&$format=json
  ListaDeRelatorio  -> ids y nombres de reportes
  Periodicidad trimestral (AnoMes = YYYYMM en 03,06,09,12). Sin API key.
Fuente precios: yfinance, tickers .SA (B3). Solo bancos listados.

Uso:
    python extract_brazil.py --discover            # lista reportes y columnas reales
    python extract_brazil.py --start 2000 --end 2026
"""
import argparse
import re
import unicodedata
import time
import requests
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "brazil"
ODATA = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata"

# Nivel de consolidacion. El ejemplo oficial usa 1. Verificar con --discover si hiciera falta.
#   1 = Conglomerado Prudencial (nivel al que se supervisa el grupo bancario)
TIPO_INST = 1
# Reportes a combinar: Resumo (Ativo Total + Patrimonio Liquido) y Passivo (deuda emitida).
# Confirmar ids con --discover (ListaDeRelatorio). Tipicamente 1=Resumo, 3=Passivo.
RELATORIOS = ["1", "3"]

# bankname_panel : {ticker .SA, nombres IFData posibles (substring, SIN acentos, MAYUSCULAS)}
BANKMAP = {
    "itau_unibanco":    {"ticker": "ITUB4.SA",  "names": ["ITAU UNIBANCO", "ITAU"]},
    "bradesco":         {"ticker": "BBDC4.SA",  "names": ["BRADESCO"]},
    "banco_do_brasil":  {"ticker": "BBAS3.SA",  "names": ["BANCO DO BRASIL"]},
    "santander_brasil": {"ticker": "SANB11.SA", "names": ["SANTANDER"]},
    "btg_pactual":      {"ticker": "BPAC11.SA", "names": ["BTG PACTUAL"]},
    "banrisul":         {"ticker": "BRSR6.SA",  "names": ["BANRISUL", "RIO GRANDE DO SUL"]},
    "banco_pan":        {"ticker": "BPAN4.SA",  "names": ["BANCO PAN", "PANAMERICANO"]},
    "abc_brasil":       {"ticker": "ABCB4.SA",  "names": ["ABC BRASIL", "ABC-BRASIL"]},
    "banco_bmg":        {"ticker": "BMGB4.SA",  "names": ["BMG"]},
    "banco_inter":      {"ticker": "INBR32.SA", "names": ["BANCO INTER", "INTERMEDIUM"]},
    "banco_do_nordeste":{"ticker": "BNBR3.SA",  "names": ["BANCO DO NORDESTE"]},
}

# Columnas CONFIRMADAS via --discover (match por PREFIJO sobre nombre normalizado).
# bonds = SOLO el total "Recursos de Aceites e Emissao de Titulos (c)"; NO sus hijos
# (Letras c1/c2/c3, Titulos no exterior c4, Outros c5) -> evita doble conteo.
ACCOUNT_RULES = {
    "tot_asset": ["ATIVO TOTAL"],                              # Relatorio 1 (Resumo)
    "equity":    ["PATRIMONIO LIQUIDO"],                       # Resumo (y Passivo (i))
    "bonds":     ["RECURSOS DE ACEITES E EMISSAO DE TITULOS"], # Passivo (c), total emitido -> LP
}


def _norm(s):
    """MAYUSCULAS sin acentos ni saltos de linea (ITAU UNIBANCO, RECURSOS ... (C))."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"\s+", " ", s)          # colapsa \n y espacios multiples
    return s.upper().strip()


_INST_KEYS = ["NomeInstituicao", "Instituicao", "NomInstituicao", "NomeInstituicaoFinanceira", "Nome"]
_VAL_KEYS = ["Saldo", "Valor", "ValorSaldo"]


def _inst_name(rec):
    for k in _INST_KEYS:
        v = rec.get(k)
        if v:
            return v
    return ""


def _rec_val(rec):
    for k in _VAL_KEYS:
        if rec.get(k) not in (None, ""):
            return rec.get(k)
    return None


_session = requests.Session()
_session.headers.update({"User-Agent": "Mozilla/5.0 JLoss-research/1.0", "Accept": "application/json"})


def _get_url(url, retries=4):
    last = None
    for k in range(retries):
        try:
            r = _session.get(url, timeout=120)
            r.raise_for_status()
            return r.json().get("value", [])
        except requests.HTTPError as e:
            sc = e.response.status_code if e.response is not None else None
            if sc is not None and 400 <= sc < 500 and sc not in (408, 429):
                raise
            last = e
        except (requests.ConnectionError, requests.Timeout) as e:
            last = e
        time.sleep(2 * (k + 1))
    raise last


def _valores(anomes, tipo, relatorio, top=None):
    """Llama al recurso de FUNCION IfDataValores con los alias @ en la query."""
    res = "IfDataValores(AnoMes=@AnoMes,TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)"
    qs = f"@AnoMes={anomes}&@TipoInstituicao={tipo}&@Relatorio='{relatorio}'&$format=json"
    if top:
        qs += f"&$top={top}"
    return _get_url(f"{ODATA}/{res}?{qs}")


def _cadastro(anomes):
    """IfDataCadastro(AnoMes=@AnoMes): instituciones/conglomerados con CodInst + nombre."""
    return _get_url(f"{ODATA}/IfDataCadastro(AnoMes=@AnoMes)?@AnoMes={anomes}&$format=json")


_codmap_cache = {}

# CodInst (CNPJ base, 8 digitos) de la institucion lider de cada banco. Estable y unico
# (tomado de IfDataCadastro). Se mapean TODOS los codigos del grupo: institucion,
# conglomerado financiero y PRUDENCIAL. A TipoInstituicao=1 los valores vienen con el
# codigo PRUDENCIAL (C00800xx); por eso hay que resolver el grupo, no el nombre.
BANK_CNPJ = {
    "itau_unibanco":    ["60701190", "60872504"],
    "bradesco":         ["60746948"],
    "banco_do_brasil":  ["00000000"],
    "santander_brasil": ["90400888"],
    "btg_pactual":      ["30306294", "00997804"],
    "banrisul":         ["92702067"],
    "banco_pan":        ["59285411", "09777343"],
    "abc_brasil":       ["28195667"],
    "banco_bmg":        ["61186680"],
    "banco_inter":      ["00416968"],
    "banco_do_nordeste":["07237373"],
}
_CNPJ2BANK = {c: bk for bk, lst in BANK_CNPJ.items() for c in lst}


def _codmap(anomes):
    """Construye {codigo -> bankname} resolviendo por CNPJ de la institucion lider.
    Mapea CodInst, CodConglomeradoPrudencial y CodConglomeradoFinanceiro del grupo.
    Evita falsos positivos (cooperativas con 'BANCO DO BRASIL'/'RIO GRANDE DO SUL' en el nombre)."""
    if anomes in _codmap_cache:
        return _codmap_cache[anomes]
    m = {}
    try:
        for rec in _cadastro(anomes):
            cod = str(rec.get("CodInst", "")).strip()
            lider = str(rec.get("CnpjInstituicaoLider", "")).strip()
            bk = _CNPJ2BANK.get(cod) or _CNPJ2BANK.get(lider)
            if not bk:
                continue
            for k in (rec.get("CodInst"), rec.get("CodConglomeradoPrudencial"),
                      rec.get("CodConglomeradoFinanceiro")):
                if k:
                    m[str(k).strip()] = bk
    except requests.RequestException as e:
        print(f"  aviso: cadastro {anomes} omitido ({type(e).__name__})")
    _codmap_cache[anomes] = m
    return m


def discover(anomes="202403"):
    """Lista reportes y, para los de RELATORIOS, vuelca las columnas reales (NomeColuna)."""
    print("=== IfDataCadastro (campos + bancos resueltos) ===")
    try:
        cad = _cadastro(anomes)
        if cad:
            print("   CAMPOS:", list(cad[0].keys()))
            print("   ejemplo:", cad[0])
        cm = _codmap(anomes)
        print(f"   bancos resueltos por CodInst ({len(cm)}):")
        for cod, bk in sorted(cm.items(), key=lambda kv: kv[1]):
            print(f"     {cod} -> {bk}")
    except Exception as e:
        print("  error cadastro:", e)
    for rel in RELATORIOS:
        print(f"\n=== Columnas de Relatorio {rel} en {anomes} (TipoInstituicao={TIPO_INST}) ===")
        try:
            recs = _valores(anomes, TIPO_INST, rel, top=2000)
            if recs:
                print("   CAMPOS del registro:", list(recs[0].keys()))
                print("   registro de ejemplo:", recs[0])
            cols = sorted({r.get("NomeColuna", "") for r in recs})
            for c in cols:
                print("  col:", repr(c))
            inst = sorted({_inst_name(r) for r in recs})
            print(f"  ({len(cols)} columnas, {len(recs)} filas; instituciones ej.: {inst[:6]})")
        except Exception as e:
            print("  error:", e)


def quarters(start_year, end_year):
    out = []
    for y in range(start_year, end_year + 1):
        for m in ("03", "06", "09", "12"):
            out.append(f"{y}{m}")
    return out


_TAG_RE = re.compile(r"\(([A-Z0-9]+)\)\s*$")   # etiqueta final tipo (c), (c5), (i), (j)...


def _classify(colname):
    c = _norm(colname)
    # bonds = la linea de "deuda emitida" del Passivo, etiqueta (c). El NOMBRE cambia entre
    # epocas (2014-2024: "Recursos de Aceites e Emissao de Titulos (c)"; 2025+: "Outros
    # Instrumentos de Divida (c)"), pero la etiqueta estructural (c) se mantiene.
    m = _TAG_RE.search(c)
    if m and m.group(1) == "C":
        return "bonds"
    if c.startswith("ATIVO TOTAL"):
        return "tot_asset"
    if c.startswith("PATRIMONIO LIQUIDO"):
        return "equity"
    return None


def _match_bank(inst_name):
    u = _norm(inst_name)
    for bankname, meta in BANKMAP.items():
        if any(n in u for n in meta["names"]):
            return bankname
    return None


def fetch_balances(start_year, end_year):
    acc = {}    # (bankname, anomes) -> {field: suma}
    n_ok = 0
    qs = quarters(start_year, end_year)
    for a in qs:
        got = False
        cm = _codmap(a)                                    # CodInst -> bankname para este trimestre
        if not cm:
            continue
        for rel in RELATORIOS:
            try:
                recs = _valores(a, TIPO_INST, rel)
            except requests.RequestException as e:
                print(f"  aviso: {a} rel {rel} omitido ({type(e).__name__})")
                continue
            for rec in recs:
                bankname = cm.get(str(rec.get("CodInst", "")).strip())
                if bankname is None:
                    continue
                field = _classify(rec.get("NomeColuna", ""))
                if field is None:
                    continue
                val = jc.to_float_latam(_rec_val(rec))
                if val is None or (isinstance(val, float) and np.isnan(val)):
                    continue
                acc.setdefault((bankname, a), {})
                acc[(bankname, a)].setdefault(field, val)   # cada campo es UNA sola linea
                got = True
        if got:
            n_ok += 1
    print(f"  trimestres con datos: {n_ok}/{len(qs)}")

    rows = []
    for (bankname, a), f in acc.items():
        date = pd.Timestamp(int(a[:4]), int(a[4:6]), 1)
        row = jc.empty_balance_row(COUNTRY, bankname, date)
        row.update({"bonds": f.get("bonds", np.nan),
                    "tot_asset": f.get("tot_asset", np.nan),
                    "equity_book": f.get("equity", np.nan)})
        rows.append(row)
    if not rows:
        print("  ATENCION: 0 filas. Corre --discover y confirma RELATORIOS y nombres de columna.")
        return pd.DataFrame(columns=["countryname", "bankname", "date",
                                     "bonds", "tot_asset", "equity_book"])
    return jc.derive_st_lt_bonds_vs_rest(jc.finalize_balance(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--discover-anomes", default="202403")
    ap.add_argument("--find", default=None, help="Busca en IfDataCadastro nombres que contengan el texto.")
    a = ap.parse_args()
    if a.find:
        key = _norm(a.find)
        for rec in _cadastro(a.discover_anomes):
            nom = _inst_name(rec)
            if key in _norm(nom):
                print(f"  {rec.get('CodInst','')} | {nom}")
        return
    if a.discover:
        discover(a.discover_anomes)
        return
    print("1/2 Balances IFData (BCB)...")
    bal = fetch_balances(a.start, a.end)
    bal.to_csv("balance_brazil.csv", index=False)
    if len(bal):
        jc.coverage_report(bal).to_csv("coverage_brazil.csv", index=False)
        print(f"   {len(bal)} filas, {bal['bankname'].nunique()} bancos, "
              f"{bal['date'].min().date()} a {bal['date'].max().date()}")
    print("2/2 Market cap...")
    mkt = jc.fetch_mktcap_yf(BANKMAP, COUNTRY, a.start, a.end)
    mkt.to_csv("mktcap_brazil.csv", index=False)
    print(f"   mktcap {len(mkt)} filas, {mkt['bankname'].nunique() if len(mkt) else 0} bancos")


if __name__ == "__main__":
    main()