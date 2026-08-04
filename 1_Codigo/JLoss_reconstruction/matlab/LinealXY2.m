function LinealXYA=LinealXY2(yy,xx,t)

n0 = 1;
n = length(xx);
LinealXYA=0;
lin=0;

x(1:n,1)=xx(:,1);
y(1:n,1)=yy(:,1);

if t <= x(n0,1)
    lin = y(n0,1);
end
if t >= x(n,1)
    lin = y(n,1);
end
if ((t>x(n0,1)) && (t<x(n,1)))
i = n0;
while(x(i,1)<t)
  i = i + 1;
end
lin = y(i-1,1)*(t-x(i,1))/(x(i-1,1)-x(i,1))+y(i,1)*(t-x(i-1,1))/(x(i,1)-x(i-1,1));
end
LinealXYA = lin;