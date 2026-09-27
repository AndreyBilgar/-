import json, numpy as np, time
from scipy.optimize import least_squares
from sim import Model
mdl=Model()
P=json.load(open('exp1_proc.json')); tex=np.array(P['tu'])*1e-3; xex=np.array(P['xu'])*1e-3
sel=(tex>=0.045)&(tex<=0.198)
ID=json.load(open('ident2.json'))['p']
def full(p7): return [p7[0],p7[1],p7[2],p7[3],p7[4],p7[5],0.0,10.0,p7[6]]
def resid(p7):
    rec,E=mdl.run({},T=0.199,p=full(p7),rec_every=5)
    return (np.interp(tex[sel],rec['t'],rec['X'])-xex[sel])*1e3
p0=[ID[0],ID[1],ID[2],ID[3],ID[4],ID[5],ID[8]]
t0=time.time()
r=least_squares(resid,p0,bounds=([0.05,44,3,0.05,50,3,0],[20,62,25,20,75,30,30]),x_scale='jac',max_nfev=200,diff_step=1e-3)
print('time %.0f s'%(time.time()-t0))
p=r.x; res=r.fun
J=r.jac; s2=np.sum(res**2)/(len(res)-len(p)); neff=len(res)/10
cov=np.linalg.inv(J.T@J)*s2*len(res)/neff; se=np.sqrt(np.diag(cov))
names=['P0 MN','tP ms','tauP ms','Q0 MN','tQ ms','tauQ ms','Fr kN']
for n,v,e in zip(names,p,se): print(f'  {n:8s} = {v:8.3f} +- {e:.3f}')
print('rms %.3f mm max %.3f mm'%(np.sqrt(np.mean(res**2)),np.abs(res).max()))
IP=p[0]*1e6*p[2]*1e-3/2; IQ=p[3]*1e6*p[5]*1e-3/2; eIP=IP*np.sqrt((se[0]/p[0])**2+(se[2]/p[2])**2+2*np.corrcoef(cov)[0,2]*0)
print('I_P=%.0f I_Q=%.0f N s'%(IP,IQ))
json.dump(dict(p=full(p),se=se.tolist(),cov=cov.tolist()), open('ident_phys.json','w'))
rec,E=mdl.run({},T=0.2,p=full(p))
print('Energy:',{k:round(float(v),1) for k,v in E.items()}, 'rel %.1e'%(E['balance_err']/E['Wext']))
print('vcm min %.3f at %.1f ms; v(80)=%.4f; v(200)=%.4f'%(rec['vcm'].min(),rec['t'][rec['vcm'].argmin()]*1e3,np.interp(0.08,rec['t'],rec['vcm']),rec['vcm'][-1]))
