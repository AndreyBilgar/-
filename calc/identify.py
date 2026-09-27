import json, numpy as np
from scipy.optimize import least_squares
from femodel_lib import *
zn,K,Mm,ke=build()
w,V=modes(zn,K,Mm,nm=10)
M=Mm.sum(); print('M=%.1f  f=%s'%(M,np.round(w/2/np.pi,2)))
zeta1=0.0148; zeta=np.where(w>0, zeta1*w/w[1], 0)
phP=interp_mode(zn,V,1.28); phQ=interp_mode(zn,V,21.3); phFK=interp_mode(zn,V,Z_FK)
phA=interp_mode(zn,V,Z_A); phB=interp_mode(zn,V,Z_B)
P=json.load(open('exp1_proc.json')); tex=np.array(P['tu'])*1e-3; xex=np.array(P['xu'])*1e-3
dt=2e-5; t=np.arange(0.040,0.199,dt)
def pulse(t,t0,tau):
    s=(t-t0)/tau; return np.where((s>0)&(s<1), np.sin(np.pi*s)**2, 0.0)
def loads(p,t):
    P0,tP,tauP,Q0,tQ,tauQ,R0,tauR,Fr=p
    Pf=P0*1e6*pulse(t,tP*1e-3,tauP*1e-3)
    Qf=Q0*1e6*pulse(t,tQ*1e-3,tauQ*1e-3)
    tm=0.07007; Rf=np.where(t>tm, R0*1e3*np.exp(-(t-tm)/(tauR*1e-3)),0.0)
    return Pf,Qf,Rf,Fr*1e3
def simulate(p, t=t, out='fk'):
    Pf,Qf,Rf,Fr=loads(p,t)
    # generalized forces (P backward at breech, Q forward at FK taper, R backward at FK), rolling resistance on rigid mode only
    nm=len(w); q=np.zeros(nm); qd=np.zeros(nm)
    X=np.zeros(len(t)); DL=np.zeros(len(t)); V0=np.zeros(len(t))
    fg=np.outer(-Pf,phP)+np.outer(Qf-Rf,phQ)
    # Newmark average acceleration, per mode analytic coefficients
    for i in range(len(t)):
        f=fg[i].copy()
        # Coulomb rolling resistance on rigid-body mode (phi0 = 1/sqrt(M))
        vcm=qd[0]*V[0,0]*1.0 if False else qd[0]/np.sqrt(M)
        f[0]+= -Fr*np.tanh(vcm/1e-3)/np.sqrt(M)
        acc=f-2*zeta*w*qd-w**2*q
        # semi-implicit (symplectic) Euler is fine for dt=2e-5 << 1/f_max
        qd=qd+acc*dt; q=q+qd*dt
        X[i]=q@phFK; DL[i]=q@(phB-phA); V0[i]=qd[0]/np.sqrt(M)
    return X,DL,V0
sel=(tex>=0.045)&(tex<=0.198)
xin=lambda X: np.interp(tex[sel],t,X)
def resid(p):
    X,_,_=simulate(p); r=(xin(X)-xex[sel])*1e3
    return r
p0=[2.0,52.0,10.0,2.0,58.0,10.0,5.0,20.0,2.4]
lb=[0.05,45,3,0.05,50,3,0,1,0]; ub=[20,62,25,20,72,25,200,200,20]
best=None
for tQ0 in (56,60,63):
  for tauP0 in (8,12):
    p0[4]=tQ0; p0[2]=tauP0
    r=least_squares(resid,p0,bounds=(lb,ub),x_scale='jac',max_nfev=300)
    print('start',tQ0,tauP0,'cost',round(r.cost,2), np.round(r.x,3))
    if best is None or r.cost<best.cost: best=r
p=best.x; r=resid(p)
print('BEST params:', dict(zip(['P0 MN','tP ms','tauP ms','Q0 MN','tQ ms','tauQ ms','R0 kN','tauR ms','Fr kN'],np.round(p,3))))
print('rms misfit %.3f mm, max %.3f mm'%(np.sqrt(np.mean(r**2)),np.max(abs(r))))
X,DL,V0=simulate(p)
Pf,Qf,Rf,Fr=loads(p,t)
IP=np.trapezoid(Pf,t); IQ=np.trapezoid(Qf,t); IR=np.trapezoid(Rf,t)
print('impulses: P %.0f N s, Q %.0f N s, R %.0f N s; net %.0f; M*v(198ms)=%.0f'%(IP,IQ,IR,IQ-IP-IR,M*V0[-1]))
print('peak CM velocity %.3f m/s at %.1f ms; v(80ms)=%.3f; v(198)=%.3f'%(V0.min(),t[V0.argmin()]*1e3,np.interp(0.08,t,V0),V0[-1]))
print('sim dL range %.3f mm (max %.3f min %.3f)'%((DL.max()-DL.min())*1e3,DL.max()*1e3,DL.min()*1e3))
json.dump(dict(p=p.tolist(), t=t.tolist(), X=X.tolist(), DL=DL.tolist(), V0=V0.tolist(), P=Pf.tolist(), Q=Qf.tolist(), R=Rf.tolist()), open('ident.json','w'))
