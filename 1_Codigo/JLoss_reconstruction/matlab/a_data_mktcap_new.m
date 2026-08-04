%%Read data from prices
clc
clear memory
clear all
close all
%format from origin: [countryname bankname date mktcap]

% 
 [data_bank_equity stringsa]=xlsread('mktcap_long.xlsx');
N=size((stringsa),1);
%N=10000;

%databank_equity=data_bank_equity(:,[2 3]);
databank_equity=data_bank_equity;

save data_mktcap.mat

load data_mktcap.mat

datenew=x2mdate(databank_equity(:,1));
databank_equity=[datenew databank_equity(:,2)];
stringsa=stringsa(2:N,1:2);
countriesall=stringsa(:,1);
banksall=stringsa(:,2);
indiv_countries=unique(countriesall);
indiv_bank=unique(banksall);
%n_countries=length(indiv_countries);
N=length(countriesall);
n_countries=5; %%change it!!
initial_countries=5;

for i=initial_countries:n_countries
for j=1:N
    if(strcmp(countriesall(j),indiv_countries(i))==1)
    bankcountry(i,j)={stringsa(j,2)};
    end
end
end

for p=1:size(bankcountry,1)
   for q=1:size(bankcountry,2)
   empties(q)=~isempty(bankcountry{p,q});
   end
   B=bankcountry(p,empties);
   C{p,1}=[B{:}];
end
C=C';
for i=initial_countries:n_countries
 abankarray{i}={indiv_countries(i) unique({C{1,i}{:,:}})};
end

for j=1:N
for i=initial_countries:n_countries
    cond1(j,i)=strcmp(countriesall(j),indiv_countries(i));
    banklength(i)=length(abankarray{1,i}{1,2});
for k=1:banklength(i)
    cond2(j,k)=strcmp(abankarray{1,i}{1,2}{1,k},banksall(j,:));
    if(cond1(j,i)==1 && cond2(j,k)==1)
        equitydata(j,i,k)={databank_equity(j,:)};
    end
end
end
end         


for i=initial_countries:n_countries
    banklength(i)=length(abankarray{1,i}{1,2});
for k=1:banklength(i)
    banco{i,k}={unique({C{1,i}{:,:}})};
    rows=size([equitydata{:,i,k}],2)/2;
    requityres{i,k}=reshape([equitydata{:,i,k}],[2 rows])';
    abankarrayn{i}={indiv_countries(i) banco{i,k}};
end
end

mktcap_array_daily=abankarrayn;
mktcap_array_quarterly=abankarrayn;
mktcap_array_quarter=abankarrayn;

for i=initial_countries:n_countries
for k=1:banklength(i)
    %abankarrayn{1,i}{1,2}{1,1}{2,k}=requityres{i,k};
    [ts_volume_date_array{i,k} ts_volume_array{i,k}] = quarterly(requityres{i,k}(:,1), requityres{i,k}(:,2));%%
    mktcap_array_daily{1,i}{1,2}{1,1}{2,k}=requityres{i,k};%%change this to quarterly
    mktcap_array_quarterly{1,i}{1,2}{1,1}{2,k}=[ts_volume_date_array{i,k}, ts_volume_array{i,k}];%%change this to quarterly
end
end

save data_mktcap_processed.mat

clear all
clc
load data_mktcap_processed.mat

mktcap_array_quarterly=abankarrayn;

for i=initial_countries:n_countries
for k=1:banklength(i)
    lengthdataeq{i,k}=length(requityres{i,k});
    date{i,k}=requityres{i,k}(2:lengthdataeq{i,k},1);
    [year_date{i,k} month_date{i,k} day_date{i,k}]=datevec(date{i,k});
    M{i,k}=length(year_date{i,k});
    for l=1:M{i,k}
        groupdate_year_month{i,k}(l)=str2num([num2str(year_date{i,k}(l)),num2str(month_date{i,k}(l))]);
        if (month_date{i,k}(l) >=1 && month_date{i,k}(l)<=3)
        quarter_date{i,k}(l)=1;
        elseif (month_date{i,k}(l) >=4 && month_date{i,k}(l) <=6)
        quarter_date{i,k}(l)=2;
        elseif (month_date{i,k}(l) >=7 && month_date{i,k}(l) <=9)
        quarter_date{i,k}(l)=3;
        elseif (month_date{i,k}(l) >=10 && month_date{i,k}(l) <=12)
        quarter_date{i,k}(l)=4;
        end
    end
    for l=1:M{i,k}
    groupdate_year_quarter{i,k}(l)=str2num([num2str(year_date{i,k}(l)),num2str(quarter_date{i,k}(l))]);
    end
    quarter_date{i,k}=quarter_date{i,k}';
    id_group_date_year_month{i,k}=groupdate_year_month{i,k}';
    id_group_date_year_quarter{i,k}=groupdate_year_quarter{i,k}';
    mktcap_array{1,i}{1,2}{1,1}{2,k}=[date{i,k} year_date{i,k} day_date{i,k} quarter_date{i,k} id_group_date_year_quarter{i,k} mktcap_array_daily{1,i}{1,2}{1,1}{2,k}(2:end,2)]; %%id_group_date for month_date
    end
end

for i=initial_countries:n_countries
for k=1:banklength(i)
     mktcap_array_quarter{1,i}{1,2}{1,1}{2,k}=[GroupSummary(mktcap_array{1,i}{1,2}{1,1}{2,k}(:,5:6),2,1,2,'last')];
end
end

save data_mktcap_processed_5_5.mat