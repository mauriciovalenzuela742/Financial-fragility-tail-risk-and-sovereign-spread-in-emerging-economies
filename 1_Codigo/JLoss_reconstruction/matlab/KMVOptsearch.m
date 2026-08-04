%KMVOptsearch.m
function [Va,AssetTheta]=KMVOptsearch(E,D,r,T,EquityTheta)
EtoD=E/D;
x0=[1,1];
VaThetaX=fsolve(@(x)KMVfun(EtoD,r,T,EquityTheta,x),x0);
Va=VaThetaX(1)*E;
AssetTheta=VaThetaX(2);
% x=[1636234261/E,0.0688];
% F=KMVfun(EtoD,r,T,EquityTheta,x);