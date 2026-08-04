function k1st=get_K1st(n_ctrp,mult_a, a, e_tot, p_def, saddle)
k1st=0;
for i=1:n_ctrp
    exp_term = exp(saddle * a(i));
    k1st = k1st+mult_a(i)*p_def(i)*a(i)*exp_term/(1-p_def(i)+p_def(i)*exp_term);
end
k1st=k1st;