clear all
close all
clc

import_dataequity('dataequity.xlsx')
dataequity=dataequity(:,[1 4]);
N=length(dataequity)+1;
for i=2:N
text_country{i-1,1}=textdata{i,2};
end


for i=2:N
text_bankname{i-1,1}=textdata{i,3};
end

rownames={'country', 'bank', 'date', 'price'};
all_dataarray={text_country text_bankname dataequity};
countries=all_dataarray{1};
banks=all_dataarray{2};
datatemp=all_dataarray{3};
date=datatemp(:,1);
prices=datatemp(:,2);

unique_countries=unique(text_country);
unique_banks=unique(text_bankname);

lengthcountries=length(unique_countries);
lengthbanks=length(unique_banks);


for i=1:lengthcountries
for j=1:(N-1)
if(strcmp(text_country(j),unique_countries(i))==1) 
    banksincountry(j,i)=text_bankname(j);
else 
    banksincountry(j,i)={'nulo'};
end
end
    abankarray{i}={unique_countries(i) unique(banksincountry(:,i))};
end


for i=1:lengthcountries
lenght_banks(i)=length(abankarray{1,i}{1,2});
    for j=1:lenght_banks(i)
        for k=1:(N-1)
            if (strcmp(abankarray{1,i}{1,1},text_country(k))==1 && strcmp(abankarray{1,i}{1,2}{j,1},text_bankname(k))==1)
            abankarrayn{i}{k}={abankarray{i} dataequity(k,:)}; 
            end
        end
    end
end



% for i=1:lengthcountries
%     lenght_banks(i)=length(abankarray{1,i}{1,2});
% for j=1:lenght_banks(i)
%     for k=1:(N-1)
%         if (strcmp(abankarray{1,i}{1,1},text_country(k))==1 && strcmp(abankarray{1,i}{1,2}{j,1},text_bankname(k))==1)
%          alldata_array_EQ{i}= dataequity(k,:); 
%         end
%     end
% end
% end

%%%%%%%%%%%%%%%%%%%%%%%%
%%%%calculate returns

for i=1:(N-1)
    value1(i)=strcmp(text_country(i),'ARG');
    value2(i)=strcmp(text_bankname(i),'santanderarg');
    if(value1(i)+ value2(i)==2)
        priceargsantander(i)=dataequity(i,2);
    else 
        priceargsantander(i)=NaN;
    end  
end

Nmatpriceargsantander=~isnan(priceargsantander);
returnaa=diff(log((Nmatpriceargsantander)));