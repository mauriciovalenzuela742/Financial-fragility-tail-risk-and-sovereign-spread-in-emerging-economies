# -*- coding: utf-8 -*-
"""
p39_eventos_respaldo.py -- estudio de eventos diario en torno a los anuncios de líneas de respaldo
externo (mejora C12 de 4_Redaccion/evaluacion_experta.md). Se corren exactamente estas pruebas y se
reportan todas:

El acceso a las líneas swap de la Reserva Federal y a la Línea de Crédito Flexible (FCL) del FMI es
endógeno al riesgo, de modo que la comparación trimestral entre economías con y sin acceso no
identifica su efecto. Con datos diarios se mira lo que ocurre alrededor de la fecha del anuncio,
donde el resto de los determinantes cambia poco. Nueve eventos país-fecha:
  Fed, 29-oct-2008: Brasil y México.     Fed, 19-mar-2020: Brasil y México.
  FCL: México 17-abr-2009, Polonia 6-may-2009, Colombia 11-may-2009, Perú 28-may-2020,
       Chile 29-may-2020 (fechas de aprobación del Directorio del FMI).

  1. Spread anormal: cambio acumulado de ln EMBI del país menos el cambio medio de las demás economías
     del panel sin respaldo anunciado ese día (modelo de mercado con beta 1), en las ventanas
     [-5,-1], [0,+1], [0,+5] y [0,+10] días hábiles, en puntos porcentuales.
  2. Desacople (con diferencia en diferencias frente a las economías sin línea, misma fecha, para no
     confundirlo con la normalización que sigue a cualquier pico de estrés): beta de la regresión diaria de d ln EMBI del país sobre el retorno del índice de
     capitalización de sus bancos (los mismos de JLoss), en los 60 días hábiles previos frente a los 60
     posteriores (excluido el día del anuncio). Si el respaldo corta el vínculo banca-soberano, la beta
     (negativa: bancos que caen, spread que sube) debería acercarse a cero.
Inferencia por placebo: para cada evento, las mismas medidas en 999 fechas al azar del mismo país
(a más de 30 días hábiles de cualquier evento); p unilateral = fracción de placebos con un valor al
menos tan favorable a la hipótesis. Para el promedio de los nueve eventos, cada réplica sortea una
fecha placebo por evento.

Simplificaciones: el índice bancario es la suma de las capitalizaciones (incluye emisiones); la FCL de
2009 se anunció como solicitud días antes de la aprobación, lo que la ventana [-5,-1] permite ver.

Salida: bbg/paper_p39_numeros.csv. Reutiliza p32 (diccionario de cifras).
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
import pandas as pd

import p32_aporte_riesgo_cola as p32
import p37_mensual_fechado as p37

NUM = p32.NUM
BBG = p37.BBG
EVENTOS = [("brazil", "2008-10-29", "fed08"), ("mexico", "2008-10-29", "fed08"),
           ("brazil", "2020-03-19", "fed20"), ("mexico", "2020-03-19", "fed20"),
           ("mexico", "2009-04-17", "fcl09"), ("poland", "2009-05-06", "fcl09"),
           ("colombia", "2009-05-11", "fcl09"), ("peru", "2020-05-28", "fcl20"),
           ("chile", "2020-05-29", "fcl20")]
VENT = {"pre": (-5, -1), "d01": (0, 1), "d05": (0, 5), "d10": (0, 10)}
L = 60
R = 999


def num(k, v):
    NUM[k] = float(v)


def datos():
    e = pd.read_excel(p37.EMBI_XLSX); e["Fecha"] = pd.to_datetime(e["Fecha"])
    y = pd.DataFrame({c: np.log(e.set_index("Fecha")[col]) for c, col in p37.PAISES.items()}).sort_index()
    dy = y.diff()
    bank = {}
    for c in p37.PAISES:
        m = pd.read_csv(os.path.join(BBG, c, f"mktcap_{c}.csv"), parse_dates=["date"]).dropna(subset=["mktcap"])
        w = m.pivot_table(index="date", columns="bankname", values="mktcap")
        r = np.log(w).diff()                                   # retorno por banco
        wt = w.shift(1).div(w.shift(1).sum(axis=1), axis=0)     # pesos del día anterior
        bank[c] = (r * wt).sum(axis=1, min_count=1)
    rb = pd.DataFrame(bank).reindex(dy.index)
    return dy, rb


def car(dy, c, t0, controles, a, b):
    idx = dy.index
    if t0 not in idx:
        t0 = idx[idx.searchsorted(t0)]
    i = idx.get_loc(t0)
    w = dy.iloc[i + a:i + b + 1]
    return float((w[c] - w[controles].mean(axis=1)).sum() * 100)


def beta_cambio(dy, rb, c, t0):
    idx = dy.index
    if t0 not in idx:
        t0 = idx[idx.searchsorted(t0)]
    i = idx.get_loc(t0)
    def beta(sl):
        z = pd.concat([dy[c].iloc[sl], rb[c].iloc[sl]], axis=1).dropna()
        if len(z) < 30 or z.iloc[:, 1].var() == 0:
            return np.nan
        return float(np.cov(z.iloc[:, 0], z.iloc[:, 1])[0, 1] / z.iloc[:, 1].var())
    return beta(slice(i - L, i)), beta(slice(i + 1, i + L + 1))


def main():
    dy, rb = datos()
    fechas_ev = {pd.Timestamp(f) for _, f, _ in EVENTOS}
    tratados = {}
    for c, f, _ in EVENTOS:
        tratados.setdefault(pd.Timestamp(f), set()).add(c)
    rng = np.random.default_rng(39)
    pos_ev = [dy.index.searchsorted(f) for f in fechas_ev]
    obs, plac = {}, {}
    for c, f, tag in EVENTOS:
        t0 = pd.Timestamp(f)
        ctrl = [k for k in p37.PAISES if k not in tratados[t0] and dy[k].iloc[dy.index.searchsorted(t0) - 15:
                                                                              dy.index.searchsorted(t0) + 15].notna().sum() > 15]
        key = f"{c}_{tag}"
        num(f"ev_{key}_n_control", len(ctrl))
        o = {v: car(dy, c, t0, ctrl, *ab) for v, ab in VENT.items()}
        b0, b1 = beta_cambio(dy, rb, c, t0)
        o["beta_pre"], o["beta_post"] = b0, b1
        o["dbeta"] = b1 - b0 if np.isfinite(b0) and np.isfinite(b1) else np.nan
        # diferencia en diferencias: cambio de beta del tratado menos el medio de los controles, misma fecha
        dctrl = []
        for k in ctrl:
            q0, q1 = beta_cambio(dy, rb, k, t0)
            if np.isfinite(q0) and np.isfinite(q1):
                dctrl.append(q1 - q0)
        o["dbeta_ctrl"] = float(np.mean(dctrl)) if dctrl else np.nan
        o["dbeta_rel"] = o["dbeta"] - o["dbeta_ctrl"]
        obs[key] = o
        for v, val in o.items():
            num(f"ev_{key}_{v}", val)
        # placebos: fechas del mismo país con dato, lejos de todo evento
        valid = np.where(dy[c].notna().values & rb[c].notna().values)[0]
        valid = valid[(valid > L + 10) & (valid < len(dy) - L - 12)]
        valid = np.array([p for p in valid if min(abs(p - q) for q in pos_ev) > 30])
        ps = {v: [] for v in list(VENT) + ["dbeta"]}
        for p in rng.choice(valid, size=R, replace=False):
            tp = dy.index[p]
            cc = [k for k in ctrl if pd.notna(dy[k].iloc[p])]
            for v, ab in VENT.items():
                ps[v].append(car(dy, c, tp, cc, *ab))
            q0, q1 = beta_cambio(dy, rb, c, tp)
            ps["dbeta"].append(q1 - q0 if np.isfinite(q0) and np.isfinite(q1) else np.nan)
        plac[key] = {v: np.array(x, float) for v, x in ps.items()}
        for v in VENT:
            num(f"ev_{key}_{v}_p", (1 + (plac[key][v] <= o[v]).sum()) / (R + 1))    # se espera una caída
        pb = plac[key]["dbeta"][np.isfinite(plac[key]["dbeta"])]
        if np.isfinite(o["dbeta"]):
            num(f"ev_{key}_dbeta_p", (1 + (pb >= o["dbeta"]).sum()) / (len(pb) + 1))  # beta negativa que sube
        print(f"  {key}: CAR[0,5] = {o['d05']:+.1f} pp; beta {b0:+.3f} -> {b1:+.3f}", flush=True)
    # promedio de los nueve eventos y por grupo
    grupos = {"todos": list(obs), "fed": [k for k in obs if "fed" in k], "fcl": [k for k in obs if "fcl" in k]}
    for g, ks in grupos.items():
        for v in ["dbeta_ctrl", "dbeta_rel"]:
            vals = np.array([obs[k][v] for k in ks], float)
            num(f"prom_{g}_{v}", np.nanmean(vals)); num(f"prom_{g}_{v}_n_pos", int(np.nansum(vals > 0)))
        for v in list(VENT) + ["dbeta"]:
            vals = np.array([obs[k][v] for k in ks], float)
            m = np.nanmean(vals)
            sims = np.nanmean(np.column_stack([plac[k][v] for k in ks]), axis=1)
            num(f"prom_{g}_{v}", m)
            p = (1 + (sims >= m).sum()) / (R + 1) if v == "dbeta" else (1 + (sims <= m).sum()) / (R + 1)
            num(f"prom_{g}_{v}_p", p)
        num(f"prom_{g}_n", len(ks))
    out = os.path.join(HERE, "paper_p39_numeros.csv")
    pd.Series(NUM, name="valor").rename_axis("clave").to_csv(out)
    for k, v in NUM.items():
        if k.startswith("prom_") or k.endswith("_d05") or k.endswith("_dbeta") or k.endswith("_pre"):
            print(f"  {k:30s} {v: .4f}")
    print("->", out)


if __name__ == "__main__":
    main()
