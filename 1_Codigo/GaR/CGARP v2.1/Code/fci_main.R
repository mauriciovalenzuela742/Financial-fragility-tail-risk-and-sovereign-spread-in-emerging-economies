### Optional: CLEAN ENVIRONMENT AND COMMAND LINE

cat("\014")
rm(list=ls())


### Mandatory: Set Working Directory

workingDirectory <- "C:/Users/HOME/Documents/Jloss/CGARP v2.1/Code"
#--------------------------------------------------------------


### CODE

setwd(workingDirectory)

print("Loading Packages...")
source("fci_packages.R")

print("Loading Parameters...")
source("fci_parameters.R")

print("Loading Core...")
source("fci_wrapper.R")

if(saveXLSX){
  print("Storing Output...")
  source("fci_output.R")
}

# rm(list=setdiff(ls(),
#                 c("aggregatedFCI",
#                 "iData","mData","dData",
#                 "parametersDF")
#                 ))