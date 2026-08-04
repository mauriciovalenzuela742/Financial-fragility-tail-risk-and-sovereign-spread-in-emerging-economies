function CNDA=CND(z)
%Cumulative Normal Distribution
    a = [0.31938153,-0.356563782,1.781477937,-1.821255978,1.330274429]';
    y = 1/(1+0.2316419*abs(z));
    CNDA = (1 /sqrt(2*pi)*exp(-0.5*z^2))*y*(a(1)+y*(a(2)+y*(a(3)+y*(a(4)+y*a(5)))));
    if z > 0 
        CNDA = 1-CNDA;
    end
    CNDA=CNDA;