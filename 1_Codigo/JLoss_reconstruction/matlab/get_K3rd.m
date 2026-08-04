function k3rd=get_K3rd(n_ctrp,mult_a, a, e_tot, p_def, saddle)
k3rd=0;
for i=1:n_ctrp
denom =(1-p_def(i)+p_def(i)*exp(saddle*a(i)));
k3rd = k3rd+mult_a(i)*(p_def(i)*a(i)*a(i)*a(i)*exp(a(i)*saddle)/denom-...
3*p_def(i)*p_def(i)*a(i)*a(i)*a(i)*exp(2*saddle*a(i))/(denom*denom)+...
2*p_def(i)*p_def(i)*p_def(i)*a(i)*a(i)*a(i)*exp(3*saddle*a(i))/(denom*denom*denom));
end
k3rd=k3rd;