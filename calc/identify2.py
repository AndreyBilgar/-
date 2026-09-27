import json, numpy as np
from scipy.optimize import least_squares
exec(open('identify.py').read().split("p0=[2.0")[0])
names=['P0 MN','tP ms','tauP ms','Q0 MN','tQ ms','tauQ ms','Fr kN']
def full(p7): return [p7[0],p7[1],p7[2],p7[3],p7[4],p7[5],0.0,10.0,p7[6]]
def resid7(p7): return resid(full(p7))
best=None
for s in ([2.9,48.9,8.5,1.8,63.7,14.2,3.0],[2.5,50,10,2.5,60,10,2.0],[3.5,48,7,1.5,65,16,5]):
    r=least_squares(resid7,s,bounds=([0.05,44,3,0.05,50,3,0],[20,62,25,20,75,30,30]),x_scale='jac',max_nfev=400)
    print('cost',round(r.cost,3),np.round(r.x,3))
    if best is None or r.cost<best.cost: best=r
p=best.x; r=resid7(p); dof=len(r)-len(p)
J=best.jac; s2=np.sum(r**2)/dof
# data points are strongly autocorrelated (0.1 ms sampling vs ~1 px digitization); inflate by effective sample factor
neff=len(r)/ (0.2/0.1*5)  # ~ one independent sample per 1 ms
cov=np.linalg.inv(J.T@J)*s2*len(r)/neff
se=np.sqrt(np.diag(cov))
for n,v,e in zip(names,p,se): print(f'  {n:8s} = {v:8.3f} +- {e:.3f}')
print('rms %.3f mm'%np.sqrt(np.mean(r**2)))
X,DL,V0=simulate(full(p)); Pf,Qf,Rf,Fr=loads(full(p),t)
IP=np.trapezoid(Pf,t); IQ=np.trapezoid(Qf,t)
print('I_P=%.0f I_Q=%.0f net=%.0f N s; vmin=%.3f at %.1f ms; v(80)=%.3f v(198)=%.3f'%(IP,IQ,IQ-IP,V0.min(),t[V0.argmin()]*1e3,np.interp(0.08,t,V0),V0[-1]))
C=cov/np.outer(se,se); print('corr(Q0,Fr)=%.2f corr(P0,Q0)=%.2f corr(P0,tauP)=%.2f'%(C[3,6],C[0,3],C[0,2]))
json.dump(dict(p=list(full(p)), se=se.tolist(), t=t.tolist(), X=X.tolist(), DL=DL.tolist(), V0=V0.tolist(), P=Pf.tolist(), Q=Qf.tolist()), open('ident2.json','w'))
