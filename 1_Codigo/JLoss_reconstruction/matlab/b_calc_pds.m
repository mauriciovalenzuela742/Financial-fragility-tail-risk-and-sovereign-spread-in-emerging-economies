%%%individualpds

clear all
clc
%load data_pds_processed_filled_complete.mat
load data_pds_processed_allcountries.mat
% load data_stckmktindex.mat
% load data_intrate.mat
%%%format origin
%%%(1idgroup	2volstk	3idgroup	4datematlab	5 LTLIAB	6 STLIAB	7TOASSET	
%8 SHTASSET	9 income	10 revenue	11 profitmargin	12 date	13 mktcap) 

%r=0.05;%%%change this
T=1;
EDF=alldata_array_quarter;%abankarrayn
%EDFstucked=alldata_array_quarter{1,1}{1,2}{1,1}; %%%%check this
initial_country=1;
n_countriespds=22;

for i=initial_country:n_countriespds
banklength(i)=size(EDF{1,i}{1,2}{1,1},2);%%%see concistency when running all the countries    

for k=1:banklength(i)
    
r{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,14);
index{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,15);
SD{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,6);%short term debt 
LD{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,5);%long term debt  
Vol_stk{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,2).^.5;%vol stk mkt
Mkt_Cap{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,13);%Mkt cap
B=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k},1);
EDF{1,i}{1,2}{1,1}{2,k}(:,2:end)=[];

for b=1:B
if (SD{i,k}(b,1)==0 || Mkt_Cap{i,k}(b,1)==0 || isnan(SD{i,k}(b,1))==1 || isnan(LD{i,k}(b,1))==1 || isnan(Vol_stk{i,k}(b,1))== 1 || isnan(Mkt_Cap{i,k}(b,1))== 1)
[EDF{1,i}{1,2}{1,1}{2,k}(b,2)]=0;%could be NaN Check this too
else
[EDF{1,i}{1,2}{1,1}{2,k}(b,2)]= indivpds(SD{i,k}(b,1), LD{i,k}(b,1), r{i,k}(b,1),T, Vol_stk{i,k}(b,1), Mkt_Cap{i,k}(b,1)) ;
end
end 
end
end

save pd_indiv.mat
%%%%%%%%%%%%%%%up to here
%%stucking

%EDF{1,i}{1,2}{1,1}{2,k}(b,2);

datesall=[19991;19992;19993;19994;...
    20001;20002;20003;20004;...
    20011;20012;20013;20014;...
    20021;20022;20023;20024;...
    20031;20032;20033;20034;...
    20041;20042;20043;20044;...
    20051;20052;20053;20054;...
    20061;20062;20063;20064;...
    20071;20072;20073;20074;...
    20081;20082;20083;20084;...
    20091;20092;20093;20094;...
    20101;20102;20103;20104;...
    20111;20112;20113;20114];

auxiliarstuckEDF=[];
EDFstucked=stckmkt_ret_quarter_array;

for i=initial_country:n_countriespds
for k=1:banklength(i)
    W=size(datesall,1);
    R{i,k}=size(EDF{1,i}{1,2}{1,1}{2,k}(:,2),1);
    auxiliarstuckEDF{i}(:,1)=datesall;
    for w=1:W
        for r=1:R{i,k}
            if(auxiliarstuckEDF{i}(w,1)==EDF{1,i}{1,2}{1,1}{2,k}(r,1)&& isnan(EDF{1,i}{1,2}{1,1}{2,k}(r,2))==0)
            auxiliarstuckEDF{i}(w,k+1)=EDF{1,i}{1,2}{1,1}{2,k}(r,2);
            end
        end
    end
end
EDFstucked{1,i}{1,2}=[auxiliarstuckEDF{i}(:,:)];
end

%%%%%%%%%%%%%%%%now the other variables
%%%%%%%%%exposure
auxiliarstuckEXP=[];
EXPstucked=stckmkt_ret_quarter_array;
for i=initial_country:n_countriespds
for k=1:banklength(i)
    W=size(datesall,1);
    R{i,k}=size(alldata_array_quarter{1,i}{1,2}{1,1}{2,k},1);
    auxiliarstuckEXP{i}(:,1)=datesall;
    for w=1:W
        for r=1:R{i,k}
            if(auxiliarstuckEXP{i}(w,1)==alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(r,1) && isnan(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(r,5))==0 && isnan(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(r,6))==0)
            auxiliarstuckEXP{i}(w,k+1)=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(r,5)+alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(r,6);
            end
        end
    end
end
EXPstucked{1,i}{1,2}=[auxiliarstuckEXP{i}(:,:)];
end


%%%aggregated pd
%%%%%INITIAL PARAMETERS
num_order	= 7;
num_factors	= 1;
loss_inf	= 0.01;
loss_sup	= 0.048;
num_steps	= 500;
percentil   = 0.99; %0.9997
L=[];
T=[];
for i=initial_country:n_countriespds
L(i)=size(EDFstucked{1,i}{1,2},2)-1;
T(i)=size(EDFstucked{1,i}{1,2},1);
probs{1,i}=[];
exposition{1,i}=[];
rho1{1,i}= [];
rho2{1,i}= [];
rho3{1,i}= [];
rho4{1,i}= [];
ctrp_mult{1,i}=[];
severity{1,i}=[];


%rho1{1,i}(1:L(i),1)= 0.5;
rho2{1,i}(1:L(i),1)= 0;
rho3{1,i}(1:L(i),1)= 0;
rho4{1,i}(1:L(i),1)= 0;
severity{1,i}(1:L(i),1) = 0.45;%%%basel II number for corporates and banks, assuming they are unsecured (Basel II capital agreement)
ctrp_mult{1,i}(1:L(i),1)=1;
rhos{1,i} = [];
CR{1,i}=[];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%CORRELATION%%%%%%%%%%%%%%
indexcorr{i,k}=[];
%for i=1:n_countriespds
for k=1:banklength(i)
    return_tocorr{i,k}=[];
    stckmkt_tocorr{i,k}=[];
    indexcorr{i,k}=find(alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(:,1));
    return_tocorr{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(indexcorr{i,k},12);
    stckmkt_tocorr{i,k}=alldata_array_quarter{1,i}{1,2}{1,1}{2,k}(indexcorr{i,k},15);
    cocorrelation_stck{i,k}=corrcoef(return_tocorr{i,k},stckmkt_tocorr{i,k});
    correlation_stck{i,k}=cocorrelation_stck{i,k}(1,2);
    rho1{1,i}(k,1)=correlation_stck{i,k};
    if(isnan(rho1{1,i}(k,1)))
        rho1{1,i}(k,1)=0.4;
    end
end

rhos{1,i} = [rho1{1,i} rho2{1,i} rho3{1,i} rho4{1,i}];


for t=1:T(i)
    
probs{1,i}(:,t)= EDFstucked{1,i}{1,2}(t,2:end)';
exposition{1,i}(:,t)= EXPstucked{1,i}{1,2}(t,2:end)';


%%%%%%%OTHER ALTERNATIVE%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%REMEMBER TO PULL THE NON ZEROS%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% COEFF{1,i}=[];
% SCORE{1,i}=[];
% latent{1,i}=[];
% correlationint{1,i}=[];
% 
% [COEFF{1,i},SCORE{1,i},latent{1,i}] = princomp(probs{1,i}(:,:)); 
% explanatory{1,i}=cumsum(latent{1,i})./sum(latent{1,i});
% correlationint{t,i}=corrcoef(probs{1,i}(:,t),SCORE{1,i}(:,1));
% cocorrelation{1,i}(t,1)=correlationint{t,i}(1,2);
% if (isnan(cocorrelation{1,i}(t,1))==0)
%     correlation{1,i}(t,1)=cocorrelation{1,i}(t,1);
% else 
%     correlation{1,i}(t,1)=0.5;
% end
% rho1{1,i}(1:L(i),t)= correlation{1,i}(t,1);


%%data_used_to_CR{1,i}=[ctrp_mult{1,i}, probs{1,i}, rhos{t,i}, severity{1,i}, exposition{1,i}];
%%%%%%%%%%%%%%%%%%%%%%%%%%%

[CR{1,i}(t,1) CR{1,i}(t,2) CR{1,i}(t,3)]=countrypd(ctrp_mult{1,i}, probs{1,i}(:,t), rhos{1,i}, loss_inf, loss_sup, num_order, num_factors, severity{1,i}, exposition{1,i}(:,t),percentil,num_steps);

end
end


%%%%%calculate a third measure average of pds, just to check results????
save jloss.mat