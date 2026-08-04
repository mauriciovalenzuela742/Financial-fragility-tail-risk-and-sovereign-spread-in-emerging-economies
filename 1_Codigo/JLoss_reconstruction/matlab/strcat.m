function t = strcat(varargin)
%STRCATP Concatenate strings.
%   T = STRCAT(S1,S2,S3,...) horizontally concatenates corresponding
%   rows of the character arrays S1, S2, S3 etc.  The trailing
%   padding ARE NOT ignored.  All the inputs must have the same number of
%   rows (or any can be a single string).  When the inputs are all 
%   character arrays, the output is also a character array.
%   
%   T = STRCAT(S1,S2,...), when any of the inputs is a cell array of 
%   strings, returns a cell array of strings formed by concatenating
%   corresponding elements of S1,S2, etc.  The inputs must all have
%   the same size (or any can be a scalar). Any of the inputs can 
%   also be character arrays.
%
%   Example
%       strcat({'Red','Yellow'},{'Green','Blue'})
%   returns
%       'RedGreen'    'YellowBlue'
%
%   See also STRVCAT, CAT, CELLSTR.
%
%   AMENDED by PNath@London.edu 24-10-2000 to NOT IGNORE TRAILING BLANKS
%   Copyright (c) 1984-98 by The MathWorks, Inc.
%   $Revision: 1.11 $  $Date: 1998/06/23 16:27:06 $

%   The cell array implementation is in @cell/strcat.m

if nargin<1, error('Not enough input arguments.'); end

for i=nargin:-1:1,
  rows(i) = size(varargin{i},1);
  twod(i) = ndims(varargin{i})==2;
end
if ~all(twod), error('All the inputs must be two dimensional.'); end

% Remove empty inputs
k = (rows == 0);
varargin(k) = [];
rows(k) = [];

% Scalar expansion
for i=1:length(varargin),
  if rows(i)==1 & rows(i)<max(rows),
    varargin{i} = varargin{i}(ones(1,max(rows)),:);
    rows(i) = max(rows);
  end
end

if any(rows~=rows(1)),  
  error('All the inputs must have the same number of rows or a single row.');
end

n = rows(1);
t = '';
for i=1:n,
  %s = deblank(varargin{1}(i,:));
  s = (varargin{1}(i,:));  % PNath@London.edu did this to NOT exclude trailing blanks
  for j=2:length(varargin),
     %s = [s deblank(varargin{j}(i,:))];
     s = [s (varargin{j}(i,:))];  % PNath@London.edu did this to NOT exclude trailing blanks
  end
  t = strvcat(t,s);
end