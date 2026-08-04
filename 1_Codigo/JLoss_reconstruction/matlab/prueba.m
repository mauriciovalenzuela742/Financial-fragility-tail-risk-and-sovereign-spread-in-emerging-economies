%prueba.m

m=[1	8	47;1	9	38;1	10	35;2	8	52;2	9	42;2	10	37;3	8	43;3	9	34;3	10	45];
%[hour,totals] = bucket(m(:,2),m(:,3))
[hour,totals,menas,stdev] = bucket(m(:,2),m(:,3))
% [day,totals,means,stdev] = bucket(m(:,1),m(:,3))