import numpy as np, pickle, time
from scipy.stats import t as tdist
# ===== Monte Carlo ampliado, convencion GaR (beta3,beta4<0). Panel balanceado (N,T). =====
N,T,R = 45,80,1500
b1,b2,b3,b4 = 0.40,-0.30,-0.80,-3.0
K_absorb = N+T-1

def demean2(M):                       # M: (N,T) -> within bidireccional
    return M - M.mean(1,keepdims=True) - M.mean(0,keepdims=True) + M.mean()

def one(seed):
    rng=np.random.default_rng(seed)
    HHI_i=rng.uniform(0.06,0.34,N)
    f=np.zeros(T)
    for t in range(1,T): f[t]=0.7*f[t-1]+rng.normal(0,1)
    a_i=rng.normal(0,0.15,N); d_t=0.02*f+rng.normal(0,0.05,T)
    HHI=np.clip(HHI_i[:,None]+rng.normal(0,0.01,(N,T)),0.03,0.45)
    F=np.broadcast_to(f,(N,T))
    JL=np.clip(0.12+0.05*F+0.6*HHI+rng.normal(0,0.05,(N,T)),0.01,0.6)
    GaR=0.01-(0.25+0.8*HHI)*JL-0.02*F+rng.normal(0,0.015,(N,T))
    debt=np.clip(0.5+0.1*F+rng.normal(0,0.1,(N,T)),0.2,1.2)
    E=(a_i[:,None]+d_t[None,:]+b1*JL+b2*GaR+b3*JL*GaR+b4*JL*GaR*HHI+0.15*debt+rng.normal(0,0.03,(N,T)))
    # regresores
    cols={'JLoss':JL,'GaR':GaR,'JL_G':JL*GaR,'JL_G_HHI':JL*GaR*HHI,
          'JL_HHI':JL*HHI,'G_HHI':GaR*HHI,'debt':debt}
    names=list(cols); y=demean2(E).ravel()
    Xmats=[demean2(cols[c]) for c in names]
    X=np.column_stack([m.ravel() for m in Xmats])
    XtX=X.T@X; XtXi=np.linalg.inv(XtX); beta=XtXi@(X.T@y); e=y-X@beta
    # cluster por pais (fila i): reshape residuos y X a (N,T,k)
    k=X.shape[1]; Xr=X.reshape(N,T,k); er=e.reshape(N,T)
    meat=np.zeros((k,k))
    for i in range(N):
        s=Xr[i].T@er[i]; meat+=np.outer(s,s)
    G=N; n=N*T; dof=n-(k+K_absorb); adj=(G/(G-1))*((n-1)/dof)
    V=adj*(XtXi@meat@XtXi); se=np.sqrt(np.diag(V))
    tv=beta/se; pv=2*tdist.sf(np.abs(tv),G-1)
    idx={c:j for j,c in enumerate(names)}
    return (beta[idx['JL_G']],pv[idx['JL_G']],beta[idx['JL_G_HHI']],pv[idx['JL_G_HHI']],
            beta[idx['JLoss']],beta[idx['GaR']])

t0=time.time()
out=np.array([one(s) for s in range(R)])
b3h,p3,b4h,p4,b1h,b2h=out[:,0],out[:,1],out[:,2],out[:,3],out[:,4],out[:,5]
res=dict(N=N,T=T,R=R,true=dict(b1=b1,b2=b2,b3=b3,b4=b4),
    b3=b3h,b4=b4h,p3=p3,p4=p4,b1=b1h,b2=b2h,secs=time.time()-t0)
pickle.dump(res,open('/tmp/mc_gar.pkl','wb'))
print("R=%d N=%d T=%d  (%.1fs)"%(R,N,T,res['secs']))
print("beta1 mean=%+.3f (verd %.2f) ; beta2 mean=%+.3f (verd %.2f)"%(b1h.mean(),b1,b2h.mean(),b2))
print("beta3 (JLoss x GaR):     mean=%+.3f (verd %.2f)  %%<0=%.1f%%  potencia@5%%=%.1f%%"%(b3h.mean(),b3,100*(b3h<0).mean(),100*(p3<.05).mean()))
print("beta4 (JLoss x GaR x HHI): mean=%+.3f (verd %.2f)  %%<0=%.1f%%  potencia@5%%=%.1f%%  @10%%=%.1f%%"%(b4h.mean(),b4,100*(b4h<0).mean(),100*(p4<.05).mean(),100*(p4<.10).mean()))
EOF
echo "script escrito"; cd /sessions/loving-bold-knuth/mnt/outputs && nohup python3 mc_gar.py > /tmp/mc_run.log 2>&1 & echo "MC lanzado pid $!"