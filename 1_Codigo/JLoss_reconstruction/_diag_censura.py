# Diagnóstico: ¿la cota superior del grid de pérdidas (LOSS_SUP=0.048) censura el VaR99?
import sys, numpy as np
import jloss_engine as je

hits = {"n": 0, "cap": 0, "floor": 0, "vals": []}
_orig = je.find_var99
def patched(lp):
    v = _orig(lp)
    hits["n"] += 1
    hits["vals"].append(v)
    if v >= je.LOSS_SUP - 1e-9:
        hits["cap"] += 1
    if v <= je.LOSS_INF + 1e-9:
        hits["floor"] += 1
    return v
je.find_var99 = patched

countries = ["china", "turkey", "brazil", "mexico", "chile", "indonesia"]
panel, qa = je.build_panel(countries, indir="_stage")
v = np.array(hits["vals"])
with open("_diag_censura.out", "w", encoding="utf-8") as f:
    f.write(f"grid VaR99 = [{je.LOSS_INF}, {je.LOSS_SUP}]  llamadas = {hits['n']}\n")
    f.write(f"en el TECHO (0.048): {hits['cap']} ({hits['cap']/max(hits['n'],1):.1%})\n")
    f.write(f"en el PISO  (0.010): {hits['floor']} ({hits['floor']/max(hits['n'],1):.1%})\n")
    f.write(f"VaR99 dist: p50={np.median(v):.4f} p90={np.percentile(v,90):.4f} "
            f"p99={np.percentile(v,99):.4f} max={v.max():.4f}\n\n")
    f.write(panel.groupby("countryname")["JLoss"].agg(["median", "max", "count"]).round(2).to_string())
    f.write("\n")
print("listo -> _diag_censura.out")
