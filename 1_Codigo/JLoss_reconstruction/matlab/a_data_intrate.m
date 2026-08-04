clc
clear memory
clear all
close all
% format from origin: [date price]

[data_bank_equity stringsa]=xlsread('data_intrate.xls');
N=size((stringsa),1)-1;
quarter_date=data_bank_equity(:,1);
databank_equity=data_bank_equity(:,2:end);
namesall=stringsa;
n_countriesint=size(namesall,2)-1;
for i=1:n_countriesint
countries{1,i}=namesall{1,i+1};
end
stckmkt_quarter_array=[];
for i=1:n_countriesint
    intrate_quarter_array{1,i}{1,1}=countries{1,i};
    intrate_quarter_array{1,i}{1,2}=[quarter_date databank_equity(:,i)];
end
save data_intrate.mat