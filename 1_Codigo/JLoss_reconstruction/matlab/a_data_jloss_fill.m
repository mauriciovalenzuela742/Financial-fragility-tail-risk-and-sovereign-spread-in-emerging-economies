
clear all
clc
load jloss.mat

[datematlab]=xlsread('datesall_complete.xls');

n_countries=2;

for i=1:n_countries
  CR{1,i}(:,3)=datematlab(:,2);
end

for i=1:n_countries
  CR_fill{i,1}=indiv_countries{i,1};
  CR_fill{i,2}=CR{1,i};
  CR=CR_fill;
  CR{i,2}=real(CR{i,2}(:,:));
end

for i=1:n_countries
  CR{i,2}=real(CR{i,2}(:,:));
end

% monday start from here


for i=1:n_countries
    for l=1:2
    datalength(i)=size(CR_fill{i,2}(:,3),1);
    xxxx(:,1)=1:datalength(i);
    for k=2:datalength(i)
               if(isnan(CR_fill{i,2}(k,l))==1 && isnan(CR_fill{i,2}(k-1,l))==0)
               missdata{1,i}(k,1)=spline(xxxx,...
                (real(CR_fill{i,2}(:,l))).^.5,...
               xxxx(k,1));
               CR_fill{i,2}(k,l)=missdata{1,i}(k,1).^2;
               end
    end
    end
    CR_fill{i,2}(:,:)=real(CR_fill{i,2}(:,:));
end



save jloss_filled.mat

% [uniqueA i j] = unique(A,'first');
% indexToDupes = find(not(ismember(1:numel(A),i)))



        