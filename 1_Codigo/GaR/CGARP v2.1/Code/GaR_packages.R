################################################################################
### Necessary packages
################################################################################

packages <- c(
  'readxl',
  'openxlsx',
  'lubridate',
  'ggplot2',
  'dplyr',
  'ggpubr',
  'plotly',
  'latex2exp',
  'caTools',
  'rqpd',
  'broom',
  'snpar',
  'tidyverse',
  'stringr'
)


################################################################################
### Packages setup
################################################################################

for(p in packages){
  if(! p %in% installed.packages()){
    install.packages(p)
  }
}

#Check for newer R versions that do not provide the rqpd package.
if(! 'rqpd' %in% installed.packages()){
  install.packages("rqpd", repos="http://R-Forge.R-project.org")
}

for(p in packages){
  if(! p %in% tolower((.packages()))){
    library(p,character.only = TRUE)
  }
}

rm(p)
