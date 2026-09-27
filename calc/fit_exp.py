import json, numpy as np
from scipy.optimize import least_squares
from scipy.signal import savgol_filter, argrelextrema
D=json.load(open('fig3_digitized.json'))
t=np.array(D['t']); x=np.array(D['x'])
m=t<=199.0; t=t[m]; x=x[m]
# resample uniform 0.1 ms
tu=np.arange(1.0,199.0,0.1); xu=np.interp(tu,t,x)
xs=savgol_filter(xu, 31, 3)
# extrema after 60 ms
idx_max=argrelextrema(xs, np.greater, order=25)[0]; idx_min=argrelextrema(xs, np.less, order=25)[0]
ext=sorted([(tu[i],xs[i],'max') for i in idx_max if tu[i]>60]+[(tu[i],xs[i],'min') for i in idx_min if tu[i]>60])
labels=[67.13,71.43,80.48,88.35,96.62,103.96,112.78,119.51,128.52,135.00,143.73,151.08,159.41,166.17,174.92,181.61,189.66,196.71]
print('digitized extrema vs labels:')
E=[]
for (te,xe,k) in ext:
    lab=min(labels,key=lambda L:abs(L-te)); E.append((te,xe,k,lab)); print(f"  {k} t={te:7.2f} (label {lab:7.2f}, diff {te-lab:+.2f}) x={xe:7.2f}")
# half periods from labels (as in article)
L=np.array(labels)
# labels are alternating min,max,... starting 67.13 (min)
dn=[]; up=[]
for i in range(len(L)-1):
    d=L[i+1]-L[i]
    (up if i%2==0 else dn).append(d)   # min->max = up(extension toward +), max->min = down
print('min->max (rise) mean %.3f ms  n=%d'%(np.mean(up),len(up)), np.round(up,2))
print('max->min (fall) mean %.3f ms  n=%d'%(np.mean(dn),len(dn)), np.round(dn,2))
# article used 19 extrema starting with 57.25? check periods from labels excluding first
Tm=[L[i+2]-L[i] for i in range(len(L)-2)]
print('full periods mean %.3f std %.3f'%(np.mean(Tm),np.std(Tm,ddof=1)))
# minima and maxima sequences
mins=[(te,xe) for te,xe,k,l in E if k=='min']; maxs=[(te,xe) for te,xe,k,l in E if k=='max']
json.dump(dict(tu=tu.tolist(),xu=xu.tolist(),xs=xs.tolist(),ext=E), open('exp1_proc.json','w'))
# ---- model fit for t>=72 ms
def model(p,tt):
    a0,a1,a2,A,al,w,ph=p; tau=(tt-72.0)*1e-3
    return a0+a1*tau+a2*tau**2+A*np.exp(-al*tau)*np.cos(w*tau+ph)
sel=(tu>=72)&(tu<=198)
p0=[-12.5,-100.0,0.0,2.0,7.0,2*np.pi*64.6,0.0]
best=None
for ph0 in np.linspace(-np.pi,np.pi,12,endpoint=False):
    p0[-1]=ph0
    r=least_squares(lambda p:model(p,tu[sel])-xu[sel], p0)
    if best is None or r.cost<best.cost: best=r
p=best.x; res=model(p,tu[sel])-xu[sel]
J=best.jac; cov=np.linalg.inv(J.T@J)*np.sum(res**2)/(len(res)-len(p)); se=np.sqrt(np.diag(cov))
names=['a0 mm','v mm/s','a2 mm/s2','A mm','alpha 1/s','omega rad/s','phi']
for n,v,s in zip(names,p,se): print(f"  {n:12s} = {v:12.4f} +- {s:.4f}")
f=p[5]/2/np.pi; print('f=%.2f Hz, T=%.3f ms, zeta=%.4f, rms residual=%.3f mm'%(f,1000/f,p[4]/p[5],np.sqrt(np.mean(res**2))))
print('drift velocity at 72 ms = %.4f m/s, decel = %.3f m/s2 (a=2*a2)'%(p[1]*1e-3, 2*p[2]*1e-3))
# half-period asymmetry predicted by drift
v=abs(p[1]+2*p[2]*0.06)*1e-3; A=abs(p[3])*np.exp(-p[4]*0.06)*1e-3; w=p[5]
beta=np.arcsin(v/(A*w)); print('mid-window v=%.4f m/s A=%.3f mm beta=%.4f rad -> dT=4beta/w=%.3f ms'%(v,A*1e3,beta,4*beta/w*1e3))
json.dump(dict(p=p.tolist(),se=se.tolist()), open('fit1.json','w'))
