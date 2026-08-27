"""
banks_bloomberg.py — universo de bancos y tickers de pais (indice bursatil, FX, bono
soberano 10Y) para los 12 paises de Fase 1, tomados literalmente de las tablas §4 y §5
del runbook Bloomberg. Los tickers marcados con comentario "verificar" dependen de la
licencia contratada y deben confirmarse en el terminal (FLDS<GO> / SECF<GO>) antes de
automatizar el pull completo — usar bloomberg_common.verify_fields() para eso.

Fase 1 = los 12 paises marcados "extractor listo, sin datos" en el runbook:
Argentina, China, Egipto, Indonesia, Malasia, Pakistan, Filipinas, Polonia, Rusia,
Sudafrica, Turquia, Bulgaria.

Rusia y Bulgaria/Egipto quedan al final del orden de ejecucion (mercados delgados /
sancionados — ver notas por pais en el runbook §7).
"""

# ---------------------------------------------------------------------------
# BANKS: countryname -> {bankname: {"ticker": "<Bloomberg Equity ticker>"}}
# countryname en minusculas (coincide con la convencion de los extractores del repo,
# ej. "argentina", "china"); bankname en snake_case (coincide con la convencion de
# jloss_common / extract_<pais>.py).
# ---------------------------------------------------------------------------
BANKS = {
    "argentina": {
        "galicia":       {"ticker": "GGAL AR Equity", "ticker_adr": "GGAL US Equity"},
        "macro":         {"ticker": "BMA AR Equity",  "ticker_adr": "BMA US Equity"},
        "bbva_argentina":{"ticker": "BBAR AR Equity", "ticker_adr": "BBAR US Equity"},
        "supervielle":   {"ticker": "SUPV AR Equity", "ticker_adr": "SUPV US Equity"},
    },
    "bulgaria": {
        # unico banco bulgaro con free float relevante; resto son filiales no listadas
        # ex-5F4 BU (TKCH). FIB cotiza en EUR, igual que el EQY_FUND_CRNCY del balance;
        # 5F4 devolvia CUR_MKT_CAP en BGN -> mktcap inflado x1.95583 respecto al balance.
        "fibank": {"ticker": "FIB BU Equity"},
    },
    "china": {
        # H-shares (HKEX) — Industrial Bank/SPDB/Ping An Bank son solo A-share: verificar en SECF
        "icbc":              {"ticker": "1398 HK Equity"},
        "ccb":               {"ticker": "939 HK Equity"},
        "abc":               {"ticker": "1288 HK Equity"},
        "boc":               {"ticker": "3988 HK Equity"},
        "bocom":             {"ticker": "3328 HK Equity"},
        "cmb":               {"ticker": "3968 HK Equity"},
        "citic":             {"ticker": "998 HK Equity"},
        "minsheng":          {"ticker": "1988 HK Equity"},
        "psbc":              {"ticker": "1658 HK Equity"},
        "china_everbright":  {"ticker": "6818 HK Equity"},
    },
    "egypt": {
        # unico banco egipcio realmente liquido; National Bank of Egypt y Banque Misr son estatales
        "cib": {"ticker": "COMI EY Equity"},
    },
    "indonesia": {
        "bca":     {"ticker": "BBCA IJ Equity"},
        "bri":     {"ticker": "BBRI IJ Equity"},
        "mandiri": {"ticker": "BMRI IJ Equity"},
        "bni":     {"ticker": "BBNI IJ Equity"},
        "bsi":     {"ticker": "BRIS IJ Equity"},
    },
    "malaysia": {
        "maybank":          {"ticker": "MAY MK Equity"},
        "public_bank":      {"ticker": "PBK MK Equity"},
        "cimb":             {"ticker": "CIMB MK Equity"},
        "rhb_bank":         {"ticker": "RHBBANK MK Equity"},
        "hong_leong_bank":  {"ticker": "HLBK MK Equity"},
        "ambank":           {"ticker": "AMM MK Equity"},
    },
    "pakistan": {
        "habib_bank":      {"ticker": "HBL PA Equity"},
        "united_bank":     {"ticker": "UBL PA Equity"},
        "mcb_bank":        {"ticker": "MCB PA Equity"},
        "national_bank_pk":{"ticker": "NBP PA Equity"},
        "allied_bank":     {"ticker": "ABL PA Equity"},
        "bank_alfalah":    {"ticker": "BAFL PA Equity"},
    },
    "philippines": {
        "bdo_unibank":  {"ticker": "BDO PM Equity"},
        "bpi":          {"ticker": "BPI PM Equity"},
        "metrobank":    {"ticker": "MBT PM Equity"},
        "security_bank":{"ticker": "SECB PM Equity"},
        "china_banking":{"ticker": "CBC PM Equity"},   # ex-CHIB PM (TKCH): CHIB devolvia 0 obs de mktcap
    },
    "poland": {
        "pko_bp":           {"ticker": "PKO PW Equity"},
        "pekao":            {"ticker": "PEO PW Equity"},
        "santander_polska": {"ticker": "EBP PW Equity"},   # ex-SPL PW (TKCH): SPL devolvia 0 obs de mktcap
        "mbank":            {"ticker": "MBK PW Equity"},
        "ing_bsk":          {"ticker": "ING PW Equity"},
        "millennium":       {"ticker": "MIL PW Equity"},
        "alior":            {"ticker": "ALR PW Equity"},
        "handlowy":         {"ticker": "BHW PW Equity"},
    },
    "russia": {
        # cobertura probablemente rota/congelada en terminales fuera de Rusia desde feb-2022
        # Rusia: ambos MARKET_STATUS=PRNA (pricing not available). Bloomberg dejo de precificar
        # tras las sanciones -> la serie de mercado termina el 2024-08-09. No hay ticker
        # alternativo; el panel de Rusia queda truncado ahi (verificado 2026-08-27).
        "sberbank": {"ticker": "SBER RM Equity"},
        "vtb":      {"ticker": "VTBR RM Equity"},
    },
    "southafrica": {
        "standard_bank": {"ticker": "SBK SJ Equity"},
        "firstrand":     {"ticker": "FSR SJ Equity"},
        "absa":          {"ticker": "ABG SJ Equity"},
        "nedbank":       {"ticker": "NED SJ Equity"},
        "capitec":       {"ticker": "CPI SJ Equity"},
        "investec":      {"ticker": "INL SJ Equity", "ticker_alt": "INVP LN Equity"},
    },
    "turkey": {
        "akbank":       {"ticker": "AKBNK TI Equity"},
        "garanti_bbva": {"ticker": "GARAN TI Equity"},
        "isbank":       {"ticker": "ISCTR TI Equity"},
        "yapi_kredi":   {"ticker": "YKBNK TI Equity"},
        "vakifbank":    {"ticker": "VAKBN TI Equity"},
        "halkbank":     {"ticker": "HALKB TI Equity"},
        "tskb":         {"ticker": "TSKB TI Equity"},
        "sekerbank":    {"ticker": "SKBNK TI Equity"},
    },
}

# ---------------------------------------------------------------------------
# COUNTRY_INDEX: indice bursatil, FX (Curncy) y bono soberano 10Y por pais (runbook §4)
# ---------------------------------------------------------------------------
COUNTRY_INDEX = {
    "argentina":   {"ccy": "ARS", "stx": "MERVAL Index",  "fx": "USDARS Curncy",
                     "sov10y": None, "sov_note": "sin generico limpio — usar CDS soberano 5Y"},
    "bulgaria":    {"ccy": "BGN", "stx": "SOFIX Index",   "fx": "USDBGN Curncy",
                     "sov10y": None, "sov_note": "verificar liquidez (peg a EUR)"},
    "china":       {"ccy": "CNY", "stx": "SHCOMP Index",  "fx": "USDCNY Curncy",
                     "sov10y": "GTCNY10Y Govt"},
    "egypt":       {"ccy": "EGP", "stx": "EGX30 Index",   "fx": "USDEGP Curncy",
                     "sov10y": None, "sov_note": "verificar liquidez"},
    "indonesia":   {"ccy": "IDR", "stx": "JCI Index",     "fx": "USDIDR Curncy",
                     "sov10y": "GTIDR10Y Govt"},
    "malaysia":    {"ccy": "MYR", "stx": "FBMKLCI Index", "fx": "USDMYR Curncy",
                     "sov10y": "GTMYR10Y Govt"},
    "pakistan":    {"ccy": "PKR", "stx": "KSE100 Index",  "fx": "USDPKR Curncy",
                     "sov10y": None, "sov_note": "verificar liquidez"},
    "philippines": {"ccy": "PHP", "stx": "PCOMP Index",   "fx": "USDPHP Curncy",
                     "sov10y": "GTPHP10Y Govt"},
    "poland":      {"ccy": "PLN", "stx": "WIG20 Index",   "fx": "USDPLN Curncy",
                     "sov10y": "GTPLN10Y Govt"},
    "russia":      {"ccy": "RUB", "stx": "IMOEX Index",   "fx": "USDRUB Curncy",
                     "sov10y": "GTRUB10Y Govt", "sov_note": "sanciones feb-2022 — verificar cobertura"},
    "southafrica": {"ccy": "ZAR", "stx": "JALSH Index",   "fx": "USDZAR Curncy",
                     "sov10y": "GTZAR10Y Govt"},
    "turkey":      {"ccy": "TRY", "stx": "XU100 Index",   "fx": "USDTRY Curncy",
                     "sov10y": "GTTRY10Y Govt"},
}

# Nombre corto de emisor soberano para CDS (convencion Bloomberg/Markit: "<NOMBRE> CDS USD
# SR 5Y Corp" usa el nombre/abreviatura del PAIS emisor, NO el codigo de moneda). Estos son
# los mnemonicos habituales de mercado — SIN VERIFICAR en este terminal especifico; confirmar
# con SECF<GO> antes de automatizar el pull (bloomberg_common.verify_fields ya lo intenta y
# avisa si el ticker no responde).
CDS_ISSUER_NAME = {
    "argentina": "ARGENT", "bulgaria": "BULGAR", "china": "CHINA", "egypt": "EGYPT",
    "indonesia": "INDON", "malaysia": "MALAYS", "pakistan": "PAKIST",
    "philippines": "PHILIP", "poland": "POLAND", "russia": "RUSSIA",
    "southafrica": "SOAF", "turkey": "TURKEY",
}

# Orden de ejecucion sugerido (runbook §6 + advertencias §7): confianza alta primero,
# mercados delgados / sancionados al final.
# El CDS soberano de China NO resuelve por convencion de nombre de emisor: "CHINA CDS USD
# SR 5Y Corp" y todas sus variantes dan BAD_SEC. Si resuelve por el ticker Markit
# (CCHIN1U5 Curncy -> "CHINAGOV CDS USD SR 5Y D14", 4059 obs 2010-2026). Para el resto de
# paises el ticker Markit resuelve al MISMO security que el nombre, asi que no se cambia.
CDS_TICKER_OVERRIDE = {
    "china": "CCHIN1U5 Curncy",
}

# Cobertura real del CDS 5Y en este terminal (verificado 2026-08-27). Los huecos NO son
# error de ticker: el security resuelve, simplemente no hay precios fuera de esa ventana.
CDS_COVERAGE_NOTE = {
    "poland":   "solo 2012-07-13..2015-10-16 (504 obs) — sin serie utilizable",
    "bulgaria": "solo 2012-07-13..2015-10-16 (491 obs) — sin serie utilizable",
    "russia":   "solo 2012-07-13..2015-10-16 (619 obs) — sin serie utilizable",
    "pakistan": "solo desde 2026-03-18 (115 obs) — sin historia",
    "egypt":    "468 obs dispersas en 2010-2026 — serie muy rala",
}

EXECUTION_ORDER = [
    "poland", "southafrica", "turkey", "china", "indonesia", "malaysia",
    "philippines", "pakistan", "argentina", "bulgaria", "egypt", "russia",
]

# Variables globales (runbook §1 y §3) — se piden una sola vez, no por pais.
GLOBAL_TICKERS = {
    "vix": "VIX Index",
    "ust10y": "USGG10YR Index",
    # HY spread: BEBGHYCS Index NO EXISTE en este terminal (BAD_SEC, verificado 2026-08-27).
    # LF98OAS = "Bloomberg US Corporate High Yield Average OAS", que es el equivalente
    # directo del FRED BAMLH0A0HYM2 usado en el repo. 4196 obs, 2010-01-04..2026-08-26.
    # Alternativa global: LG30OAS Index (Bloomberg Global High Yield Avg OAS, 4329 obs).
    "hy_spread": "LF98OAS Index",
}
