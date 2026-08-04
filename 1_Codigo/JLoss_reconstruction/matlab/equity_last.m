%import data
clc
clear all
close all
[databank_equity stringsa]=xlsread('data_bank_equity.xls');
N=length(stringsa);

datenew=x2mdate(databank_equity(:,1));
databank_equity=[datenew databank_equity(:,2)];
stringsa=stringsa(2:N,1:2);
countriesall=stringsa(:,1);
banksall=stringsa(:,2);
indiv_countries=unique(stringsa(:,1));
indiv_bank=unique(stringsa(:,2));
n_countries=length(indiv_countries);


for i=1:n_countries
for j=1:N-1
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
for i=1:n_countries
 abankarray{i}={indiv_countries(i) unique({C{1,i}{:,:}})};
end

for j=1:N-1
for i=1:n_countries
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


for i=1:n_countries
    banklength(i)=length(abankarray{1,i}{1,2});
for k=1:banklength(i)
    banco{i,k}={unique({C{1,i}{:,:}})};
    rows=size([equitydata{:,i,k}],2)/2;
    requityres{i,k}=reshape([equitydata{:,i,k}],[2 rows])';
    abankarrayn{i}={indiv_countries(i) banco{i,k}};
end
end

for i=1:n_countries
for k=1:banklength(i)
    abankarrayn{1,i}{1,2}{1,1}{2,k}=requityres{i,k};
    returns_array{1,i}{1,2}{1,1}{2,k}={diff(log(requityres{i,k}(:,2)))};
end
end

returns_array=abankarrayn;
variance_array=abankarrayn;
realizedvar_array=abankarrayn;

for i=1:n_countries
for k=1:banklength(i)
    lengthdataeq{i,k}=length(requityres{i,k});
    date{i,k}=requityres{i,k}(2:lengthdataeq{i,k},1);
    [year_date{i,k} month_date{i,k} day_date{i,k}]=datevec(date{i,k});
    returns_array{1,i}{1,2}{1,1}{2,k}=[date{i,k} year_date{i,k} day_date{i,k} month_date{i,k} diff(log(requityres{i,k}(:,2)))];
    variance_array{1,i}{1,2}{1,1}{2,k}=var(diff(log(requityres{i,k}(:,2))));
end
end

for i=1:n_countries
for k=1:banklength(i)
    year_date_rv{i,k}=unique(returns_array{1,i}{1,2}{1,1}{2,k}(:,[2 4]),'rows');
    realizedvar_array{1,i}{1,2}{1,1}{2,k}=[year_date_rv{i,k}(:,1) GroupSummary(returns_array{1,i}{1,2}{1,1}{2,k}(:,4:5),2,1,2,'realizedvar')];
end
end

%%%%%%comeback
processed={'country' , 'bank' , 'year', 'month', 'rv'};
for i=1:n_countries
for k=1:banklength(i)
    length_rv{i,k}=size(realizedvar_array{1,i}{1,2}{1,1}{2,k},1);
    country_rv_array{i}={realizedvar_array{1,i}{1,1}{1,1}};
    bank_rv_array{i,k}={realizedvar_array{1,i}{1,2}{1,1}{1,k}};
    country_bank_array{i,k}(1:length_rv{i,k},1)=country_rv_array{i};
    country_bank_array{i,k}(1:length_rv{i,k},2)=bank_rv_array{i,k};
    processedi=[country_bank_array{i,k} realizedvar_array{1,i}{1,2}{1,1}{2,k}(:,1) realizedvar_array{1,i}{1,2}{1,1}{2,k}(:,2) realizedvar_array{1,i}{1,2}{1,1}{2,k}(:,3)];
    processed=[processed; processedi];
end
end

xlswrite('rv.xls', processed);
