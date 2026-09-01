# Solo el motor: JLoss con malla ancha [0.01, 0.20] -> Panel_JLoss_wide.csv
# Escribe país por país para sobrevivir a un kill.
import os, sys, csv
import jloss_engine as je

je.LOSS_SUP = 0.20
PAISES = ["brazil", "chile", "china", "colombia", "indonesia", "malaysia", "mexico",
          "peru", "philippines", "southafrica", "turkey", "hungary", "poland", "pakistan"]
OUT = os.path.join(os.path.dirname(__file__), "Panel_JLoss_wide.csv")

# reusar el bucle interno de build_panel por país
first = not os.path.exists(OUT)
done = set()
if not first:
    with open(OUT) as f:
        done = {r["countryname"] for r in csv.DictReader(f)}

for c in PAISES:
    if c in done:
        print(f"{c}: ya está, salto"); continue
    try:
        panel, _ = je.build_panel([c], indir=os.path.join(os.path.dirname(__file__), "_stage"))
    except Exception as e:
        print(f"{c}: ERROR {e}"); continue
    panel = panel[["countryname", "quarter", "JLoss", "n_banks", "below_min_banks"]]
    panel.to_csv(OUT, mode="a", header=first, index=False)
    first = False
    print(f"{c}: {len(panel)} filas escritas", flush=True)
print("MOTOR WIDE COMPLETO ->", OUT)
