# -*- coding: utf-8 -*-
"""
p10_boot_gar_nlhpc.py -- version NLHPC (autocontenida, fidelidad completa,
solo PRIMERA ETAPA) del bootstrap de regresor generado del GaR. Punto C1 del
plan de arbitro (`~/.claude/plans/arma-el-dag-de-moonlit-moonbeam.md`).

Misma logica que `1_Codigo/Panel/bbg/p10_boot_gar.py` (que corrio local con
n_tau=19 reducido y murio repetidamente por falta de RAM del sistema --
maquina de 8GB con ~600MB libres de base). Esta version:
  - usa n_tau=39 (el de la serie OFICIAL de la tesis, no la aproximacion
    reducida) y B=500 por defecto (ajustable);
  - SOLO hace la PRIMERA ETAPA (re-muestreo + regresion cuantilica de panel
    -> GaR-replica para los 13 paises del panel EMBI). NO corre la segunda
    etapa (regresion beta3/beta4) aqui -- eso requiere `linearmodels`, que el
    venv_gar de NLHPC (solo numpy/scipy/pandas/openpyxl) no tiene, y es
    computacionalmente trivial (segundos, no horas), asi que se deja para
    correr LOCAL sobre el resultado de este job:
        python p10_boot_gar.py segunda_etapa <ruta a gar_replicas_nlhpc.csv>
  - checkpoint/resume igual que `run_gar_all18_noCDIFF.sbatch`: si el job
    corta por walltime, reenviar el mismo sbatch, retoma desde
    `gar_replicas_nlhpc.csv` (una fila por pais-trimestre-replica; una
    replica se considera terminada si su `seed` ya aparece en el archivo).

DISENO (ver docstring completo en la version local `p10_boot_gar.py`):
  - Primera etapa: c_hat(tau), b_hat(tau) COMPARTIDOS entre los 18 paises del
    pool GaR (regresion cuantilica de panel con FE, `gar_engine.fit_pfe`).
  - B replicas: se re-muestrea CON REEMPLAZO el conjunto de 18 bloques-pais
    (bootstrap de bloques, unidad = pais completo) y se re-ajusta el LP ->
    c_hat*_b, b_hat*_b.
  - Se proyecta el GaR de los 13 paises del panel EMBI usando c_hat*_b,
    b_hat*_b + su PROPIO a_hat_i (de la corrida real, sin remuestrear -- bien
    identificado con ~125 trimestres propios, no es el objeto de
    incertidumbre que este bootstrap propaga).

REQUIERE junto a este script (misma carpeta):
  - GaR_panel_all18.xlsx    (ya deberia estar aqui)
  - gar_engine.py           (ya deberia estar aqui)

Uso:
  python p10_boot_gar_nlhpc.py validar
  python p10_boot_gar_nlhpc.py boot [B] [workers]
"""
import csv
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gar_engine as ge  # noqa: E402

XLSX = os.path.join(HERE, "GaR_panel_all18.xlsx")
DEP = "g_GDP"
INDEP = ("g_GDP", "VIX")
ORTH_DEP = ("FCI",)
ORTH_IND = ("VIX",)
H = 1
N_TAU = 39          # fidelidad completa (la serie oficial de la tesis)
PROB = 0.05
OUT = os.path.join(HERE, "gar_replicas_nlhpc.csv")
PANEL_PKL = os.path.join(HERE, "_boot_panel_tmp.pkl")


def load_panel():
    p = pd.read_excel(XLSX, sheet_name="Panel")
    p = p.dropna(subset=["Country"]).copy()
    p["_d"] = pd.to_datetime(p["Date"], format="%d/%m/%Y")
    return p


def fit_shared(panel_slice, last, n_tau=N_TAU):
    est_all, orth_vars = ge.preprocess(panel_slice, last, DEP, list(INDEP),
                                       list(ORTH_DEP), list(ORTH_IND), H)
    p_names = list(INDEP) + orth_vars
    est = est_all[est_all[["future_dep_var"] + p_names].notna().all(axis=1)].copy()
    c_hat, b_hat, a_hat = ge.fit_pfe(est, p_names, n_tau)
    return c_hat, b_hat, a_hat, p_names, est_all


def project_gar(est_all, p_names, c_hat, b_hat, a_hat_by_country, n_tau=N_TAU, prob=PROB):
    taus = np.arange(1, n_tau + 1) / (n_tau + 1)
    rows = []
    for _, row in est_all.iterrows():
        c = row["N_Country"]
        if pd.isna(c):
            continue
        c = int(c)
        if c not in a_hat_by_country:
            continue
        xv = row[p_names].values.astype(float)
        if np.isnan(xv).any():
            continue
        Q = c_hat + (xv @ b_hat.T) + a_hat_by_country[c]
        d = ge.gar_from_quantiles(Q, taus, prob)
        q = row["Date"] if not isinstance(row["Date"], str) else pd.to_datetime(row["Date"], format="%d/%m/%Y")
        q = pd.Timestamp(q)
        rows.append({"country": str(row["Country"]).lower(),
                     "quarter": f"{q.year}Q{(q.month - 1) // 3 + 1}", "GaR": d["GaR"]})
    return pd.DataFrame(rows).dropna(subset=["GaR"])


def validar():
    t0 = time.time()
    panel = load_panel()
    last = panel["_d"].max().strftime("%d/%m/%Y")
    c_hat, b_hat, a_hat, p_names, est_all = fit_shared(panel, last)
    gar_df = project_gar(est_all, p_names, c_hat, b_hat, a_hat)
    dt = time.time() - t0
    print(f"[validar n_tau={N_TAU}] tiempo={dt:.0f}s  filas GaR={len(gar_df)}  p_names={p_names}")
    gar_df.to_csv(os.path.join(HERE, "gar_true_ntau39_nlhpc.csv"), index=False)
    print("Guardado: gar_true_ntau39_nlhpc.csv  "
          "(comparar con bbg/gar_true_ntau19.csv y con el GaR oficial expansivo)")
    return dt


def _do_replica(seed, panel, a_hat0, p_names0, last):
    """Devuelve una lista de filas (seed,country,quarter,GaR) o una fila de
    error (seed,country=None,quarter=None,GaR=NaN,error=...)."""
    rng = np.random.default_rng(seed)
    country_ids = sorted(panel["N_Country"].dropna().unique().astype(int))
    draw = rng.choice(country_ids, size=len(country_ids), replace=True)
    blocks = []
    for slot, c in enumerate(draw, start=1):
        b = panel[panel["N_Country"] == c].copy()
        b["N_Country"] = slot
        b["Country"] = f"BOOT{slot}"
        blocks.append(b)
    boot_panel = pd.concat(blocks, ignore_index=True)
    try:
        c_hat, b_hat, a_hat, p_names, _ = fit_shared(boot_panel, last)
        if p_names != p_names0:
            raise RuntimeError(f"p_names cambiaron: {p_names}")
        est_all_orig, _ = ge.preprocess(panel, last, DEP, list(INDEP), list(ORTH_DEP), list(ORTH_IND), H)
        gar_df = project_gar(est_all_orig, p_names, c_hat, b_hat, a_hat0)
    except Exception as e:
        return [dict(seed=seed, country=None, quarter=None, GaR=np.nan, error=str(e))]
    gar_df["seed"] = seed
    gar_df["error"] = ""
    return gar_df[["seed", "country", "quarter", "GaR", "error"]].to_dict("records")


def _init_worker(panel_pkl, a_hat0, p_names0, last):
    global _PANEL, _A0, _PNAMES0, _LAST
    _PANEL = pd.read_pickle(panel_pkl)
    _A0 = a_hat0
    _PNAMES0 = p_names0
    _LAST = last


def _replica_task(seed):
    return _do_replica(seed, _PANEL, _A0, _PNAMES0, _LAST)


def _done_seeds():
    if not os.path.exists(OUT):
        return set()
    df = pd.read_csv(OUT, usecols=["seed"])
    return set(df["seed"].astype(int))


def boot(B=500, workers=8):
    import multiprocessing as mp
    t0 = time.time()
    panel = load_panel()
    last = panel["_d"].max().strftime("%d/%m/%Y")

    done = _done_seeds()
    pending = [s for s in range(B) if s not in done]
    print(f"[boot] checkpoint: {len(done)}/{B} ya en {os.path.basename(OUT)} -- "
          f"faltan {len(pending)}", flush=True)
    if not pending:
        print("Nada pendiente -- correr la segunda etapa local con "
              "p10_boot_gar.py segunda_etapa gar_replicas_nlhpc.csv")
        return

    print("[boot] ajuste original (ancla de a_hat) ...", flush=True)
    c_hat0, b_hat0, a_hat0, p_names0, est_all0 = fit_shared(panel, last)
    print(f"[boot] B={B} workers={workers} n_tau={N_TAU} -- lanzando {len(pending)} pendientes ...",
          flush=True)

    fieldnames = ["seed", "country", "quarter", "GaR", "error"]
    write_header = not os.path.exists(OUT)
    f = open(OUT, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    if write_header:
        writer.writeheader()

    n_done = len(done)
    if workers <= 1:
        for s in pending:
            for r in _do_replica(s, panel, a_hat0, p_names0, last):
                writer.writerow(r)
            f.flush()
            n_done += 1
            el = time.time() - t0
            n_this = n_done - len(done)
            eta = el / n_this * (len(pending) - n_this) if n_this else float("nan")
            print(f"  {n_done}/{B}  elapsed={el/60:.1f}min  eta={eta/60:.1f}min", flush=True)
    else:
        panel.to_pickle(PANEL_PKL)
        with mp.Pool(workers, initializer=_init_worker, initargs=(PANEL_PKL, a_hat0, p_names0, last)) as pool:
            for rows in pool.imap_unordered(_replica_task, pending):
                for r in rows:
                    writer.writerow(r)
                f.flush()
                n_done += 1
                el = time.time() - t0
                n_this = n_done - len(done)
                eta = el / n_this * (len(pending) - n_this) if n_this else float("nan")
                print(f"  {n_done}/{B}  elapsed={el/60:.1f}min  eta={eta/60:.1f}min", flush=True)
    f.close()

    if os.path.exists(PANEL_PKL):
        os.remove(PANEL_PKL)
    print(f"\n[boot] listo en {(time.time()-t0)/60:.1f} min. Guardado: {os.path.basename(OUT)}")
    print("Siguiente paso (LOCAL): python p10_boot_gar.py segunda_etapa gar_replicas_nlhpc.csv")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "validar"
    if mode == "validar":
        validar()
    elif mode == "boot":
        B = int(sys.argv[2]) if len(sys.argv) > 2 else 500
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        boot(B, workers)
    else:
        print("uso: p10_boot_gar_nlhpc.py [validar|boot B workers]")
