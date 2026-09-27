import json, numpy as np, time
from sim import Model
from femodel_lib import STATIONS, JOINTS
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']
ST=['S1','S2','S3','S4','S5']
# modal amplitudes at stations (mode 1, normalised to max |phi|)
phi=mdl.V[:,1]; phin=phi/np.max(np.abs(phi))
amp={s:float(phin[mdl.st[s]]) for s in ST}
node_z=float(mdl.zn[np.nonzero(np.diff(np.sign(phi)))[0][0]])
print('mode1 amplitudes at stations', {k:round(v,3) for k,v in amp.items()}, 'node z=%.2f'%node_z, 'phi at FK=%.3f'%phin[mdl.iFK])
# mass-proportional weights: Voronoi cells between stations
zs=np.array([STATIONS[s] for s in ST]); edges=np.r_[-1e9,(zs[1:]+zs[:-1])/2,1e9]
mw=[float(mdl.m[(mdl.zn>=edges[i])&(mdl.zn<edges[i+1])].sum()) for i in range(5)]
print('station tributary masses', np.round(mw,0))
L={'5 пар (1-1-1-1-1)':[1,1,1,1,1],'4 пары без S1':[0,1,1,1,1],'4 пары без S2':[1,0,1,1,1],'4 пары без S3':[1,1,0,1,1],
   '4 пары без S4':[1,1,1,0,1],'4 пары без S5':[1,1,1,1,0],'аналог 2-1-1':[2,0,1,1,0],'концевые S1+S5':[1,0,0,0,1],
   'узловая S2-S3-S4':[0,1,1,1,0],'пропорц. массе':mw}
def metrics(rec):
    t=rec['t']; X=rec['X']; xc=rec['xcm']; v=rec['vcm']
    w200=t<=0.2
    osc=X-np.interp(t,t,xc)  # FK displacement relative to CM
    def env(t0,t1):
        s=(t>=t0)&(t<t1); return 0.5*(osc[s].max()-osc[s].min())
    # arrest time: first time after 0.08 s when |vcm|<1e-3 for rest of record
    idx=np.nonzero(np.abs(v)>1e-3)[0]; ta=t[idx[-1]] if len(idx) else 0.0
    return dict(Xmax200=-X[w200].min()*1e3, Xfin=-xc[-1]*1e3, Xcm_max=-xc.min()*1e3, t_arrest=ta*1e3,
                A_100_130=env(0.10,0.13)*1e3, A_170_200=env(0.17,0.20)*1e3, A_300_330=env(0.30,0.33)*1e3,
                NJmax=np.abs(rec['NJ']).max()/1e6, dLrange=(rec['dL'].max()-rec['dL'].min())*1e3)
results={}
t0=time.time()
base,Eb=mdl.run({},T=0.6,p=PID); results['без тормозов']={0:{**metrics(base),**{k:float(v) for k,v in Eb.items()}}}
print('baseline', {k:round(v,3) for k,v in metrics(base).items()})
for name,w in L.items():
    results[name]={}
    for F in (30e3,100e3,200e3):
        ww=np.array(w,float); ww/=ww.sum(); Fb={s:F*x for s,x in zip(ST,ww)}
        rec,E=mdl.run(Fb,T=0.6,p=PID)
        m=metrics(rec); m.update({k:float(v) for k,v in E.items()})
        results[name][int(F/1e3)]=m
        print('%-20s F=%3d kN: Xmax200=%.2f Xfin=%.2f t_arr=%.0f A(100-130)=%.3f A(170-200)=%.3f A(300-330)=%.3f NJmax=%.3f dL=%.3f Dfr=%.0f J Ebal=%.1e'%(name,F/1e3,m['Xmax200'],m['Xfin'],m['t_arrest'],m['A_100_130'],m['A_170_200'],m['A_300_330'],m['NJmax'],m['dLrange'],E['Dfr'],E['balance_err']/E['Wext']), round(time.time()-t0))
json.dump(dict(results=results,amp=amp,node_z=node_z,mw=mw,layouts=L),open('layouts.json','w'),ensure_ascii=False)
