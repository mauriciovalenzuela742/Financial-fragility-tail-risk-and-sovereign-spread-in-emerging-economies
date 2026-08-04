Read data from prices
clc
clear all
close all
%format from origin: [countryname,bankname,date,lt_borrow,st_borrow,tot_asset,cash_and_st_investments,net_income,net_rev,prof_margin]


[data_bank_equity stringsa]=xlsread('balance_data_monthly.xls');

save data_bs.mat

load data_bs.mat

%stringsa={[]};
N=length(stringsa);
databank_equity=data_bank_equity;

datenew=x2mdate(databank_equity(:,1));
databank_equity=[datenew databank_equity(:,2:8)];
stringsa=stringsa(2:N,1:2);
countriesall=stringsa(:,1);
banksall=stringsa(:,2);
indiv_countries=unique(countriesall);
indiv_bank=unique(banksall);
n_countries=length(indiv_countries);%%change this!!!!!
n_countries=3;%%change this!!!!!
N=length(stringsa);

for i=1:n_countries
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
for i=1:n_countries
 abankarray{i}={indiv_countries(i) unique({C{1,i}{:,:}})};
end


for j=1:N
for i=1:n_countries
    cond1(j,i)=strcmp(countriesall(j),indiv_countries(i));
    banklength(i)=length(abankarray{1,i}{1,2});
for k=1:banklength(i)
    cond2(j,k)=strcmp(abankarray{1,i}{1,2}{1,k},banksall{j,:});
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
    rows{i,k}=size([equitydata{:,i,k}],2)/8;
    requityres{i,k}=reshape([equitydata{:,i,k}],[8 rows{i,k}])';
    abankarrayn{i}={indiv_countries(i) banco{i,k}};
end
end

bs_array_daily=abankarrayn;
bs_array_quarter=abankarrayn;
bs_array_quarterly=abankarrayn;

for i=1:n_countries
for k=1:banklength(i)
    [ts_bs_date_array{i,k} ts_bs_array{i,k}] = quarterly(requityres{i,k}(:,1), requityres{i,k}(:,2:8));%%
    bs_array_daily{1,i}{1,2}{1,1}{2,k}=requityres{i,k};%%change this to quarterly
    bs_array_quarterly{1,i}{1,2}{1,1}{2,k}=[ts_bs_date_array{i,k}, ts_bs_array{i,k}];%%change this to quarterly
end
end

save data_bs_processed.mat

load data_bs_processed.mat
%%%new from here
%Group data

n_countries=size(bs_array_quarterly,2);

for i=1:n_countries
    banklength(i)=size(bs_array_quarterly{1,i}{1,2}{1,1},2);
for k=1:banklength(i)
    lengthdataeq{i,k}=size(bs_array_quarterly{1,i}{1,2}{1,1}{2,k},1);
    date{i,k}=bs_array_quarterly{1,i}{1,2}{1,1}{2,k}(:,1);%1:lengthdataeq{i,k}
    [year_date{i,k} month_date{i,k} day_date{i,k}]=datevec(date{i,k});
    M{i,k}=lengthdataeq{i,k};
    for l=1:M{i,k}
        groupdate_year_month{i,k}(l)=str2num([num2str(year_date{i,k}(l)),num2str(month_date{i,k}(l))]);
        if (month_date{i,k}(l,1) >=1 && month_date{i,k}(l)<=3)
        quarter_date{i,k}(l)=1;
        elseif (month_date{i,k}(l) >=4 && month_date{i,k}(l) <=6)
        quarter_date{i,k}(l)=2;
        elseif (month_date{i,k}(l) >=7 && month_date{i,k}(l) <=9)
        quarter_date{i,k}(l)=3;
        elseif (month_date{i,k}(l) >=10 && month_date{i,k}(l) <=12)
        quarter_date{i,k}(l)=4;
        end
    end
    quarter_date{i,k}=quarter_date{i,k}';
    for l=1:M{i,k}
    groupdate_year_quarter{i,k}(l,1)=str2num([num2str(year_date{i,k}(l)),num2str(quarter_date{i,k}(l))]);
    end
    quarter_date{i,k}=quarter_date{i,k}';
    id_group_date_year_month{i,k}=groupdate_year_month{i,k};
    id_group_date_year_quarter{i,k}=groupdate_year_quarter{i,k};
    bs_array_quarter{1,i}{1,2}{1,1}{2,k}=[id_group_date_year_quarter{i,k}, bs_array_quarterly{1,i}{1,2}{1,1}{2,k}]; %%id_group_date for month_date
end
end


save data_bs_processed.mat
clear 
clc
load data_bs_processed.mat
load data_mktcap_processed.mat
load data_price_processedsaved.mat



%%%New all data

alldata_array_quarter=realizedvar_array_quarter;%%new
%alldata_array_quarter=bs_array_quarter;

alldata_array_quarter{1,1}{1,2}{1,1}=alldata_array_quarter{1,1}{1,2}{1,1}(:,[1 2 3 4 6 7 8]); %make it more general!!!!drop if names are not equal!!!
alldata_array_quarter{1,2}{1,2}{1,1}=alldata_array_quarter{1,2}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 14 17 19 21 22 24]); %make it more general!!!!drop if names are not equal!!!
realizedvar_array_quarter{1,1}{1,2}{1,1}=realizedvar_array_quarter{1,1}{1,2}{1,1}(:,[1 2 3 4 6 7 8]); %make it more general!!!!drop if names are not equal!!!
bs_array_quarter{1,1}{1,2}{1,1}=bs_array_quarter{1,1}{1,2}{1,1}(:,[1 2 3 4 6 7 8]);
bs_array_quarter{1,2}{1,2}{1,1}=bs_array_quarter{1,2}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 14 17 19 21 22 24]);
%banklength(1)=banklength(1)-1;
n_countries=2;


for i=1:n_countries
%for i=1:1
banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);
for k=1:banklength(i)
%for k=1:4
%if(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(l,1)==realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,1))
   K{i,k}=size(bs_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   O{i,k}=size(realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   for l=1:K{i,k}
       for m=1:O{i,k}
            if(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(l,1)==realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,1))
            aux{i,k}(l,:)=[realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,:), alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(l,:)];
%             elseif(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(l,1)~=realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,1))
%             aux{i,k}(l,:)=[realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,:), 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
            end
       end
   end
   alldata_array_quarter{1,i}{1,2}{1,1}{2,k}=aux{i,k};    
end
end

% 
% for i=1:2
% banklength(i)=size(alldata_array_quarter{1,i}{1,2}{1,1},2);%%%see concistency when running all the countries        
% for k=1:banklength(i)
%     X{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
%     for x=2:X{i,k}
%     if (alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)==0 && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(1,1)~=0 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=19994 ... 
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20004 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20014 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20024 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20034 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20044 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20054 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20064 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20074 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20084 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20094 ...
%         && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20104)
%     
%         alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)+1;
%     end
%     
%     if (alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)==0 && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(1,1)~=0)
%         if(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==19994 ... 
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20004 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20014 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20024 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20034 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20044 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20054 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20064 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20074 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20084 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20094 ...
%         |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20104)
% 
%         alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)+7;
%         end
%     end
%     
%     end
% end
% end
% 

%%check this
for i=1:n_countries
banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);
for k=1:banklength(i)
%for k=1:4
   L{i,k}=size(bs_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   O{i,k}=size(realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   P{i,k}=size(mktcap_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   for l=1:L{i,k}
        for m=1:O{i,k}
            if(bs_array_quarter{1,i}{1,2}{1,1}{2,k}(l,1)==realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,1))
            auxi{i,k}(m,:)=[realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,:), alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(l,:)];
            end
       end
   end
   Q{i,k}=size(auxi{i,k},1);

   for p=1:P{i,k}
       for q=1:Q{i,k}
            if(auxi{i,k}(q,1)==mktcap_array_quarter{1,i}{1,2}{1,1}{2,k}(p,1))
            auxii{i,k}(p,:)=[auxi{i,k}(q,:),mktcap_array_quarter{1,i}{1,2}{1,1}{2,k}(p,:)];
            end
       end
   end
   alldata_array_quarter{1,i}{1,2}{1,1}{2,k}=auxii{i,k}(:,:);    
end
end

load data_stckmktindex.mat
load data_intrate.mat

%%%%%%%%%%%merge data interest rates %%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
for i=1:2
banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);%%%see concistency when running all the countries        
for k=1:banklength(i)
    ravg{i,k}=mean(intrate_quarter_array{1,i}{1,2}(:,2));
    raux{i,k}=intrate_quarter_array{1,i}{1,2}(:,1:2);
    X{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
    for x=1:X{i,k}
        for y=1:52
             if(raux{i,k}(y,1)==alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1))%%%%
                 alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,14)=raux{i,k}(y,2);
             end
        end
    end
end
end


%%%%%%%%%%%merge stock market data%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

for i=1:2
banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);%%%see concistency when running all the countries        
for k=1:banklength(i)
    savg{i,k}=mean(stckmkt_ret_quarter_array{1,i}{1,2}(:,2));
    saux{i,k}=stckmkt_ret_quarter_array{1,i}{1,2}(:,1:2);
    X{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
    for x=1:X{i,k}
        for y=1:50
             if(saux{i,k}(y,1)==alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1))%%%%
                 alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,15)=saux{i,k}(y,2);
             end
        end
    end
end
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%end
%%%now the spline yy = spline(x,y,xx) xx=dates, 

%save data_pds_processed.mat
save data_pds_processed_morecountries.mat

%%%%%run data mkt cap to generate quarters, then use it to add to the other
%%%%%data finally generate the complete data and estimate the individual
%%%%%pds