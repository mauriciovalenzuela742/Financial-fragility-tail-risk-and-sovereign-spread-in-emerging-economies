%% Data Import Setup
% I cleaned the data so that it contains only numbers (converted dates into
% numbers), and only included the dates (first column) and adjusted close.
% I use cell arrays to hold both the index names and filenames.

% Use a cell array (note the use of brace { } rather than parentheses ( ))
% to hold the csv filenames
csvFileNames{1} = 'bank1';
csvFileNames{2} = 'bank2';
csvFileNames{3} = 'bank3';
csvFileNames{4} = 'bank4';
csvFileNames{5} = 'N225_clean.csv';
csvFileNames{6} = 'SP500_clean.csv';

% Use a cell array
marketNames{1} = 'All Ordinaries';
marketNames{2} = 'IBOVESPA ';
marketNames{3} = 'DAX 40';
marketNames{4} = 'Tel Aviv 100';
marketNames{5} = 'Nikkei 225';
marketNames{6} = 'S&P 500';

% Initialize an array to hold the data
allData = cell(6,1);

for j=1:6
    % This is the only tricky part of the assignment.  The rest is copy and
    % paste form the top.  The key to automating is to change as few lines
    % as possible.  I do this by redefinig "data" to to hold the data from
    % each index as the loop goes from 1 to 6
    allData{j} = csvread(csvFileNames{j},1);
    % From this point the rest of the program is identical.  I have remoded
    % comments except for the lines which use cell arrays
    data = sortrows(allData{j});
    dates = data(:,1);
    dates = x2mdate(dates);
    prices = data(:,2);