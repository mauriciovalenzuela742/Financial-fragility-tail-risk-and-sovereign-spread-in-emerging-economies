function g=ghi(n)

EPS = 0.0000000000001;
PIM4 = 1/pi^0.25;
m = (n+1)/2;
x=zeros(n,1);
w=zeros(n,1);
for i = 1:m
        if i == 1
            z = sqrt(2*n+1)-1.85575*(2*n+1)^(-0.16667);
        elseif i == 2
            z = z - 1.14*n^0.426/z;
        elseif i == 3
            z = 1.86*z - 0.86*x(1,1);
        elseif i == 4
            z = 1.91*z - 0.91*x(2,1);
        else
            z = 2*z - x(i-2,1);
        end
        dif=1;
        while (abs(dif)>=EPS),
            p1 = PIM4;
            p2 = 0;
            for j = 1:n
                p3 = p2;
                p2 = p1;
                p1 = z*sqrt(2/j)*p2-sqrt((j-1)/j)*p3;
            end
            pp = sqrt(2*n)*p2;
            z1 = z;
            z = z1-p1/pp;
            dif = z-z1;
        end
        x(i,1) = z;
        x(n+1-i,1) = -z;
        w(i,1) = 2/pp^2;
        w(n+1-i,1) = w(i,1);
end

zz=zeros(n,2);
    for i = 1:n
        zz(i, 1) = x(n+1-i,1) * sqrt(2);
        zz(i, 2) = w(n+1-i,1) / sqrt(pi);
    end
g=zz;