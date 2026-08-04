function loss_contriba=loss_contrib(ctrp_mult, exs, probs, rhos,loss_inf, loss_sup, num_steps,num_order, num_factors)
%=loss_contrib(ctrpmult,severity,pdef,rhos,percentile,percentile,0,order,nfactors)
ctrp_mult = ctrp_mult;
probs = probs;
rhos = rhos;
N_ctrps = length(probs);
e_tot = 0;%change

for i = 1:N_ctrps
e_tot = e_tot + ctrp_mult(i, 1) * exs(i, 1);
end

for i = 1:N_ctrps
    a(i) = exs(i, 1) / e_tot;
    mult_a(i) = ctrp_mult(i, 1);
end

loss_step = 0;%change
if(num_steps > 0)
    loss_step = (loss_sup - loss_inf) / num_steps;
end
%static quadrature data
zz = ghi(num_order);
for i = 1:num_order
    p_temp(i) = zz(i, 2);
    v_temp(i) = zz(i, 1);
end

for i = 1:(num_order ^ num_factors)
    P_state(i) = 1;%check
    saddle_guesses(i) = 0;%check
    for j = 1:num_factors 
        V_state(j, i) = 0;
    end
end

for j = num_factors:(-1):1 %check
K = 1;
count = 1;

for i = 1:num_order ^ num_factors
    if (count <= num_order ^ (j - 1))
        count = count + 1;
    else (count > num_order ^ (j - 1));
        count = 2;
        K = K + 1;
        if(K > num_order) 
            K = 1;
        end
    end
        %building probability of being in a particular state
    P_state(i) = P_state(i) * p_temp(K);
    V_state(j, i) = v_temp(K);
end
end

%gauss quadrature completed for n_factors and n_order

norm_contrib_total = 0;
exs_total = 0;
for i = 1:(num_steps + 1)
    prob_total(i) = 0;
end

for i = 1:N_ctrps
    contribs(i) = 0;
    exs_total = exs_total + ctrp_mult(i, 1) * exs(i, 1);
end

for i = 1:num_order ^ num_factors
for j = 1:N_ctrps
    p_cond(j) = 0;
    v_state_ctrp = 0;
    rho_norm_ctrp = 0;
    for n_factor = 1:num_factors
        v_state_ctrp = v_state_ctrp + rhos(j, n_factor) * V_state(n_factor, i);
        rho_norm_ctrp = rho_norm_ctrp + rhos(j, n_factor) * rhos(j, n_factor);
    end
    p_cond(j) = CND((ICND(probs(j, 1)) - v_state_ctrp) / sqrt(1 - rho_norm_ctrp));
end

%produce adequate initial guess
saddle_guess = -20;
while (get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_guess) < loss_inf)
saddle_guess = saddle_guess + 10;
end

for n_loss = 1:(num_steps + 1)

saddle_tmp = find_saddlev1(N_ctrps, mult_a, a, e_tot, p_cond, loss_inf + (n_loss - 1) * loss_step, saddle_guess);
%saddle_guess = saddle_tmp
    
%building cgf's for the prob
    k0th = get_K(N_ctrps, mult_a, a, e_tot, p_cond, saddle_tmp);
    k1st = get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_tmp);
    k2nd = get_K2nd(N_ctrps, mult_a, a, e_tot, p_cond, saddle_tmp);
    norm_contrib = P_state(i) * exp(k0th - k1st * saddle_tmp) / sqrt(k2nd);
    norm_contrib_total = norm_contrib_total + norm_contrib;
%add contributions
    for n_ctrp = 1:N_ctrps
        contribs(n_ctrp) = contribs(n_ctrp) + ...
        norm_contrib * p_cond(n_ctrp) * exp(saddle_tmp * exs(n_ctrp, 1) / exs_total) /...
        (1 - p_cond(n_ctrp) + p_cond(n_ctrp) * exp(saddle_tmp * exs(n_ctrp, 1) / exs_total));
    end

%prob_tmp = get_prob(k0th, k1st, k2nd, saddle_tmp)
%prob_total(n_loss) = prob_total(n_loss) + prob_tmp * P_state(i)

end
end

for i = 1:N_ctrps
    result(i, 1) = exs(i, 1) * contribs(i) / norm_contrib_total;
end
loss_contriba = result;




