"""
extract_venezuela.py — Inputs JLoss para Venezuela (Hito 5). STUB DOCUMENTADO.

RECOMENDACIÓN METODOLÓGICA (honesta): una actualización significativa del JLoss de Venezuela con
datos públicos NO es viable con el aparato de Merton, por razones estructurales:

  1. Hiperinflación y redenominaciones del bolívar (2008, 2018, 2021) hacen que las cifras
     monetarias de balance no sean comparables en el tiempo sin un deflactor/criterio de
     re-expresión que el propio supervisor no aplica de forma consistente.
  2. Distorsión cambiaria (múltiples tipos de cambio, controles) impide convertir E (valor de
     mercado del equity) y D (deuda) a una unidad común estable.
  3. La Bolsa de Valores de Caracas es ilíquida y la capitalización de mercado de los bancos no es
     informativa => la PD de mercado de Merton no es estimable de forma creíble.
  4. La publicación de SUDEBAN es discontinua y de calidad variable a nivel banco.

CURSO DE ACCIÓN RECOMENDADO: conservar la serie histórica de Venezuela del panel de referencia
(la calculada en su momento) y DOCUMENTAR explícitamente por qué no se actualiza a nivel banco,
en lugar de forzar una extracción de baja calidad que contamine el panel.

DECISIÓN DEL COMITÉ (ago-2026): no se usa PD contable en ningún país del pipeline. La alternativa
parcial que se consideraba antes (book_pd sobre CAR/ROA) queda descartada — ninguno de los bancos
de BANKMAP tiene equity listado útil, así que Venezuela no produce JLoss bajo la política vigente,
punto. No se busca sustituto contable.

Fuente nominal: SUDEBAN (Superintendencia de las Instituciones del Sector Bancario).
Bancos relevantes (mayormente sin precio de mercado útil): Banco de Venezuela, Banesco,
Banco Mercantil, BBVA Provincial, Banco Occidental de Descuento.

Este módulo deja la estructura lista (mismo esquema v8 y criterio bonos-vs-resto) por si se
dispone de un long-format re-expresado en términos reales, pero por defecto NO produce serie.
"""
import argparse
import pandas as pd
import numpy as np
import jloss_common as jc

COUNTRY = "venezuela"

BANKMAP = {}  # ninguno de los bancos venezolanos tiene equity listado util -> universo vacio.
ACCOUNT_MAP = {
    "bonds": ["OBLIGACIONES", "BONOS", "TITULOS DE DEUDA EMITIDOS", "DEUDA SUBORDINADA"],
    "tot_asset": ["TOTAL ACTIVO", "ACTIVO TOTAL"],
    "equity": ["PATRIMONIO", "TOTAL PATRIMONIO"],
}


def fetch_balances(export_file, start_year, end_year, col_code=None):
    """Solo se ejecuta si se provee un long-format ya RE-EXPRESADO en términos reales/comparables.
    Marca todas las observaciones como no comparables (real_terms=True en metadatos del análisis)."""
    df = pd.read_csv(export_file) if str(export_file).endswith(".csv") else pd.read_excel(export_file)
    df.columns = [str(c).strip().lower() for c in df.columns]
    rows = jc.transform_long_generic(df, BANKMAP, ACCOUNT_MAP, COUNTRY,
                                     col_bank="bank", col_account="account",
                                     col_period="period", col_value="value", col_code=col_code)
    bal = jc.derive_st_lt_bonds_vs_rest(jc.finalize_balance(rows))
    return bal[(bal["date"].dt.year >= start_year) & (bal["date"].dt.year <= end_year)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="(opcional) long-format RE-EXPRESADO en términos reales")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    a = ap.parse_args()
    if not a.file:
        print("Venezuela: por defecto NO se actualiza (ver docstring). Conservar serie histórica y "
              "documentar la discontinuación. Provea --file solo con datos re-expresados en términos reales.")
        return
    bal = fetch_balances(a.file, a.start, a.end)
    print("ADVERTENCIA: observaciones de Venezuela marcadas como NO comparables con el resto del panel.")
    bal.to_csv(f"balance_{COUNTRY}.csv", index=False)


if __name__ == "__main__":
    main()
