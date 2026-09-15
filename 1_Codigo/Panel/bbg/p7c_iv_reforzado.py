# -*- coding: utf-8 -*-
"""
p7c_iv_reforzado.py -- C2 del plan de arbitro: IV reforzado con el instrumento
de terminos de intercambio por exposicion sectorial a commodities
(`p7b_iv_commodity_tot.py` -> columna `CTOT_shock` en Panel_bloomberg.csv).

Corre:
  (1) CTOT solo, JUST-IDENTIFICADO -- el test mas limpio: un instrumento cuya
      "participacion" (share) es exogena por construccion (exportaciones
      pre-muestra, WDI 1998-2003), no estimada regresando JLoss contra el
      shock (a diferencia de OnOffRun/USD NEER).
  (2) CTOT + OnOffRun + USD NEER, SOBRE-IDENTIFICADO (3 instrumentos) -- si
      el Sargan rechaza incluso agregando el instrumento mas exogeno, la
      sobre-identificacion del panel de 13 paises no se resuelve con mas
      instrumentos.

Entrada  : bbg/Panel_bloomberg.csv (col. CTOT_shock, OnOffRun_spread_log,
           USD_NEER_log ya mezcladas)
Salida   : bbg/iv_reforzado_bbg.csv
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.dirname(HERE)
sys.path.insert(0, PANEL)
import causal_core as cc  # noqa: E402

PANEL_CSV = os.path.join(HERE, "Panel_bloomberg.csv")


def load_for_causal(dv="EMBI_bps"):
    d = pd.read_csv(PANEL_CSV)
    d = d.dropna(subset=[dv, "JLoss", "GaR"]).copy()
    tmp = os.path.join(HERE, "_causal_input_reforzado.csv")
    d.to_csv(tmp, index=False)
    return tmp


def main():
    tmp = load_for_causal()
    P = cc.load(tmp)
    ctr = cc.ctrls_in(P)
    print(f"Panel: N={len(P)}, {P['country'].nunique()} paises, controles={ctr}")
    print(f"CTOT_shock disponible en {P['CTOT_shock'].notna().sum()}/{len(P)} filas\n")

    rows = []

    print("(1) CTOT solo (just-identificado) ...")
    try:
        iv1 = cc.iv_commodity_tot(P, ctrls=ctr)
        print(f"  F_1a etapa={iv1['F_conjunto']:.1f}  beta_JLoss_IV={iv1['beta_JLoss_IV']:+.2f} "
              f"(se={iv1['se_JLoss']:.2f}, p={iv1['p_JLoss']:.3f})  "
              f"n={iv1['n']} paises={iv1['paises']}")
        rows.append(dict(spec="CTOT solo (just-id)", **{k: v for k, v in iv1.items()
                                                          if k not in ("F_individual", "instrumentos", "label")}))
    except Exception as e:
        print(f"  ERROR: {e}")
        rows.append(dict(spec="CTOT solo (just-id)", error=str(e)[:120]))

    print("\n(2) CTOT + OnOffRun + USD NEER (sobre-identificado, 3 instrumentos) ...")
    try:
        iv2 = cc.iv_commodity_tot_plus_existentes(
            P, ctrls=ctr, global_vars=("OnOffRun_spread_log", "USD_NEER_log"), pre_year=2012)
        sargan_p = iv2.get("sargan_p")
        print(f"  F_conjunto={iv2['F_conjunto']:.1f}  F_individual={iv2['F_individual']}")
        print(f"  beta_JLoss_IV={iv2['beta_JLoss_IV']:+.2f} (se={iv2['se_JLoss']:.2f}, p={iv2['p_JLoss']:.3f})  "
              f"Sargan p={sargan_p if sargan_p is None else round(sargan_p, 4)}")
        rows.append(dict(spec="CTOT+OnOffRun+USD (sobre-id, 3 instr.)",
                         **{k: v for k, v in iv2.items() if k not in ("F_individual", "instrumentos", "label")}))
    except Exception as e:
        print(f"  ERROR: {e}")
        rows.append(dict(spec="CTOT+OnOffRun+USD (sobre-id)", error=str(e)[:120]))

    # (3) referencia: los 2 instrumentos ORIGINALES sin CTOT (para comparar el Sargan)
    print("\n(3) referencia -- OnOffRun + USD NEER solos (sin CTOT, ya documentado antes) ...")
    try:
        iv3 = cc.iv_shiftshare_overid(P, ["OnOffRun_spread_log", "USD_NEER_log"], ctrls=ctr, pre_year=2012)
        sargan_p = iv3.get("sargan_p")
        print(f"  F_conjunto={iv3['F_conjunto']:.1f}  beta_JLoss_IV={iv3['beta_JLoss_IV']:+.2f} "
              f"(p={iv3['p_JLoss']:.3f})  Sargan p={sargan_p if sargan_p is None else round(sargan_p, 4)}")
        rows.append(dict(spec="OnOffRun+USD (sobre-id, 2 instr., referencia)",
                         **{k: v for k, v in iv3.items() if k not in ("F_individual", "instrumentos", "label")}))
    except Exception as e:
        print(f"  ERROR: {e}")

    os.remove(tmp)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "iv_reforzado_bbg.csv"), index=False)
    print("\nGuardado: bbg/iv_reforzado_bbg.csv")


if __name__ == "__main__":
    main()
