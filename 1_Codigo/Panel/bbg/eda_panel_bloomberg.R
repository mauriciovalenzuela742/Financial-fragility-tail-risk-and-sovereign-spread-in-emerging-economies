# ==============================================================================
# eda_panel_bloomberg.R
#
# EDA rapido y autocontenido del panel unico anclado en Bloomberg (Cap. 2 de la
# tesis): JLoss, GaR y el spread soberano (EMBI Global Diversified / CDS 5A) de
# 13 economias emergentes. No usa paquetes fuera de R base -- corre en
# cualquier maquina con R instalado, sin depender de que algo este actualizado.
#
# Uso:
#   1. Working directory en 1_Codigo/Panel/bbg/ (donde vive Panel_bloomberg.csv)
#   2. source("eda_panel_bloomberg.R")
#   3. Genera EDA_panel_bloomberg.pdf en la misma carpeta con todos los graficos,
#      ademas de imprimir las tablas en consola. Util para tenerlo abierto en
#      la reunion aunque no se corra en vivo.
# ==============================================================================

options(width = 100)

# ------------------------------------------------------------------------------
# 1. Datos
# ------------------------------------------------------------------------------
ruta_csv <- "Panel_bloomberg.csv"
if (!file.exists(ruta_csv)) {
  stop("No se encuentra '", ruta_csv, "'. Corre este script con el working ",
       "directory en 1_Codigo/Panel/bbg/, o cambia `ruta_csv` al inicio.")
}
panel <- read.csv(ruta_csv, stringsAsFactors = FALSE)
panel$GaR_pp <- panel$GaR * 100

# Muestra de estimacion: EMBI + JLoss + GaR disponibles simultaneamente
est <- subset(panel, !is.na(EMBI_bps) & !is.na(JLoss) & !is.na(GaR))
est$country <- factor(est$country)

cat("======================================================================\n")
cat(" PANEL COMPLETO (roster):", nrow(panel), "filas,", length(unique(panel$country)),
    "economias,", min(panel$quarter), "a", max(panel$quarter), "\n")
cat(" MUESTRA DE ESTIMACION (EMBI+JLoss+GaR):", nrow(est), "filas,",
    length(unique(est$country)), "paises\n")
cat("======================================================================\n\n")

# ------------------------------------------------------------------------------
# 2. Estructura y variables disponibles
# ------------------------------------------------------------------------------
cat("--- Estructura (str) de la muestra de estimacion ---\n")
str(est[, c("country", "quarter", "EMBI_bps", "CDS_bps", "JLoss", "GaR", "GaR_pp",
            "debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer")])

# ------------------------------------------------------------------------------
# 3. Cobertura por pais: N, ventana, EMBI vs CDS
# ------------------------------------------------------------------------------
cat("\n--- Cobertura por pais (muestra de estimacion) ---\n")
cobertura <- do.call(rbind, lapply(split(est, est$country), function(g) {
  data.frame(
    pais       = unique(g$country),
    n_trim     = nrow(g),
    desde      = min(g$quarter),
    hasta      = max(g$quarter),
    con_cds    = sum(!is.na(g$CDS_bps)),
    JLoss_med  = round(median(g$JLoss), 2),
    JLoss_max  = round(max(g$JLoss), 1)
  )
}))
cobertura <- cobertura[order(-cobertura$n_trim), ]
rownames(cobertura) <- NULL
print(cobertura)

# ------------------------------------------------------------------------------
# 4. Estadistica descriptiva (Tabla 2.2 de la tesis)
# ------------------------------------------------------------------------------
cat("\n--- Estadistica descriptiva ---\n")
vars_desc <- c("EMBI_bps", "CDS_bps", "JLoss", "GaR_pp",
               "debt_gdp", "fisc_bal", "res_gdp", "ca_gdp", "infl_yoy", "reer")
desc <- do.call(rbind, lapply(vars_desc, function(v) {
  x <- est[[v]]
  data.frame(variable = v, media = mean(x, na.rm = TRUE), sd = sd(x, na.rm = TRUE),
             min = min(x, na.rm = TRUE), max = max(x, na.rm = TRUE),
             n_na = sum(is.na(x)))
}))
print(round(desc[, -1], 2), row.names = FALSE)
cat("(variables, en el mismo orden):", paste(vars_desc, collapse = ", "), "\n")

# ------------------------------------------------------------------------------
# 5. Dispersion TRANSVERSAL de JLoss (motiva por que la identificacion del
#    termino de interaccion descansa en pocos paises -- Seccion 6.6 del Cap. 2)
# ------------------------------------------------------------------------------
cat("\n--- Dispersion de JLoss por pais (mediana, ordenado) ---\n")
jl_pais <- aggregate(JLoss ~ country, est, median)
jl_pais <- jl_pais[order(jl_pais$JLoss), ]
print(jl_pais, row.names = FALSE)
cat(sprintf("\nsd de JLoss ENTRE paises (de sus medianas): %.2f\n", sd(jl_pais$JLoss)))
cat(sprintf("sd de JLoss DENTRO del panel (todas las obs.): %.2f\n", sd(est$JLoss)))

# ------------------------------------------------------------------------------
# 6. Correlaciones
# ------------------------------------------------------------------------------
cat("\n--- Matriz de correlacion (EMBI, CDS, JLoss, GaR, controles) ---\n")
vars_cor <- c("EMBI_bps", "CDS_bps", "JLoss", "GaR_pp", "debt_gdp", "infl_yoy", "reer")
cormat <- round(cor(est[, vars_cor], use = "pairwise.complete.obs"), 2)
print(cormat)

comun <- subset(est, !is.na(EMBI_bps) & !is.na(CDS_bps))
cat(sprintf("\nEMBI vs CDS, submuestra donde ambos existen: N=%d, corr=%.2f\n",
            nrow(comun), cor(comun$EMBI_bps, comun$CDS_bps)))

# ------------------------------------------------------------------------------
# 7. Graficos -> PDF (y en pantalla si se corre interactivamente)
# ------------------------------------------------------------------------------
pdf("EDA_panel_bloomberg.pdf", width = 10, height = 7)

# 7.1 Distribuciones univariadas
par(mfrow = c(2, 2), mar = c(4, 4, 3, 1))
hist(est$EMBI_bps, breaks = 30, col = "#3A5A8C", border = "white",
     main = "EMBI Global Diversified (pb)", xlab = "pb")
hist(est$JLoss, breaks = 30, col = "#9A3B32", border = "white",
     main = "JLoss", xlab = "JLoss")
hist(est$GaR_pp, breaks = 30, col = "#2E6E52", border = "white",
     main = "GaR (q05, pp)", xlab = "pp")
hist(est$CDS_bps, breaks = 30, col = "#A9701F", border = "white",
     main = "CDS soberano 5A (pb)", xlab = "pb")

# 7.2 JLoss en el tiempo, un panel por pais (como fig_jloss_paises de la tesis)
paises <- sort(unique(panel$country))
par(mfrow = c(4, 5), mar = c(2, 2, 2, 1), oma = c(0, 0, 2, 0))
for (p in paises) {
  g <- subset(panel, country == p & !is.na(JLoss))
  if (nrow(g) == 0) next
  t <- as.numeric(substr(g$quarter, 1, 4)) + (as.numeric(substr(g$quarter, 6, 6)) - 1) / 4
  plot(t, g$JLoss, type = "l", col = "#3A5A8C", lwd = 1.5, main = p, cex.main = 0.9,
       xlab = "", ylab = "")
}
mtext("JLoss trimestral por pais (roster completo)", outer = TRUE, cex = 1.1, font = 2)

# 7.3 Relaciones bivariadas crudas (motivan H1 y H2 antes de controlar por FE)
par(mfrow = c(1, 2), mar = c(4, 4, 3, 1))
plot(est$JLoss, est$EMBI_bps, pch = 16, col = adjustcolor("#3A5A8C", 0.35),
     xlab = "JLoss", ylab = "EMBI (pb)", main = "EMBI vs. JLoss (crudo, sin FE)")
abline(lm(EMBI_bps ~ JLoss, est), col = "#9A3B32", lwd = 2)
plot(est$GaR_pp, est$EMBI_bps, pch = 16, col = adjustcolor("#2E6E52", 0.35),
     xlab = "GaR (pp)", ylab = "EMBI (pb)", main = "EMBI vs. GaR (crudo, sin FE)")
abline(lm(EMBI_bps ~ GaR_pp, est), col = "#9A3B32", lwd = 2)

# 7.4 Dispersion transversal de JLoss por pais (boxplot, ordenado por mediana)
par(mfrow = c(1, 1), mar = c(7, 4, 3, 1))
ord <- names(sort(tapply(est$JLoss, est$country, median)))
boxplot(JLoss ~ factor(country, levels = ord), data = est, las = 2,
        col = "#3A5A8C22", border = "#3A5A8C", main = "JLoss por pais (caja = RIC, muestra de estimacion)",
        xlab = "", ylab = "JLoss")

# 7.5 EMBI vs CDS, la submuestra comun (motiva "la metrica no cambia el resultado")
par(mfrow = c(1, 1), mar = c(4, 4, 3, 1))
plot(comun$CDS_bps, comun$EMBI_bps, pch = 16, col = adjustcolor("#A9701F", 0.4),
     xlab = "CDS soberano 5A (pb)", ylab = "EMBI (pb)",
     main = sprintf("EMBI vs. CDS (N=%d, corr=%.2f)", nrow(comun), cor(comun$EMBI_bps, comun$CDS_bps)))
abline(0, 1, lty = 2, col = "grey50")
abline(lm(EMBI_bps ~ CDS_bps, comun), col = "#9A3B32", lwd = 2)
legend("topleft", legend = c("ajuste lineal", "diagonal 45°"),
       col = c("#9A3B32", "grey50"), lty = c(1, 2), lwd = c(2, 1), bty = "n")

dev.off()
cat("\nGraficos guardados en: EDA_panel_bloomberg.pdf\n")
