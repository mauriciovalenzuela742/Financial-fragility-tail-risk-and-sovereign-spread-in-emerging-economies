# -*- coding: utf-8 -*-
"""
verificar_canonicos.py -- N7 de 4_Redaccion/plan_nota7.md: compara las salidas bbg/paper_*_numeros.csv con
los valores canónicos congelados en canonicos_esperados.json (las cifras que cita la tesis).

  python verificar_canonicos.py             # verifica; código de salida 1 si alguna cifra no coincide
  python verificar_canonicos.py --congelar  # reescribe canonicos_esperados.json con los valores actuales

Tolerancia: relativa de 1e-4 para coeficientes y conteos; absoluta de 0,01 para los p de bootstrap y de
permutación (claves con "_p"), que dependen de la semilla y del álgebra lineal de la máquina.
Solo usa pandas, para que corra también en la integración continua sin los datos de Bloomberg.
"""
import json
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
BBG = os.path.join(AQUI, "bbg")
ESP = os.path.join(AQUI, "canonicos_esperados.json")

# archivo -> claves que la tesis cita
CLAVES = {
    "paper_lnlag_numeros.csv": ["principal_N", "principal_b1", "principal_b2", "principal_b3", "principal_b1_p",
                                "principal_b2_p", "principal_b3_p"],
    "paper_p42_numeros.csv": ["rh3_N", "rh3_b", "rh3_p_uni", "rh3_p_holm", "rh3_loo_ok", "rh2_b", "rh2_p_holm"],
    "paper_p45_numeros.csv": ["r2h3_b2", "r2h3_b2_p_uni", "r2h3_p_holm", "r2h3_loo_ok", "r2h1_b", "r2h2_b",
                              "sec_rh3_D4_b", "sec_rh3_D4_p_uni"],
    "paper_p47_numeros.csv": ["rho_spearman", "dp_spearman", "ancha_spearman", "rho_log_b1", "dp_log_b1", "ancha_log_b1"],
    "paper_p51_numeros.csv": ["familia_mu1h1_p_holm", "familia_mu4h1_p_holm", "mu6_min4_b1", "mu6_cobertura_mexico"],
    "paper_p52_numeros.csv": ["U1_gamma", "U1_LR", "U1_p_bloques", "U1_T_c_dif", "U1_C1_contienen", "U1_C2_p",
                              "U1_potencia", "U2_gamma", "U2_LR", "U2_p_bloques", "U2_T_c_dif", "U2_C1_contienen",
                              "U2_C2_p", "U2_C5_quiebre_mejor", "U2_potencia", "U3_p_bloques", "U3_C2_p"],
    "paper_p53_numeros.csv": ["U4_auc_in", "U4_auc_oos", "U4_oos_eventos", "familia_P1_holm", "familia_P2_holm",
                              "familia_P3_holm"],
    "paper_p55_numeros.csv": ["MES_spearman", "DCoVaR_spearman", "U1MES_p_bloques", "U1DCoVaR_p_bloques"],
    "paper_p56_numeros.csv": ["conj_R2-H3_holm", "conj_R-H3_holm", "conj_R2-H3_bh", "conj_holm05",
                              "perm_rh3_b_obs", "perm_rh3_p_perm", "perm_rh3D4_b_obs", "perm_rh3D4_p_perm"],
    "paper_p57_numeros.csv": ["N2_psi_original", "N2_psi", "N2_N", "N2_p_uni", "N2_dif_p", "N2_no_replica",
                              "N2_hungary_psi", "N2_southkorea_psi", "N2cds_psi", "N2_potencia"],
    "paper_p58_numeros.csv": ["N1_TM", "N1_F_T", "N1_F_TM", "N1_debil", "N1_p_uni", "N1_fs_Z", "N1_rf_ZM",
                              "familia5_N2-H1_holm", "familia5_N1-H1_holm"],
}


def actuales():
    out = {}
    for f, ks in CLAVES.items():
        v = pd.read_csv(os.path.join(BBG, f), index_col=0)["valor"]
        for k in ks:
            out[f"{f}::{k}"] = float(v[k])
    return out


def main():
    act = actuales()
    if "--congelar" in sys.argv:
        with open(ESP, "w", encoding="utf-8") as fh:
            json.dump(act, fh, indent=1, ensure_ascii=False, sort_keys=True)
        print(f"{len(act)} cifras congeladas en {ESP}")
        return 0
    with open(ESP, encoding="utf-8") as fh:
        esp = json.load(fh)
    malas = 0
    for k, e in sorted(esp.items()):
        a = act.get(k)
        clave = k.split("::")[1]
        ok = a is not None and (abs(a - e) <= 0.01 if "_p" in clave else abs(a - e) <= 1e-4 * max(1.0, abs(e)))
        if not ok:
            malas += 1
            print(f"  NO COINCIDE  {k}: esperado {e:.6g}, obtenido {a}")
    print(f"{len(esp) - malas} de {len(esp)} cifras canónicas coinciden.")
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
