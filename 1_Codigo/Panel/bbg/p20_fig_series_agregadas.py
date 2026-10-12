# -*- coding: utf-8 -*-
"""
p20_fig_series_agregadas.py -- series de tiempo agregadas de JLoss y del riesgo de cola.

Pedido del profesor guia (predefensa, 2026-10-09): mostrar las variables JLoss y GaR como series de
tiempo, en forma agregada y con la ventana mas larga posible, antes de las regresiones, para ver que
tienen sentido economico (saltan en las crisis). Para cada trimestre: mediana transversal y banda
p25-p75 entre los paises del panel con dato; sombreado: crisis financiera global, estres emergente
de 2015-16 y pandemia.

Salida: paper_empirico/figuras/fig_series_agregadas_embiext.{pdf,png}. Reutiliza la paleta y el
guardado de p13.
"""
import os
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("JLOSS_PANEL_CSV", os.path.join(HERE, "Panel_bloomberg_embiext.csv"))
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(HERE))

import pandas as pd
import matplotlib.pyplot as plt

import p13_figuras_paper as p13
import p9b_bateria_crisis as p9b

PAISES = ["brazil", "chile", "china", "colombia", "india", "indonesia", "malaysia", "mexico", "peru",
          "philippines", "poland", "southafrica", "turkey"]
EPISODIOS = [(p9b.GFC, "Crisis financiera global"), (p9b.EM1516, "Estrés emergente"), (p9b.COVID, "Pandemia")]


def main():
    d = pd.read_csv(os.environ["JLOSS_PANEL_CSV"])
    d = d[d["country"].isin(PAISES)].copy()
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    d["D"] = -d["GaR"] * 100.0
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6))
    for ax, col, tit, ylab, color in (
            (axes[0], "JLoss", "Fragilidad bancaria (JLoss)", "% de la exposición", p13.BLUE),
            (axes[1], "D", "Riesgo de cola del crecimiento (D = −GaR)", "puntos porcentuales", p13.RED)):
        s = d.dropna(subset=[col])
        g = s.groupby("t")[col]
        n = g.count()
        q = pd.DataFrame({"med": g.median(), "p25": g.quantile(0.25), "p75": g.quantile(0.75)})[n >= 5]
        ax.fill_between(q.index, q["p25"], q["p75"], color=color, alpha=0.18, lw=0, label="p25–p75 entre países")
        ax.plot(q.index, q["med"], color=color, lw=1.8, label="mediana")
        for qs, _ in EPISODIOS:
            t0 = pd.Period(qs[0], freq="Q").to_timestamp()
            t1 = pd.Period(qs[-1], freq="Q").to_timestamp(how="end")
            ax.axvspan(t0, t1, color=p13.INK2, alpha=0.10, lw=0)
        ax.set_title(tit, fontsize=10); ax.set_ylabel(ylab)
        ax.legend(frameon=False, fontsize=7, loc="upper left")
        print(f"  {col}: {q.index.min().date()} .. {q.index.max().date()}  ({len(q)} trimestres)")
    p13.save(fig, "fig_series_agregadas_embiext")


if __name__ == "__main__":
    main()
