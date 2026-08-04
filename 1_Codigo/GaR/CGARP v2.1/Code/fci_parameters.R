#### Parameters

initialDate <- "1990-01-01"
finalDate   <- "2024-03-31"

countries <- c("BRAZIL",
               "CHILE",
               "COLOMBIA",
               "MEXICO",
               "PERU")

referenceRyrCountry <- "US"

lagTilde  <- 260*10-1
lagPeriod <- 20
lagWindow <- 260*2
lagYear   <- 261

lagTildeMonth <- 119
lagMonth <- 1
lagWindowMonth <- 6

#standardizationMethod <- "method_a_cdf"
standardizationMethod <- "method_b_max"

timeFrame<- 120

lambda = 0.85


### Saving output options

saveXLSX <- TRUE
saveLong <- FALSE
saveIndexRelatedData <- TRUE
saveMonthlyRelatedData <- TRUE
saveDailyRelatedData <- TRUE


saveIndividuals <- TRUE
# saveIndividuals <- FALSE
# saveIndividuals <- "ask"

outputPath <- "C:/Users/HOME/Documents/Jloss/CGARP v2.1/output"
fileTag <- "test1"


