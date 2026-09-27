import json, numpy as np, time
from scipy.optimize import minimize
from sim import Model
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']
ST=['S1','S2','S3','S4','S5']
def evalw(w,F,T=0.45):
    w=np.clip(np.array(w,float),0,None); w=w/w.sum()
    rec,E=mdl.run({s:F*x for s,x in zip(ST,w)},T=T,p=PID)
    t=rec['t']; osc=rec['X']-rec['xcm']; s=(t>=0.17)&(t<0.20)
    A=0.5*(osc[s].max()-osc[s].min())*1e3
    return -rec['xcm'][-1]*1e3, A, -rec['X'][t<=0.2].min()*1e3
res={}
for F in (30e3,60e3):
    Xu,Au,Mu=evalw([1,1,1,1,1],F)
    print('F=%d kN uniform: Xfin=%.2f A170=%.3f Xmax200=%.2f'%(F/1e3,Xu,Au,Mu))
    hist=[]
    def obj(z):
        w=np.exp(z); X,A,Mx=evalw(w,F); pen=100*max(0,A-Au)
        hist.append((w/w.sum(),X,A)); return X+pen
    t0=time.time()
    r=minimize(obj,np.zeros(5),method='Nelder-Mead',options=dict(maxfev=70,xatol=0.05,fatol=0.02,initial_simplex=np.vstack([np.zeros(5),0.7*np.eye(5)])))
    w=np.exp(r.x); w/=w.sum(); X,A,Mx=evalw(w,F)
    print('  optimum weights', np.round(w,3), 'Xfin=%.2f A170=%.3f Xmax200=%.2f  (%d evals, %.0f s)'%(X,A,Mx,len(hist),time.time()-t0))
    res[int(F/1e3)]=dict(uniform=[Xu,Au,Mu],w=w.tolist(),opt=[X,A,Mx])
json.dump(res,open('optim.json','w'))
