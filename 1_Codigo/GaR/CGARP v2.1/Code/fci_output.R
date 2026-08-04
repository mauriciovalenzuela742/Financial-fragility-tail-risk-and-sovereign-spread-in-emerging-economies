#STORING XLSX TIME AND PARAMETER STAMPED FILE OUTPUT

auxTime <-
  str_remove_all(as.character(Sys.time()) , pattern = "[-: ]")
auxTime <-
  paste (substr(auxTime, 1, 8), "_", substr(auxTime, 9, 14), sep = "")

outputFile <- paste(outputPath, "/", "FCI_", auxTime, "_", fileTag,".xlsx", sep = "")


wb <- createWorkbook()

addWorksheet(wb = wb,
             sheetName = "FCI")

# Saving long data frame
if (saveLong) {
  writeData(wb = wb, sheet = "FCI", x = iData[, c('DATES', 'country', 'fcis')])
} else{
  writeData(wb = wb, sheet = "FCI", x = aggregatedFCI)
}


if(saveIndexRelatedData){
  addWorksheet(wb = wb,
               sheetName = "Index_Data")
  writeData(wb = wb, sheet = "Index_Data", x = iData)
}

if(saveMonthlyRelatedData){
  addWorksheet(wb = wb,
               sheetName = "Monthly_Data")
  writeData(wb = wb, sheet = "Monthly_Data", x = mData)
}

if(saveDailyRelatedData){
  addWorksheet(wb = wb,
               sheetName = "Daily_Data")
  writeData(wb = wb, sheet = "Monthly_Data", x = dData)
}


addWorksheet(wb = wb,
             sheetName = "Parameters")

writeData(wb = wb,
  x = parametersDF,
  sheet = "Parameters"
)

saveWorkbook(wb, file = outputFile, overwrite = TRUE)


if(!exists("saveIndividuals")){
  saveIndividuals <- FALSE
}

if(saveIndividuals){
  for(country_output in colnames(aggregatedFCI)[-1]){
    aux_output_individual <- aggregatedFCI[,c("DATES", country_output)]
    aux_output_individual <- aux_output_individual[!is.na(aux_output_individual[[country_output]]),]
    aux_output_individual$DATES <- format(x = aux_output_individual$DATES, "%d/%m%/%Y")
    colnames(aux_output_individual) <- c("DATES", "FCI")
    write.csv(x = aux_output_individual, row.names = FALSE,
              file = str_c("../individuals/",country_output,"/FCI_", country_output, ".csv"))
  }
}


#Output to clipboard
# write.table(x=dData, file="clipboard-16384", sep="\t")
# write.table(x=iData, file="clipboard-16384", sep="\t")
# write.table(x=mData, file="clipboard-16384", sep="\t")