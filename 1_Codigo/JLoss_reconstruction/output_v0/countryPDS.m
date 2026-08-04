%%Aggregate pds
% num_order	= 7;
% num_factors	= 1;
% loss_inf	= 0.01;
% loss_sup	= 0.048;
% num_steps	= 500;
% percentil   = 0.99; %0.9997
%array{countryname, bankname, PDS!}
%write a function to transform the data...to

%from array calculations= arraycalcs{countryname, bankname}[PD t] reshape to an
%arrayprobs=array{countryname}[PD1..PDnbanks(countryj]

% ctrp_mult(1:N)=1,
% probs=array (country, bank) if time==t
% array{Country, t}(cross section banks): array{country}[ctrp_mult probs rho1 rho2 rho3 rho4 exposition severity]
% exposition = array{country, bank} lt_borrow	st_borrow, from balance_data_monthly.xls

% severity (1,N) = .5

function [totlossperc exploss unexploss]=countryPDS(data, numorder, numfactors, lossinf, lossup, numsteps, percentil)

num_order	= numorder;
num_factors	= numfactors;
loss_inf	= lossinf;
loss_sup	= lossup;
num_steps	= numsteps;
percentil   = percentil; %0.9997

ctrp_mult	= data(:,1);
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

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

saddle_ul=loss_contrib(ctrp_mult, exs, probs, rhos, loss_inf, loss_sup, 0, num_order, num_factors);
exploss=sum(exs1);
unexploss=sum(saddle_ul);
totloss=sum(exs1)+ sum(saddle_ul);
totlossperc=totloss*100/sum(exposition);