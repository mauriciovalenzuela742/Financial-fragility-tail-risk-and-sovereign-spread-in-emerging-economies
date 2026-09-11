# ==============================================================================
# crisis_interaccion.R
#
# Version R (plm) de p9_crisis_interaccion.py: la complementariedad JLoss x D
# dentro y fuera de crisis, SIN botar trimestres (indicacion del profesor coguia).
#
#   EMBI ~ JLoss_c + D_c + JxD + JxD_cr + JLoss_cr + D_cr [+ 6 controles] + FE
#
#   JxD      = JLoss_c x D_c                 -> b3  (complementariedad fuera de crisis)
#   JxD_cr   = JLoss_c x D_c x Crisis        -> b4
#   b3 + b4  = complementariedad en crisis   -> test de Wald H0: b3 + b4 = 0
#
# D = -GaR (pp). Prediccion del coguia: b4 ~ -b3  =>  b3 + b4 ~ 0.
#
# Uso:  "C:/Program Files/R/R-4.5.3/bin/Rscript.exe" crisis_interaccion.R
# Paquetes: plm, lmtest, sandwich, car
# ==============================================================================
suppressMessages({ library(plm); library(lmtest); library(sandwich); library(car) })

d <- read.csv("Panel_bloomberg.csv", stringsAsFactors = FALSE)
d <- subset(d, !is.na(EMBI_bps) & !is.na(JLoss) & !is.na(GaR))
d$GaR_pp <- d$GaR * 100
d$D_pp   <- -d$GaR_pp

GFC    <- c("2008Q4","2009Q1","2009Q2","2009Q3","2009Q4")
COVID  <- c("2020Q1","2020Q2","2020Q3","2020Q4","2021Q1","2021Q2","2021Q3","2021Q4")
EM1516 <- c("2015Q3","2015Q4","2016Q1")
CRISIS   <- c(GFC, COVID, EM1516)
BACKSTOP <- c(GFC, COVID)

CTRLS <- c("debt_gdp","fisc_bal","res_gdp","ca_gdp","infl_yoy","reer")

# centrado en la muestra completa (una sola muestra; coincide con Python)
d$JLoss_c <- d$JLoss - mean(d$JLoss)
d$D_c     <- d$D_pp  - mean(d$D_pp)
d$JxD     <- d$JLoss_c * d$D_c

mk_terms <- function(df, dummies) {
  for (nm in names(dummies)) {
    cr <- as.numeric(df$quarter %in% dummies[[nm]])
    df[[paste0("JxD_",   nm)]] <- df$JxD     * cr
    df[[paste0("JLoss_", nm)]] <- df$JLoss_c * cr
    df[[paste0("D_",     nm)]] <- df$D_c     * cr
  }
  df
}

run_spec <- function(dummies, ctrls, effect) {
  df <- mk_terms(d, dummies)
  if (length(ctrls)) df <- df[stats::complete.cases(df[, ctrls]), ]
  terms_int <- unlist(lapply(names(dummies), function(nm)
    c(paste0("JxD_", nm), paste0("JLoss_", nm), paste0("D_", nm))))
  rhs <- c("JLoss_c", "D_c", "JxD", terms_int, ctrls)
  f  <- as.formula(paste("EMBI_bps ~", paste(rhs, collapse = " + ")))
  pd <- pdata.frame(df, index = c("country", "quarter"))
  m  <- plm(f, data = pd, model = "within", effect = effect)
  V  <- tryCatch(vcovSCC(m), error = function(e) vcovHC(m, method = "arellano"))
  ct <- coeftest(m, vcov = V)
  out <- list(N = nobs(m), b3 = ct["JxD", "Estimate"], b3_t = ct["JxD", 3],
              b3_p = ct["JxD", 4])
  for (nm in names(dummies)) {
    k <- paste0("JxD_", nm)
    lh <- linearHypothesis(m, paste0("JxD + ", k, " = 0"), vcov. = V, test = "Chisq")
    out[[paste0("b4_", nm)]]        <- ct[k, "Estimate"]
    out[[paste0("b4_", nm, "_t")]]  <- ct[k, 3]
    out[[paste0("b4_", nm, "_p")]]  <- ct[k, 4]
    out[[paste0("s_",  nm)]]        <- ct["JxD", "Estimate"] + ct[k, "Estimate"]
    out[[paste0("s_",  nm, "_p")]]  <- lh[2, "Pr(>Chisq)"]
  }
  out
}

FE <- c(T = "time", P = "individual", PT = "twoways")
grids <- list("vector unico"          = list(cr = CRISIS),
              "Backstop vs EMstress"  = list(bk = BACKSTOP, em = EM1516))

cat(sprintf("N = %d, %d paises. Crisis=1 en %d obs (GFC %d, COVID %d, EM15-16 %d)\n\n",
            nrow(d), length(unique(d$country)), sum(d$quarter %in% CRISIS),
            sum(d$quarter %in% GFC), sum(d$quarter %in% COVID), sum(d$quarter %in% EM1516)))

res <- list()
for (gn in names(grids)) for (cl in c("sin controles", "+6 controles")) for (fe in names(FE)) {
  ctrls <- if (cl == "+6 controles") CTRLS else character(0)
  o <- run_spec(grids[[gn]], ctrls, FE[[fe]])
  res[[length(res) + 1]] <- c(list(grid = gn, controles = cl, fe = fe), o)
  cat(sprintf("[%-22s | %-13s | FE %-2s] N=%d\n", gn, cl, fe, o$N))
  cat(sprintf("    b3 (fuera de crisis) = %+.3f (t=%+.2f, p=%.3f)\n", o$b3, o$b3_t, o$b3_p))
  for (nm in names(grids[[gn]])) {
    lbl <- c(cr="Crisis", bk="Backstop", em="EMstress")[[nm]]
    cat(sprintf("    b4 x %-9s = %+.3f (t=%+.2f, p=%.3f) ; b3+b4 = %+.3f (Wald p = %.3f)\n",
                lbl, o[[paste0("b4_",nm)]], o[[paste0("b4_",nm,"_t")]],
                o[[paste0("b4_",nm,"_p")]], o[[paste0("s_",nm)]], o[[paste0("s_",nm,"_p")]]))
  }
  cat("\n")
}

allcols <- unique(unlist(lapply(res, names)))
flat <- do.call(rbind, lapply(res, function(r) {
  r[setdiff(allcols, names(r))] <- NA
  as.data.frame(r[allcols], stringsAsFactors = FALSE)
}))
write.csv(flat, "crisis_interaccion_bbg_R.csv", row.names = FALSE)
cat("Guardado: crisis_interaccion_bbg_R.csv\n")
