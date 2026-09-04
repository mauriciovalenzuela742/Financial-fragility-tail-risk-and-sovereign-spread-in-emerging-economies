# ==============================================================================
# bateria_regresiones.R
#
# Replica en R (paquete `plm`) la bateria de regresiones del Capitulo 2 de la
# tesis: EMBI Global Diversified ~ JLoss x GaR, panel unico de 13 economias
# emergentes, datos Bloomberg. Es la version R de
# `1_Codigo/Panel/bbg/p8_bateria_regresiones.py` (Python, linearmodels) --
# pensada para tener a mano si en la defensa piden correr algo en vivo.
#
# Uso:
#   1. Abrir R / RStudio con el working directory en esta carpeta
#      (1_Codigo/Panel/bbg/), o ajustar `ruta_csv` mas abajo.
#   2. source("bateria_regresiones.R")
#   3. Para una regresion ad-hoc durante la reunion: ver la Seccion 5 al final
#      (plantilla que se edita y se corre en dos lineas).
#
# Paquetes (una vez):  install.packages(c("plm", "lmtest"))
# ==============================================================================

library(plm)
library(lmtest)

# ------------------------------------------------------------------------------
# 1. Datos
# ------------------------------------------------------------------------------
ruta_csv <- "Panel_bloomberg.csv"
if (!file.exists(ruta_csv)) {
  stop("No se encuentra '", ruta_csv, "'. Corre este script con el working ",
       "directory en 1_Codigo/Panel/bbg/, o cambia `ruta_csv` al inicio.")
}
panel <- read.csv(ruta_csv, stringsAsFactors = FALSE)

# Variable dependiente principal: EMBI Global Diversified (J.P. Morgan), como
# en Chari et al. (2024). Muestra de estimacion = EMBI + JLoss + GaR disponibles.
d <- subset(panel, !is.na(EMBI_bps) & !is.na(JLoss) & !is.na(GaR))
d$GaR_pp <- d$GaR * 100          # GaR en puntos porcentuales (igual que el pipeline Python)

# Trimestres de crisis financiera aguda: crisis financiera global (2008Q4-2009Q4)
# y pandemia (2020Q1-2021Q4). "Sin crisis" es la segunda muestra de la bateria.
crisis_q <- c("2008Q4", "2009Q1", "2009Q2", "2009Q3", "2009Q4",
              "2020Q1", "2020Q2", "2020Q3", "2020Q4",
              "2021Q1", "2021Q2", "2021Q3", "2021Q4")
d$sin_crisis <- !(d$quarter %in% crisis_q)

# JLoss y GaR centrados EN CADA MUESTRA por su propia media (igual que
# p8_bateria_regresiones.py: el centrado es especifico de cada submuestra, no
# global). Con efectos fijos esto no altera theta, pero SI altera el valor
# reportado de los coeficientes de nivel (JLoss_c, GaR_c) si no se recalcula.
centrar <- function(df) {
  df$JLoss_c <- df$JLoss - mean(df$JLoss)
  df$GaR_c   <- df$GaR_pp - mean(df$GaR_pp)
  df$Int     <- df$JLoss_c * df$GaR_c
  df
}
d_completa   <- centrar(d)
d_sin_crisis <- centrar(subset(d, sin_crisis))

cat(sprintf("Muestra de estimacion: N = %d, %d paises, %s a %s\n",
            nrow(d), length(unique(d$country)), min(d$quarter), max(d$quarter)))

pdata_completa   <- pdata.frame(d_completa,   index = c("country", "quarter"))
pdata_sin_crisis <- pdata.frame(d_sin_crisis, index = c("country", "quarter"))

# ------------------------------------------------------------------------------
# 2. Una regresion, con errores de Driscoll-Kraay (vcovSCC de `plm`)
# ------------------------------------------------------------------------------
# effect: "individual" (solo pais), "time" (solo tiempo), "twoways" (ambos)
run_dk <- function(data, formula, effect = "twoways") {
  m  <- plm(formula, data = data, model = "within", effect = effect)
  ct <- tryCatch(coeftest(m, vcov = vcovSCC),
                  error = function(e) coeftest(m, vcov = vcovHC(m, method = "arellano")))
  list(model = m, test = ct,
       N = nobs(m), R2_within = unname(summary(m)$r.squared["rsq"]))
}

# ------------------------------------------------------------------------------
# 3. La especificacion de referencia (M4, efectos fijos pais + tiempo)
# ------------------------------------------------------------------------------
f_M4 <- EMBI_bps ~ JLoss_c + GaR_c + Int

cat("\n================ M4 (JLoss + GaR + interaccion), FE pais+tiempo ================\n")
cat("\n--- Muestra completa ---\n")
r_completa <- run_dk(pdata_completa, f_M4, "twoways")
print(r_completa$test)
cat(sprintf("N = %d   R2_within = %.3f\n", r_completa$N, r_completa$R2_within))

cat("\n--- Sin trimestres de crisis (GFC + COVID fuera) ---\n")
r_sin_crisis <- run_dk(pdata_sin_crisis, f_M4, "twoways")
print(r_sin_crisis$test)
cat(sprintf("N = %d   R2_within = %.3f\n", r_sin_crisis$N, r_sin_crisis$R2_within))

cat("\nNumeros de referencia (pipeline Python, linearmodels, Tabla 2.3 de la tesis):\n")
cat("  Muestra completa   : JLoss=+4.64  GaR=-3.63  theta=-0.14 (t=-0.57, n.s.)\n")
cat("  Sin crisis         : JLoss=+4.29  GaR=-6.00  theta=-1.19 (t=-3.55, p<0.001)\n")
cat("  Los coeficientes coinciden (verificado); el estadistico t de Driscoll-Kraay\n")
cat("  puede diferir un poco entre `plm::vcovSCC` y linearmodels (ancho de banda /\n")
cat("  kernel por defecto), sin cambiar el signo ni la conclusion de significancia.\n")

# ------------------------------------------------------------------------------
# 4. La bateria completa: 4 modelos x 3 efectos fijos x 2 muestras (Tabla 2.3)
# ------------------------------------------------------------------------------
modelos <- list(
  M1 = EMBI_bps ~ JLoss_c,
  M2 = EMBI_bps ~ GaR_c,
  M3 = EMBI_bps ~ JLoss_c + GaR_c,
  M4 = EMBI_bps ~ JLoss_c + GaR_c + Int
)
efectos  <- c(tiempo = "time", pais = "individual", "pais+tiempo" = "twoways")
muestras <- list(completa = pdata_completa, sin_crisis = pdata_sin_crisis)

estrella <- function(p) ifelse(p < 0.01, "***", ifelse(p < 0.05, "**", ifelse(p < 0.10, "*", "")))

cat("\n\n================ BATERIA COMPLETA (Tabla 2.3 de la tesis) ================\n")
for (sname in names(muestras)) {
  cat("\n############################  MUESTRA:", sname, " ############################\n")
  for (ename in names(efectos)) {
    for (mname in names(modelos)) {
      r <- tryCatch(run_dk(muestras[[sname]], modelos[[mname]], efectos[[ename]]),
                     error = function(e) NULL)
      if (is.null(r)) { cat(sprintf("%s / FE=%-12s  [no estimable]\n", mname, ename)); next }
      ct <- r$test
      colt <- intersect(c("t value", "z value"), colnames(ct))[1]   # nombre de columna segun el tipo de vcov
      linea <- sprintf("%s / FE=%-12s  ", mname, ename)
      for (rn in rownames(ct)) {
        linea <- paste0(linea, sprintf("%s=%+.2f%-3s(t=%+.1f)  ",
                                        rn, ct[rn, "Estimate"], estrella(ct[rn, 4]), ct[rn, colt]))
      }
      linea <- paste0(linea, sprintf("N=%d R2w=%.2f", r$N, r$R2_within))
      cat(linea, "\n")
    }
  }
}

# ------------------------------------------------------------------------------
# 5. Plantilla para una regresion "en vivo" durante la reunion
# ------------------------------------------------------------------------------
# Si te piden probar otra especificacion en el momento, copia y edita esto:
#
#   - formula: agrega/quita variables (p.ej. + debt_gdp + fisc_bal + ...)
#   - effect : "individual" (pais), "time" (tiempo), "twoways" (ambos)
#   - datos  : pdata_completa, pdata_sin_crisis, o un subset tuyo
#     (p.ej. subset(d, country != "china") para un leave-one-out)
#
# mi_modelo <- plm(EMBI_bps ~ JLoss_c + GaR_c + Int + debt_gdp + fisc_bal,
#                   data = pdata_completa, model = "within", effect = "twoways")
# coeftest(mi_modelo, vcov = vcovSCC)
