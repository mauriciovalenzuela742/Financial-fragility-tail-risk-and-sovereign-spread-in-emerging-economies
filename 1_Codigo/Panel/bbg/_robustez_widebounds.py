# -*- coding: utf-8 -*-
"""
Robustez: theta bajo JLoss con grid de perdidas ANCHO [0.01, 0.20] (vs [0.01, 0.048]).
Re-corre el motor JLoss para los 14 paises de la muestra de estimacion, sustituye la
columna JLoss en el panel y re-estima M1/M2. Salida -> _robustez_widebounds.out
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
JLR = os.path.join(HERE, "..", "..", "JLoss_reconstruction")
sys.path.insert(0, JLR)
sys.path.insert(0, HERE)
import jloss_engine as je
from p2_regresiones import fit, row, CTRLS

PAISES = ["brazil", "chile", "china", "colombia", "indonesia", "malaysia", "mexico",
          "peru", "philippines", "southafrica", "turkey", "hungary", "poland", "pakistan"]
STAGE = os.path.join(JLR, "_stage")

lines = []
def log(s):
    print(s); lines.append(str(s))

je.LOSS_SUP = 0.20
wide, _ = je.build_panel(PAISES, indir=STAGE)
wide = wide.rename(columns={"JLoss": "JLoss_wide"})
wide["country"] = wide["countryname"].str.lower()
wide = wide[["country", "quarter", "JLoss_wide"]].dropna()

panel = pd.read_csv(os.path.join(HERE, "Panel_bloomberg.csv"))
m = panel.merge(wide, on=["country", "quarter"], how="left")
log(f"cobertura wide: {m['JLoss_wide'].notna().sum()} / {panel['JLoss'].notna().sum()} filas con JLoss")
log(f"corr(JLoss_base, JLoss_wide) = {m[['JLoss','JLoss_wide']].corr().iloc[0,1]:.4f}")
r = (m['JLoss_wide'] / m['JLoss']).dropna()
log(f"ratio wide/base: media={r.mean():.2f}  p50={r.median():.2f}\n")

def prep_from(df):
    d = df.copy()
    d["GaR_pp"] = d["GaR"] * 100.0
    if "ES" in d:
        d["ES_pp"] = d["ES"] * 100.0
    d["t"] = pd.PeriodIndex(d["quarter"], freq="Q").to_timestamp()
    d["year"] = pd.PeriodIndex(d["quarter"], freq="Q").year
    return d.dropna(subset=["EMBI_cds", "JLoss", "GaR_pp"]).copy()

ctr = [c for c in CTRLS if c in panel.columns and panel[c].notna().sum() > 50]

for lbl, jcol in [("JLoss BASE  [0.01,0.048]", "JLoss"),
                  ("JLoss WIDE  [0.01,0.20 ]", "JLoss_wide")]:
    d = m.copy()
    d["JLoss"] = d[jcol]
    d = prep_from(d)
    for spec, ex in [("M1 sin controles", []), ("M2 +controles", ctr)]:
        mm, _ = fit(d, ex, "dk")
        if mm is None:
            log(f"  {lbl} | {spec}: no estimable"); continue
        rr = row(mm, spec)
        log(f"  {lbl} | {spec:16s}  theta={rr['theta']:+.4f}  t={rr['t']:+.2f}  "
            f"p={rr['p']:.3f}  N={rr['N']}  b1(JLoss)={rr['b1']:+.3f}")
    log("")

with open(os.path.join(HERE, "_robustez_widebounds.out"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("listo -> _robustez_widebounds.out")
