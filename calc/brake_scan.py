import json, numpy as np, time
from sim import Model
from scipy.optimize import brentq
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']
ST=['S1','S2','S3','S4','S5']
def run(Ftot, weights=None, T=0.2, kb=5.6e8, stop=False):
    w=np.ones(5) if weights is None else np.array(weights,float)
    w=w/w.sum(); Fb={s:Ftot*wi for s,wi in zip(ST,w)}
    return mdl.run(Fb,T=T,p=PID,kb=kb,stop_check=stop)
t0=time.time()
out=[]
for F in [0,5e3,10e3,20e3,30e3,50e3,100e3,200e3]:
    rec,E=run(F)
    X=rec['X']; out.append((F, -X.min()*1e3, -X[-1]*1e3))
    print('F=%6.0f kN  max|X_FK|(0-200ms)=%.2f mm  X(200)=%.2f  vcm(200)=%.4f  Ebal=%.1e'%(F/1e3,-X.min()*1e3,-X[-1]*1e3,rec['vcm'][-1],E['balance_err']/E['Wext']), round(time.time()-t0,1))
json.dump(out,open('scan_window.json','w'))
f=lambda F,target: -run(F)[0]['X'].min()*1e3-target
for target in (18.0,17.0):
    F=brentq(f,0,200e3,xtol=100); print('target %.0f mm -> F_sum = %.1f kN'%(target,F/1e3))
