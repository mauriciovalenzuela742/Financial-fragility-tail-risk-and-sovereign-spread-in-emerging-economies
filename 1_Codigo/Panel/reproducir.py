# -*- coding: utf-8 -*-
"""
reproducir.py -- N7 de 4_Redaccion/plan_nota7.md: un solo comando que regenera, desde los CSV de datos
del repositorio, las cifras de la especificación vigente de la tesis (Pasos 2e-2g de
4_Redaccion/REPRODUCIBILIDAD.md y la inferencia conjunta), y al final las verifica contra los valores
canónicos congelados (verificar_canonicos.py).

  python reproducir.py                 # estimación desde los CSV cacheados (sin red, sin pasos lentos)
  python reproducir.py --lentos        # agrega los pasos lentos (cuantílica ~70 min; motor JLoss, horas)
  python reproducir.py --red           # agrega los pasos que descargan datos (Banco Mundial, QPSD/QEDS)
  python reproducir.py --desde p42     # retoma desde un script
  python reproducir.py --listar        # muestra el plan sin ejecutar
  python reproducir.py --solo-verificar

La construcción del panel base (p0-p11: controles, EMBI, JLoss, GaR, instrumentos) sigue el Paso 2 de
REPRODUCIBILIDAD.md, porque depende de red y de la extracción de Bloomberg. Se ejecuta desde
1_Codigo/Panel/ con el .venv de la raíz.
"""
import argparse
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
GAR = os.path.join("..", "GaR", "individuals", "nlhpc_gar_all18")

# (script, argumentos, tipo) -- tipo: "base" | "lento" | "red"; el orden importa
PASOS = [
    ("bbg/p12_tablas_latex_lnlag.py", [], "base"),
    ("bbg/p13_figuras_paper.py", [], "base"),
    ("bbg/p14_arbitro_lnlag.py", [], "base"),
    ("bbg/p32_aporte_riesgo_cola.py", [], "lento"),     # más de una hora (bootstrap); exige memoria
    ("bbg/p33_simultaneidad_precedencia_tost.py", [], "base"),
    ("bbg/p34_fragilidad_alternativa.py", [], "base"),
    ("bbg/p35_cuantilica_spread.py", [], "lento"),
    ("bbg/p36_giv_granular.py", [], "base"),
    ("bbg/p37_mensual_fechado.py", [], "base"),
    ("bbg/p38_panel_ampliado.py", [], "base"),
    ("bbg/p39_eventos_respaldo.py", [], "base"),
    ("bbg/p40_tabla_compacta.py", [], "base"),
    ("bbg/p41_datos_resiliencia.py", [], "red"),
    ("bbg/p42_resiliencia_preregistrada.py", [], "base"),
    ("bbg/p43_revision_econometrica.py", [], "base"),
    ("bbg/p44_datos_macro.py", [], "red"),
    ("bbg/p45_macro_preregistrada.py", [], "base"),
    ("bbg/p45b_rezago_gar.py", [], "base"),
    ("bbg/p46_panel_bancos.py", [], "base"),
    ("bbg/p47_sensibilidad_motor.py", ["calcular", "rho"], "lento"),
    ("bbg/p47_sensibilidad_motor.py", ["calcular", "dp"], "lento"),
    ("bbg/p47_sensibilidad_motor.py", ["calcular", "ancha"], "lento"),
    ("bbg/p47_sensibilidad_motor.py", ["estimar"], "base"),
    ("bbg/p48_garantias.py", [], "base"),
    ("bbg/p49_concentracion_oi.py", [], "base"),
    ("bbg/p50_exposicion_soberana.py", [], "base"),
    ("bbg/p51_cobertura_sistema.py", [], "base"),
    ("bbg/p52_umbrales.py", [], "base"),
    ("bbg/p53_alerta_temprana.py", [], "base"),
    ("bbg/p55_medidas_sistemicas.py", [], "base"),
    ("bbg/p56_inferencia_conjunta.py", [], "base"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lentos", action="store_true")
    ap.add_argument("--red", action="store_true")
    ap.add_argument("--desde", default=None)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--solo-verificar", action="store_true")
    a = ap.parse_args()
    plan = [p for p in PASOS if p[2] == "base" or (p[2] == "lento" and a.lentos) or (p[2] == "red" and a.red)]
    if a.desde:
        i = next(k for k, p in enumerate(plan) if os.path.basename(p[0]).startswith(a.desde))
        plan = plan[i:]
    if a.listar:
        for s, args, t in plan:
            print(f"  {t:5s} {s} {' '.join(args)}")
        return
    os.makedirs(os.path.join(AQUI, "bbg", "_logs"), exist_ok=True)
    if not a.solo_verificar:
        for s, args, t in plan:
            log = os.path.join(AQUI, "bbg", "_logs", os.path.basename(s).replace(".py", "") + ("_" + "_".join(args) if args else "") + ".log")
            t0 = time.time()
            print(f"-> {s} {' '.join(args)}", flush=True)
            with open(log, "w", encoding="utf-8") as fh:
                r = subprocess.run([PY, s] + args, cwd=AQUI, stdout=fh, stderr=subprocess.STDOUT)
            print(f"   {'ok' if r.returncode == 0 else 'ERROR'} ({time.time() - t0:.0f} s; registro en {log})", flush=True)
            if r.returncode != 0:
                sys.exit(f"Falló {s}; ver {log}")
    r = subprocess.run([PY, "verificar_canonicos.py"], cwd=AQUI)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
