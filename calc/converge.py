import json, numpy as np
from sim import Model
PID=json.load(open('ident_phys.json'))['p']
ST=['S1','S2','S3','S4','S5']
res={}
for dz in (0.2,0.1,0.05):
    m=Model(dz=dz)
    for lab,F in (('0',0),('100',100e3)):
        for fac in ((0.4,0.2) if dz==0.1 else (0.4,)):
            rec,E=m.run({s:F/5 for s in ST} if F else {},T=0.6,p=PID,dt=fac*m.dtcrit)
            t=rec['t']; key='dz=%.2f F=%s dt=%.1fdtcr'%(dz,lab,fac)
            res[key]=dict(f1=m.w[1]/2/np.pi, X200=-rec['X'][t<=0.2].min()*1e3, Xfin=-rec['xcm'][-1]*1e3, NJ=np.abs(rec['NJ']).max()/1e6, dL=(rec['dL'].max()-rec['dL'].min())*1e3, err=E['balance_err']/E['Wext'])
            print(key, {k:round(v,4) for k,v in res[key].items()})
json.dump(res,open('converge.json','w'))
