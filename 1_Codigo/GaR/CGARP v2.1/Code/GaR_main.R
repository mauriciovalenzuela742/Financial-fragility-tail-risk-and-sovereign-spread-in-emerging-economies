### CLEAN ENVIRONMENT AND COMMAND LINE

cat("\014")
rm(list = ls())


### Working Directory

# workingDirectory <- ""


### If you are using a recent version of RStudio, activate the following code
### line to automatically point the current directory to the path of this
### main file.
### Only if running from RStudio!!!
workingDirectory <- "C:/Users/HOME/Documents/Jloss/CGARP v2.1/Code"




### Missing packages installation
### Comment back once the packages are properly installed

### Command to install rqpd package.
#### It installs the package directly from the repository.
#install.packages("rqpd", repos="http://R-Forge.R-project.org")

### Command to install snpar package.
#### It installs the package directly from the compressed file.
## Define la ruta exacta al archivo
#ruta_paquete <- "C:/Users/HOME/Documents/Jloss/CGARP v2.1/Code/packages/snpar_1.0.tar.gz"

# Instalación desde archivo local
#install.packages(ruta_paquete, repos = NULL, type = "source")



### CODE

setwd(workingDirectory)

source("GaR_packages.R")
source("GaR_parameters.R")
source("GaR_functions.R")
source("GaR_wrapper.R")
source("GaR_output.R")