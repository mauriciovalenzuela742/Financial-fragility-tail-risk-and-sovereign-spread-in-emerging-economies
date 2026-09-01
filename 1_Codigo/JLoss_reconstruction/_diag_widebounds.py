# ¿Cuánto cambia JLoss si se amplía la cota superior del grid de pérdidas?
import numpy as np, pandas as pd
import jloss_engine as je

countries = ["china", "chile", "turkey", "mexico"]
base, _ = je.build_panel(countries, indir="_stage")
base = base.rename(columns={"JLoss": "JLoss_base"})[["countryname", "quarter", "JLoss_base"]]

je.LOSS_SUP = 0.20          # 4,8% -> 20% de la exposición
wide, _ = je.build_panel(countries, indir="_stage")
wide = wide.rename(columns={"JLoss": "JLoss_wide"})[["countryname", "quarter", "JLoss_wide"]]

m = base.merge(wide, on=["countryname", "quarter"])
m["ratio"] = m["JLoss_wide"] / m["JLoss_base"]
g = m.groupby("countryname").agg(
    JLoss_base_med=("JLoss_base", "median"),
    JLoss_wide_med=("JLoss_wide", "median"),
    ratio_med=("ratio", "median"),
    ratio_p90=("ratio", lambda s: s.quantile(0.9)),
).round(3)
with open("_diag_widebounds.out", "w", encoding="utf-8") as f:
    f.write("JLoss con grid [0.01, 0.048] (base) vs [0.01, 0.20] (wide)\n\n")
    f.write(g.to_string())
    f.write(f"\n\ncorr(base, wide) = {m[['JLoss_base','JLoss_wide']].corr().iloc[0,1]:.4f}\n")
    f.write(f"ratio wide/base: media={m['ratio'].mean():.3f}  p50={m['ratio'].median():.3f}  "
            f"min={m['ratio'].min():.3f}  max={m['ratio'].max():.3f}\n")
print("listo")
