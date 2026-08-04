function k2nd=get_K2nd(n_ctrp,mult_a, a, e_tot, p_def, saddle)
k2nd=0;
for i=1:n_ctrp
 exp_term = exp(saddle * a(i)); 
 k2nd = k2nd+mult_a(i)*(p_def(i)*a(i)*a(i)*exp_term/(1-p_def(i)+p_def(i)*...
 exp_term)-p_def(i)*p_def(i)*a(i)*a(i)*exp_term*exp_term/(1-p_def(i)+...
 p_def(i)*exp_term)^2);
end
k2nd=k2nd;