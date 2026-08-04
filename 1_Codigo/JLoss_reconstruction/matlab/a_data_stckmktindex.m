clc
clear memory
clear all
close all
% format from origin: [date price]

[data_bank_equity stringsa]=xlsread('data_stckmktindex.xls');
N=size((stringsa),1)-1;
quarter_date=data_bank_equity(:,1);
databank_equity=data_bank_equity(:,2:end);
namesall=stringsa;
n_countriestk=size(namesall,2)-1;
for i=1:n_countriestk
countries{1,i}=namesall{1,i+1};
end
stckmkt_quarter_array=[];
for i=1:n_countriestk
    stckmkt_quarter_array{1,i}{1,1}=countries{1,i};
    stckmkt_quarter_array{1,i}{1,2}=[quarter_date databank_equity(:,i)];
end

for i=1:n_countriestk
    stckmkt_ret_quarter_array{1,i}{1,1}=countries{1,i};
    stckmkt_ret_quarter_array{1,i}{1,2}=[quarter_date(2:end,1) diff(log(databank_equity(:,i)))];
    end_stck=size(stckmkt_ret_quarter_array{1,i}{1,2},1);
    stckmkt_ret_quarter_array{1,i}{1,2}(end_stck-1:end_stck,:)=[];
end

save data_stckmktindex.mat