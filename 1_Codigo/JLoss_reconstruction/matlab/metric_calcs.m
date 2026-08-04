clear
clc

close all
clear all
clc

load data_corpbanca.mat
r=0.05; 
T=1;%T: time to expiration
EQ_ret=diff(log(data_CORPBANCA(:,8)));
M=length(data_CORPBANCA(:,8));
for k=2:M
data_CORPBANCA1(k-1,:)=data_CORPBANCA(k,:);
end
data_CORPBANCA=data_CORPBANCA1;
clear data_CORPBANCA1;
N=length(EQ_ret);
Vol_stock=zeros(N,1);
Vol_stock(1)=std(EQ_ret(1:12));
lambda=0.94;
for i=2:N
Vol_stock(i,1)=(1-lambda)*EQ_ret(i)^2+lambda*Vol_stock(i-1);%Vol_stock1=EQ_ret.*EQ_ret;%Garch
end

SD=data_CORPBANCA(:,3); %SD(i)=databanks(i,1);
LD=data_CORPBANCA(:,4); %LD(i)=databanks(i,2);
DP=SD+0.5*LD; %DP(i)=SD(i)+0.5*LD(i);% DP:Defaut point;% SD: short debt, LD: long debt
%D: Debt maket value
D=DP;
%theta:volatility
% PriceTheta:   volatility of stock price
PriceTheta=Vol_stock;
%EquityTheta: volatility of stock price
EquityTheta=PriceTheta*sqrt(12);
%AssetTheta: volatility of asset
%E:Equit maket value price by quantity
E=data_CORPBANCA(:,8).*data_CORPBANCA(:,9);
%Va: Value of asset to compute the Va and AssetTheta
for i=1:N
[Va(i),AssetTheta(i)]=KMVOptsearch(E(i),D(i),r,T,EquityTheta(i));
DD(i)=(Va(i)-DP(i))/(Va(i)*AssetTheta(i));
EDF(i)=normcdf(-DD(i));
end

DD=DD';
EDF=EDF';

dates=data_CORPBANCA(1:N,1);
plot(dates,Vol_stock,'--', dates, EDF, '-.', dates,DD, dates, EQ_ret, ':');
datetick('x',12);
legend('Vol stock', 'EDF', 'DD', 'return')
% Optimization terminated: first-order optimality is less than options.Tolfun.
% Va=2.5888e+008
% AssetTheta=0.5797
% DD=0.8922
% EDF=0.1861



%%%%%%Individual PDS correlation%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
datapds=xlsread('pds.xlsx');
[COEFF,SCORE,latent] = princomp(datapds); 
explanatory=cumsum(latent)./sum(latent);
correlation=corrcoef(datapds(:,1),SCORE(:,1));
correlation=correlation(1,2);

%%%%%%Joint PDs%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%data reading and parameters%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

data=xlsread('data_replica.xlsx','data');
num_order	= 7;
num_factors	= 1;
loss_inf	= 0.01;
loss_sup	= 0.048;
num_steps	= 500;
percentil   = 0.99; %0.9997

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
totlossperc=totloss*100/sum(exposition)