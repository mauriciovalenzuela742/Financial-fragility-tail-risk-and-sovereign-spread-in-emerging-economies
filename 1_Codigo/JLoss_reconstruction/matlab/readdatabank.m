%data
clear all
close all
clc
% Read the data
data = xlsread('databanks.xls',1);
data = sortrows(data);
N=length(data);
dates = data(:,1);
dates = x2mdate(dates);
datadates=datevec(dates);
year = datadates(:,1);
month = datadates(:,2);
day = datadates(:,3);

country = data(:,2);
bank = data(:,3);
SD=data(:,4);
LD=data(:,5);
SA=data(:,6);
LA=data(:,7);
EQ=data(:,8);
nc=max(country);
nb=max(bank);
ny=max(year)-min(year)+1;
nm=max(month);
ndates=nm*ny;


data=[country bank dates year month SD LD SA LA EQ];
save data.mat

for i=1:nc
    for j=1:nb
        for n=1:N
        if ((country(n)==i) && (bank(n)==j))
        databank(i,j)=data(n);
        end
        end
    end
end

% nc=max(country);
% nb=max(bank);
% ny=max(year)-min(year)+1;
% nm=max(month);
% ndates=nm*ny;
% %datemy=1:ndates;
% EQorg=zeros(nc,nb,ny,nm);
% %EQ_monthret=zeros(nc,nb,ndates);
% %EQ_sd_year=zeros(nc,nb,ny);
% 
condic=zeros(N,1);
for k=min(dates):max(dates)
    for n=1:N
     if ((dates(n)==k))
               condic(n)=1;                     
     end
    end
end

%for n=1:N
    for i=1:nc
        for j=1:nb
            for k=dates'
                    if ((country(n)==i) && (bank(n)==j) && (dates(n)==k))
                            EQorg(i,j,k)=EQ(n);                              
                    end
            end
      %  EQ_monthret(i,j,k)=diff(log(EQorg(i,j,:))); 
        %EQ_sd_year(i,j)=std(EQ_monthret(i,j,:));   
        end
    end
%end 

% for o=1:12
% corte(o)=EQorg(1,1,2004,o);
% end
% 
% for u=1:11
% corte_ret(u)= EQ_monthret(1,1,2004,u);
% end
% 
% EQ_sd_year(1,1,2004)