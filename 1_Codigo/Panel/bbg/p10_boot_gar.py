# -*- coding: utf-8 -*-
"""
p10_boot_gar.py -- bootstrap de regresor generado: re-estima el GaR (primera
etapa, regresion cuantilica de panel con FE compartidos) en cada replica y
propaga esa incertidumbre a beta3 / beta3+beta4 (segunda etapa). Punto C1 del
plan de arbitro (`~/.claude/plans/arma-el-dag-de-moonlit-moonbeam.md`).

DISENO (block bootstrap POR PAIS -- la variante computacionalmente tratable):
  - La primera etapa (fit_pfe, `gar_engine.py`) estima PARAMETROS COMPARTIDOS
    entre los 18 paises del pool GaR: la funcion cuantil c_hat(tau) y la
    pendiente b_hat(tau) sobre (g_GDP, VIX, FCI_VIX_res). Los efectos fijos
    a_hat_i son especificos de cada pais y estan bien identificados con ~125
    trimestres propios cada uno -- no son el objeto de incertidumbre que este
    bootstrap busca propagar.
  - En cada replica b=1..B: se re-muestrea CON REEMPLAZO el conjunto de 18
    bloques-pais (la unidad de remuestreo es el pais completo, preservando su
    estructura temporal interna) y se re-ajusta el LP de regresion cuantilica
    de panel -> c_hat*_b, b_hat*_b (parametros COMPARTIDOS re-estimados).
  - Se proyecta el GaR de los 13 paises OBJETIVO (los del panel EMBI) usando
    c_hat*_b, b_hat*_b junto con su PROPIO a_hat_i (de la corrida real, SIN
    remuestrear).
  - Se re-estima beta3 (M2, muestra completa) y beta3+beta4 (Backstop /
    EMstress) sobre el panel Bloomberg real con este GaR-replica
    (reutilizando `with_gar`, `fit_m2`, `fit_crisis` de
    `p9_robustez_gar_nocdiff.py`).
  - sd(beta3*_{1..B}) = SE bootstrap que SI propaga el error de la primera
    etapa (a diferencia del SE de Driscoll-Kraay, que trata al GaR como dato
    fijo -- el problema clasico de "generated regressors", Pagan 1984).

NOTA DE FIDELIDAD: para que sea computable en horas (no dias, con 4 nucleos
locales) se usa n_tau=19 en vez de los 39 de la serie oficial -- el LP escala
~cuadraticamente en n_tau (39->~250s/ajuste, 19->~57s/ajuste). tau_min =
1/(19+1) = 0,05 coincide EXACTO con el nivel de interes (GaR=Q(0,05)): no hay
extrapolacion. `validar()` confirma que el ajuste UNICO (sin remuestrear) a
n_tau=19 reproduce beta3 muy cerca del oficial (n_tau=39) antes de lanzar las
B replicas.

Uso:
  python p10_boot_gar.py validar
  python p10_boot_gar.py boot [B] [workers]
"""
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
GARNC = os.path.abspath(os.path.join(HERE, "..", "..", "GaR", "individuals", "nlhpc_gar_all18"))
sys.path.insert(0, GARNC)
sys.path.insert(0, HERE)
import gar_engine as ge          # noqa: E402
import p9_robustez_gar_nocdiff as rgc  # noqa: E402

XLSX = os.path.join(GARNC, "GaR_panel_all18.xlsx")
DEP = "g_GDP"
INDEP = ("g_GDP", "VIX")
ORTH_DEP = ("FCI",)
ORTH_IND = ("VIX",)
H = 1
N_TAU = 19          # tau_min = 1/(N_TAU+1) = 0.05 -> sin extrapolacion en GaR=Q(0.05)
PROB = 0.05
OUT = os.path.join(HERE, "boot_gar_bbg.csv")
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
    """GaR de todas las filas de est_all cuyo pais este en a_hat_by_country,
    usando c_hat/b_hat COMPARTIDOS + el a_hat de ESE pais."""
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


def gar_to_beta3(gar_df, panel_bbg):
    dm = rgc.with_gar(panel_bbg, gar_df)
    m2 = rgc.fit_m2(dm)
    cr = rgc.fit_crisis(dm)
    return m2, cr


def true_fit(panel, last, n_tau=N_TAU):
    c_hat, b_hat, a_hat, p_names, est_all = fit_shared(panel, last, n_tau)
    gar_df = project_gar(est_all, p_names, c_hat, b_hat, a_hat, n_tau)
    return c_hat, b_hat, a_hat, p_names, est_all, gar_df


def validar():
    t0 = time.time()
    panel = load_panel()
    last = panel["_d"].max().strftime("%d/%m/%Y")
    c_hat, b_hat, a_hat, p_names, est_all, gar_df = true_fit(panel, last)
    panel_bbg = rgc.base_panel()
    m2, cr = gar_to_beta3(gar_df, panel_bbg)
    dt = time.time() - t0
    print(f"[validar n_tau={N_TAU}] tiempo={dt:.0f}s  N(M2)={m2['N']}  p_names={p_names}")
    print(f"  beta3 (M2, completa) = {m2['b3']:+.3f} (t={m2['t3']:+.2f}, p={m2['p3']:.3f})  "
          f"[oficial n_tau=39, GaR expansivo: +0.16 (p=0.26)]")
    print(f"  crisis: beta3(fuera)={cr['b3']:+.3f} (t={cr['t3']:+.2f})  "
          f"Backstop b3+b4={cr['sum_bk']:+.3f} (p={cr['sum_bk_p']:.3f})  "
          f"EMstress b3+b4={cr['sum_em']:+.3f} (p={cr['sum_em_p']:.3f})  "
          f"[oficial: +0.81 / -0.03 (p=0.77) / +1.05 (p<0.001)]")
    gar_df.to_csv(os.path.join(HERE, "gar_true_ntau19.csv"), index=False)
    print(f"Guardado: bbg/gar_true_ntau19.csv")
    return dt


# --------------------------------------------------------------------------- #
# Bootstrap -- una replica (funcion pura, sin estado de proceso: la usan tanto
# el camino serial (mismo proceso, footprint minimo) como cada worker de
# multiprocessing (via _replica_task, que solo envuelve el estado global).
# --------------------------------------------------------------------------- #

def _do_replica(seed, panel, a_hat0, p_names0, last, panel_bbg):
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
    except Exception as e:
        return dict(seed=seed, error=str(e))
    if p_names != p_names0:
        return dict(seed=seed, error=f"p_names cambiaron: {p_names}")
    est_all_orig, _ = ge.preprocess(panel, last, DEP, list(INDEP), list(ORTH_DEP), list(ORTH_IND), H)
    gar_df = project_gar(est_all_orig, p_names, c_hat, b_hat, a_hat0)
    m2, cr = gar_to_beta3(gar_df, panel_bbg)
    return dict(seed=seed, N=m2["N"], b3=m2["b3"], t3=m2["t3"], p3=m2["p3"],
               b1=m2["b1"], bD=m2["bD"],
               cr_N=cr["N"], cr_b3=cr["b3"], cr_t3=cr["t3"], cr_p3=cr["p3"],
               b4_bk=cr["b4_bk"], sum_bk=cr["sum_bk"], sum_bk_p=cr["sum_bk_p"],
               b4_em=cr["b4_em"], sum_em=cr["sum_em"], sum_em_p=cr["sum_em_p"])


# -- camino multiprocessing (Windows: spawn + initializer por worker) -- solo
# se usa si boot() se llama con workers>1; el camino serial de abajo evita
# por completo la sobrecarga de memoria de un segundo proceso.

def _init_worker(panel_pkl, a_hat0, p_names0, last):
    global _PANEL, _A0, _PNAMES0, _LAST, _PANEL_BBG
    _PANEL = pd.read_pickle(panel_pkl)
    _A0 = a_hat0
    _PNAMES0 = p_names0
    _LAST = last
    _PANEL_BBG = rgc.base_panel()


def _replica_task(seed):
    return _do_replica(seed, _PANEL, _A0, _PNAMES0, _LAST, _PANEL_BBG)


def summarize(df):
    ok = df[df.get("error").isna()] if "error" in df.columns else df
    print(f"\nReplicas OK: {len(ok)}/{len(df)}")
    for lbl, col in [("beta3 (M2, completa)", "b3"),
                     ("beta3 (fuera de crisis)", "cr_b3"),
                     ("beta3+beta4 Backstop", "sum_bk"),
                     ("beta3+beta4 EMstress", "sum_em")]:
        x = ok[col].dropna()
        se = x.std(ddof=1)
        lo, hi = np.percentile(x, [2.5, 97.5])
        print(f"  {lbl:28s} media={x.mean():+.3f}  SE_boot={se:.3f}  IC95 percentil=({lo:+.3f},{hi:+.3f})")


def segunda_etapa(gar_replicas_csv):
    """Toma el resultado de la PRIMERA ETAPA corrida en NLHPC
    (`p10_boot_gar_nlhpc.py boot`, fidelidad completa n_tau=39, columnas
    seed,country,quarter,GaR,error) y corre localmente la SEGUNDA ETAPA
    (beta3/beta4 por replica, PanelOLS+DK) -- trivial en tiempo/memoria, no
    requiere resolver ningun LP. Escribe/actualiza bbg/boot_gar_bbg.csv con el
    MISMO esquema que produce boot() local, asi summarize() y el resto del
    reporte no distinguen el origen de las replicas."""
    raw = pd.read_csv(gar_replicas_csv)
    panel_bbg = rgc.base_panel()
    done, prev_rows = _done_seeds()
    seeds = sorted(raw["seed"].dropna().astype(int).unique())
    pending = [s for s in seeds if s not in done]
    print(f"[segunda_etapa] {len(seeds)} replicas en {os.path.basename(gar_replicas_csv)}, "
          f"{len(done)} ya procesadas, {len(pending)} pendientes", flush=True)

    fieldnames = ["seed", "N", "b3", "t3", "p3", "b1", "bD",
                  "cr_N", "cr_b3", "cr_t3", "cr_p3",
                  "b4_bk", "sum_bk", "sum_bk_p", "b4_em", "sum_em", "sum_em_p", "error"]
    write_header = not os.path.exists(OUT)
    f = open(OUT, "a", newline="", encoding="utf-8")
    import csv
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    if write_header:
        writer.writeheader()

    for i, s in enumerate(pending, 1):
        sub = raw[raw["seed"] == s]
        err = sub["error"].dropna().astype(str)
        err = err[err != ""]
        if len(err) or sub["GaR"].isna().all():
            r = dict(seed=s, error=(err.iloc[0] if len(err) else "sin filas GaR"))
        else:
            gar_df = sub[["country", "quarter", "GaR"]].dropna(subset=["GaR"])
            m2, cr = gar_to_beta3(gar_df, panel_bbg)
            r = dict(seed=s, N=m2["N"], b3=m2["b3"], t3=m2["t3"], p3=m2["p3"],
                     b1=m2["b1"], bD=m2["bD"],
                     cr_N=cr["N"], cr_b3=cr["b3"], cr_t3=cr["t3"], cr_p3=cr["p3"],
                     b4_bk=cr["b4_bk"], sum_bk=cr["sum_bk"], sum_bk_p=cr["sum_bk_p"],
                     b4_em=cr["b4_em"], sum_em=cr["sum_em"], sum_em_p=cr["sum_em_p"])
        writer.writerow(r)
        if i % 25 == 0 or i == len(pending):
            print(f"  {i}/{len(pending)}", flush=True)
    f.close()
    print(f"Guardado: {os.path.basename(OUT)}")
    summarize(pd.read_csv(OUT))


def _done_seeds():
    """Semillas ya completadas en OUT (checkpoint) -- permite reanudar tras un
    corte (p.ej. el proceso muere por falta de memoria del sistema)."""
    if not os.path.exists(OUT):
        return set(), []
    df = pd.read_csv(OUT)
    return set(df["seed"].astype(int)), df.to_dict("records")


def boot(B=200, workers=2):
    import csv
    import multiprocessing as mp
    t0 = time.time()
    panel = load_panel()
    last = panel["_d"].max().strftime("%d/%m/%Y")

    done, prev_rows = _done_seeds()
    pending = [s for s in range(B) if s not in done]
    print(f"[boot] checkpoint: {len(done)}/{B} ya en {os.path.basename(OUT)} -- "
          f"faltan {len(pending)}", flush=True)
    if not pending:
        summarize(pd.DataFrame(prev_rows))
        return

    print(f"[boot] ajuste original (ancla de a_hat) ...", flush=True)
    c_hat0, b_hat0, a_hat0, p_names0, est_all0 = fit_shared(panel, last)
    print(f"[boot] B={B} workers={workers} n_tau={N_TAU} -- lanzando {len(pending)} pendientes ...",
          flush=True)

    fieldnames = ["seed", "N", "b3", "t3", "p3", "b1", "bD",
                  "cr_N", "cr_b3", "cr_t3", "cr_p3",
                  "b4_bk", "sum_bk", "sum_bk_p", "b4_em", "sum_em", "sum_em_p", "error"]
    write_header = not os.path.exists(OUT)
    f = open(OUT, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    if write_header:
        writer.writeheader()

    n_done = len(done)
    panel_bbg = rgc.base_panel()

    if workers <= 1:
        # Camino serial: MISMO proceso, sin multiprocessing -- footprint minimo.
        # Maquina con muy poca RAM libre (~600MB de 8GB): un segundo proceso
        # (incluso Pool(1)) ya duplica el import de numpy/scipy y el panel.
        for s in pending:
            r = _do_replica(s, panel, a_hat0, p_names0, last, panel_bbg)
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
            for r in pool.imap_unordered(_replica_task, pending):
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
    print(f"\n[boot] listo en {(time.time()-t0)/60:.1f} min. Guardado: bbg/boot_gar_bbg.csv")
    summarize(pd.read_csv(OUT))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "validar"
    if mode == "validar":
        validar()
    elif mode == "boot":
        B = int(sys.argv[2]) if len(sys.argv) > 2 else 120
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        boot(B, workers)
    elif mode == "segunda_etapa":
        csv_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(GARNC, "gar_replicas_nlhpc.csv")
        segunda_etapa(csv_path)
    else:
        print("uso: p10_boot_gar.py [validar|boot B workers|segunda_etapa ruta_csv]")
