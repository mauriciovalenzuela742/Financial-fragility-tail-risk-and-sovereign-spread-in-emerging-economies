
################################################################################
### Preamble parameters
################################################################################


source_file = "C:/Users/HOME/Documents/Jloss/CGARP v2.1/Source/GaR_panel.xlsx"
sheet = "Panel"

dependent_variable <- "g_GDP"

independent_variables <- c("VIX","FCI")

orth_var_dep <- c("FCI")
orth_var_ind <- c("VIX")


#Forecast horizon
h <- 12

#Number of quantiles (19 -> tau in {0.05,0.10,...,0.95})
n_tau <- 19


#Enable to introduce interaction terms
#interaction_term <- 


selected_date_v = c('01/03/2023')

selected_date_next_v = c('01/03/2024')

# a = 0.05 -> 5% GaR
GaR_level <- 0.05

#Expected Shortfall and Expected Longrise quantile level
probability <- 0.05

#Confidence level of coefficient intervals
alpha_CI <- 0.05

### Saving output options

outputPath <- "C:/Users/HOME/Documents/Jloss/CGARP v2.1/output"
fileTag <- "test1"