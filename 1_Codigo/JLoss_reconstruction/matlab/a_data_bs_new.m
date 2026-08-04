% Read data from prices
% clc
% clear all
% close all
% %format from origin: [countryname,bankname,date,lt_borrow,st_borrow,tot_asset,cash_and_st_investments,net_income,net_rev,prof_margin]
% 
% 
% [data_bank_equity stringsa]=xlsread('balance_data_monthly.xls');
% 
% save data_bs.mat
% 
% load data_bs.mat
% 
% %stringsa={[]};
% N=length(stringsa);
% databank_equity=data_bank_equity;
% 
% datenew=x2mdate(databank_equity(:,1));
% databank_equity=[datenew databank_equity(:,2:8)];
% stringsa=stringsa(2:N,1:2);
% countriesall=stringsa(:,1);
% banksall=stringsa(:,2);
% indiv_countries=unique(countriesall);
% indiv_bank=unique(banksall);
% n_countries=length(indiv_countries);%%change this!!!!!
% %n_countries=1;%%change this!!!!!
% N=length(stringsa);
% 
% for i=1:n_countries
% for j=1:N
%     if(strcmp(countriesall(j),indiv_countries(i))==1)
%     bankcountry(i,j)={stringsa(j,2)};
%     end
% end
% end
% 
% for p=1:size(bankcountry,1)
%    for q=1:size(bankcountry,2)
%    empties(q)=~isempty(bankcountry{p,q});
%    end
%    B=bankcountry(p,empties);
%    C{p,1}=[B{:}];
% end
% C=C';
% for i=1:n_countries
%  abankarray{i}={indiv_countries(i) unique({C{1,i}{:,:}})};
% end
% 
% 
% for j=1:N
% for i=1:n_countries
%     cond1(j,i)=strcmp(countriesall(j),indiv_countries(i));
%     banklength(i)=length(abankarray{1,i}{1,2});
% for k=1:banklength(i)
%     cond2(j,k)=strcmp(abankarray{1,i}{1,2}{1,k},banksall{j,:});
%     if(cond1(j,i)==1 && cond2(j,k)==1)
%         equitydata(j,i,k)={databank_equity(j,:)};
%     end
% end
% end
% end         
% 
% for i=1:n_countries
%     banklength(i)=length(abankarray{1,i}{1,2});
% for k=1:banklength(i)
%     banco{i,k}={unique({C{1,i}{:,:}})};
%     rows{i,k}=size([equitydata{:,i,k}],2)/8;
%     requityres{i,k}=reshape([equitydata{:,i,k}],[8 rows{i,k}])';
%     abankarrayn{i}={indiv_countries(i) banco{i,k}};
% end
% end
% 
% bs_array_daily=abankarrayn;
% bs_array_quarter=abankarrayn;
% bs_array_quarterly=abankarrayn;
% 
% for i=1:n_countries
% for k=1:banklength(i)
%     [ts_bs_date_array{i,k} ts_bs_array{i,k}] = quarterly(requityres{i,k}(:,1), requityres{i,k}(:,2:8));%%
%     bs_array_daily{1,i}{1,2}{1,1}{2,k}=requityres{i,k};%%change this to quarterly
%     bs_array_quarterly{1,i}{1,2}{1,1}{2,k}=[ts_bs_date_array{i,k}, ts_bs_array{i,k}];%%change this to quarterly
% end
% end
% 
% save data_bs_processed.mat
% 
% load data_bs_processed.mat
% %%%new from here
% %Group data
% 
% n_countries=size(bs_array_quarterly,2);
% 
% for i=1:n_countries
%     banklength(i)=size(bs_array_quarterly{1,i}{1,2}{1,1},2);
% for k=1:banklength(i)
%     lengthdataeq{i,k}=size(bs_array_quarterly{1,i}{1,2}{1,1}{2,k},1);
%     date{i,k}=bs_array_quarterly{1,i}{1,2}{1,1}{2,k}(:,1);%1:lengthdataeq{i,k}
%     [year_date{i,k} month_date{i,k} day_date{i,k}]=datevec(date{i,k});
%     M{i,k}=lengthdataeq{i,k};
%     for l=1:M{i,k}
%         groupdate_year_month{i,k}(l)=str2num([num2str(year_date{i,k}(l)),num2str(month_date{i,k}(l))]);
%         if (month_date{i,k}(l,1) >=1 && month_date{i,k}(l)<=3)
%         quarter_date{i,k}(l)=1;
%         elseif (month_date{i,k}(l) >=4 && month_date{i,k}(l) <=6)
%         quarter_date{i,k}(l)=2;
%         elseif (month_date{i,k}(l) >=7 && month_date{i,k}(l) <=9)
%         quarter_date{i,k}(l)=3;
%         elseif (month_date{i,k}(l) >=10 && month_date{i,k}(l) <=12)
%         quarter_date{i,k}(l)=4;
%         end
%     end
%     quarter_date{i,k}=quarter_date{i,k}';
%     for l=1:M{i,k}
%     groupdate_year_quarter{i,k}(l,1)=str2num([num2str(year_date{i,k}(l)),num2str(quarter_date{i,k}(l))]);
%     end
%     quarter_date{i,k}=quarter_date{i,k}';
%     id_group_date_year_month{i,k}=groupdate_year_month{i,k};
%     id_group_date_year_quarter{i,k}=groupdate_year_quarter{i,k};
%     bs_array_quarter{1,i}{1,2}{1,1}{2,k}=[id_group_date_year_quarter{i,k}, bs_array_quarterly{1,i}{1,2}{1,1}{2,k}]; %%id_group_date for month_date
% end
% end
% 
% 
% save data_bs_processed.mat
clear 
clc
%load data_bs_processed.mat
load bsdata_filled.mat
% load data_mktcap_processed.mat
% load data_price_processed_merged.mat
load MKTCAP_MERGED
load PRICE_MERGED
load data_stckmktindex.mat
load data_intrate.mat

%%%New all data


%%%RESHAPE THE SERIES TO MATCH ALL THE COUNTRIES

%%% Argentina
realizedvar_array_quarter{1,1}{1,2}{1,1}=realizedvar_array_quarter{1,1}{1,2}{1,1}(:,[1 2 3 4 6 7 8]); 
realizedvar_array_quarter{1,1}{1,1}{1,1}=realizedvar_array_quarter{1,1}{1,1}{1,1};
returns_array_quarter{1,1}{1,2}{1,1}=returns_array_quarter{1,1}{1,2}{1,1}(:,[1 2 3 4 6 7 8]);
returns_array_quarter{1,1}{1,1}{1,1}=returns_array_quarter{1,1}{1,1}{1,1};
mktcap_array_quarter{1,1}{1,2}{1,1}=mktcap_array_quarter{1,1}{1,2}{1,1}(:,[1 2 3 4 5 6 7]);
mktcap_array_quarter{1,1}{1,1}{1,1}=mktcap_array_quarter{1,1}{1,1}{1,1};
intrate_quarter_array{1,1}{1,2}=intrate_quarter_array{1,1}{1,2};
intrate_quarter_array{1,1}{1,1}=intrate_quarter_array{1,1}{1,1};
stckmkt_ret_quarter_array{1,1}{1,2}=stckmkt_ret_quarter_array{1,1}{1,2};
stckmkt_ret_quarter_array{1,1}{1,1}=stckmkt_ret_quarter_array{1,1}{1,1};

%%% Brazil
returns_array_quarter{1,2}{1,2}{1,1}=returns_array_quarter{1,2}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 10 12 13 14 17 18 20 21 23]);
realizedvar_array_quarter{1,2}{1,2}{1,1}=realizedvar_array_quarter{1,2}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 10 12 13 14 17 18 20 21 23]);
mktcap_array_quarter{1,2}{1,2}{1,1}=mktcap_array_quarter{1,2}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 10 12 13 14 17 18 20 21 23]);

returns_array_quarter{1,2}{1,1}{1,1}=returns_array_quarter{1,2}{1,1}{1,1};
realizedvar_array_quarter{1,2}{1,1}{1,1}=realizedvar_array_quarter{1,2}{1,1}{1,1};
mktcap_array_quarter{1,2}{1,1}{1,1}=mktcap_array_quarter{1,2}{1,1}{1,1};
intrate_quarter_array{1,2}{1,2}=intrate_quarter_array{1,2}{1,2};
intrate_quarter_array{1,2}{1,1}=intrate_quarter_array{1,2}{1,1};
stckmkt_ret_quarter_array{1,2}{1,2}=stckmkt_ret_quarter_array{1,2}{1,2};
stckmkt_ret_quarter_array{1,2}{1,1}=stckmkt_ret_quarter_array{1,2}{1,1};

%%% Bulgaria
returns_array_quarter{1,3}{1,2}{1,1}=returns_array_quarter{1,3}{1,2}{1,1}(:,[1 2 3 4 6]);
realizedvar_array_quarter{1,3}{1,2}{1,1}=realizedvar_array_quarter{1,3}{1,2}{1,1}(:,[1 2 3 4 6]);
mktcap_array_quarter{1,3}{1,2}{1,1}=mktcap_array_quarter{1,3}{1,2}{1,1}(:,[1 2 3 4 6]);
bs_array_quarter_filled{1,3}{1,2}{1,1}=bs_array_quarter_filled{1,3}{1,2}{1,1}(:,[1 2 3 4 5]);
bs_array_quarter{1,3}{1,2}{1,1}=bs_array_quarter{1,3}{1,2}{1,1}(:,[1 2 3 4 5]);

returns_array_quarter{1,3}{1,1}{1,1}=returns_array_quarter{1,3}{1,1}{1,1};
realizedvar_array_quarter{1,3}{1,1}{1,1}=realizedvar_array_quarter{1,3}{1,1}{1,1};
mktcap_array_quarter{1,3}{1,1}{1,1}=mktcap_array_quarter{1,3}{1,1}{1,1};
bs_array_quarter_filled{1,3}{1,1}{1,1}=bs_array_quarter_filled{1,3}{1,1}{1,1};
bs_array_quarter{1,3}{1,1}{1,1}=bs_array_quarter{1,3}{1,1}{1,1};
intrate_quarter_array{1,3}{1,2}=intrate_quarter_array{1,3}{1,2};
intrate_quarter_array{1,3}{1,1}=intrate_quarter_array{1,3}{1,1};
stckmkt_ret_quarter_array{1,3}{1,2}=stckmkt_ret_quarter_array{1,3}{1,2};
stckmkt_ret_quarter_array{1,3}{1,1}=stckmkt_ret_quarter_array{1,3}{1,1};


%%% Chile
returns_array_quarter{1,4}{1,2}{1,1}=returns_array_quarter{1,4}{1,2}{1,1}(:,[1 2 3 4 5 6]);
realizedvar_array_quarter{1,4}{1,2}{1,1}=realizedvar_array_quarter{1,4}{1,2}{1,1}(:,[1 2 3 4 5 6]);
mktcap_array_quarter{1,4}{1,2}{1,1}=mktcap_array_quarter{1,4}{1,2}{1,1}(:,[1 2 3 4 5 6]);
bs_array_quarter_filled{1,4}{1,2}{1,1}=bs_array_quarter_filled{1,4}{1,2}{1,1}(:,[1 2 3 4 5 6]);
bs_array_quarter{1,4}{1,2}{1,1}=bs_array_quarter{1,4}{1,2}{1,1}(:,[1 2 3 4 5 6]);

returns_array_quarter{1,4}{1,1}{1,1}=returns_array_quarter{1,4}{1,1}{1,1};
realizedvar_array_quarter{1,4}{1,1}{1,1}=realizedvar_array_quarter{1,4}{1,1}{1,1};
mktcap_array_quarter{1,4}{1,1}{1,1}=mktcap_array_quarter{1,4}{1,1}{1,1};
bs_array_quarter_filled {1,4}{1,1}{1,1}=bs_array_quarter_filled{1,4}{1,1}{1,1};
bs_array_quarter{1,4}{1,1}{1,1}=bs_array_quarter{1,4}{1,1}{1,1};
intrate_quarter_array{1,4}{1,2}=intrate_quarter_array{1,4}{1,2};
intrate_quarter_array{1,4}{1,1}=intrate_quarter_array{1,4}{1,1};
stckmkt_ret_quarter_array{1,4}{1,2}=stckmkt_ret_quarter_array{1,4}{1,2};
stckmkt_ret_quarter_array{1,4}{1,1}=stckmkt_ret_quarter_array{1,4}{1,1};


%%% China
returns_array_quarter{1,5}{1,2}{1,1}=returns_array_quarter{1,5}{1,2}{1,1}(:,[1 2 3 5 6 7 8 9 10 11 12 14]);
realizedvar_array_quarter{1,5}{1,2}{1,1}=realizedvar_array_quarter{1,5}{1,2}{1,1}(:,[1 2 3 5 6 7 8 9 10 11 12 14]);
mktcap_array_quarter{1,5}{1,2}{1,1}=mktcap_array_quarter{1,5}{1,2}{1,1}(:,[1 2 3 5 6 7 8 9 10 11 12 14]);
bs_array_quarter_filled{1,5}{1,2}{1,1}=bs_array_quarter_filled{1,5}{1,2}{1,1}(:,[1 2 3 5 6 7 8 9 10 11 12 14]);
bs_array_quarter{1,5}{1,2}{1,1}=bs_array_quarter{1,5}{1,2}{1,1}(:,[1 2 3 5 6 7 8 9 10 11 12 14]);

returns_array_quarter{1,5}{1,1}{1,1}=returns_array_quarter{1,5}{1,1}{1,1};
realizedvar_array_quarter{1,5}{1,1}{1,1}=realizedvar_array_quarter{1,5}{1,1}{1,1};
mktcap_array_quarter{1,5}{1,1}{1,1}=mktcap_array_quarter{1,5}{1,1}{1,1};
bs_array_quarter_filled {1,5}{1,1}{1,1}=bs_array_quarter_filled{1,5}{1,1}{1,1};
bs_array_quarter{1,5}{1,1}{1,1}=bs_array_quarter{1,5}{1,1}{1,1};
intrate_quarter_array{1,5}{1,2}=intrate_quarter_array{1,5}{1,2};
intrate_quarter_array{1,5}{1,1}=intrate_quarter_array{1,5}{1,1};
stckmkt_ret_quarter_array{1,5}{1,2}=stckmkt_ret_quarter_array{1,5}{1,2};
stckmkt_ret_quarter_array{1,5}{1,1}=stckmkt_ret_quarter_array{1,5}{1,1};


%%% Colombia
returns_array_quarter{1,6}{1,2}{1,1}=returns_array_quarter{1,6}{1,2}{1,1}(:,[1 2 3 4 5 9 10]);
realizedvar_array_quarter{1,6}{1,2}{1,1}=realizedvar_array_quarter{1,6}{1,2}{1,1}(:,[1 2 3 4 5 9 10]);
mktcap_array_quarter{1,6}{1,2}{1,1}=mktcap_array_quarter{1,6}{1,2}{1,1}(:,[1 2 3 4 5 9 10]);
bs_array_quarter_filled{1,6}{1,2}{1,1}=bs_array_quarter_filled{1,6}{1,2}{1,1}(:,[1 2 3 4 5 9 10]);
bs_array_quarter{1,6}{1,2}{1,1}=bs_array_quarter{1,6}{1,2}{1,1}(:,[1 2 3 4 5 9 10]);

returns_array_quarter{1,6}{1,1}{1,1}=returns_array_quarter{1,6}{1,1}{1,1};
realizedvar_array_quarter{1,6}{1,1}{1,1}=realizedvar_array_quarter{1,6}{1,1}{1,1};
mktcap_array_quarter{1,6}{1,1}{1,1}=mktcap_array_quarter{1,6}{1,1}{1,1};
bs_array_quarter_filled {1,6}{1,1}{1,1}=bs_array_quarter_filled{1,6}{1,1}{1,1};
bs_array_quarter{1,6}{1,1}{1,1}=bs_array_quarter{1,6}{1,1}{1,1};
intrate_quarter_array{1,6}{1,2}=intrate_quarter_array{1,6}{1,2};
intrate_quarter_array{1,6}{1,1}=intrate_quarter_array{1,6}{1,1};
stckmkt_ret_quarter_array{1,6}{1,2}=stckmkt_ret_quarter_array{1,6}{1,2};
stckmkt_ret_quarter_array{1,6}{1,1}=stckmkt_ret_quarter_array{1,6}{1,1};

%%% Croatia
returns_array_quarter{1,7}{1,2}{1,1}=returns_array_quarter{1,7}{1,2}{1,1}(:,[1 3 4 5 7 8 9 10 11 12 13 15 16 17 18 19]);
realizedvar_array_quarter{1,7}{1,2}{1,1}=realizedvar_array_quarter{1,7}{1,2}{1,1}(:,[1 3 4 5 7 8 9 10 11 12 13 15 16 17 18 19]);
mktcap_array_quarter{1,7}{1,2}{1,1}=mktcap_array_quarter{1,7}{1,2}{1,1}(:,[1 3 4 5 7 8 9 10 11 12 13 15 16 17 18 19]);
bs_array_quarter_filled{1,7}{1,2}{1,1}=bs_array_quarter_filled{1,7}{1,2}{1,1}(:,[1 2 3 4 6 7 8 9 10 11 12 14 15 16 17 18]);
bs_array_quarter{1,7}{1,2}{1,1}=bs_array_quarter{1,7}{1,2}{1,1}(:,[1 2 3 4 6 7 8 9 10 11 12 14 15 16 17 18]);

returns_array_quarter{1,7}{1,1}{1,1}=returns_array_quarter{1,7}{1,1}{1,1};
realizedvar_array_quarter{1,7}{1,1}{1,1}=realizedvar_array_quarter{1,7}{1,1}{1,1};
mktcap_array_quarter{1,7}{1,1}{1,1}=mktcap_array_quarter{1,7}{1,1}{1,1};
bs_array_quarter_filled{1,7}{1,1}{1,1}=bs_array_quarter_filled{1,7}{1,1}{1,1};
bs_array_quarter{1,7}{1,1}{1,1}=bs_array_quarter{1,7}{1,1}{1,1};
intrate_quarter_array{1,7}{1,2}=intrate_quarter_array{1,7}{1,2};
intrate_quarter_array{1,7}{1,1}=intrate_quarter_array{1,7}{1,1};
stckmkt_ret_quarter_array{1,7}{1,2}=stckmkt_ret_quarter_array{1,7}{1,2};
stckmkt_ret_quarter_array{1,7}{1,1}=stckmkt_ret_quarter_array{1,7}{1,1};


%%% Ecuador, eliminate, Egypt generate
returns_array_quarter{1,8}{1,2}{1,1}=returns_array_quarter{1,9}{1,2}{1,1}(:,[3 4 5 8 9 10 11 13 14]);
realizedvar_array_quarter{1,8}{1,2}{1,1}=realizedvar_array_quarter{1,9}{1,2}{1,1}(:,[3 4 5 8 9 10 11 13 14]);
mktcap_array_quarter{1,8}{1,2}{1,1}=mktcap_array_quarter{1,8}{1,2}{1,1}(:,[3 4 5 8 9 10 11 13 14]);
bs_array_quarter_filled{1,8}{1,2}{1,1}=bs_array_quarter_filled{1,9}{1,2}{1,1}(:,[3 4 5 8 9 10 11 13 14]);
bs_array_quarter{1,8}{1,2}{1,1}=bs_array_quarter{1,9}{1,2}{1,1}(:,[3 4 5 8 9 10 11 13 14]);

returns_array_quarter{1,8}{1,1}{1,1}=returns_array_quarter{1,9}{1,1}{1,1};
realizedvar_array_quarter{1,8}{1,1}{1,1}=realizedvar_array_quarter{1,9}{1,1}{1,1};
mktcap_array_quarter{1,8}{1,1}{1,1}=mktcap_array_quarter{1,8}{1,1}{1,1};
bs_array_quarter_filled {1,8}{1,1}{1,1}=bs_array_quarter_filled{1,9}{1,1}{1,1};
bs_array_quarter{1,8}{1,1}{1,1}=bs_array_quarter{1,9}{1,1}{1,1};
intrate_quarter_array{1,8}{1,2}=intrate_quarter_array{1,9}{1,2};
intrate_quarter_array{1,8}{1,1}=intrate_quarter_array{1,9}{1,1};
stckmkt_ret_quarter_array{1,8}{1,2}=stckmkt_ret_quarter_array{1,9}{1,2};
stckmkt_ret_quarter_array{1,8}{1,1}=stckmkt_ret_quarter_array{1,9}{1,1};


%%% Indonesia, skip Hungary and El Salvador
returns_array_quarter{1,9}{1,2}{1,1}=returns_array_quarter{1,11}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 20 21 22 23 24 25 26 27 28 29]);
realizedvar_array_quarter{1,9}{1,2}{1,1}=realizedvar_array_quarter{1,11}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 20 21 22 23 24 25 26 27 28 29]);
mktcap_array_quarter{1,9}{1,2}{1,1}=mktcap_array_quarter{1,10}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 20 21 22 23 24 25 26 27 28 29]);
bs_array_quarter_filled{1,9}{1,2}{1,1}=bs_array_quarter_filled{1,12}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 20 21 22 23 24 25 26 27 28 29]);
bs_array_quarter{1,9}{1,2}{1,1}=bs_array_quarter{1,12}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 20 21 22 23 24 25 26 27 28 29]);

returns_array_quarter{1,9}{1,1}{1,1}=returns_array_quarter{1,11}{1,1}{1,1};
realizedvar_array_quarter{1,9}{1,1}{1,1}=realizedvar_array_quarter{1,11}{1,1}{1,1};
mktcap_array_quarter{1,9}{1,1}{1,1}=mktcap_array_quarter{1,10}{1,1}{1,1};
bs_array_quarter_filled{1,9}{1,1}{1,1}=bs_array_quarter_filled{1,12}{1,1}{1,1};
bs_array_quarter{1,9}{1,1}{1,1}=bs_array_quarter{1,12}{1,1}{1,1};
intrate_quarter_array{1,9}{1,2}=intrate_quarter_array{1,12}{1,2};
intrate_quarter_array{1,9}{1,1}=intrate_quarter_array{1,12}{1,1};
stckmkt_ret_quarter_array{1,9}{1,2}=stckmkt_ret_quarter_array{1,12}{1,2};
stckmkt_ret_quarter_array{1,9}{1,1}=stckmkt_ret_quarter_array{1,12}{1,1};

%%% Lebanon very short!, skip Ivory_coast
returns_array_quarter{1,10}{1,2}{1,1}=returns_array_quarter{1,13}{1,2}{1,1}(:,[1]);
realizedvar_array_quarter{1,10}{1,2}{1,1}=realizedvar_array_quarter{1,13}{1,2}{1,1}(:,[1]);
mktcap_array_quarter{1,10}{1,2}{1,1}=mktcap_array_quarter{1,12}{1,2}{1,1}(:,[1]);
bs_array_quarter_filled{1,10}{1,2}{1,1}=bs_array_quarter_filled{1,14}{1,2}{1,1}(:,[1]);
bs_array_quarter{1,10}{1,2}{1,1}=bs_array_quarter{1,14}{1,2}{1,1}(:,[1]);

returns_array_quarter{1,10}{1,1}{1,1}=returns_array_quarter{1,13}{1,1}{1,1};
realizedvar_array_quarter{1,10}{1,1}{1,1}=realizedvar_array_quarter{1,13}{1,1}{1,1};
mktcap_array_quarter{1,10}{1,1}{1,1}=mktcap_array_quarter{1,12}{1,1}{1,1};
bs_array_quarter_filled{1,10}{1,1}{1,1}=bs_array_quarter_filled{1,14}{1,1}{1,1};
bs_array_quarter{1,10}{1,1}{1,1}=bs_array_quarter{1,14}{1,1}{1,1};
intrate_quarter_array{1,10}{1,2}=intrate_quarter_array{1,14}{1,2};
intrate_quarter_array{1,10}{1,1}=intrate_quarter_array{1,14}{1,1};
stckmkt_ret_quarter_array{1,10}{1,2}=stckmkt_ret_quarter_array{1,14}{1,2};
stckmkt_ret_quarter_array{1,10}{1,1}=stckmkt_ret_quarter_array{1,14}{1,1};

%%% Malaysia
returns_array_quarter{1,11}{1,2}{1,1}=returns_array_quarter{1,14}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12]);
realizedvar_array_quarter{1,11}{1,2}{1,1}=realizedvar_array_quarter{1,14}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12]);
mktcap_array_quarter{1,11}{1,2}{1,1}=mktcap_array_quarter{1,13}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12]);
bs_array_quarter_filled{1,11}{1,2}{1,1}=bs_array_quarter_filled{1,15}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12]);
bs_array_quarter{1,11}{1,2}{1,1}=bs_array_quarter{1,15}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12]);

returns_array_quarter{1,11}{1,1}{1,1}=returns_array_quarter{1,14}{1,1}{1,1};
realizedvar_array_quarter{1,11}{1,1}{1,1}=realizedvar_array_quarter{1,14}{1,1}{1,1};
mktcap_array_quarter{1,11}{1,1}{1,1}=mktcap_array_quarter{1,13}{1,1}{1,1};
bs_array_quarter_filled{1,11}{1,1}{1,1}=bs_array_quarter_filled{1,15}{1,1}{1,1};
bs_array_quarter{1,11}{1,1}{1,1}=bs_array_quarter{1,15}{1,1}{1,1};
intrate_quarter_array{1,11}{1,2}=intrate_quarter_array{1,15}{1,2};
intrate_quarter_array{1,11}{1,1}=intrate_quarter_array{1,15}{1,1};
stckmkt_ret_quarter_array{1,11}{1,2}=stckmkt_ret_quarter_array{1,15}{1,2};
stckmkt_ret_quarter_array{1,11}{1,1}=stckmkt_ret_quarter_array{1,15}{1,1};

%%% %Mexico
returns_array_quarter{1,12}{1,2}{1,1}=returns_array_quarter{1,15}{1,2}{1,1}(:,[3 4 5 8]);
realizedvar_array_quarter{1,12}{1,2}{1,1}=realizedvar_array_quarter{1,15}{1,2}{1,1}(:,[3 4 5 8]);
mktcap_array_quarter{1,12}{1,2}{1,1}=mktcap_array_quarter{1,14}{1,2}{1,1}(:,[2 3 4 6]);
bs_array_quarter_filled{1,12}{1,2}{1,1}=bs_array_quarter_filled{1,16}{1,2}{1,1}(:,[2 3 4 7]);
bs_array_quarter{1,12}{1,2}{1,1}=bs_array_quarter{1,16}{1,2}{1,1}(:,[2 3 4 7]);

returns_array_quarter{1,12}{1,1}{1,1}=returns_array_quarter{1,15}{1,1}{1,1};
realizedvar_array_quarter{1,12}{1,1}{1,1}=realizedvar_array_quarter{1,15}{1,1}{1,1};
mktcap_array_quarter{1,12}{1,1}{1,1}=mktcap_array_quarter{1,14}{1,1}{1,1};
bs_array_quarter_filled{1,12}{1,1}{1,1}=bs_array_quarter_filled{1,16}{1,1}{1,1};
bs_array_quarter{1,12}{1,1}{1,1}=bs_array_quarter{1,16}{1,1}{1,1};
intrate_quarter_array{1,12}{1,2}=intrate_quarter_array{1,16}{1,2};
intrate_quarter_array{1,12}{1,1}=intrate_quarter_array{1,16}{1,1};
stckmkt_ret_quarter_array{1,12}{1,2}=stckmkt_ret_quarter_array{1,16}{1,2};
stckmkt_ret_quarter_array{1,12}{1,1}=stckmkt_ret_quarter_array{1,16}{1,1}; 

%%% Pakistan (Nigeria out too few datapoints) 
returns_array_quarter{1,13}{1,2}{1,1}=returns_array_quarter{1,17}{1,2}{1,1}(:,[2 4 8 10 13 15 16 23]);
realizedvar_array_quarter{1,13}{1,2}{1,1}=realizedvar_array_quarter{1,17}{1,2}{1,1}(:,[2 4 8 10 13 15 16 23]);
mktcap_array_quarter{1,13}{1,2}{1,1}=mktcap_array_quarter{1,16}{1,2}{1,1}(:,[2 4 8 10 13 15 16 23]);
bs_array_quarter_filled{1,13}{1,2}{1,1}=bs_array_quarter_filled{1,18}{1,2}{1,1}(:,[2 4 8 10 13 15 16 22]);
bs_array_quarter{1,13}{1,2}{1,1}=bs_array_quarter{1,18}{1,2}{1,1}(:,[2 4 8 10 13 15 16 22]);

returns_array_quarter{1,13}{1,1}{1,1}=returns_array_quarter{1,17}{1,1}{1,1};
realizedvar_array_quarter{1,13}{1,1}{1,1}=realizedvar_array_quarter{1,17}{1,1}{1,1};
mktcap_array_quarter{1,13}{1,1}{1,1}=mktcap_array_quarter{1,16}{1,1}{1,1};
bs_array_quarter_filled{1,13}{1,1}{1,1}=bs_array_quarter_filled{1,18}{1,1}{1,1};
bs_array_quarter{1,13}{1,1}{1,1}=bs_array_quarter{1,18}{1,1}{1,1};
intrate_quarter_array{1,13}{1,2}=intrate_quarter_array{1,18}{1,2};
intrate_quarter_array{1,13}{1,1}=intrate_quarter_array{1,18}{1,1};
stckmkt_ret_quarter_array{1,13}{1,2}=stckmkt_ret_quarter_array{1,18}{1,2};
stckmkt_ret_quarter_array{1,13}{1,1}=stckmkt_ret_quarter_array{1,18}{1,1}; 

%%% Panama (not very good)
returns_array_quarter{1,14}{1,2}{1,1}=returns_array_quarter{1,18}{1,2}{1,1}(:,[2 3]);
realizedvar_array_quarter{1,14}{1,2}{1,1}=realizedvar_array_quarter{1,18}{1,2}{1,1}(:,[2 3]);
mktcap_array_quarter{1,14}{1,2}{1,1}=mktcap_array_quarter{1,17}{1,2}{1,1}(:,[2 3]);
bs_array_quarter_filled{1,14}{1,2}{1,1}=bs_array_quarter_filled{1,19}{1,2}{1,1}(:,[3 4]);
bs_array_quarter{1,14}{1,2}{1,1}=bs_array_quarter{1,19}{1,2}{1,1}(:,[3 4]);

returns_array_quarter{1,14}{1,1}{1,1}=returns_array_quarter{1,18}{1,1}{1,1};
realizedvar_array_quarter{1,14}{1,1}{1,1}=realizedvar_array_quarter{1,18}{1,1}{1,1};
mktcap_array_quarter{1,14}{1,1}{1,1}=mktcap_array_quarter{1,17}{1,1}{1,1};
bs_array_quarter_filled{1,14}{1,1}{1,1}=bs_array_quarter_filled{1,19}{1,1}{1,1};
bs_array_quarter{1,14}{1,1}{1,1}=bs_array_quarter{1,19}{1,1}{1,1};
intrate_quarter_array{1,14}{1,2}=intrate_quarter_array{1,19}{1,2};
intrate_quarter_array{1,14}{1,1}=intrate_quarter_array{1,19}{1,1};
stckmkt_ret_quarter_array{1,14}{1,2}=stckmkt_ret_quarter_array{1,19}{1,2};
stckmkt_ret_quarter_array{1,14}{1,1}=stckmkt_ret_quarter_array{1,19}{1,1}; 

%%% Peru a bit weird, very stable...
returns_array_quarter{1,15}{1,2}{1,1}=returns_array_quarter{1,19}{1,2}{1,1}(:,[2 4 5 8]);
realizedvar_array_quarter{1,15}{1,2}{1,1}=realizedvar_array_quarter{1,19}{1,2}{1,1}(:,[2 4 5 8]);
mktcap_array_quarter{1,15}{1,2}{1,1}=mktcap_array_quarter{1,18}{1,2}{1,1}(:,[1 3 4 7]);
bs_array_quarter_filled{1,15}{1,2}{1,1}=bs_array_quarter_filled{1,20}{1,2}{1,1}(:,[4 9 10 15]);
bs_array_quarter{1,15}{1,2}{1,1}=bs_array_quarter{1,20}{1,2}{1,1}(:,[4 9 10 15]);

returns_array_quarter{1,15}{1,1}{1,1}=returns_array_quarter{1,19}{1,1}{1,1};
realizedvar_array_quarter{1,15}{1,1}{1,1}=realizedvar_array_quarter{1,19}{1,1}{1,1};
mktcap_array_quarter{1,15}{1,1}{1,1}=mktcap_array_quarter{1,18}{1,1}{1,1};
bs_array_quarter_filled{1,15}{1,1}{1,1}=bs_array_quarter_filled{1,20}{1,1}{1,1};
bs_array_quarter{1,15}{1,1}{1,1}=bs_array_quarter{1,20}{1,1}{1,1};
intrate_quarter_array{1,15}{1,2}=intrate_quarter_array{1,20}{1,2};
intrate_quarter_array{1,15}{1,1}=intrate_quarter_array{1,20}{1,1};
stckmkt_ret_quarter_array{1,15}{1,2}=stckmkt_ret_quarter_array{1,20}{1,2};
stckmkt_ret_quarter_array{1,15}{1,1}=stckmkt_ret_quarter_array{1,20}{1,1}; 

%%% Philippines
returns_array_quarter{1,16}{1,2}{1,1}=returns_array_quarter{1,20}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 16 17 18]);
realizedvar_array_quarter{1,16}{1,2}{1,1}=realizedvar_array_quarter{1,20}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 16 17 18]);
mktcap_array_quarter{1,16}{1,2}{1,1}=mktcap_array_quarter{1,19}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 16 17 18]);
bs_array_quarter_filled{1,16}{1,2}{1,1}=bs_array_quarter_filled{1,21}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 15 16 17]);
bs_array_quarter{1,16}{1,2}{1,1}=bs_array_quarter{1,21}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 9 10 11 12 13 15 16 17]);

returns_array_quarter{1,16}{1,1}{1,1}=returns_array_quarter{1,20}{1,1}{1,1};
realizedvar_array_quarter{1,16}{1,1}{1,1}=realizedvar_array_quarter{1,20}{1,1}{1,1};
mktcap_array_quarter{1,16}{1,1}{1,1}=mktcap_array_quarter{1,19}{1,1}{1,1};
bs_array_quarter_filled{1,16}{1,1}{1,1}=bs_array_quarter_filled{1,21}{1,1}{1,1};
bs_array_quarter{1,16}{1,1}{1,1}=bs_array_quarter{1,21}{1,1}{1,1};
intrate_quarter_array{1,16}{1,2}=intrate_quarter_array{1,21}{1,2};
intrate_quarter_array{1,16}{1,1}=intrate_quarter_array{1,21}{1,1};
stckmkt_ret_quarter_array{1,16}{1,2}=stckmkt_ret_quarter_array{1,21}{1,2};
stckmkt_ret_quarter_array{1,16}{1,1}=stckmkt_ret_quarter_array{1,21}{1,1}; 


%%% Poland
returns_array_quarter{1,17}{1,2}{1,1}=returns_array_quarter{1,21}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 15]);
realizedvar_array_quarter{1,17}{1,2}{1,1}=realizedvar_array_quarter{1,21}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 15]);
mktcap_array_quarter{1,17}{1,2}{1,1}=mktcap_array_quarter{1,20}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 15]);
bs_array_quarter_filled{1,17}{1,2}{1,1}=bs_array_quarter_filled{1,22}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 15]);
bs_array_quarter{1,17}{1,2}{1,1}=bs_array_quarter{1,22}{1,2}{1,1}(:,[2 3 4 5 6 7 8 9 10 11 12 13 14 15]);

returns_array_quarter{1,17}{1,1}{1,1}=returns_array_quarter{1,21}{1,1}{1,1};
realizedvar_array_quarter{1,17}{1,1}{1,1}=realizedvar_array_quarter{1,21}{1,1}{1,1};
mktcap_array_quarter{1,17}{1,1}{1,1}=mktcap_array_quarter{1,20}{1,1}{1,1};
bs_array_quarter_filled{1,17}{1,1}{1,1}=bs_array_quarter_filled{1,22}{1,1}{1,1};
bs_array_quarter{1,17}{1,1}{1,1}=bs_array_quarter{1,22}{1,1}{1,1};
intrate_quarter_array{1,17}{1,2}=intrate_quarter_array{1,22}{1,2};
intrate_quarter_array{1,17}{1,1}=intrate_quarter_array{1,22}{1,1};
stckmkt_ret_quarter_array{1,17}{1,2}=stckmkt_ret_quarter_array{1,22}{1,2};
stckmkt_ret_quarter_array{1,17}{1,1}=stckmkt_ret_quarter_array{1,22}{1,1}; 


%%% Russia (not very good)
returns_array_quarter{1,18}{1,2}{1,1}=returns_array_quarter{1,22}{1,2}{1,1}(:,[1 4 5 14 25 26 29]);
realizedvar_array_quarter{1,18}{1,2}{1,1}=realizedvar_array_quarter{1,22}{1,2}{1,1}(:,[1 4 5 14 25 26 29]);
mktcap_array_quarter{1,18}{1,2}{1,1}=mktcap_array_quarter{1,21}{1,2}{1,1}(:,[1 5 6 15 26 27 29]);
bs_array_quarter_filled{1,18}{1,2}{1,1}=bs_array_quarter_filled{1,23}{1,2}{1,1}(:,[2 13 14 27 50 51 54]);
bs_array_quarter{1,18}{1,2}{1,1}=bs_array_quarter{1,23}{1,2}{1,1}(:,[2 13 14 27 50 51 54]);

returns_array_quarter{1,18}{1,1}{1,1}=returns_array_quarter{1,22}{1,1}{1,1};
realizedvar_array_quarter{1,18}{1,1}{1,1}=realizedvar_array_quarter{1,22}{1,1}{1,1};
mktcap_array_quarter{1,18}{1,1}{1,1}=mktcap_array_quarter{1,21}{1,1}{1,1};
bs_array_quarter_filled{1,18}{1,1}{1,1}=bs_array_quarter_filled{1,23}{1,1}{1,1};
bs_array_quarter{1,18}{1,1}{1,1}=bs_array_quarter{1,23}{1,1}{1,1};
intrate_quarter_array{1,18}{1,2}=intrate_quarter_array{1,23}{1,2};
intrate_quarter_array{1,18}{1,1}=intrate_quarter_array{1,23}{1,1};
stckmkt_ret_quarter_array{1,18}{1,2}=stckmkt_ret_quarter_array{1,23}{1,2};
stckmkt_ret_quarter_array{1,18}{1,1}=stckmkt_ret_quarter_array{1,23}{1,1}; 

%%% South Africa
returns_array_quarter{1,19}{1,2}{1,1}=returns_array_quarter{1,23}{1,2}{1,1}(:,[1 3 4 5 7]);
realizedvar_array_quarter{1,19}{1,2}{1,1}=realizedvar_array_quarter{1,23}{1,2}{1,1}(:,[1 3 4 5 7]);
mktcap_array_quarter{1,19}{1,2}{1,1}=mktcap_array_quarter{1,22}{1,2}{1,1}(:,[1 3 4 5 7]);
bs_array_quarter_filled{1,19}{1,2}{1,1}=bs_array_quarter_filled{1,24}{1,2}{1,1}(:,[1 2 3 4 6]);
bs_array_quarter{1,19}{1,2}{1,1}=bs_array_quarter{1,24}{1,2}{1,1}(:,[1 2 3 4 6]);

returns_array_quarter{1,19}{1,1}{1,1}=returns_array_quarter{1,23}{1,1}{1,1};
realizedvar_array_quarter{1,19}{1,1}{1,1}=realizedvar_array_quarter{1,23}{1,1}{1,1};
mktcap_array_quarter{1,19}{1,1}{1,1}=mktcap_array_quarter{1,22}{1,1}{1,1};
bs_array_quarter_filled{1,19}{1,1}{1,1}=bs_array_quarter_filled{1,24}{1,1}{1,1};
bs_array_quarter{1,19}{1,1}{1,1}=bs_array_quarter{1,24}{1,1}{1,1};
intrate_quarter_array{1,19}{1,2}=intrate_quarter_array{1,24}{1,2};
intrate_quarter_array{1,19}{1,1}=intrate_quarter_array{1,24}{1,1};
stckmkt_ret_quarter_array{1,19}{1,2}=stckmkt_ret_quarter_array{1,24}{1,2};
stckmkt_ret_quarter_array{1,19}{1,1}=stckmkt_ret_quarter_array{1,24}{1,1}; 


%%% % Tunisia (not very good too few data)
returns_array_quarter{1,20}{1,2}{1,1}=returns_array_quarter{1,24}{1,2}{1,1}(:,[2 11]);
realizedvar_array_quarter{1,20}{1,2}{1,1}=realizedvar_array_quarter{1,24}{1,2}{1,1}(:,[2 11]);
mktcap_array_quarter{1,20}{1,2}{1,1}=mktcap_array_quarter{1,23}{1,2}{1,1}(:,[2 11]);
bs_array_quarter_filled{1,20}{1,2}{1,1}=bs_array_quarter_filled{1,25}{1,2}{1,1}(:,[2 11]);
bs_array_quarter{1,20}{1,2}{1,1}=bs_array_quarter{1,25}{1,2}{1,1}(:,[2 11]);

returns_array_quarter{1,20}{1,1}{1,1}=returns_array_quarter{1,24}{1,1}{1,1};
realizedvar_array_quarter{1,20}{1,1}{1,1}=realizedvar_array_quarter{1,24}{1,1}{1,1};
mktcap_array_quarter{1,20}{1,1}{1,1}=mktcap_array_quarter{1,23}{1,1}{1,1};
bs_array_quarter_filled{1,20}{1,1}{1,1}=bs_array_quarter_filled{1,25}{1,1}{1,1};
bs_array_quarter{1,20}{1,1}{1,1}=bs_array_quarter{1,25}{1,1}{1,1};
intrate_quarter_array{1,20}{1,2}=intrate_quarter_array{1,25}{1,2};
intrate_quarter_array{1,20}{1,1}=intrate_quarter_array{1,25}{1,1};
stckmkt_ret_quarter_array{1,20}{1,2}=stckmkt_ret_quarter_array{1,25}{1,2};
stckmkt_ret_quarter_array{1,20}{1,1}=stckmkt_ret_quarter_array{1,25}{1,1}; 

%%% % Turkey
returns_array_quarter{1,21}{1,2}{1,1}=returns_array_quarter{1,25}{1,2}{1,1}(:,[1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17]);
realizedvar_array_quarter{1,21}{1,2}{1,1}=realizedvar_array_quarter{1,25}{1,2}{1,1}(:,[1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17]);
mktcap_array_quarter{1,21}{1,2}{1,1}=mktcap_array_quarter{1,24}{1,2}{1,1}(:,[1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17]);
bs_array_quarter_filled{1,21}{1,2}{1,1}=bs_array_quarter_filled{1,26}{1,2}{1,1}(:,[1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17]);
bs_array_quarter{1,21}{1,2}{1,1}=bs_array_quarter{1,26}{1,2}{1,1}(:,[1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17]);

returns_array_quarter{1,21}{1,1}{1,1}=returns_array_quarter{1,25}{1,1}{1,1};
realizedvar_array_quarter{1,21}{1,1}{1,1}=realizedvar_array_quarter{1,25}{1,1}{1,1};
mktcap_array_quarter{1,21}{1,1}{1,1}=mktcap_array_quarter{1,24}{1,1}{1,1};
bs_array_quarter_filled{1,21}{1,1}{1,1}=bs_array_quarter_filled{1,26}{1,1}{1,1};
bs_array_quarter{1,21}{1,1}{1,1}=bs_array_quarter{1,26}{1,1}{1,1};
intrate_quarter_array{1,21}{1,2}=intrate_quarter_array{1,26}{1,2};
intrate_quarter_array{1,21}{1,1}=intrate_quarter_array{1,26}{1,1};
stckmkt_ret_quarter_array{1,21}{1,2}=stckmkt_ret_quarter_array{1,26}{1,2};
stckmkt_ret_quarter_array{1,21}{1,1}=stckmkt_ret_quarter_array{1,26}{1,1}; 

% %%% % Venezuela (Ukraine bye)
returns_array_quarter{1,22}{1,2}{1,1}=returns_array_quarter{1,27}{1,2}{1,1}(:,[2 10]);
realizedvar_array_quarter{1,22}{1,2}{1,1}=realizedvar_array_quarter{1,27}{1,2}{1,1}(:,[2 10]);
mktcap_array_quarter{1,22}{1,2}{1,1}=mktcap_array_quarter{1,26}{1,2}{1,1}(:,[2 10]);
bs_array_quarter_filled{1,22}{1,2}{1,1}=bs_array_quarter_filled{1,28}{1,2}{1,1}(:,[2 10]);
bs_array_quarter{1,22}{1,2}{1,1}=bs_array_quarter{1,28}{1,2}{1,1}(:,[2 10]);

returns_array_quarter{1,22}{1,1}{1,1}=returns_array_quarter{1,27}{1,1}{1,1};
realizedvar_array_quarter{1,22}{1,1}{1,1}=realizedvar_array_quarter{1,27}{1,1}{1,1};
mktcap_array_quarter{1,22}{1,1}{1,1}=mktcap_array_quarter{1,26}{1,1}{1,1};
bs_array_quarter_filled{1,22}{1,1}{1,1}=bs_array_quarter_filled{1,28}{1,1}{1,1};
bs_array_quarter{1,22}{1,1}{1,1}=bs_array_quarter{1,28}{1,1}{1,1};
intrate_quarter_array{1,22}{1,2}=intrate_quarter_array{1,28}{1,2};
intrate_quarter_array{1,22}{1,1}=intrate_quarter_array{1,28}{1,1};
stckmkt_ret_quarter_array{1,22}{1,2}=stckmkt_ret_quarter_array{1,28}{1,2};
stckmkt_ret_quarter_array{1,22}{1,1}=stckmkt_ret_quarter_array{1,28}{1,1}; 


realizedvar_array_quarter{1,23}{1,1}{1,1}=[];
realizedvar_array_quarter{1,23}{1,2}{1,1}=[];
realizedvar_array_quarter{1,24}{1,1}{1,1}=[];
realizedvar_array_quarter{1,24}{1,2}{1,1}=[];
realizedvar_array_quarter{1,25}{1,1}{1,1}=[];
realizedvar_array_quarter{1,25}{1,2}{1,1}=[];
realizedvar_array_quarter{1,26}{1,1}{1,1}=[];
realizedvar_array_quarter{1,26}{1,2}{1,1}=[];
realizedvar_array_quarter{1,27}{1,1}{1,1}=[];
realizedvar_array_quarter{1,27}{1,2}{1,1}=[];


alldata_array_quarter=realizedvar_array_quarter;%%new
initial_countries=1;
n_countries=22; 

aux{i,k}=[];
for i=initial_countries:n_countries
banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);

for k=1:banklength(i)
   K{i,k}=size(bs_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   O{i,k}=size(realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   for l=1:K{i,k}
       for m=1:O{i,k}
            aux{i,k}(m,:)=[realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(m,:),0,0,0,0,0,0,0,0,0];
       end
       for m=1:O{i,k}
            if(bs_array_quarter{1,i}{1,2}{1,1}{2,k}(l,1)== aux{i,k}(m,1))
            aux1{i,k}(m,:)=[aux{i,k}(m,1:2), bs_array_quarter{1,i}{1,2}{1,1}{2,k}(l,:)];
            end
       end
   end
   alldata_array_quarter{1,i}{1,2}{1,1}{2,k}=aux1{i,k};    
end
end


for i=initial_countries:n_countries
banklength(i)=size(alldata_array_quarter{1,i}{1,2}{1,1},2);%%%see consistency when running all the countries        
for k=1:banklength(i)
    X{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
    for x=2:X{i,k}
    if (alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)==0 && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(1,1)~=0 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=19994 ... 
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20004 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20014 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20024 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20034 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20044 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20054 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20064 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20074 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20084 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20094 ...
        && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)~=20104)
    
        alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)+1;
    end
    
    if (alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)==0 && alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(1,1)~=0)
        if(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==19994 ... 
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20004 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20014 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20024 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20034 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20044 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20054 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20064 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20074 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20084 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20094 ...
        |alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)==20104)

        alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1)=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x-1,1)+7;
        end
    end
    
    end
end
end

aux2{i,k}=[];
for i=initial_countries:n_countries
%for i=1:1
banklength(i)=size(alldata_array_quarter{1,i}{1,2}{1,1},2);

for k=1:banklength(i)
   K{i,k}=size(realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   O{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k},1);
   for l=1:K{i,k}
       for m=1:O{i,k}
            if(realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(l,1)== alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(m,1))
            alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(m,2)=realizedvar_array_quarter{1,i}{1,2}{1,1}{2,k}(l,2);
            end
       end
   end
end
end

%%%%%%%merge returns
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


for i=initial_countries:n_countries
banklength(i)=size(alldata_array_quarter{1,i}{1,2}{1,1},2);%%%see consistency when running all the countries        
for k=1:banklength(i)
    raux1{i,k}=returns_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1:2);%%%%check!!!!the problem is when generated a 1:2, see where is this generated
    X{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
    Y{i,k}=size(returns_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
    for x=1:X{i,k}
        for y=1:Y{i,k}
             if(raux1{i,k}(y,1)==alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1))%%%%
                 alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,12)=raux1{i,k}(y,2);
             end
        end
    end
end
end


%%%%%%%merge mktcap
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

for i=initial_countries:n_countries
banklength(i)=size(alldata_array_quarter{1,i}{1,2}{1,1},2);%%%see consistency when running all the countries        
for k=1:banklength(i)
    raux{i,k}=mktcap_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1:2);
    X{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
    Y{i,k}=size(mktcap_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1),1);
    for x=1:X{i,k}
        for y=1:Y{i,k}
             if(raux{i,k}(y,1)==alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,1))%%%%
                 alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(x,13)=raux{i,k}(y,2);
             end
        end
    end
end
end



%%%%%%%%%%%merge data interest rates %%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

for i=initial_countries:n_countries
banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);%%%see consistency when running all the countries        
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

for i=initial_countries:n_countries
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


%%%%%%%GET RID OF THE MISSING VALUES%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%filling the remaining data


save data_pds_processed_allcountries.mat

%save data_pds_processed_filled.mat
%save data_pds_processed.mat

%%%%%run data mkt cap to generate quarters, then use it to add to the other
%%%%%data finally generate the complete data and estimate the individual
%%%%%pds