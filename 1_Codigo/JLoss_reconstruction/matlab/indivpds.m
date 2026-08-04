function [EDF DD]= indivpds( SD, LD, r, T, Vol_stk, Mkt_Cap) 
DP=SD+05*LD;
D=DP;
PriceTheta=Vol_stk;
EquityTheta=PriceTheta*sqrt(4); %see if sqrt(4)
E=Mkt_Cap;
Timeperiods=size(PriceTheta,1);

for i=1:Timeperiods
[Va(i),AssetTheta(i)]=KMVOptsearch(E(i),D(i),r,T,EquityTheta(i));
DD(i)=(Va(i)-DP(i))/(Va(i)*AssetTheta(i));
EDF(i)=normcdf(-DD(i));
end
DD=DD';
EDF=EDF';
