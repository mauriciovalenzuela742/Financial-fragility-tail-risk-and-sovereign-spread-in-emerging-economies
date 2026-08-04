function realizedvar = realizedvar(returns)
returnssq=returns .* returns;
realizedvar=sum(returnssq);
