function [quarterlydate, quarterlydata]=quarterly(dates, data)
% Compute Quarterly Price Series
% The strategy is identical to that of finding the last day of the month,
% except that I only consider months where the month value is 3, 6, 9 or
% 12.
isLastDayOfQuarter = false(size(dates));
isLastDayOfQuarter(1)=true;
T = length(dates);
for i=2:T
    % There are, again, faster ways to do this.  This is relatively simply
    % and illustrated the use of loops
    [y, mi] = datevec(dates(i-1));
    [y, mplusi] = datevec(dates(i));
    if mi~=mplusi && ismember(mi,[3 6 9 12])
        isLastDayOfQuarter(i) = true;
    end
end
% Use the logical 1s to pick the prices and dates on the last day of the
% quarter
quarterlydata = data(isLastDayOfQuarter,:);
quarterlydate = dates(isLastDayOfQuarter);

