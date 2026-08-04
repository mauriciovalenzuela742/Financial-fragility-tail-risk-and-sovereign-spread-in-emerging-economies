clear all
clc
load data_pds_processed_allcountries

n_countries=size(bs_array_quarter_filled,2);
initial_countries=1;
%countryname,bankname,date,lt_borrow,st_borrow,tot_asset,cash_and_st_investments,net_income,net_rev,prof_margin
%bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,7) net_income	
%bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,8) net_rev	
%bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,9) prof_margin
%ver promedio, sd

%%%%NETINCOME 

for i=initial_countries:n_countries
banklength(i)=size(bs_array_quarter_filled{1,i}{1,2}{1,1},2);      
 for k=1:banklength(i)
    raux{i}=bs_array_quarter_filled{1,i}{1,1}{1,1};
    raux0{i,k}=bs_array_quarter_filled{1,i}{1,2}{1,1}{1,k};
    raux1{i,k}=bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,7);
    X{i,k}=size(quarter_date,1);
    Y{i,k}=size(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,1),1);
    net_income{1,i}{1,2}{1,1}{2,k}=zeros(size(quarter_date,1),1);
    for x=1:X{i,k}
        for y=1:Y{i,k}
             if(quarter_date(x,1)==bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(y,1))
                 net_income{1,i}{1,1}{1,1}=raux{i};
                 net_income{1,i}{1,2}{1,1}{1,k}=raux0{i,k};
                 net_income{1,i}{1,2}{1,1}{2,k}(x,1)=raux1{i,k}(y,1);
             end
        end
    end
 end
end

for i=initial_countries:n_countries
    banklength(i)=size(bs_array_quarter_filled{1,i}{1,2}{1,1},2);     
    net_incomesum{1,i}{1,1}=net_income{1,i}{1,1}{1,1};
    net_incomesum{1,i}{1,2}{1,1}=net_income{1,i}{1,2}{1,1}{2,1};
    net_incomesum_ready{1,i}{1,1}{1,1}=net_income{1,i}{1,1}{1,1};
for k=2:banklength(i)
    net_incomesum{1,i}{1,2}{1,k}=net_income{1,i}{1,2}{1,1}{2,k}+net_incomesum{1,i}{1,2}{1,k-1};
    net_incomesum_ready{1,i}=net_incomesum{1,i}{1,2}{1,k};
    matrix_net_incomesum_ready(:,i)=net_incomesum_ready{1,i};
    matrix_net_incomeavg_ready(:,i)=net_incomesum_ready{1,i}/banklength(i);
end
end


%%%%%%%%%%%%%%%%%%
%%%%NET revenues


for i=initial_countries:n_countries
banklength(i)=size(bs_array_quarter_filled{1,i}{1,2}{1,1},2);      
 for k=1:banklength(i)
    raux{i}=bs_array_quarter_filled{1,i}{1,1}{1,1};
    raux0{i,k}=bs_array_quarter_filled{1,i}{1,2}{1,1}{1,k};
    raux1{i,k}=bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,8);
    X{i,k}=size(quarter_date,1);
    Y{i,k}=size(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,1),1);
    net_revenues{1,i}{1,2}{1,1}{2,k}=zeros(size(quarter_date,1),1);
    for x=1:X{i,k}
        for y=1:Y{i,k}
             if(quarter_date(x,1)==bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(y,1))
                 net_revenues{1,i}{1,1}{1,1}=raux{i};
                 net_revenues{1,i}{1,2}{1,1}{1,k}=raux0{i,k};
                 net_revenues{1,i}{1,2}{1,1}{2,k}(x,1)=raux1{i,k}(y,1);
             end
        end
    end
 end
end

for i=initial_countries:n_countries
    banklength(i)=size(bs_array_quarter_filled{1,i}{1,2}{1,1},2);     
    net_revenuessum{1,i}{1,1}=net_revenues{1,i}{1,1}{1,1};
    net_revenuessum{1,i}{1,2}{1,1}=net_revenues{1,i}{1,2}{1,1}{2,1};
    net_revenuessum_ready{1,i}{1,1}{1,1}=net_revenues{1,i}{1,1}{1,1};
for k=2:banklength(i)
    net_revenuessum{1,i}{1,2}{1,k}=net_revenues{1,i}{1,2}{1,1}{2,k}+net_revenuessum{1,i}{1,2}{1,k-1};
    net_revenuessum_ready{1,i}=net_revenuessum{1,i}{1,2}{1,k};
    matrix_net_revenuessum_ready(:,i)=net_revenuessum_ready{1,i};
    matrix_net_revenuesavg_ready(:,i)=net_revenuessum_ready{1,i}/banklength(i);
end
end


%%% PROFIT MARGIN
for i=initial_countries:n_countries
banklength(i)=size(bs_array_quarter_filled{1,i}{1,2}{1,1},2);      
 for k=1:banklength(i)
    raux{i}=bs_array_quarter_filled{1,i}{1,1}{1,1};
    raux0{i,k}=bs_array_quarter_filled{1,i}{1,2}{1,1}{1,k};
    raux1{i,k}=bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,9);
    X{i,k}=size(quarter_date,1);
    Y{i,k}=size(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,1),1);
    profit_margin{1,i}{1,2}{1,1}{2,k}=zeros(size(quarter_date,1),1);
    for x=1:X{i,k}
        for y=1:Y{i,k}
             if(quarter_date(x,1)==bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(y,1))
                 profit_margin{1,i}{1,1}{1,1}=raux{i};
                 profit_margin{1,i}{1,2}{1,1}{1,k}=raux0{i,k};
                 profit_margin{1,i}{1,2}{1,1}{2,k}(x,1)=raux1{i,k}(y,1);
             end
        end
    end
 end
end

for i=initial_countries:n_countries
    banklength(i)=size(bs_array_quarter_filled{1,i}{1,2}{1,1},2);     
    profit_marginsum{1,i}{1,1}=profit_margin{1,i}{1,1}{1,1};
    profit_marginsum{1,i}{1,2}{1,1}=profit_margin{1,i}{1,2}{1,1}{2,1};
    profit_marginsum_ready{1,i}{1,1}{1,1}=profit_margin{1,i}{1,1}{1,1};
for k=2:banklength(i)
    profit_marginsum{1,i}{1,2}{1,k}=profit_margin{1,i}{1,2}{1,1}{2,k}+profit_marginsum{1,i}{1,2}{1,k-1};
    profit_marginsum_ready{1,i}=profit_marginsum{1,i}{1,2}{1,k};
    matrix_profit_marginsum_ready(:,i)=profit_marginsum_ready{1,i};
    matrix_profit_marginavg_ready(:,i)=profit_marginsum_ready{1,i}/banklength(i);
end
end


xlswrite('data_banks_netincome.xls', matrix_net_incomesum_ready);
xlswrite('data_banks_avgincome.xls', matrix_net_incomeavg_ready);
xlswrite('data_banks_netrevenues.xls', matrix_net_revenuessum_ready);
xlswrite('data_banks_avgrevenues.xls', matrix_net_revenuesavg_ready);
xlswrite('data_banks_profitmargin.xls', matrix_profit_marginsum_ready);
xlswrite('data_banks_avgprofitmargin.xls', matrix_profit_marginavg_ready);
 