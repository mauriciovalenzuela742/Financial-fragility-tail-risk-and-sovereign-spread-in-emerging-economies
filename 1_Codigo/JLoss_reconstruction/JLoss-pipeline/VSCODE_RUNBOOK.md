# Metodología paso a paso — correr los códigos de extracción en Visual Studio Code (desde cero)

Guía completa para ejecutar el pipeline JLoss con Visual Studio Code. No requiere
experiencia previa de programación más allá de seguir los pasos. Los comandos del terminal se
muestran para Windows (PowerShell) y macOS/Linux donde difieren.

---

## PASO 0 — Instalar lo básico (una sola vez)

1. **Python 3.11 o superior.** Descárgalo de https://www.python.org/downloads/
   - Windows: en el instalador, **marca "Add python.exe to PATH"** antes de "Install Now".
   - macOS: instálalo desde python.org o con Homebrew (`brew install python`).
   - Verifica en un terminal: `python --version` (Windows) o `python3 --version` (macOS/Linux).
2. **Visual Studio Code.** Descárgalo de https://code.visualstudio.com/ e instálalo.
3. **Extensiones de VS Code.** Abre VS Code → icono de extensiones (Ctrl+Shift+X) e instala:
   - **Python** (Microsoft)
   - **Jupyter** (Microsoft) — para abrir el notebook `JLoss_reconstruction_v8.ipynb`.

---

## PASO 1 — Crear la carpeta del proyecto y abrirla en VS Code

1. Crea una carpeta, p.ej. `JLoss-pipeline`, y copia dentro **todos los archivos** del repositorio:
   `jloss_common.py`, `book_pd.py`, todas las carpetas con los 19 `extract_<país>.py`, el notebook v8, y los `.md`.
2. En VS Code: **File → Open Folder…** y selecciona `JLoss-pipeline`.
3. Abre el terminal integrado: **Terminal → New Terminal** (o Ctrl+`). Trabajarás aquí.

---

## PASO 2 — Crear el entorno virtual e instalar dependencias

En el terminal integrado de VS Code, dentro de la carpeta del proyecto:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas numpy scipy matplotlib seaborn requests openpyxl "xlrd>=2.0.1" yfinance
```
> Si PowerShell bloquea el script de activación, ejecuta una vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y reintenta la activación.

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install pandas numpy scipy matplotlib seaborn requests openpyxl "xlrd>=2.0.1" yfinance
```

**Seleccionar el intérprete en VS Code:** Ctrl+Shift+P → "Python: Select Interpreter" → elige el que
diga `.../venv`. Así VS Code usa el entorno que acabas de crear (verás `(venv)` al inicio del prompt).

---

## PASO 3 — Conseguir las credenciales y los datos por país

Cada país tiene una de tres formas de acceso. Identifica la de cada uno (detalle en
`JLoss_update_plan.md`) y prepara lo necesario **antes** de correr el extractor.

**A) API directa (no requiere descarga manual):**
- **Chile (CMF):** registra una API key gratuita en https://api.cmfchile.cl y guárdala como variable
  de entorno antes de correr:
  - Windows: `$env:CMF_API_KEY = "4a2558ea9fd55e6ab971b7a133e1a8688fb07414"`
  - macOS/Linux: `export CMF_API_KEY="4a2558ea9fd55e6ab971b7a133e1a8688fb07414"`
- **Brasil (BCB Olinda):** sin clave; el extractor consulta la API directamente.
- **Colombia (Socrata):** sin clave; primero corre `python extract_colombia.py --discover` para
  obtener el `dataset_id` del dataset de balances y pásalo con `--dataset`.

**B) Descarga manual previa (guarda los archivos en una subcarpeta y apunta el extractor a ella):**
- **Perú (SBS):** descarga los Excel del Balance General de Banca Múltiple por período a `./sbs_xlsx/`.
- **México (CNBV):** exporta el Balance General desde el Portafolio de Información a un CSV/Excel.
- **Turquía (TBB), Argentina (BCRA), Sudáfrica (SARB BA900):** descarga los reportes/zip por período.
- **Hito 4 y 5 (Polonia, Indonesia, Malasia, Filipinas, Pakistán, Bulgaria, China, Egipto, Rusia,
  Panamá):** ensambla un archivo **long-format** con columnas exactamente: `bank, account, period,
  value` (una fila por banco-cuenta-período), desde el regulador o los estados de los bancos.

**C) Precios de mercado (automático):** los extractores bajan la capitalización de mercado vía
`yfinance` para los bancos con `ticker` definido. Los bancos sin ticker usan PD contable (book_pd).

> Importante: este pipeline corre en TU computador con internet abierto. Las APIs de los reguladores
> y de mercado no son accesibles desde entornos restringidos.

---

## PASO 4 — Confirmar los nombres de cuenta (una vez por país)

Los mapeos de cuenta (`ACCOUNT_MAP`) traen valores por defecto marcados como "confirmar". Antes de la
corrida masiva, verifica que los nombres coinciden con tu fuente:
- Chile: `python extract_chile.py --discover` lista las cuentas reales de la CMF.
- Brasil: `python extract_brazil.py --discover` lista los reportes Olinda.
- Resto: abre el `extract_<país>.py` en VS Code y ajusta las cadenas de `ACCOUNT_MAP["bonds"]`,
  `["tot_asset"]`, `["equity"]` para que contengan los nombres de cuenta de tu archivo (criterio del
  profesor: **bonos = deuda emitida = largo plazo; el resto = corto plazo**).

---

## PASO 5 — Correr los extractores

Con `(venv)` activo, ejecuta cada país. Ejemplos:
```bash
# API directa
python extract_chile.py    --start 1999 --end 2026
python extract_brazil.py   --start 2000 --end 2026
python extract_colombia.py --dataset <ID> --start 2000 --end 2026

# Descarga previa
python extract_peru.py   --dir ./sbs_xlsx --start 2001 --end 2026
python extract_mexico.py --file ./cnbv_export.csv --start 2000 --end 2026

# Long-format ensamblado (Hito 4 y 5 + Panamá)
python extract_indonesia.py --file ./indonesia_long.csv --start 2000 --end 2026
python extract_panama.py    --file ./panama_long.csv    --start 2000 --end 2026
# ...y así para cada país
```
Cada extractor genera tres archivos: `balance_<país>.csv`, `mktcap_<país>.csv`,
`coverage_<país>.csv`.

> Atajo: puedes ejecutar un script abierto en VS Code con el botón ▶ (Run Python File), pero para
> pasar argumentos (`--file`, `--start`, etc.) usa el terminal integrado como arriba.

---

## PASO 6 — Validar la reconciliación por país

Tras cada extracción, confirma que el criterio bonos-vs-resto cuadra. En el terminal:
```bash
python -c "import pandas as pd, jloss_common as jc; \
print(jc.reconcile_bonds_vs_rest(pd.read_csv('balance_chile.csv')))"
```
Debe dar `ok_rate` cercano a 1.0. Revisa también `coverage_<país>.csv` (fracción de activos del
sistema cubierta) y que ningún banco tenga `st_borrow` negativo o `bonds > total_liab` (señal de que
la partida de deuda emitida necesita ajuste local en ese país).

---

## PASO 7 — Consolidar al esquema del panel

```python
# guarda esto como consolidar.py y córrelo con: python consolidar.py
import pandas as pd, glob
bal = pd.concat([pd.read_csv(f) for f in glob.glob('balance_*.csv')], ignore_index=True)
mkt = pd.concat([pd.read_csv(f) for f in glob.glob('mktcap_*.csv')],  ignore_index=True)
bal['date'] = pd.to_datetime(bal['date']); mkt['date'] = pd.to_datetime(mkt['date'])
bal.to_csv('balance_all.csv', index=False); mkt.to_csv('mktcap_all.csv', index=False)
print('consolidado:', bal['countryname'].nunique(), 'paises,', len(bal), 'filas de balance')
```

---

## PASO 8 — Calcular PD y JLoss (ρ doble, PD de mercado + contable)

Sigue el `RUNBOOK.md` (pasos 4–8): PD de mercado para listados (`calc_merton_pd` del notebook v8),
PD contable calibrada para no listados (`book_pd`), fusión con `merge_pds`, y el motor `compute_jloss`
con ρ=0.4 y ρ estimado. El notebook `JLoss_reconstruction_v8.ipynb` se abre en VS Code (con la
extensión Jupyter) y se corre celda por celda con Shift+Enter.

---

## Solución de problemas frecuentes

- **`ModuleNotFoundError`** → el `(venv)` no está activo o falta instalar una librería: repite el
  PASO 2 y selecciona el intérprete `venv` (Ctrl+Shift+P → Python: Select Interpreter).
- **`Import xlrd failed`** → `pip install "xlrd>=2.0.1"` (para leer `.xls` antiguos).
- **`CMF_API_KEY` falta** → define la variable de entorno (PASO 3.A) en la MISMA sesión de terminal.
- **yfinance devuelve vacío para un ticker** → ese banco no tiene precio fiable; quedará con `ticker`
  None y usará PD contable. Es esperado para Pakistán, Panamá y varios bancos menores.
- **PowerShell no activa el venv** → `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **`reconcile_bonds_vs_rest` da ok_rate bajo** → revisa que `tot_asset` y `equity` se extrajeron
  (sin ellos no se puede calcular `total_liab`) y que la cadena de bonos en `ACCOUNT_MAP` coincide
  con el nombre real de la cuenta en tu archivo.
- **Acentos/encoding al leer CSV** → guarda los archivos fuente en UTF-8; si vienen en otra
  codificación, `pd.read_csv(f, encoding='latin-1')`.
