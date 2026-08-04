function loss_distriba=loss_distrib(ctrp_mult, exs, probs, rhos, loss_inf,...
                      loss_sup, num_steps, num_order, num_factors)
                  
ctrp_mult(:,1) = ctrp_mult;
exs(:,1) = exs;
probs(:,1) = probs;
rhos(:,:) = rhos;
N_ctrps = length(probs);
e_tot = 0;
prob_total(1:num_steps+1,1)       = 0;
p_temp(1:num_order,1)             = 0;
v_temp(1:num_order,1)             = 0;
P_state(1:num_order^num_factors,1)  = 0;
V_state(1:num_factors, 1:num_order^num_factors)=0;
saddle_guesses(1:num_order^num_factors,1)=0;
saddle_sup_bisec=0;
saddle_inf_bisec=0;
    
for i = 1:N_ctrps
    e_tot = e_tot + ctrp_mult(i, 1) * exs(i, 1);  
end;

p_cond(1:N_ctrps,1)              = 0;
p_incond(1:N_ctrps,1)            = 0;
a(1:N_ctrps,1)                   = 0;
mult_a(1:N_ctrps,1)              = 0;

for i = 1:N_ctrps
    a(i)=exs(i,1)/e_tot;
    mult_a(i) = ctrp_mult(i, 1);
    p_incond(i) = probs(i, 1);
end

loss_step = 0;

if num_steps > 0 
loss_step = (loss_sup-loss_inf)/num_steps;
end

zz = ghi(num_order);
for i = 1:num_order
    p_temp(i) = zz(i, 2);
    v_temp(i) = zz(i, 1);
end

for i = 1:num_order^num_factors
    P_state(i) = 1;
    saddle_guesses(i) = 0;
    for j = 1:num_factors
        V_state(j, i) = 0;
    end
end

for j = num_factors:-1:1
K = 1;
count = 1;
for i = 1:num_order^num_factors
    if count <= num_order^(j-1) 
        count = count+1;
    elseif count > num_order^(j-1) 
        count = 2;
        K = K + 1;
        if K > num_order 
        K = 1;
        end
    end
   P_state(i) = P_state(i) * p_temp(K);
   V_state(j, i) = v_temp(K);
    
end
end

for i = 1:(num_steps+1)
    prob_total(i) = 0;
end

for i=1:num_order ^ num_factors
    for j = 1:N_ctrps
    p_cond(j) = 0;
    v_state_ctrp = 0;
    rho_norm_ctrp = 0;
    for n_factor = 1:num_factors
        v_state_ctrp = v_state_ctrp+rhos(j,n_factor)*V_state(n_factor,i);
        rho_norm_ctrp = rho_norm_ctrp+rhos(j,n_factor)*rhos(j,n_factor);
    end
    p_cond(j) = CND((ICND(p_incond(j)) - v_state_ctrp) / sqrt(1 - rho_norm_ctrp));
    end
    
    big_guess=100000000;
    k0thG = get_K(N_ctrps, mult_a, a, e_tot, p_cond, 0);
    k1stG = get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, 0);
    k2ndG = get_K2nd(N_ctrps, mult_a, a, e_tot, p_cond, 0);
    k3rdG = get_K3rd(N_ctrps, mult_a, a, e_tot, p_cond, 0);
    saddle_guessD = k2ndG*k2ndG-2*k3rdG*(k1stG-loss_inf+(big_guess-1)*loss_step);
    if (saddle_guessD < 0)
    saddle_guess = -k2ndG/k3rdG;
    else
    saddle_guess = 0.6*(-k2ndG+sqrt(saddle_guessD))/k3rdG;
    end
    
    for n_loss = 1:(num_steps+1)
    loss_level = loss_inf + (n_loss - 1) * loss_step;
    %bisection like
    k1st_bisec = get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_guess);
    if k1st_bisec < loss_level
    saddle_inf_bisec = saddle_guess;
    is_inf = 1;
    is_sup = 0;
    elseif k1st_bisec > loss_level
    saddle_sup_bisec = saddle_guess;
    is_inf = 0;
    is_sup = 1;
    else
        break
    end
    
    if is_inf==1
    saddle_sup_bisec = saddle_inf_bisec;
    bisec_step = 0.1 * abs(saddle_sup_bisec) + 1;
        while (get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_sup_bisec) < loss_level),
            saddle_sup_bisec = saddle_sup_bisec + bisec_step;
        end
    elseif is_sup==1
        saddle_inf_bisec = saddle_sup_bisec;
        while (get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_inf_bisec) > loss_level),
            bisec_step = loss_level-get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_inf_bisec);
            bisec_step = bisec_step/get_K2nd(N_ctrps, mult_a, a, e_tot, p_cond, saddle_inf_bisec);
            saddle_inf_bisec = saddle_inf_bisec-0.5*abs(bisec_step)-1;
        end
    end
    saddle_diff = 10;
    saddle_guess = 0.5 * (saddle_sup_bisec + saddle_inf_bisec);
    while abs(saddle_diff) > 5,
    k1st_bisec = get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_guess);
    if k1st_bisec > loss_level
        saddle_sup_bisec = saddle_guess;
    elseif k1st_bisec < loss_level
        saddle_inf_bisec = saddle_guess;
    else
        break
    end
    saddle_guess = 0.5 * (saddle_sup_bisec + saddle_inf_bisec);
    saddle_diff = saddle_sup_bisec - saddle_inf_bisec;
    end
    
    saddle_tmp = find_saddlev1(N_ctrps, mult_a, a, e_tot, p_cond, loss_level, saddle_guess);
    saddle_guess = saddle_tmp;
    %building cgf's for the prob
    k0th = get_K(N_ctrps, mult_a, a, e_tot, p_cond, saddle_tmp);
    k1st = get_K1st(N_ctrps, mult_a, a, e_tot, p_cond, saddle_tmp);
    k2nd = get_K2nd(N_ctrps, mult_a, a, e_tot, p_cond, saddle_tmp);
    prob_tmp = get_prob(k0th, k1st, k2nd, saddle_tmp);
    %prob_tmp = 0; 
    prob_total(n_loss) = prob_total(n_loss) + prob_tmp * P_state(i);
  
    end
end

res(1:(num_steps+1),1:2)=0;

for i = 1:(num_steps+1)
    res(i,1) = loss_inf+(i-1)*loss_step;
    res(i,2) = prob_total(i);
end

saddleguess(1:length(res))=saddle_guess;
loss_distriba = [res saddleguess'];


