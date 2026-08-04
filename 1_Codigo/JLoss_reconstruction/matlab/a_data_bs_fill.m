%%%%%fill the missing data for BS, then fill the rest.
%%%%%%%PROCEDURE
%%%RUN A_DATA_BS_NEW, THEN RUN THIS ONE, RUN SECOND PART OF THE
%%%A_DATA_BS_NEW, TAKE THIS FILE AND FILL IT IN THE SECOND PART OF THIS
%%%FILE.

clear all
clc
load data_bs_processed.mat

n_countries=2;
bs_array_quarter{1,1}{1,2}{1,1}=bs_array_quarter{1,1}{1,2}{1,1}(:,[1 2 3 4 6 7 8]);
bs_array_quarter{1,2}{1,2}{1,1}=bs_array_quarter{1,2}{1,2}{1,1}(:,[1 2 3 4 5 6 7 8 10 12 13 14 17 19 21 22 24]);
bs_array_quarter_filled=bs_array_quarter;

for i=1:n_countries
    banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);
    for k=1:banklength(i)
        L{i,k}=size(bs_array_quarter{1,i}{1,2}{1,1}{2,k},1);
        M{i,k}=size(bs_array_quarter{1,i}{1,2}{1,1}{2,k},2);
        for m=3:M{i,k}
            for l=1:L{i,k}
                if(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,m)==0||isempty(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,m))==1)
                bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,m)=NaN;
                end
            end
        end
    end
end
 
for i=1:n_countries
    banklength(i)=size(bs_array_quarter{1,i}{1,2}{1,1},2);
    for k=1:banklength(i)
        L{i,k}=size(bs_array_quarter{1,i}{1,2}{1,1}{2,k},1);
        M{i,k}=size(bs_array_quarter{1,i}{1,2}{1,1}{2,k},2);
       % for m=3:M{i,k}
       for m=3:6
            for l=1:L{i,k}
                if(isnan(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,m))==1)
                missdata{i,k}(l,m)=(spline(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,2),...
                (bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,m)).^.5,...
                 bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,2)));
                 bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,m)=missdata{i,k}(l,m).^2;
                end
            end
       end
       for m=7:M{i,k}
            for l=1:L{i,k}
                if(isnan(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,m))==1)
                missdata{i,k}(l,m)=(spline(bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,2),...
                (bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(:,m)),...
                 bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,2)));
                 bs_array_quarter_filled{1,i}{1,2}{1,1}{2,k}(l,m)=missdata{i,k}(l,m);
                end
            end
       end
    end
end

bs_array_quarter=bs_array_quarter_filled;
save bsdata_filled.mat

