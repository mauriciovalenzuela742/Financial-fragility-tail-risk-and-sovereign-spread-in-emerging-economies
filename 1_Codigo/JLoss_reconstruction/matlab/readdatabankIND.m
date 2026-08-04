%data
clear all
close all
clc
% Read the data
data = xlsread('CORPBANCA.xlsx');
%data = sortrows(data);
N=length(data);
dates = data(:,1);
dates = x2mdate(dates);
datadates=datevec(dates);
year = datadates(:,1);
month = datadates(:,2);
day = datadates(:,3);

SD=data(:,2);
LD=data(:,3);
SA=data(:,4);
LA=data(:,5);
EQ_price=data(:,6);
EQ_vol=data(:,7);
ny=max(year)-min(year)+1;
nm=max(month);
ndates=nm*ny;

data_CORPBANCA=[dates year month SD LD SA LA EQ_price EQ_vol];
save('data_corpbanca.mat','data_CORPBANCA'); 