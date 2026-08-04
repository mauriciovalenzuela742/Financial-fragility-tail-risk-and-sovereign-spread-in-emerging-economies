function gprob=get_prob(K, k1st, k2nd, saddle)
prob = exp(K-saddle*k1st+0.5*saddle*saddle*k2nd)*CND(-sqrt(saddle*saddle*k2nd));
if (saddle > 0)
    prob = 1 - prob;
end
gprob = prob;
