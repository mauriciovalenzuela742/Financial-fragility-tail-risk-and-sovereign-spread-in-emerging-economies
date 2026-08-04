"""
Fase III - Calibracion del modelo Cournot (competencia-fragilidad + JLoss).
Reproduce PD(n) en U (Prop.1), desplazamiento del minimo de JLoss (Prop.2)
y ES de fraccion de quiebras decreciente en n (Prop.3). Genera fase3_calibracion.png
"""
import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm, binom
from scipy.stats import multivariate_normal as mvn

A,mc,gam,rD,k,LGD,rho0,alpha,delta = 0.24,0.035,1.1,0.02,0.008,1.0,0.22,0.05,0.04
ns=np.arange(1,26)
RL=(A+ns*mc)/(ns+1); p=gam*RL                      # Cournot cerrado, demanda lineal
xbar=np.clip(((RL-rD)+k)/LGD,1e-9,1-1e-9)          # umbral de quiebra (margen+capital)
rho=lambda n,d: rho0*np.exp(-d*(n-1))
BVN=lambda a,b,r: float(mvn(mean=[0,0],cov=[[1,r],[r,1]]).cdf([a,b]))

# PD bancaria (Merton/Vasicek), U-shape
PD=np.array([norm.cdf((norm.ppf(p[i])-np.sqrt(1-rho0)*norm.ppf(xbar[i]))/np.sqrt(rho0)) for i in range(len(ns))])
# JLoss = ES sistemico de quiebras bancarias con correlacion rho(n)  (ec. 11)
jloss=lambda d: np.array([BVN(norm.ppf(PD[i]),norm.ppf(alpha),np.sqrt(rho(ns[i],d)))/alpha for i in range(len(ns))])
JL0,JLd=jloss(0.0),jloss(delta)

def sysES(i,d):                                     # ES finito-n de la fraccion de quiebras
    n=ns[i]; r=rho(n,d); zb=norm.ppf(PD[i])
    Zs=np.linspace(-6,6,400); w=norm.pdf(Zs)*(Zs[1]-Zs[0])
    q=norm.cdf((zb-np.sqrt(r)*Zs)/np.sqrt(1-r)); ks=np.arange(n+1); F=ks/n
    pmf=(w[:,None]*binom.pmf(ks[None,:],n,q[:,None])).sum(0); pmf/=pmf.sum()
    o=np.argsort(-F); mass=acc=0.0
    for f,pr in zip(F[o],pmf[o]):
        t=min(pr,alpha-mass); acc+=t*f; mass+=t
        if mass>=alpha: break
    return acc/alpha
ES=np.array([sysES(i,0.0) for i in range(len(ns))])
print("argmin PD=%d  JLoss(0)=%d  JLoss(%.2f)=%d"%(ns[np.argmin(PD)],ns[np.argmin(JL0)],delta,ns[np.argmin(JLd)]))
# (codigo de figura identico al del informe; omitido por brevedad)
