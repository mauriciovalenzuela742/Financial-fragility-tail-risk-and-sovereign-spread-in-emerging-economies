function TestGaussHermite(k,b)
% test Gauss-Hermite quadrature function
% S Bocquet 5 August 2008 Tested with MATLAB Version 7.6.0.324 (R2008a)
switch k % select test function
  case 1
    f = @(x) x.^2; % test function
    g0 = sqrt(pi)/2; % integral of f*exp(-x^2) from -Inf to Inf
  case 2
    % Note: Gauss-Hermite quadrature doesn't work if f varies too rapidly.
    % This can be demonstrated with f = cos(bx) and b > npts/2.
    if nargin==1; b=2; end;
    f = @(x) cos(b*x); % test function
    g0 = sqrt(pi)*exp(-b*b/4); % integral of f*exp(-x^2) from -Inf to Inf
  otherwise
    f = @(x) ones(size(x)); % test function
    g0 = sqrt(pi); % integral of f*exp(-x^2) from -Inf to Inf
end
npts(1:8) = int8([ 2, 4, 6, 8, 10, 12, 16, 20 ]);
fprintf(' npts        integral                error\r')
fprintf('   -   %20.16f            -\r', g0)
for i=1:8
  g = GaussHermite(f, npts(i));
  err = g0 - g;
  fprintf(' %3i   %20.16f   %20.16f\r', npts(i), g, err)
end
end