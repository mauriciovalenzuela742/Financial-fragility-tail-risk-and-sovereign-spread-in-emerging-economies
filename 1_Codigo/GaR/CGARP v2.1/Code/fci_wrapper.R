################################################################################
### Preamble functions
################################################################################

source("fci_funs.R")


################################################################################
### Parameters reference
################################################################################

originalLag <- FALSE

variables <- c("initialDate",
               "finalDate",
               "lagTilde ",
               "lagPeriod",
               "lagWindow",
               "lagYear",
               "originalLag",
               "lagTildeMonth",
               "lagMonth",
               "lagWindowMonth",
               "standardizationMethod",
               "lambda")

variablesValues <- c(initialDate,
                     finalDate,
                     lagTilde ,
                     lagPeriod,
                     lagWindow,
                     lagYear  ,
                     originalLag,
                     lagTildeMonth,
                     lagMonth,
                     lagWindowMonth,
                     standardizationMethod,
                     lambda)

parametersDF <- data.frame(Variables = variables,
                           Values = variablesValues)




################################################################################
### Main code
################################################################################

f1 <- as.Date.character(initialDate)
f2 <- as.Date.character(  finalDate)

auxf1 <- strsplit(initialDate,"-")
auxf2 <- strsplit(  finalDate,"-")

f1Month <- as.numeric(auxf1[[1]][1])*100 + as.numeric(auxf1[[1]][2])
f2Month <- as.numeric(auxf2[[1]][1])*100 + as.numeric(auxf2[[1]][2])
  
aggDates <- range_eom(f1Month, f2Month)
aggDates <- eomInt2Date(aggDates$DATES)
aggregatedFCI <- data.frame('DATES' = aggDates)

flag = TRUE

date_formats <- c("%Y-%m-%d", "%d/%m/%Y")


for(country in countries){
  
  print(paste0("   ",country))
  f1 <- as.Date.character(initialDate)
  f2 <- as.Date.character(  finalDate)
  D <- range_business_days(f1,f2)
  dailyData <- data.frame('DATES' = D)
  
  countryFiles <- dir(paste0("../individuals/", country))

  print(paste0("   ","   ",country," ","STX"))
  var2read <- "STX"
  fileVarName <- countryFiles[str_detect(countryFiles, paste0("^",var2read,"*"))]
  filePath <- paste("..", "individuals", country, fileVarName, sep="/")
  STX <- read.csv(filePath,
                  stringsAsFactors = FALSE, )
  STX$DATES <- as.Date.character(STX$DATES, tryFormats = date_formats)
  
  print(paste0("   ","   ",country," ","Ryr"))
  var2read <- "Ryr"
  fileVarName <- countryFiles[str_detect(countryFiles, paste0("^",var2read,"*"))]
  filePath <- paste("..", "individuals", country, fileVarName, sep="/")
  Ryr <-  read.csv(filePath,
                   stringsAsFactors = FALSE)
  Ryr$DATES <- as.Date.character(Ryr$DATES, tryFormats = date_formats)
  
  print(paste0("   ","   ",country," ","CPI"))
  var2read <- "CPI"
  fileVarName <- countryFiles[str_detect(countryFiles, paste0("^",var2read,"*"))]
  filePath <- paste("..", "individuals", country, fileVarName, sep="/")
  CPI <-  read.csv(filePath,
                   stringsAsFactors = FALSE)
  CPI$DATES <- as.Date.character(CPI$DATES, tryFormats = date_formats)
  
  basisFiles <- dir(paste0("../individuals/", referenceRyrCountry))
  
  print(paste0("   ","   ",country," ","CPI reference"))
  var2read <- "CPI"
  fileVarName <- basisFiles[str_detect(basisFiles, paste0("^",var2read,"*"))]
  filePath <- paste("..", "individuals", referenceRyrCountry, fileVarName, sep="/")
  CPIbs <-  read.csv(filePath,
                     stringsAsFactors = FALSE)
  colnames(CPIbs) <- c("DATES","CPIbs")
  CPIbs$DATES <- as.Date.character(CPIbs$DATES, tryFormats = date_formats)
  
  
  print(paste0("   ","   ",country," ","Ryr reference"))
  var2read <- "Ryr"
  fileVarName <- basisFiles[str_detect(basisFiles, paste0("^",var2read,"*"))]
  filePath <- paste("..", "individuals", referenceRyrCountry, fileVarName, sep="/")
  Rbs <-  read.csv(filePath,
                   stringsAsFactors = FALSE)
  colnames(Rbs) <- c("DATES","Rbs")
  Rbs$DATES <- as.Date.character(Rbs$DATES, tryFormats = date_formats)
  
  print(paste0("   ",country," ","Daily Data"))
  dailyData <- join_STX  (dailyData, STX)
  dailyData <- join_CPI  (dailyData, CPI)
  dailyData <- join_Ryr  (dailyData, Ryr)
  dailyData <- join_Rbs  (dailyData, Rbs)
  dailyData <- join_CPIbs(dailyData, CPIbs)
  
  
  dailyData <- get_STX      (dailyData = dailyData,
                             lagTilde = lagTilde,
                             lagPeriod = lagPeriod,
                             lagWindow = lagWindow)
  
  dailyData <- get_Rbs_daily(dailyData = dailyData,
                             lagYear = lagYear)

  if(country!=referenceRyrCountry){
    dailyData <- get_Ryr_daily(dailyData = dailyData,
                               lagTilde = lagTilde,
                               lagPeriod = lagPeriod,
                               lagWindow = lagWindow,
                               lagYear = lagYear)
    
  }else{
    dailyData <- get_Ryr_daily_reference(dailyData = dailyData,
                                         lagTilde = lagTilde,
                                         lagPeriod = lagPeriod,
                                         lagWindow = lagWindow,
                                         lagYear = lagYear)
    
  }
  
  print(paste0("   ",country," ","Monthly Data"))
  
  dailyData <- get_d2m_dates(dailyData)
  
  d2mData <- dailyData[dailyData$EOM,
                       c('YM','VSTX','CMAX','VRyr','CDIFF')]
  
  colnames(d2mData)[1] <- "DATES"
  
  var2read <- "rEER"
  fileVarName <- countryFiles[str_detect(countryFiles, paste0("^",var2read,"*"))]
  filePath <- paste("..", "individuals", country, fileVarName, sep="/")
  rEER <- read.csv(filePath, stringsAsFactors = FALSE)
  
  monthlyData <- range_eom(from = f1Month,
                           to = f2Month)
  
  monthlyData <- join_rEER(mData = monthlyData,
                           rEER = rEER)
  
  monthlyData <- get_rEER(monthlyData = monthlyData,
                          lagTildeMonth = lagTildeMonth,
                          lagMonth = lagMonth,
                          lagWindowMonth = lagWindowMonth)
  
  
  monthlyIndices <- monthlyData[,c('DATES','VEER','CUMUL')]
  
  monthlyIndices <- join_daily(mData = monthlyIndices,
                               dData = d2mData)
  
  monthlyIndices <- monthlyIndices[1:get_min_index(monthlyIndices),]
  
  monthlyIndices <- monthlyIndices[order(monthlyIndices$DATES,decreasing = FALSE),]
  
  
  print(paste0("   ",country," ","Subindices"))
  
  columns <- c('VSTX','CMAX','VRyr','CDIFF','VEER','CUMUL')
  
  for(k in columns){
    
    if(standardizationMethod=="method_a_cdf"){
     monthlyIndices[,k] <- method_a_cdf(monthlyIndices[,k],timeFrame = timeFrame)
    }
    if(standardizationMethod=="method_b_max"){
     monthlyIndices[,k] <- method_b_max(monthlyIndices[,k],timeFrame = timeFrame)
    }
  }
  
  monthlyIndices$iSTX <- (monthlyIndices$VSTX + monthlyIndices$CMAX )/2
  monthlyIndices$iRyr <- (monthlyIndices$VRyr + monthlyIndices$CDIFF)/2
  monthlyIndices$iEER <- (monthlyIndices$VEER + monthlyIndices$CUMUL)/2
  
  print(paste0("   ",country," ","Correlations"))
  
  monthlyIndices$cSTX_Ryr <- corr_EWMA(monthlyIndices$iSTX,monthlyIndices$iRyr, lambda = lambda)
  monthlyIndices$cSTX_EER <- corr_EWMA(monthlyIndices$iSTX,monthlyIndices$iEER, lambda = lambda)
  monthlyIndices$cRyr_EER <- corr_EWMA(monthlyIndices$iRyr,monthlyIndices$iEER, lambda = lambda)
  
  print(paste0("   ",country," ","FCI"))
  
  monthlyIndices$fcis <- FCIS(monthlyIndices)
  
  print(paste0("   ",country," ","Storing data"))
  
  monthlyIndices$DATES <- eomInt2Date(monthlyIndices$DATES)

  if(flag){
    dData <- dailyData
    dData$country <- country
    mData <- monthlyData
    mData$country <- country
    iData <- monthlyIndices
    iData$country <- country
    flag = FALSE
  }
  else{
    auxdailyData <- dailyData
    auxdailyData$country <- country
    dData <- rbind(dData, auxdailyData)
    auxmonthlyData <- monthlyData
    auxmonthlyData$country <- country
    mData <- rbind(mData, auxmonthlyData)
    auxmonthlyIndices <- monthlyIndices
    auxmonthlyIndices$country <- country
    iData <- rbind(iData, auxmonthlyIndices)
  }
  
  colnames(monthlyIndices)[colnames(monthlyIndices)=="fcis"] = country
  
  aggregatedFCI <- merge.data.frame(x = aggregatedFCI,
                               y = monthlyIndices[,c("DATES", country)],
                               by="DATES",
                               all.x = TRUE, sort = FALSE)
}

aggregatedFCI <- aggregatedFCI[order(aggregatedFCI$DATES,decreasing = TRUE),]

if(length(countries)==1){
  aggregatedFCI$aux <- NA
  idx_agg <- get_min_1value(aggregatedFCI[,-1])
  aggregatedFCI <- aggregatedFCI[,-3]
}else{
  idx_agg <- get_min_1value(aggregatedFCI[,-1])
}

aggregatedFCI <- aggregatedFCI[1:idx_agg,]