%%Read data from prices
%%%Maybe it would be good to change the returns data to something more
%%%filled, like an average, instead of the "quarter" function.

clc
clear memory
clear all
close all
% format from origin: [countryname bankname date price]
% [data_bank_equity stringsa]=xlsread('price_long.csv');
% N=size((stringsa),1);
% databank_equity=data_bank_equity(:,[2 3]);

%when old versions of matlab use the following
% fid = fopen('price_long.csv');
% textdata = textscan(fid, '%s');
% fclose(fid);
% N=length(textdata{1});
% 
% for i=1:N
% splitted_text{i,1}=split(',"',textdata{1}{i});
% end
% 
% for i=2:N
% countriesall{i-1,1}=splitted_text{i,1}{1,1};
% banksall{i-1,1}=splitted_text{i,1}{1,2};
% datenew(i-1,1)=x2mdate(str2num(splitted_text{i,1}{1,3}));
% databank_equity(i-1,1)=str2num(splitted_text{i,1}{1,4});
% end

% databank_equity=[datenew databank_equity];
% save data_prices_a.mat

clear all
clc
load data_prices.mat

% omit this in case using an old matlab version
datenew=x2mdate(databank_equity(:,1));
databank_equity=[datenew databank_equity(:,2)];
stringsa=stringsa(2:N,1:2);
countriesall=stringsa(:,1);
banksall=stringsa(:,2);

indiv_countries=unique(countriesall);
indiv_bank=unique(banksall);
%n_countries=length(indiv_countries);
n_countries=22; %%change it!! 22 25 26 pending
%N=length(countriesall);
N=801850; %change ths number, its only to fix russia
initial_countries=22;

for i=initial_countries:n_countries
for j=766000:N
    if(strcmp(countriesall(j),indiv_countries(i))==1)
    bankcountry(i,j)={banksall(j,1)};%%here I have changed stringsa
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

for j=766000:N
for i=initial_countries:n_countries
    cond1(j,i)=strcmp(countriesall(j),indiv_countries(i));
    banklength(i)=size(abankarray{1,i}{1,2},2);
for k=1:banklength(i)
    cond2(j,k)=strcmp(abankarray{1,i}{1,2}{1,k},banksall(j,:));
    if(cond1(j,i)==1 && cond2(j,k)==1)
        equitydata(j,i,k)={databank_equity(j,:)};
    end
end
end
end         


for i=initial_countries:n_countries
    banklength(i)=size(abankarray{1,i}{1,2},2);
for k=1:banklength(i)
    banco{i,k}={unique({C{1,i}{:,:}})};
    rows=size([equitydata{:,i,k}],2)/2;
    requityres{i,k}=reshape([equitydata{:,i,k}],[2 rows])';
    abankarrayn{i}={indiv_countries(i) banco{i,k}};
end
end

for i=initial_countries:n_countries
     banklength(i)=size(abankarray{1,i}{1,2},2);
for k=1:banklength(i)
    abankarrayn{1,i}{1,2}{1,1}{2,k}=requityres{i,k};
    returns_array{1,i}{1,2}{1,1}{2,k}={diff(log(requityres{i,k}(:,2)))};
end
end

%returns_array=abankarrayn;
returns_array=abankarrayn;
returns_array_quarter=abankarrayn;
variance_array_quarter=abankarrayn;
realizedvar_array_quarter=abankarrayn;

for i=initial_countries:n_countries
     banklength(i)=size(abankarray{1,i}{1,2},2);
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
    returns_array{1,i}{1,2}{1,1}{2,k}=[date{i,k} year_date{i,k} day_date{i,k} quarter_date{i,k} id_group_date_year_quarter{i,k} diff(log(requityres{i,k}(:,2)))]; %%id_group_date for month_date
    variance_array_quarter{1,i}{1,2}{1,1}{2,k}=var(diff(log(requityres{i,k}(:,2))));
end
end

for i=initial_countries:n_countries
     banklength(i)=size(abankarray{1,i}{1,2},2);
for k=1:banklength(i)
     %year_date_rv{i,k}=unique(returns_array{1,i}{1,2}{1,1}{2,k}(:,[2 4]),'rows');
     %realizedvar_array{1,i}{1,2}{1,1}{2,k}=[year_date_rv{i,k}(:,1) GroupSummary(returns_array{1,i}{1,2}{1,1}{2,k}(:,5:6),2,1,2,'realizedvar')];
     realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}=[GroupSummary(returns_array{1,i}{1,2}{1,1}{2,k}(:,5:6),2,1,2,'realizedvar')];
end
end
%%%%CHANGE FOR THE FUTURE USE SEE THE QUARTERLY DATES%%%%
for i=initial_countries:n_countries
    banklength(i)=size(abankarray{1,i}{1,2},2);
    %%%%%%%%%%%%%%%%%%%%%%the problem is shere should be the number of
    %%%%%%%%%%%%%%%%%%%%%%banks or sth like this
for k=1:banklength(i)
    %%%%[returns_array_quartera{i,k},returns_array_quarterb{i,k}]=quarterly(returns_array{1,i}{1,2}{1,1}{2,k}(:,4),returns_array{1,i}{1,2}{1,1}{2,k}(:,6));
    [returns_array_quartera{i,k},returns_array_quarterb{i,k}]=quarterly(returns_array{1,i}{1,2}{1,1}{2,k}(:,1), returns_array{1,i}{1,2}{1,1}{2,k}(:,5:6));
    returns_array_quarter{1,i}{1,2}{1,1}{2,k}=[returns_array_quartera{i,k},returns_array_quarterb{i,k}];
end
end

%%%%%%comeback to file kind of variable

% processed={'country' , 'bank' , 'yearquarter', 'rv'};
% for i=1:n_countries
% for k=1:banklength(i)
%     length_rv{i,k}=size(realizedvar_array{1,i}{1,2}{1,1}{2,k},1);
%     country_rv_array{i}={realizedvar_array{1,i}{1,1}{1,1}};
%     bank_rv_array{i,k}={realizedvar_array{1,i}{1,2}{1,1}{1,k}};
%     country_bank_array{i,k}(1:length_rv{i,k},1)=country_rv_array{i};
%     country_bank_array{i,k}(1:length_rv{i,k},2)=bank_rv_array{i,k};
% end
% end
% 
% for i=1:n_countries
% for k=1:banklength(i)
%    processedi=[realizedvar_array{1,i}{1,2}{1,1}{2,k}(:,1) realizedvar_array{1,i}{1,2}{1,1}{2,k}(:,2)];
%    processedj=[country_bank_array{i,k}];
%    L=length(processedj);
%    for l=1:L
%        processedk(l,:)=[processedj(l,:), processedi(l,1), processedi(l,2)];
%    end
%    processed=[processed; processedk];
% end
% end

save data_price_processed_22_22.mat