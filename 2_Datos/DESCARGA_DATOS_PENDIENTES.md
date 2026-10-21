# Datos pendientes: cómo descargarlos

> **Estado al 13 de octubre de 2026: los dos puntos están HECHOS.** Lo que sigue queda como
> documentación de cómo se pidieron.
>
> 1. **Participación extranjera.** Archivo usado: `2_Datos/Database_For_Posting_EM_Frozen.xlsx`
>    (Arslanalp y Tsuda, FMI, versión de mayo de 2026); `p26_participacion_extranjera.py` escribe
>    `2_Datos/participacion_extranjera.csv` (13 países, 2004Q1–2025Q4) y estima. Resultado: nulo en las
>    tres hipótesis primarias (h3 = −0,006; wild p = 0,48; Holm 1,00, signo contrario al predicho); la
>    heterogeneidad del "núcleo de 11 economías" pasa a exploratoria.
> 2. **Chile.** Acceso continuo confirmado: en mayo de 2022 pasó a una Línea de Liquidez de Corto
>    Plazo y el 29 de agosto de 2022 el FMI aprobó una nueva Línea de Crédito Flexible (comunicado
>    pr22294). Perú: 2020Q2–2024Q2. El resultado no cambia (interacción × acceso = −0,004; wild p = 0,90).
>
> Detalle en `1_Codigo/Panel/bbg/NUMEROS_CANONICOS_BBG.md` §18.5 y §18.7 y en
> `4_Redaccion/informe_arbitro.md`.
>
> Lo que sigue se conserva como documentación histórica de cómo se hizo la descarga; las marcas "sin verificar" y "VERIFICAR" del texto original ya no aplican.

Dos cosas quedaron abiertas tras el informe de árbitro (`4_Redaccion/informe_arbitro.md`, sección 3).
La primera exige una descarga manual; la segunda, una verificación de fechas.

---

## 1. Participación extranjera en la deuda soberana (objeción 11)

**Para qué:** reemplazar el grupo "núcleo de 11 economías vs. Polonia e India", definido ex post, por
un moderador continuo y medido de forma independiente.

**Por qué es manual:** el sitio del FMI rechazó la descarga automática (HTTP 403, 12-oct-2026).

### Paso 1. Bajar el Excel

- Fuente: Arslanalp, S. y Tsuda, T. (2014), *Tracking Global Demand for Emerging Market Sovereign
  Debt*, IMF Working Paper 14/39. La base se actualiza periódicamente.
- Página del documento (abrir en el navegador):
  <https://www.imf.org/en/Publications/WP/Issues/2016/12/31/Tracking-Global-Demand-for-Emerging-Market-Sovereign-Debt-41399>
- En esa página, buscar el enlace al **archivo de datos** ("Data" / "Dataset", un `.xlsx`). Si el
  enlace no aparece, buscar en Google: `Arslanalp Tsuda emerging market sovereign debt investor base dataset xlsx`.
- Guardar el archivo tal cual en `2_Datos/`, por ejemplo `2_Datos/arslanalp_tsuda_em.xlsx`.

> No pude abrir la página, así que la dirección y la ubicación exacta del enlace están sin verificar.

### Paso 2. Qué serie usar

La base trae, por país y trimestre, la deuda del gobierno según quién la tiene (bancos centrales
extranjeros, bancos extranjeros, no bancos extranjeros, banco central local, bancos locales, no
bancos locales). La variable que necesita el script es:

```
foreign_share = deuda del gobierno en manos de no residentes / deuda total del gobierno × 100
```

- Usar la deuda **total** del gobierno (no solo la de moneda local), para que sea comparable con el
  EMBI, que es deuda externa en dólares. Si quieres, guarda también la de moneda local en otra
  columna para una robustez; el script solo lee `foreign_share`.
- Si la base ya trae la participación de no residentes calculada (en % del total), usar esa
  directamente.
- Los nombres exactos de las hojas y columnas hay que mirarlos en el archivo; no los conozco.

### Paso 3. Armar el CSV

Archivo: `2_Datos/participacion_extranjera.csv`, formato largo, con exactamente estas columnas:

| columna | formato | ejemplo |
|---|---|---|
| `country` | nombre en minúsculas, igual que en el panel | `brazil` |
| `quarter` | año + `Q` + trimestre | `2015Q3` |
| `foreign_share` | porcentaje de 0 a 100 | `18.4` |

Ejemplo:

```csv
country,quarter,foreign_share
brazil,2004Q1,5.2
brazil,2004Q2,5.6
chile,2004Q1,31.0
```

Nombres de país que usa el panel (los 13 de la muestra principal):

```
brazil, chile, china, colombia, india, indonesia, malaysia, mexico,
peru, philippines, poland, southafrica, turkey
```

Reglas:

- `southafrica` va sin espacio.
- Período: idealmente desde 2003Q1 (el script rezaga la serie cuatro trimestres y la muestra parte
  en 2004Q2) hasta lo último disponible.
- **No rellenar ni interpolar** huecos: dejar fuera los trimestres o países sin dato. El script
  reporta la cobertura.
- Punto decimal, no coma.

### Paso 4. Correr

Desde `1_Codigo/Panel/bbg/`:

```bash
../../../.venv/Scripts/python.exe p26_participacion_extranjera.py
```

Salida: `paper_participacion_numeros.csv`, con la cobertura por país y los tres coeficientes de
moderación (`h1` fragilidad, `h2` riesgo de cola, `h3` interacción) con sus p de Driscoll–Kraay y de
wild bootstrap. La hipótesis es `h3 > 0`: más participación extranjera, más amplificación.

Si no hay archivo, el script avisa y no estima nada.

---

## 2. Fechas del respaldo del FMI a Chile en 2022

**Para qué:** en `1_Codigo/Panel/bbg/respaldo_externo.csv` el acceso de Chile está como continuo
entre 2020Q2 y 2026Q2 y marcado "VERIFICAR".

**Lo que hay que confirmar** (lo anoto de memoria; no lo pude verificar):

1. Primera Línea de Crédito Flexible (FCL): aprobada a fines de mayo de 2020, por dos años.
2. En mayo de 2022 Chile la habría reemplazado por una Línea de Liquidez de Corto Plazo (SLL).
3. En agosto de 2022 habría vuelto a una FCL de dos años, renovada en 2024.

**Dónde mirar:** comunicados de prensa del FMI sobre Chile,
<https://www.imf.org/en/Countries/CHL> (sección de noticias, años 2020, 2022 y 2024), o los del Banco
Central de Chile.

**Qué hacer según lo que encuentres:**

- Si entre mayo y agosto de 2022 Chile tuvo la SLL, hay dos opciones defendibles. Elegir una y
  declararla en la nota de la tabla de respaldo:
  - **Acceso continuo** (como está hoy): la SLL también es liquidez oficial precautoria. No hay que
    cambiar nada; solo borrar el "VERIFICAR" y poner las fechas en la columna `nota`.
  - **Solo FCL**: partir la fila de Chile en dos ventanas, `2020Q2–2022Q1` y `2022Q3–2026Q2`, lo que
    deja 2022Q2 sin acceso.
- Si las fechas son otras, corregir `desde` y `hasta` y poner el enlace al comunicado en `fuente`.

Después de editar el CSV, volver a correr (en logaritmos y en niveles):

```bash
../../../.venv/Scripts/python.exe p25_respaldo_externo.py
JLOSS_FORMA=nivlag ../../../.venv/Scripts/python.exe p25_respaldo_externo.py
```

y comparar con la Tabla de respaldo externo de la tesis (interacción × acceso = −0,004 en la muestra
completa). Un trimestre de un país no debería mover el resultado; si lo mueve, hay que actualizar la
tabla en la tesis, el paper y las láminas.

---

## Cuando esté listo

Deja el Excel en `2_Datos/` y avísame: armo el CSV, corro `p26`, y paso el resultado a la tesis
(sección 4.5.2), al paper, a las láminas y al informe de árbitro.
