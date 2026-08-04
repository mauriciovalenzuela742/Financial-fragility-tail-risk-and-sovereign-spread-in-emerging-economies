clear all
close all
clc
% Read the data
% import_dataequity('price_long.csv');
% N=length(textdata)+1;
% for i=1:N
% splitted_text(i)=split(',,"',textdata{i});
% end

fid = fopen('price_long.csv');
textdata = textscan(fid, '%s');
fclose(fid);
N=length(textdata{1});
%for i=1:500000
for i=1:5
splitted_text{i,1}=split(',"',textdata{1}{i});
end
for i=500001:1000000
splitted_text{i}=split(',,"',textdata{1}{i});
end
for i=1000001:1500000
splitted_text{i}=split(',,"',textdata{1}{i});
end
save array_prices.dat

for i=1500001:N
splitted_text1{i-1500000}=split(',,"',textdata{1}{i});
end
save array_prices1.dat