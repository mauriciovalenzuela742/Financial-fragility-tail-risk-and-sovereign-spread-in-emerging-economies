function find_saddle=find_saddlev1(n_ctrp,mult_a,a,e_tot,probs,t,s)
ss_guess = s;
ss_old = ss_guess;
for i = 1:100
k1st = get_K1st(n_ctrp, mult_a, a, e_tot, probs, ss_old);
if (abs(k1st-t)<0.000000001)
break
end
    k2nd = get_K2nd(n_ctrp, mult_a, a, e_tot, probs, ss_old);
    ss_new = ss_old-(k1st-t)/k2nd;
    ss_old = ss_new;
end
find_saddle = ss_old;
