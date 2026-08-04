function K=get_K(n_ctrp,mult_a, a, e_tot, p_def, saddle)
K=0;
for i=1:n_ctrp
    K=K+mult_a(i)*log(1-p_def(i)+p_def(i)*exp(saddle*a(i)));
end
K=K;