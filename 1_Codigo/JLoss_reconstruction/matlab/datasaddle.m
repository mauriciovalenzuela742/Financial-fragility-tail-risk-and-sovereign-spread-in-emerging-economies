clear
clc
data=xlsread('data_replica.xlsx','data');
num_order	= 7;
num_factors	= 1;
loss_inf	= 0.01;
loss_sup	= 0.048;
num_steps	= 500;
percentil   = 0.9997; 

ctrp_mult	= data(:,1);
%exs	    = data(:,2);
probs	    = data(:,3);
rho1	    = data(:,4);
rho2	    = data(:,5);
rho3	    = data(:,6);
rho4	    = data(:,7);
exposition	= data(:,8);
severity    = data(:,9);
rhos        = [rho1 rho2 rho3 rho4];
exs         = exposition.*severity;
exs1        = exposition.*severity.*probs;

saddleresults=loss_distrib(ctrp_mult, exs, probs, rhos, loss_inf, loss_sup, num_steps, num_order, num_factors);
saddle_ul=loss_contrib(ctrp_mult, exs, probs, rhos, loss_inf, loss_sup, 0, num_order, num_factors);


saddle_dist=[saddleresults(:,1) saddleresults(:,2)]
saddle_point = saddleresults(1,3)
scatter(saddle_dist(:,1),saddle_dist(:,2),10)
percentile_loss=LinealXY2(saddle_dist(:,1),saddle_dist(:,2),percentil)*100;

disp(['The percentile is (%):']); 
disp([percentile_loss]);

disp(['The expected losses are:']);
exploss=sum(exs1)
disp(['The unexpected losses are:']);
unexploss=sum(saddle_ul)
disp(['The total losses are ($)']);
totloss=sum(exs1)+ sum(saddle_ul)
disp(['The total losses are (%)']);
totlossperc=totloss*100/sum(exposition)