################################################################################
### Preamble functions
################################################################################

z_score <- function(data) {
  return((data - mean(data, na.rm = TRUE)) / sd(data, na.rm = TRUE))
}





get_q_coeff <- function(aux_data_frame){
  
  n = nrow(aux_data_frame)
  
  aux_data_frame$rowresult <- row.names(aux_data_frame)
  aux_data_frame$q <- NA
  aux_data_frame$coefficient <- NA
  
  q1 = regex("\\[\\d+\\.\\d+\\]")
  q2 = regex("\\d+\\.\\d+")
  
  for(k in 1:n){
    aux_data_frame$coefficient[k] <- gsub(pattern = q1,
                                          replacement = "",
                                          x = aux_data_frame$rowresult[k])
    aux_data_frame$q[k] <- as.numeric(str_extract(pattern =  q2,
                                                  string =  aux_data_frame$rowresult[k]))
  }
  return(aux_data_frame)
}
