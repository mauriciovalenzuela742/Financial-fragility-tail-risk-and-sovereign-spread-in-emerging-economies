function Groups = GroupSummary(Data,DIM,PivotNumber,LookupNumber,Statistic)
%
% Groups = GroupSummary(Data,DIM,PivotNumber,LookupNumber,Statistic)
%
% Looks down the PivotNumber column (DIM=2 [default]) or row (DIM=1)
% to create groups based on distinct entries in that column/row
% and then summarises the data in the LookupNumber (default=1)
% column/row by returning for each group the Statistic (default='mean')
% requested.
%
% e.g.      
% Data=
%      [1     2
%       2     4
%       3     6
%       4     8
%       5    10
%       6    12
%       7    14
%       8    16
%       9    18
%      10    20
%       1     2
%       2     4
%       3     6
%       4     8
%       5    10
%       6    12
%       7    14
%       8    16
%       9    18
%      10    20]
%
% GroupSummary(Data,2,1,2,'sum') returns
%
%     1     4
%     2     8
%     3    12
%     4    16
%     5    20
%     6    24
%     7    28
%     8    32
%     9    36
%    10    40 
%
% Copyright(c): PNath@London.edu 24-Jan-2002
%



if nargin==1
   DIM = 2;
   PivotNumber = 1;
   LookupNumber = 1;
   Statistic = 'mean';
end
if nargin==2
   PivotNumber = 1;
   LookupNumber = 1;
   Statistic = 'mean';
end
if nargin==3
   LookupNumber = 1;
   Statistic = 'mean';
end
if nargin==4
   Statistic = 'mean';
end

if DIM == 2
   Groups = tally(Data(:,PivotNumber)); 
	Groups(:,2) = 0;
   for GroupNumber = 1:size(Groups,1);
      eval(strcatp('Groups(GroupNumber,2) = ',Statistic,'(Data(find(Data(:,PivotNumber)==Groups(GroupNumber,1)),LookupNumber));'));
   end
elseif DIM == 1
   Groups = GroupSummary(Data',2,PivotNumber,LookupNumber,Statistic)';
end


