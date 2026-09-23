# Reproducibilidad de punta a punta — capítulo empírico (tesis vigente)

*Instructivo establecido el 2026-09-18, tras auditar estáticamente todo el pipeline vigente
(scripts `1_Codigo/Panel/bbg/p0..p10`, motor JLoss, motor GaR, extracción Bloomberg y
compilación de `4_Redaccion/tesis/`) y corregir los tres hallazgos que rompían la
reproducibilidad. Complementa a [`../README.md`](../README.md) (resumen + comandos) y a
[`CONTROL_DE_VERSIONES.md`](CONTROL_DE_VERSIONES.md) (qué archivo es vigente). Este documento
responde una pregunta distinta: **si alguien clona el repo hoy, ¿hasta dónde puede llegar?**

Alcance: la cadena vigente del **capítulo empírico** (Cap. 2, `paper2_empirico.tex`) y de la
**tesis ensamblada** (`main.tex`). No audita el legado (`v0/`, `Stata_Sov_Risk/`, EDA/regresiones
`all17`/`extended_11` pre-Bloomberg) ni la línea teórica de organización industrial
(`4_Redaccion/modelo OI/`), que está pausada por decisión del comité (§0 de
`CONTROL_DE_VERSIONES.md`) y no aporta números al resultado central.

---

## 0. Frontera real de reproducibilidad

Tres cosas **no se pueden reproducir sin acceso especial**, sin importar qué tan bien esté el
código. Las tres ya están mitigadas porque su *output* quedó congelado y commiteado en git —
un tercero sin ese acceso puede reproducir el 100% de los números reportados en la tesis
arrancando *después* de estos tres pasos:

| Bloqueador | Dónde se necesita | Mitigación ya en el repo |
|---|---|---|
| **Bloomberg Terminal + licencia `blpapi`/`xbbg`** | `1_Codigo/Bloomberg_extraction/` (balances, capitalización bursátil, macro de 20 países) | Los 40 CSV ya extraídos (`output/<pais>/balance_*.csv`, `mktcap_*.csv`) y `output_macro/` están commiteados. |
| **Cluster NLHPC** | Primera etapa del bootstrap de regresor generado C1 (`1_Codigo/GaR/individuals/nlhpc_gar_all18/p10_boot_gar_nlhpc.py`, B=500, ~172 min) | `gar_replicas_nlhpc.csv` (700.000 filas) ya commiteado (commit `4a4ffec`). La segunda etapa (`p10_boot_gar.py segunda_etapa`) es local y trivial. |
| **R** (no instalado en este entorno) | `crisis_interaccion.R`, `bateria_regresiones.R`, `eda_panel_bloomberg.R` — validación cruzada de los scripts Python equivalentes | No bloquea nada: son de **registro**, no de cómputo primario. Python (`p9_crisis_interaccion.py`, `p8_bateria_regresiones.py`) es la cadena vigente y reproduce los mismos números a 4 decimales (verificado y documentado en `NUMEROS_CANONICOS_BBG.md`). |

Adicionalmente, cuatro pasos del pipeline **llaman a APIs externas** (IMF Datamapper, World
Bank, BIS Statistics, y un scraping HTML del *Pink Sheet* de commodities del Banco Mundial en
`p7b_iv_commodity_tot.py` — este último es el más frágil, depende de que esa página no cambie
de diseño). **No hace falta red para reproducir los números ya reportados**: todos sus outputs
(`controls_all_bbg.csv`, `global_controls_quarterly.csv`, `usd_neer_bbg.csv`,
`ctot_shock_bbg.csv`, `ctot_pesos_pre2004.csv`) están commiteados. La red solo es necesaria si
se quiere **refrescar** esos insumos a una fecha posterior — y en ese caso, `p0_controles_all.py`
falla **silenciosamente** (deja `NaN` en vez de abortar) si IMF/World Bank no responden, mientras
que `p7_iv_dolar_bis.py` y `p7b_iv_commodity_tot.py` sí abortan con error visible. Si se
re-ejecuta con red, revisar la cobertura de `controls_all_bbg.csv` a mano antes de confiar en
el resultado.

Una laguna menor, sin impacto en el resultado vigente: `fase4_embi.png` y `fase6_robustez.png`
(figuras del working paper de OI, línea teórica pausada) no tienen script generador en el
repo — son imágenes congeladas de una fase anterior. No afecta al capítulo empírico.

---

## 1. Prerrequisitos de entorno

- **Python 3.13** en dos entornos virtuales separados (ninguno se versiona por tamaño —
  `.gitignore`; cada uno tiene ahora su `requirements.txt` commiteado, generado el
  2026-09-18 con `pip list --format=freeze` sobre el entorno de trabajo real):
  - `.venv/` en la raíz del repo — regresiones, panel, EDA, figuras. Instalar con
    `python -m venv .venv && .venv/Scripts/pip install -r requirements.txt` (paquetes clave:
    `pandas`, `numpy`, `scipy`, `linearmodels`, `statsmodels`, `matplotlib`, `seaborn`,
    `openpyxl`, `xlrd`, `pyreadstat`, `pydynpd`, `wbgapi`, `nbformat`/`nbclient`/`ipykernel`
    para ejecutar notebooks sin la UI de Jupyter).
  - `1_Codigo/JLoss_reconstruction/JLoss-pipeline/venv/` — solo el motor JLoss. Instalar con
    `python -m venv venv && venv/Scripts/pip install -r ../requirements.txt` (el motor en sí
    solo necesita `numpy`/`pandas`/`scipy`; el freeze trae de más — `yfinance`, `selenium`,
    `curl_cffi`, `beautifulsoup4` — de experimentos de extracción anteriores no vigentes).
- **MiKTeX o TeX Live completo** para compilar la tesis. Verificado con **MiKTeX 25.12**
  (`pdfTeX 3.141592653-2.6-1.40.28`) en Windows. Paquetes no estándar usados por `main.tex`:
  `array`, `booktabs`, `longtable`, `mdframed`, `natbib`, `pdflscape`, `setspace`, `tikz` — todos
  vienen en una instalación completa; TeX Live *mínimo* no los trae. No hace falta `bibtex`
  ni `biber`: cada capítulo define su propia `thebibliography` en línea.
- **R — opcional, no necesario.** Solo para re-verificar de forma cruzada tres scripts de
  registro (ver tabla de arriba). Este entorno no lo tiene instalado y el proyecto no depende
  de él para ningún número vigente.

---

## 2. Paso a paso

Los comandos exactos están en la sección "Reproducir" de [`../README.md`](../README.md); acá
se explica **qué verificar** en cada paso y **por qué existe**.

### Paso 1 — JLoss desde Bloomberg

```bash
cd 1_Codigo/JLoss_reconstruction
mkdir -p _stage && for d in ../Bloomberg_extraction/output/*/; do c=$(basename "$d"); \
  cp "$d/balance_$c.csv" "$d/mktcap_$c.csv" _stage/; done
JLoss-pipeline/venv/Scripts/python.exe jloss_engine.py --indir _stage \
  --out jloss_bloomberg/Panel_JLoss_v9_bloomberg.csv && rm -rf _stage
```

No necesita Bloomberg Terminal (los CSV ya están extraídos y commiteados) ni red. Motor puro
`numpy`/`scipy` (punto de silla / Merton–KMV), sin rutas absolutas. Verificar: el CSV de salida
debe tener las mismas filas/columnas que el ya commiteado en `jloss_bloomberg/`; si se quiere
confirmar bit a bit, `diff` contra el archivo existente antes de sobrescribirlo.

### Paso 2 — Panel + análisis (`1_Codigo/Panel/`, con `.venv` del root)

Orden **obligatorio** (cada script lee el output del anterior):

1. `p0_controles_all.py` — controles domésticos (deuda, fiscal, reservas, CA, inflación, REER)
   para todos los países. Red: IMF Datamapper + World Bank (con reintento y *backoff*; si
   falla deja `NaN`, no aborta — revisar cobertura si se re-ejecuta con red).
2. `p1_build_panels.py` — arma `Panel_bloomberg.csv` (13 países, N=721) uniendo EMBI
   (`2_Datos/embi.xlsx`), JLoss (paso 1), GaR (`gar_panel_all18.csv`), HHI y controles. Red:
   World Bank (mismo mecanismo de reintento).
3. `p2_regresiones.py` — M1/M2/M3, robustez, umbral de Hansen, efecto marginal. Sin red.
   **Verificación clave**: debe imprimir θ (M2, N=614) ≈ **−0,16** (p≈0,26) y β₁≈+2,8/β₂≈−4,3 —
   comparar contra la fila "★ DISEÑO VIGENTE" de
   [`../1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`](../1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md).
4. `p6_concentracion_trimestral.py` — HHI trimestral de los mismos bancos que JLoss. Sin red.
5. `p7_iv_dolar_bis.py` — instrumento dólar BIS. Red: `stats.bis.org` (aborta con error visible
   si falla, a diferencia de p0). Sobrescribe `Panel_bloomberg.csv` in-place (idempotente).
6. `p7b_iv_commodity_tot.py` — instrumento términos de intercambio por exposición a
   commodities. Red: World Bank API + scraping del *Pink Sheet* (el paso más frágil del
   pipeline — si el Banco Mundial rediseña esa página, falla con `RuntimeError` explícito).
7. `p7c_iv_reforzado.py` — IV con los tres instrumentos juntos (OnOffRun, USD BIS, ToT). Sin red.
8. `p3_causal_fase5.py` — batería causal (wild cluster bootstrap, proyecciones locales, IV) +
   H4a/H4b con 3 proxies de HHI. Sin red. Importa `causal_core.py` desde `1_Codigo/Panel/`
   (legado documentado en `CONTROL_DE_VERSIONES.md` §3.8) — confirmar que ese archivo sigue ahí.
9. `p5_robustez_arbitro.py` — ventanas móviles, placebo, país influyente, regresor generado,
   GMM (`pydynpd`, con *fallback* silencioso a `NaN` si no está instalado — sí lo está en
   `.venv`). Escribe `fig_ventanas_theta.pdf` directo en `bbg/figuras/` **y** en
   `4_Redaccion/tesis/imagenes/`.
10. `p8_bateria_regresiones.py` — batería 4×3×2 estilo Chari et al. (2024), Tabla 2.3 de la
    tesis. Sin red. *(No estaba en la lista de README hasta esta revisión pese a ser vigente.)*
11. `p9_crisis_interaccion.py` — Backstop vs EMstress (test de falsación). Sin red. Es el script
    que reproduce la Sección 8 del notebook EDA (ver Paso 2d). **Verificación clave**: β₃ (fuera
    de crisis) ≈ **+0,81** (p≈0,051); β₃+β₄ bajo Backstop ≈ 0 (Wald no rechaza, p≈0,77); β₃+β₄
    bajo EMstress ≈ **+1,05** (Wald rechaza, p<0,001).
12. `p9_diag_ryr.py` y `p9_robustez_gar_nocdiff.py` — diagnóstico y robustez de la endogeneidad
    `Ryr`↔EMBI. Sin red. *(Tampoco estaban en la lista de README.)*
12b. `p9b_bateria_crisis.py` *(agregado 2026-09-23)* — extiende `p9_crisis_interaccion.py` a una
    batería de 24 especificaciones (4 modelos anidados CM1–CM4 × 3 FE, 2 paneles: vector único
    y Backstop/EMstress) → `bateria_crisis_bbg.csv`. Sin red. Verifica su propia replicación
    contra `p9_crisis_interaccion.py` al ejecutarse (aborta con `SystemExit` si no coincide).
13. `p4_figuras.py` — genera las 10 figuras `fig_*.pdf/.png` de la tesis (incluye
    `fig_gar_paises()` y `fig_comovimiento()`, agregadas 2026-09-23). **Corregido en esta
    revisión**: antes solo guardaba en `bbg/figuras/`; el README decía que se copiaban a
    `4_Redaccion/tesis/imagenes/` pero el script no lo hacía (la sincronía era manual y quedó
    rota al menos una vez — las figuras de `imagenes/` tenían timestamp de 2026-09-02 mientras
    que las de `bbg/figuras/` eran de 2026-09-05). Ahora `_save()` escribe el PDF en ambas
    carpetas en el mismo paso, igual que ya hacía `p5_robustez_arbitro.py` con
    `fig_ventanas_theta.pdf`. **Si se agregan figuras nuevas a la tesis, deben usar `_save()` o
    replicar ese mismo patrón** — de lo contrario la tesis seguirá compilando con la figura
    vieja sin ningún error visible.

### Paso 2b/2c — Robustez opcional (grid ancho de JLoss, bootstrap C1)

Opcionales, ya ejecutados y con outputs commiteados
(`robustez_widebounds_bbg.csv`, `gar_replicas_nlhpc.csv`). Solo re-ejecutar si se quiere
verificar desde cero; el grid ancho toma ~40 min, el bootstrap completo ~172 min en cluster
(la segunda etapa local es trivial).

### Paso 2d — Notebook EDA (`EDA_Panel_Final_bbg.ipynb`)

**No usar `jupyter execute` ni `jupyter nbconvert --execute`** contra el `.venv` de este
repo: son *wrappers* de `uv` y en este entorno tiran `Failed to canonicalize script path` (se
confirmó que el problema es del *launcher*, no del notebook ni del kernel). Ejecutar en su
lugar con `nbclient` directamente:

```python
import nbformat
from nbclient import NotebookClient
nb = nbformat.read("1_Codigo/Panel/bbg/EDA_Panel_Final_bbg.ipynb", as_version=4)
NotebookClient(nb, timeout=600, kernel_name="python3",
               resources={"metadata": {"path": "1_Codigo/Panel/bbg"}}).execute()
nbformat.write(nb, "1_Codigo/Panel/bbg/EDA_Panel_Final_bbg.ipynb")
```

El `resources.metadata.path` es necesario porque la celda de configuración del notebook fija
`BBG = os.path.abspath(".")` (**corregido en esta revisión** — antes era una ruta absoluta
`C:/Users/HOME/Claude/proyects/Jloss/...` hardcodeada de esta máquina, el único caso de todo
el repo; todos los `.py` ya usaban `os.path.dirname(__file__)`). Si se abre el notebook
normalmente en Jupyter Lab/Notebook, el cwd por defecto ya es la carpeta del notebook y no
hace falta pasar `resources`.

Este notebook genera las 8 figuras `eda_*.pdf/.png` (EDA complementario, no citadas en el
cuerpo de la tesis salvo como material de apoyo) — no confundir con las `fig_*.pdf` de
`p4_figuras.py`, que sí son las oficiales.

### Paso 3 — Compilar la tesis

```bash
cd 4_Redaccion/tesis
latexmk -pdf main.tex
```

Debe compilar a `main.pdf` (94 páginas al 2026-09-18) sin errores (`grep -c "^! " main.log`
debe dar 0). Dos *warnings* cosméticos esperados (sustitución de forma de fuente, *infinite
glue shrinkage*) no son bloqueantes. No requiere `bibtex`/`biber` — un solo `latexmk -pdf`
alcanza (corre `pdflatex` internamente 2–3 veces para resolver referencias cruzadas y TOC).

### Paso 3b — Envíos standalone (`4_Redaccion/envios/`)

`paper_empirico/main.tex` y `paper_teorico/main.tex` reusan el cuerpo de la tesis vía
`\input{../../tesis/paper2_empirico.tex}` / `paper1_oi.tex` (nunca diverge), pero cada uno
tiene **su propia copia** de las figuras en `envios/<paper>/figuras/` — un tercer punto de
sincronización manual, además de `tesis/imagenes/` (Paso 2, punto 13). Si se corrió el
pipeline y las figuras de `tesis/imagenes/` cambiaron, hay que recopiarlas a mano a los dos
`envios/`:

```bash
cp 4_Redaccion/tesis/imagenes/{fig_cobertura,fig_concordancia_jloss,fig_efecto_marginal,fig_forest_theta,fig_h4b,fig_jloss_paises,fig_umbral}.pdf \
   1_Codigo/Panel/bbg/figuras/fig_ventanas_theta.pdf \
   4_Redaccion/envios/paper_empirico/figuras/
cp 4_Redaccion/tesis/imagenes/{fig_h4b,fig_jloss_paises}.pdf 4_Redaccion/envios/paper_teorico/figuras/
cd 4_Redaccion/envios/paper_empirico && latexmk -pdf main.tex   # -> 49 pp, 0 errores
cd ../paper_teorico && latexmk -pdf main.tex                    # -> 31 pp, 0 errores
```

El `\begin{abstract}` y `cover_letter.md` de `paper_empirico` son texto propio (no derivado
del `\input`) y también deben revisarse a mano tras cualquier cambio de resultado central —
ver la nota "Sincronía con el envío standalone" en `CONTROL_DE_VERSIONES.md` §3.3.

---

## 3. Cómo verificar que la reproducción fue exitosa

No compares archivos byte a byte (los PDF de figuras cambian de bytes en cada corrida por
metadata/timestamps internos aunque el contenido visual sea idéntico). Compara en su lugar:

1. **Cobertura del panel**: `p1_build_panels.py` debe reportar 13 países, N=721 (M1)/614 (M2).
2. **θ oficial**: `p2_regresiones.py`, M2 (+6 controles) → θ ≈ −0,16 (p≈0,26, no significativo
   sobre la muestra completa) — no −0,338 ni ningún otro valor de los marcados "superado" en
   `CONTROL_DE_VERSIONES.md` §0.
3. **Heterogeneidad**: `p5_robustez_arbitro.py` → núcleo de 11 economías de financiamiento
   externo, θ ≈ −0,47 (p≈0,023).
4. **Test de falsación de crisis**: `p9_crisis_interaccion.py` → β₃+β₄ ≈ 0 bajo Backstop
   (Wald no rechaza), β₃+β₄ ≈ +1,05 bajo EMstress (Wald rechaza, p<0,001).
5. **Compilación limpia**: `main.pdf` sin errores, 94 páginas.

Todos los valores de referencia completos y trazables:
[`../1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md`](../1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md).

---

## 4. Hallazgos de esta revisión (2026-09-18) y qué se corrigió

| # | Hallazgo | Corrección aplicada |
|---|---|---|
| 1 | `.venv/` y `JLoss-pipeline/venv/` sin `requirements.txt` commiteado (ambos `.gitignore`d, sin forma de reconstruir el entorno exacto). | Generados `requirements.txt` en la raíz (76 paquetes) y en `1_Codigo/JLoss_reconstruction/` (75 paquetes), vía `pip list --format=freeze` sobre los entornos de trabajo reales. |
| 2 | Ruta absoluta hardcodeada (`C:/Users/HOME/Claude/proyects/Jloss/...`) en la celda 1 de `EDA_Panel_Final_bbg.ipynb` — único caso en todo el repo; si se clona en otra máquina/ruta, rompe con `FileNotFoundError`. | Cambiada a `os.path.abspath(".")`, consistente con el patrón `os.path.dirname(__file__)` que ya usan todos los `.py`. Verificado re-ejecutando el notebook con `nbclient`: mismos resultados. |
| 3 | `p4_figuras.py` no copiaba sus 7 figuras a `4_Redaccion/tesis/imagenes/` pese a que el README decía que sí — la sincronía era manual y ya se había roto (figuras de `imagenes/` con timestamp de 3 días antes que las de `bbg/figuras/`). Riesgo: re-ejecutar el pipeline con datos actualizados no actualizaba la tesis. | `_save()` ahora escribe el PDF también en `4_Redaccion/tesis/imagenes/` en el mismo paso (mismo patrón que ya usaba `p5_robustez_arbitro.py` para `fig_ventanas_theta.pdf`). Verificado: `p4_figuras.py` re-ejecutado, las 7 figuras se actualizaron en ambas carpetas, y `latexmk -pdf main.tex` recompiló limpio (94 pp, 0 errores) contra las figuras nuevas. |
| 4 | README "Reproducir" no mencionaba `p7b`/`p7c` (IV commodity ToT), `p8_bateria_regresiones.py`, `p9_crisis_interaccion.py`, `p9_diag_ryr.py`, `p9_robustez_gar_nocdiff.py` — todos vigentes y citados en `CONTROL_DE_VERSIONES.md`. | Añadidos a la lista de comandos de `../README.md`, en el orden correcto de dependencia. |
| 5 | El notebook de EDA se perdió una sección al guardarse mal en una sesión anterior (`eda_08_efecto_marginal_regimen` quedó desactualizada). | Resuelto en la sesión previa a esta auditoría (commit `03cd8f3`): sección restaurada, notebook re-ejecutado con `nbclient` y guardado in-place. |
| 6 *(2026-09-19)* | `4_Redaccion/envios/paper_empirico/figuras/` y `envios/paper_teorico/figuras/` — copias propias de las figuras, un tercer punto de sincronización manual (además de `tesis/imagenes/`) — estaban desactualizadas desde 2026-09-01, antes de varias re-ejecuciones del pipeline. | Recopiadas desde `tesis/imagenes/` ya actualizado; ambos `main.tex` recompilados limpios (`paper_empirico` 49 pp, `paper_teorico` 31 pp, 0 errores). Documentado como Paso 3b, sigue siendo manual — no se automatizó porque un envío ya presentado a revista no debería sobrescribirse solo. |

Riesgos documentados pero **sin corregir** (decisión: no forman parte del resultado vigente o
requieren decisión del usuario, no un cambio de código):

- `p0_controles_all.py` degrada silenciosamente a `NaN` si IMF/World Bank no responden, en vez
  de abortar como sí hacen `p7`/`p7b`. Se documenta acá; endurecerlo (loggear cobertura al
  final) queda a criterio del usuario.
- `fase4_embi.png`/`fase6_robustez.png` sin script generador — fuera de alcance (línea teórica
  pausada, no aporta al capítulo empírico).
