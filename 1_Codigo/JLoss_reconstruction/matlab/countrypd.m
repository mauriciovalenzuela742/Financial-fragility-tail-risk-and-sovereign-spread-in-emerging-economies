function [CR unexploss totloss]=countrypd(ctrp_mult, probs, rhos,loss_inf,loss_sup, num_order, num_factors, lgd, ead, percentil, num_steps)
exs=ead.*lgd;
exs1 = ead.*lgd.*probs;
lossprob = loss_distrib(ctrp_mult, exs, probs, rhos,loss_inf, loss_sup, num_steps,num_order,num_factors);
loss_perc=LinealXY2(lossprob(:,1), lossprob(:,2),percentil);
saddle_ul=loss_contrib(ctrp_mult, exs, probs, rhos, loss_perc, loss_perc, 0, num_order, num_factors);
exploss=sum(exs1);
unexploss=real(sum(saddle_ul));
totloss=real(exploss+ unexploss);
CR=totloss*100/sum(ead);%total percent loss
%loss_contrib(n_ctrp,lgd,probs,rhos,perc,perc,0,norder,nfactors)
%loss_distrib(C8:C116,F8:F116,G8:G116,H8:K116,M2,M3,M4,$G$3,$G$5)
%loss_distrib(ctrp_mult, exs, probs, rhos,loss_inf, loss_sup, num_steps,num_order,num_factors)
%[CR{1,i}(t,1) CR{1,i}(t,2)]=countrypd(ctrp_mult{1,i}, probs{1,i}(:,t), rhos{t,i}, loss_inf, loss_sup, num_order, num_factors, severity{1,i}, exposition{1,i}(:,t),percentil,num_steps)