# Instructivo: calcular FCI para el resto de países

`fci_engine.py` (en `individuals/fci_engine.py`) ya está validado contra el código R. Para cada país nuevo:

## 1. Verificar formato de los 4 insumos

En `individuals/<PAIS>/` deben existir, con estos nombres y convenciones exactas:

| Archivo | Frecuencia | Formato fecha | Columnas |
|---|---|---|---|
| `CPI_<PAIS>.csv` | diaria | DD/MM/YYYY | `DATES,CPI` |
| `Ryr_<PAIS>.csv` | diaria | DD/MM/YYYY | `DATES,Ryr` |
| `STX_<PAIS>.csv` | diaria | DD/MM/YYYY | `DATES,STX` |
| `rEER_<PAIS>.csv` | mensual | YYYYMM | `DATES,rEER` |

Sin comillas envolviendo la fila completa, sin columnas `;;;` sobrantes, sin doble header. Validar con:

```python
import pandas as pd
for v in ["CPI","Ryr","STX","rEER"]:
    df = pd.read_csv(f"individuals/<PAIS>/{v}_<PAIS>.csv", nrows=5)
    print(v, df.columns.tolist(), df.shape)   # debe dar 2 columnas, no 1
```

Si sale 1 sola columna (tipo `"DATES,STX"`), el archivo viene con la fila entera entre comillas — hay que limpiarlo (extraer fecha+valor con regex, como se hizo esta sesión para BRAZIL/CHILE/PERU). Revisar también fechas futuras o duplicadas antes de seguir (`pd.to_datetime(...).duplicated().sum()`).

**Bloqueante conocido:** ARGENTINA y SAUDIARABIA no tienen `Ryr` (sin fuente pública de bono soberano 10Y) — el FCI no se puede calcular para esos dos hasta conseguir esa serie.

## 2. Correr el engine

```python
import sys; sys.path.insert(0, "individuals")
import fci_engine as fe

paises = ["BULGARIA","CHINA","HUNGARY","INDIA","INDONESIA","MALAYSIA",
          "PAKISTAN","PHILIPPINES","POLAND","RUSSIA","SOUTHAFRICA",
          "SOUTHKOREA","THAILAND","TURKEY"]   # excluye ARGENTINA/SAUDIARABIA

for pais in paises:
    try:
        df = fe.compute_fci(
            country_dir=f"individuals/{pais}", country=pais,
            ref_dir="individuals/US", ref_country="US",
            initial="1990-01-01",
            final="2026-05-31",   # tope = ultimo mes con rEER real (ver paso 3)
        )
        print(pais, "OK", df.shape, df.DATES.max().date())
    except Exception as e:
        print(pais, "ERROR", e)
```

## 3. Ajustar la fecha `final`

El tope real es el **último mes con dato real de `rEER`** (no inventado). Revisar antes:

```python
r = pd.read_csv(f"individuals/{pais}/rEER_{pais}.csv")
print(r.iloc[-1])   # o el primero, según orden
```

Usar ese mes como `final`. Si se pasa una fecha posterior, el engine arrastra el último valor de rEER como constante (interpolación de borde) y contamina esos meses con datos ficticios.

## 4. Guardar el resultado

Mismo formato que los 5 países ya hechos (`DATES,FCI`, entre comillas, orden descendente, DD/MM/YYYY):

```python
out = df[["DATES","FCI"]].sort_values("DATES", ascending=False)
out["DATES"] = out["DATES"].dt.strftime("%d/%m/%Y")
with open(f"individuals/{pais}/FCI_{pais}.csv", "w", newline="\r\n") as f:
    f.write('"DATES","FCI"\n')
    for d, v in zip(out.DATES, out.FCI):
        f.write(f'"{d}",{v}\n')
```

## 5. Verificación mínima antes de dar por bueno

- Sin fechas futuras a la fecha de corte.
- Sin huecos de meses dentro de la serie (`diff` en días ≈ 28-31).
- Punto de arranque razonable: el engine necesita ~10 años de historia diaria antes de dar el primer valor no-NaN (ventana `lagTilde`/`timeFrame`), así que países con series cortas van a arrancar tarde.
